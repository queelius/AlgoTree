"""
Tree shaping functionality for open transformations.

This module provides reshaping capabilities for transforming trees into 
arbitrary structures (open transformations), inspired by dotsuite's Shape pillar.
"""

from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from .node import Node
from .pattern_matcher import dotmatch


def dotpipe(tree: Node,
           *transformers: Union[Callable, Tuple[str, Callable]]) -> Any:
    """
    Pipe tree through a series of transformations.
    
    This is the main function for open transformations - converting trees
    to any structure through a pipeline of operations.
    
    Args:
        tree: Tree to transform
        *transformers: Variable number of transformers, each can be:
            - Callable: Applied to entire result of previous stage
            - Tuple[str, Callable]: (dot_path, transformer) applies to matched nodes
            
    Returns:
        Result of the final transformation (can be any type)
        
    Examples:
        # Extract all names as a list
        names = dotpipe(tree,
                       lambda t: [n.name for n in t.traverse_preorder()])
        
        # Pipeline of transformations
        result = dotpipe(tree,
                        ("**.config", lambda n: n.payload),  # Extract config payloads
                        lambda configs: {c.get("name"): c for c in configs},  # Dict by name
                        lambda d: list(d.values()))  # Back to list
        
        # Convert tree to nested dict
        data = dotpipe(tree, to_dict)
        
        # Extract and process specific data
        totals = dotpipe(tree,
                        ("**[type=file]", lambda n: n.payload.get("size", 0)),
                        sum)  # Sum all sizes
    """
    result = tree
    
    for transformer in transformers:
        if isinstance(transformer, tuple):
            # Apply to specific nodes matching pattern
            dot_path, func = transformer
            if isinstance(result, Node):
                # Still a tree - can use dotmatch
                matches = dotmatch(result, dot_path)
                result = [func(match) for match in matches]
            else:
                # Not a tree anymore - apply to result directly
                result = func(result)
        else:
            # Apply to entire result
            result = transformer(result)
    
    return result


def to_dict(node: Node, 
           include_children: bool = True,
           include_parent: bool = False,
           key_mapper: Optional[Callable[[str], str]] = None) -> Dict[str, Any]:
    """
    Convert tree node to dictionary representation.
    
    Args:
        node: Node to convert
        include_children: If True, recursively include children
        include_parent: If True, include parent reference (careful: can be circular)
        key_mapper: Optional function to transform keys
        
    Returns:
        Dictionary representation of the node
        
    Examples:
        # Simple conversion
        data = to_dict(tree)
        
        # Without children (just this node)
        node_data = to_dict(tree, include_children=False)
        
        # With key transformation
        data = to_dict(tree, key_mapper=str.upper)
    """
    result = {"name": node.name}
    
    # Add payload
    for key, value in node.payload.items():
        mapped_key = key_mapper(key) if key_mapper else key
        result[mapped_key] = value
    
    # Add children if requested
    if include_children and node.children:
        result["children"] = [
            to_dict(child, include_children=True, include_parent=False, key_mapper=key_mapper)
            for child in node.children
        ]
    
    # Add parent reference if requested (usually not recommended due to circularity)
    if include_parent and node.parent:
        result["parent"] = node.parent.name
    
    return result


def to_list(node: Node,
           traverse_order: str = "preorder",
           include_data: bool = True) -> List[Union[str, Dict[str, Any]]]:
    """
    Convert tree to flat list representation.
    
    Args:
        node: Root node
        traverse_order: Traversal order ("preorder", "postorder", "levelorder")
        include_data: If True, include full node data; if False, just names
        
    Returns:
        List of nodes (as dicts or names)
        
    Examples:
        # List of all node names
        names = to_list(tree, include_data=False)
        
        # List of node data in level order
        nodes = to_list(tree, traverse_order="levelorder")
    """
    # Get nodes in specified order
    if traverse_order == "preorder":
        nodes = list(node.traverse_preorder())
    elif traverse_order == "postorder":
        nodes = list(node.traverse_postorder())
    elif traverse_order == "levelorder":
        nodes = list(node.traverse_levelorder())
    else:
        raise ValueError(f"Unknown traverse order: {traverse_order}")
    
    if include_data:
        return [{"name": n.name, **n.payload} for n in nodes]
    else:
        return [n.name for n in nodes]


def to_paths(node: Node,
            path_separator: str = ".",
            include_payload: bool = False) -> Union[List[str], Dict[str, Any]]:
    """
    Convert tree to path representations.
    
    Args:
        node: Root node
        path_separator: Separator for path components
        include_payload: If True, return dict mapping paths to payloads
        
    Returns:
        List of paths or dict mapping paths to payloads
        
    Examples:
        # List of all paths
        paths = to_paths(tree)
        # ["app", "app.config", "app.database", ...]
        
        # Paths with payloads
        path_data = to_paths(tree, include_payload=True)
        # {"app": {...}, "app.config": {...}, ...}
        
        # Using different separator
        paths = to_paths(tree, path_separator="/")
        # ["app", "app/config", "app/database", ...]
    """
    paths = []
    path_data = {}
    
    def collect_paths(node: Node, current_path: str = ""):
        # Build path for current node
        if current_path:
            node_path = current_path + path_separator + node.name
        else:
            node_path = node.name
        
        if include_payload:
            path_data[node_path] = node.payload
        else:
            paths.append(node_path)
        
        # Recurse to children
        for child in node.children:
            collect_paths(child, node_path)
    
    collect_paths(node)
    
    return path_data if include_payload else paths


