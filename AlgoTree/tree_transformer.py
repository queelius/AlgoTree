"""
Tree transformation functionality.

This module provides transformation capabilities for tree structures,
allowing users to modify trees while preserving their structure (closed transformations).
Inspired by dotsuite's Shape pillar.
"""

from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from copy import deepcopy
from .node import Node
from .pattern_matcher import dotmatch, Pattern, PatternMatcher


def dotmod(tree: Node, 
          transformations: Union[Dict[str, Any], List[Tuple[str, Any]]],
          in_place: bool = False) -> Node:
    """
    Apply closed tree-to-tree transformations using dot notation paths.
    
    This function modifies nodes in the tree based on dot notation paths,
    preserving the tree structure (closed transformation).
    
    Args:
        tree: Tree to transform
        transformations: Either:
            - Dict mapping dot paths to transformations
            - List of (dot_path, transformation) tuples
        in_place: If True, modify tree in place; otherwise create a copy
        
    Returns:
        Transformed tree (same object if in_place=True, copy otherwise)
        
    Transformations can be:
        - Dict: Update node payload with dict contents
        - Callable: Apply function to node (receives node, returns dict to update payload)
        - String: Rename the node
        - None: Clear the payload (but keep the node)
        
    Examples:
        # Update specific nodes
        tree = dotmod(tree, {
            "app.config": {"version": "2.0", "debug": False},
            "app.database": {"host": "localhost", "port": 5432}
        })
        
        # Rename nodes
        tree = dotmod(tree, {
            "app.oldname": "newname"
        })
        
        # Apply functions
        tree = dotmod(tree, {
            "app.**.file": lambda n: {"size": n.payload.get("size", 0) * 2}
        })
        
        # Multiple transformations to same path pattern
        tree = dotmod(tree, [
            ("app.**.test_*", lambda n: {"tested": True}),
            ("app.**.test_*", lambda n: {"priority": "high"})
        ])
    """
    # Work on a copy unless in_place is True
    if not in_place:
        tree = deepcopy(tree)
    
    # Normalize transformations to list of tuples
    if isinstance(transformations, dict):
        transform_list = list(transformations.items())
    else:
        transform_list = transformations
    
    # Apply each transformation
    for dot_path, transformation in transform_list:
        # Find matching nodes
        matches = dotmatch(tree, dot_path)
        
        for node in matches:
            if transformation is None:
                # Clear payload
                node.payload.clear()
            elif isinstance(transformation, str):
                # Rename node
                node.name = transformation
            elif isinstance(transformation, dict):
                # Update payload
                node.payload.update(transformation)
            elif callable(transformation):
                # Apply function
                result = transformation(node)
                if isinstance(result, str):
                    node.name = result
                elif isinstance(result, dict):
                    node.payload.update(result)
                elif result is None:
                    node.payload.clear()
                else:
                    raise ValueError(f"Transformation function must return str, dict, or None, got {type(result)}")
            else:
                raise ValueError(f"Invalid transformation type: {type(transformation)}")
    
    return tree


def dotmap(tree: Node,
          mapper: Union[Callable[[Node], Dict[str, Any]], Dict[str, Callable]],
          dot_path: str = "**",
          in_place: bool = False) -> Node:
    """
    Map a transformation function over nodes matching a pattern.
    
    This is a convenience function that applies the same transformation
    to all nodes matching a pattern.
    
    Args:
        tree: Tree to transform
        mapper: Either:
            - Function that takes a node and returns dict to update payload
            - Dict mapping payload keys to transformation functions
        dot_path: Pattern to match nodes (default "**" for all nodes)
        in_place: If True, modify tree in place
        
    Returns:
        Transformed tree
        
    Examples:
        # Double all sizes
        tree = dotmap(tree, lambda n: {"size": n.payload.get("size", 0) * 2})
        
        # Transform specific fields
        tree = dotmap(tree, {
            "size": lambda v: v * 2,
            "name": lambda v: v.upper(),
            "timestamp": lambda v: str(v)
        })
        
        # Apply only to specific nodes
        tree = dotmap(tree, 
                     lambda n: {"processed": True},
                     dot_path="app.data.**")
    """
    if not in_place:
        tree = deepcopy(tree)
    
    matches = dotmatch(tree, dot_path)
    
    for node in matches:
        if callable(mapper):
            # Single function mapper
            result = mapper(node)
            if isinstance(result, dict):
                node.payload.update(result)
        elif isinstance(mapper, dict):
            # Dict of field mappers
            for key, func in mapper.items():
                if key in node.payload:
                    node.payload[key] = func(node.payload[key])
    
    return tree


def dotprune(tree: Node,
            condition: Union[str, Callable[[Node], bool]],
            keep_structure: bool = False,
            in_place: bool = False) -> Node:
    """
    Prune nodes from tree based on condition.
    
    Args:
        tree: Tree to prune
        condition: Either:
            - Dot path pattern of nodes to remove
            - Predicate function (returns True for nodes to remove)
        keep_structure: If True, replace pruned nodes with empty placeholders
        in_place: If True, modify tree in place
        
    Returns:
        Pruned tree
        
    Examples:
        # Remove all test files
        tree = dotprune(tree, "**.test_*")
        
        # Remove empty directories
        tree = dotprune(tree, lambda n: n.payload.get("type") == "dir" and len(n.children) == 0)
        
        # Keep structure but clear nodes
        tree = dotprune(tree, "**.deprecated", keep_structure=True)
    """
    if not in_place:
        tree = deepcopy(tree)
    
    # Get nodes to prune
    if isinstance(condition, str):
        # Dot path pattern
        nodes_to_prune = set(dotmatch(tree, condition))
    else:
        # Predicate function
        nodes_to_prune = set(n for n in tree.traverse_preorder() if condition(n))
    
    # Prune nodes
    def prune_recursive(node: Node, parent: Optional[Node] = None) -> Optional[Node]:
        if node in nodes_to_prune:
            if keep_structure:
                # Keep node but clear it
                node.payload.clear()
                node.children.clear()
                return node
            else:
                # Remove node entirely
                return None
        
        # Process children
        new_children = []
        for child in list(node.children):
            pruned_child = prune_recursive(child, node)
            if pruned_child is not None:
                new_children.append(pruned_child)
        
        node.children = new_children
        
        # Update parent references
        for child in node.children:
            child.parent = node
        
        return node
    
    result = prune_recursive(tree)
    return result if result else Node("empty")