def to_adjacency_list(node: Node) -> Dict[str, List[str]]:
    """
    Convert tree to adjacency list representation.
    
    Args:
        node: Root node
        
    Returns:
        Dictionary mapping node names to lists of child names
        
    Examples:
        adj = to_adjacency_list(tree)
        # {"app": ["config", "database"], "config": [], ...}
    """
    adj_list = {}
    
    for n in node.traverse_preorder():
        adj_list[n.name] = [child.name for child in n.children]
    
    return adj_list


def to_edge_list(node: Node,
                include_root: bool = False) -> List[Tuple[str, str]]:
    """
    Convert tree to edge list representation.
    
    Args:
        node: Root node
        include_root: If True, include edge from None to root
        
    Returns:
        List of (parent, child) tuples
        
    Examples:
        edges = to_edge_list(tree)
        # [("app", "config"), ("app", "database"), ...]
    """
    edges = []
    
    if include_root:
        edges.append((None, node.name))
    
    for n in node.traverse_preorder():
        for child in n.children:
            edges.append((n.name, child.name))
    
    return edges


def to_nested_lists(node: Node) -> List:
    """
    Convert tree to nested list structure (like S-expressions).
    
    Args:
        node: Root node
        
    Returns:
        Nested list representation
        
    Examples:
        nested = to_nested_lists(tree)
        # ["app", ["config"], ["database"], ["modules", ["auth"], ["api"]]]
    """
    result = [node.name]
    
    for child in node.children:
        result.append(to_nested_lists(child))
    
    return result


def to_table(node: Node,
            columns: Optional[List[str]] = None,
            include_path: bool = True) -> List[Dict[str, Any]]:
    """
    Convert tree to tabular/relational format.
    
    Args:
        node: Root node
        columns: Specific payload columns to include (None = all)
        include_path: If True, include full path to node
        
    Returns:
        List of row dictionaries suitable for DataFrame or CSV
        
    Examples:
        # Convert to table format
        rows = to_table(tree, columns=["type", "size", "enabled"])
        
        # Can be used with pandas:
        # df = pd.DataFrame(rows)
    """
    rows = []
    
    for n in node.traverse_preorder():
        row = {
            "name": n.name,
            "level": n.level,
            "is_leaf": n.is_leaf,
            "child_count": len(n.children)
        }
        
        if include_path:
            path = ".".join(node.name for node in n.get_path())
            row["path"] = path
        
        if columns:
            # Include only specified columns
            for col in columns:
                row[col] = n.payload.get(col)
        else:
            # Include all payload
            row.update(n.payload)
        
        rows.append(row)
    
    return rows


def dotextract(tree: Node,
              extractor: Callable[[Node], Any],
              dot_path: str = "**",
              flatten: bool = True) -> Union[List[Any], Dict[str, Any]]:
    """
    Extract data from tree nodes using custom extractor.
    
    Args:
        tree: Tree to extract from
        extractor: Function to extract data from each node
        dot_path: Pattern to match nodes
        flatten: If True, return flat list; if False, preserve structure
        
    Returns:
        Extracted data as list or structured dict
        
    Examples:
        # Extract all sizes
        sizes = dotextract(tree, lambda n: n.payload.get("size"))
        
        # Extract node info for files
        files = dotextract(tree, 
                          lambda n: {"name": n.name, "size": n.payload["size"]},
                          dot_path="**[type=file]")
    """
    matches = dotmatch(tree, dot_path)
    extracted = [extractor(node) for node in matches]
    
    if not flatten:
        # Build structured result preserving tree relationships
        result = {}
        for node in matches:
            path = ".".join(n.name for n in node.get_path())
            result[path] = extractor(node)
        return result
    
    return extracted


def dotcollect(tree: Node,
              collector: Callable[[Node, Any], Any],
              initial: Any = None,
              dot_path: str = "**") -> Any:
    """
    Collect data from tree using a collector function.
    
    Similar to reduce but more focused on building collections.
    
    Args:
        tree: Tree to collect from
        collector: Function (node, accumulator) -> new_accumulator
        initial: Initial accumulator value
        dot_path: Pattern to match nodes
        
    Returns:
        Final collected value
        
    Examples:
        # Collect into a dict by type
        by_type = dotcollect(tree,
                           lambda n, acc: {
                               **acc,
                               n.payload.get("type", "unknown"): 
                                   acc.get(n.payload.get("type", "unknown"), []) + [n.name]
                           },
                           initial={})
        
        # Collect statistics
        stats = dotcollect(tree,
                          lambda n, acc: {
                              "count": acc["count"] + 1,
                              "total_size": acc["total_size"] + n.payload.get("size", 0),
                              "max_depth": max(acc["max_depth"], n.level)
                          },
                          initial={"count": 0, "total_size": 0, "max_depth": 0})
    """
    matches = dotmatch(tree, dot_path)
    accumulator = initial
    
    for node in matches:
        accumulator = collector(node, accumulator)
    
    return accumulator


def dotgroup(tree: Node,
            grouper: Union[str, Callable[[Node], Any]],
            dot_path: str = "**") -> Dict[Any, List[Node]]:
    """
    Group tree nodes by a key.
    
    Args:
        tree: Tree to group nodes from
        grouper: Either:
            - String: payload key to group by
            - Callable: function to compute group key
        dot_path: Pattern to match nodes
        
    Returns:
        Dictionary mapping group keys to lists of nodes
        
    Examples:
        # Group by type
        by_type = dotgroup(tree, "type")
        
        # Group by custom function
        by_level = dotgroup(tree, lambda n: n.level)
        
        # Group files by extension
        by_ext = dotgroup(tree,
                         lambda n: n.name.split(".")[-1] if "." in n.name else "no_ext",
                         dot_path="**[type=file]")
    """
    matches = dotmatch(tree, dot_path)
    groups = {}
    
    for node in matches:
        if isinstance(grouper, str):
            # Group by payload key
            key = node.payload.get(grouper)
        else:
            # Group by function result
            key = grouper(node)
        
        if key not in groups:
            groups[key] = []
        groups[key].append(node)
    
    return groups


def dotpartition(tree: Node,
                predicate: Callable[[Node], bool],
                dot_path: str = "**") -> Tuple[List[Node], List[Node]]:
    """
    Partition nodes into two groups based on predicate.
    
    Args:
        tree: Tree to partition
        predicate: Function returning True for first group, False for second
        dot_path: Pattern to match nodes
        
    Returns:
        Tuple of (matching_nodes, non_matching_nodes)
        
    Examples:
        # Partition by size
        large, small = dotpartition(tree, lambda n: n.payload.get("size", 0) > 1000)
        
        # Partition enabled/disabled
        enabled, disabled = dotpartition(tree, 
                                        lambda n: n.payload.get("enabled", False),
                                        dot_path="app.modules.*")
    """
    matches = dotmatch(tree, dot_path)
    true_group = []
    false_group = []
    
    for node in matches:
        if predicate(node):
            true_group.append(node)
        else:
            false_group.append(node)
    
    return true_group, false_group


def dotproject(tree: Node,
              projection: Union[List[str], Dict[str, str]],
              dot_path: str = "**") -> List[Dict[str, Any]]:
    """
    Project specific fields from nodes (like SQL SELECT).
    
    Args:
        tree: Tree to project from
        projection: Either:
            - List of field names to include
            - Dict mapping field names to aliases
        dot_path: Pattern to match nodes
        
    Returns:
        List of projected dictionaries
        
    Examples:
        # Select specific fields
        data = dotproject(tree, ["name", "size", "type"])
        
        # With aliases
        data = dotproject(tree, {
            "name": "file_name",
            "size": "file_size",
            "type": "file_type"
        })
    """
    matches = dotmatch(tree, dot_path)
    results = []
    
    for node in matches:
        row = {}
        
        if isinstance(projection, list):
            # Simple field list
            for field in projection:
                if field == "name":
                    row[field] = node.name
                else:
                    row[field] = node.payload.get(field)
        else:
            # Field aliases
            for field, alias in projection.items():
                if field == "name":
                    row[alias] = node.name
                else:
                    row[alias] = node.payload.get(field)
        
        results.append(row)
    
    return results


def to_graphviz_data(tree: Node) -> Dict[str, Any]:
    """
    Convert tree to GraphViz data structure.
    
    Returns dict with 'nodes' and 'edges' suitable for visualization.
    """
    nodes = []
    edges = []
    
    for n in tree.traverse_preorder():
        # Node data
        nodes.append({
            "id": id(n),
            "name": n.name,
            "label": n.name,
            **n.payload
        })
        
        # Edges to children
        for child in n.children:
            edges.append({
                "from": id(n),
                "to": id(child),
                "label": ""
            })
    
    return {"nodes": nodes, "edges": edges}


def to_json_schema(tree: Node,
                  type_key: str = "type",
                  required_key: str = "required") -> Dict[str, Any]:
    """
    Convert tree to JSON Schema-like structure.
    
    Useful for representing configuration schemas or data models.
    """
    def build_schema(node: Node) -> Dict[str, Any]:
        schema = {
            "type": node.payload.get(type_key, "object"),
            "title": node.name
        }
        
        # Add description if available
        if "description" in node.payload:
            schema["description"] = node.payload["description"]
        
        # Add constraints
        for key in ["minimum", "maximum", "minLength", "maxLength", "pattern", "enum"]:
            if key in node.payload:
                schema[key] = node.payload[key]
        
        # Handle children as properties
        if node.children:
            schema["properties"] = {}
            required = []
            
            for child in node.children:
                schema["properties"][child.name] = build_schema(child)
                if child.payload.get(required_key, False):
                    required.append(child.name)
            
            if required:
                schema["required"] = required
        
        return schema
    
    return build_schema(tree)