def dotmerge(tree1: Node,
            tree2: Node,
            merge_strategy: str = "overlay",
            conflict_resolver: Optional[Callable[[Node, Node], Node]] = None,
            in_place: bool = False) -> Node:
    """
    Merge two trees using various strategies.
    
    Args:
        tree1: First tree (base)
        tree2: Second tree (overlay)
        merge_strategy: Strategy for merging:
            - "overlay": tree2 values override tree1
            - "underlay": tree1 values take precedence
            - "combine": merge payloads, keeping both values
            - "custom": use conflict_resolver function
        conflict_resolver: Function to resolve conflicts (for custom strategy)
        in_place: If True, modify tree1 in place
        
    Returns:
        Merged tree
        
    Examples:
        # Simple overlay merge
        merged = dotmerge(tree1, tree2, "overlay")
        
        # Custom conflict resolution
        def resolver(node1, node2):
            # Combine arrays, prefer tree2 for other values
            merged_payload = {}
            for key in set(node1.payload.keys()) | set(node2.payload.keys()):
                if key in node1.payload and key in node2.payload:
                    val1, val2 = node1.payload[key], node2.payload[key]
                    if isinstance(val1, list) and isinstance(val2, list):
                        merged_payload[key] = val1 + val2
                    else:
                        merged_payload[key] = val2
                elif key in node1.payload:
                    merged_payload[key] = node1.payload[key]
                else:
                    merged_payload[key] = node2.payload[key]
            return Node(node2.name, **merged_payload)
        
        merged = dotmerge(tree1, tree2, "custom", conflict_resolver=resolver)
    """
    if not in_place:
        tree1 = deepcopy(tree1)
    
    def merge_nodes(node1: Node, node2: Node):
        """Merge node2 into node1."""
        if merge_strategy == "overlay":
            # tree2 overrides tree1
            node1.payload.update(node2.payload)
        elif merge_strategy == "underlay":
            # tree1 takes precedence
            for key, value in node2.payload.items():
                if key not in node1.payload:
                    node1.payload[key] = value
        elif merge_strategy == "combine":
            # Merge payloads, combining values
            for key, value in node2.payload.items():
                if key in node1.payload:
                    val1 = node1.payload[key]
                    if isinstance(val1, list) and isinstance(value, list):
                        node1.payload[key] = val1 + value
                    elif isinstance(val1, dict) and isinstance(value, dict):
                        val1.update(value)
                    else:
                        # Default to overlay for non-combinable types
                        node1.payload[key] = value
                else:
                    node1.payload[key] = value
        elif merge_strategy == "custom":
            if conflict_resolver:
                merged = conflict_resolver(node1, node2)
                node1.name = merged.name
                node1.payload = merged.payload
            else:
                raise ValueError("conflict_resolver required for custom merge strategy")
        else:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")
    
    def merge_recursive(node1: Node, node2: Node):
        """Recursively merge trees."""
        # Merge current nodes
        merge_nodes(node1, node2)
        
        # Build child map for node1
        child_map = {child.name: child for child in node1.children}
        
        # Keep track of merged children
        merged_children = set()
        
        # Merge children
        for child2 in node2.children:
            if child2.name in child_map:
                # Recursively merge matching children
                merge_recursive(child_map[child2.name], child2)
                merged_children.add(child2.name)
            else:
                # Add new child from tree2
                new_child = deepcopy(child2)
                new_child.parent = node1
                node1.children.append(new_child)
    
    # Perform merge
    merge_recursive(tree1, tree2)
    return tree1


def dotgraft(tree: Node,
            graft_point: str,
            subtree: Node,
            position: Union[int, str] = "append",
            in_place: bool = False) -> Node:
    """
    Graft a subtree onto a tree at specified point(s).
    
    Args:
        tree: Tree to graft onto
        graft_point: Dot path to graft point(s)
        subtree: Subtree to graft
        position: Where to add the subtree:
            - "append": Add at end of children (default)
            - "prepend": Add at beginning of children
            - int: Insert at specific index
            - "replace": Replace existing children
        in_place: If True, modify tree in place
        
    Returns:
        Tree with grafted subtree
        
    Examples:
        # Add new module to app
        new_module = Node("auth", type="module")
        tree = dotgraft(tree, "app.modules", new_module)
        
        # Insert at specific position
        tree = dotgraft(tree, "app.modules", new_module, position=0)
        
        # Replace children
        tree = dotgraft(tree, "app.old_modules", new_modules, position="replace")
    """
    if not in_place:
        tree = deepcopy(tree)
    
    graft_points = dotmatch(tree, graft_point)
    
    for point in graft_points:
        # Create a copy of the subtree for each graft point
        graft_copy = deepcopy(subtree)
        
        if position == "append":
            # Use proper method from Node class
            point.children.append(graft_copy)
            graft_copy.parent = point
        elif position == "prepend":
            point.children.insert(0, graft_copy)
            graft_copy.parent = point
        elif position == "replace":
            point.children.clear()
            point.children.append(graft_copy)
            graft_copy.parent = point
        elif isinstance(position, int):
            point.children.insert(position, graft_copy)
            graft_copy.parent = point
        else:
            raise ValueError(f"Invalid position: {position}")
    
    return tree


def dotsplit(tree: Node,
            split_point: str,
            include_point: bool = True) -> Tuple[Node, List[Node]]:
    """
    Split tree at specified point(s), extracting subtrees.
    
    Args:
        tree: Tree to split
        split_point: Dot path to split point(s)
        include_point: If True, include split point in extracted subtrees
        
    Returns:
        Tuple of (modified tree, list of extracted subtrees)
        
    Examples:
        # Extract all test modules
        tree, test_modules = dotsplit(tree, "**.tests")
        
        # Extract but keep the container node
        tree, extracted = dotsplit(tree, "app.deprecated", include_point=False)
    """
    tree_copy = deepcopy(tree)
    split_points = dotmatch(tree_copy, split_point)
    extracted = []
    
    # Process in reverse to avoid issues with modifying while iterating
    for point in reversed(split_points):
        if include_point:
            # Extract the entire node
            extracted.append(deepcopy(point))
            
            # Remove from parent
            if point.parent:
                try:
                    point.parent.children.remove(point)
                except ValueError:
                    pass  # Already removed
        else:
            # Extract only children
            for child in list(point.children):
                extracted.append(deepcopy(child))
            
            # Clear children
            point.children.clear()
    
    return tree_copy, extracted


def dotflatten(tree: Node,
              flatten_pattern: str = "**",
              max_depth: Optional[int] = None) -> List[Node]:
    """
    Flatten tree structure into a list of nodes.
    
    Args:
        tree: Tree to flatten
        flatten_pattern: Pattern for nodes to include
        max_depth: Maximum depth to flatten to
        
    Returns:
        List of nodes (flattened)
        
    Examples:
        # Get all nodes as flat list
        all_nodes = dotflatten(tree)
        
        # Get only file nodes
        files = dotflatten(tree, "**[type=file]")
        
        # Flatten only top 3 levels
        top_nodes = dotflatten(tree, max_depth=3)
    """
    matches = dotmatch(tree, flatten_pattern)
    
    if max_depth is not None:
        matches = [n for n in matches if n.level <= max_depth]
    
    return matches


def dotreduce(tree: Node,
             reducer: Callable[[Any, Node], Any],
             initial: Any = None,
             traverse_pattern: str = "**") -> Any:
    """
    Reduce tree to a single value using a reducer function.
    
    Args:
        tree: Tree to reduce
        reducer: Function (accumulator, node) -> new_accumulator
        initial: Initial value for accumulator
        traverse_pattern: Pattern for nodes to include in reduction
        
    Returns:
        Reduced value
        
    Examples:
        # Sum all sizes
        total_size = dotreduce(tree, 
                              lambda acc, n: acc + n.payload.get("size", 0),
                              initial=0)
        
        # Collect all names
        names = dotreduce(tree,
                         lambda acc, n: acc + [n.name],
                         initial=[])
        
        # Find maximum depth
        max_depth = dotreduce(tree,
                            lambda acc, n: max(acc, n.level),
                            initial=0)
    """
    nodes = dotmatch(tree, traverse_pattern)
    accumulator = initial
    
    for node in nodes:
        accumulator = reducer(accumulator, node)
    
    return accumulator


def dotannotate(tree: Node,
               annotator: Union[Callable[[Node], Dict[str, Any]], Dict[str, Any]],
               annotation_key: str = "_annotation",
               dot_path: str = "**",
               in_place: bool = False) -> Node:
    """
    Add annotations to nodes in the tree.
    
    Args:
        tree: Tree to annotate
        annotator: Either:
            - Function that returns annotation dict for each node
            - Static annotation dict to add to all matching nodes
        annotation_key: Key to store annotations under in payload
        dot_path: Pattern for nodes to annotate
        in_place: If True, modify tree in place
        
    Returns:
        Annotated tree
        
    Examples:
        # Add computed annotations
        tree = dotannotate(tree,
                          lambda n: {
                              "depth": n.level,
                              "has_children": len(n.children) > 0,
                              "path": ".".join(p.name for p in n.get_path())
                          })
        
        # Add static annotations to specific nodes
        tree = dotannotate(tree,
                          {"reviewed": True, "version": "1.0"},
                          dot_path="**.critical_*")
    """
    if not in_place:
        tree = deepcopy(tree)
    
    nodes = dotmatch(tree, dot_path)
    
    for node in nodes:
        if callable(annotator):
            annotation = annotator(node)
        else:
            annotation = annotator
        
        node.payload[annotation_key] = annotation
    
    return tree


def dotvalidate(tree: Node,
               validator: Union[Callable[[Node], bool], Dict[str, Any]],
               dot_path: str = "**",
               raise_on_invalid: bool = True) -> Union[bool, List[Node]]:
    """
    Validate nodes in the tree against criteria.
    
    Args:
        tree: Tree to validate
        validator: Either:
            - Predicate function returning True for valid nodes
            - Dict of required attributes and values
        dot_path: Pattern for nodes to validate
        raise_on_invalid: If True, raise exception on first invalid node
        
    Returns:
        If raise_on_invalid=False: List of invalid nodes (empty if all valid)
        If raise_on_invalid=True: True if all valid (raises otherwise)
        
    Examples:
        # Validate with function
        dotvalidate(tree,
                   lambda n: n.payload.get("size", 0) < 1000000,
                   dot_path="**[type=file]")
        
        # Validate required attributes
        dotvalidate(tree,
                   {"type": "file", "tested": True},
                   dot_path="app.src.**")
        
        # Get list of invalid nodes
        invalid = dotvalidate(tree,
                            lambda n: len(n.name) <= 255,
                            raise_on_invalid=False)
    """
    nodes = dotmatch(tree, dot_path)
    invalid_nodes = []
    
    for node in nodes:
        is_valid = True
        
        if callable(validator):
            is_valid = validator(node)
        elif isinstance(validator, dict):
            for key, expected_value in validator.items():
                if key not in node.payload or node.payload[key] != expected_value:
                    is_valid = False
                    break
        
        if not is_valid:
            if raise_on_invalid:
                path = ".".join(n.name for n in node.get_path())
                raise ValueError(f"Invalid node at path: {path}")
            invalid_nodes.append(node)
    
    if raise_on_invalid:
        return True
    return invalid_nodes


def dotnormalize(tree: Node,
                normalizer: Optional[Callable[[str], str]] = None,
                normalize_payload: bool = False,
                in_place: bool = False) -> Node:
    """
    Normalize node names and optionally payload keys.
    
    Args:
        tree: Tree to normalize
        normalizer: Function to normalize names (default: lowercase + underscore)
        normalize_payload: If True, also normalize payload keys
        in_place: If True, modify tree in place
        
    Returns:
        Normalized tree
        
    Examples:
        # Default normalization (lowercase, spaces to underscores)
        tree = dotnormalize(tree)
        
        # Custom normalization
        tree = dotnormalize(tree,
                          normalizer=lambda s: s.lower().replace("-", "_"))
        
        # Also normalize payload keys
        tree = dotnormalize(tree, normalize_payload=True)
    """
    if not in_place:
        tree = deepcopy(tree)
    
    if normalizer is None:
        def normalizer(s: str) -> str:
            # Default: lowercase, spaces/dashes to underscores
            return s.lower().replace(" ", "_").replace("-", "_")
    
    for node in tree.traverse_preorder():
        # Normalize node name
        node.name = normalizer(node.name)
        
        # Normalize payload keys if requested
        if normalize_payload:
            new_payload = {}
            for key, value in node.payload.items():
                new_key = normalizer(key)
                new_payload[new_key] = value
            node.payload = new_payload
    
    return tree