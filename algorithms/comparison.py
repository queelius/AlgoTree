"""
Tree comparison algorithms.

Provides algorithms for comparing trees for equality, isomorphism, and differences.
"""

from typing import Dict, List, Tuple, Set, Optional
from ..node import Node


def trees_equal(node1: Node, node2: Node, compare_attrs: bool = True) -> bool:
    """
    Check if two trees are equal (same structure and values).

    Args:
        node1: First tree root
        node2: Second tree root
        compare_attrs: Whether to compare attributes (default True)

    Returns:
        True if trees are equal

    Example:
        >>> tree1 = Node('A', Node('B'), Node('C'))
        >>> tree2 = Node('A', Node('B'), Node('C'))
        >>> trees_equal(tree1, tree2)
        True
    """
    # Check node names
    if node1.name != node2.name:
        return False

    # Check attributes if required
    if compare_attrs and node1.attrs != node2.attrs:
        return False

    # Check number of children
    if len(node1.children) != len(node2.children):
        return False

    # Recursively check all children
    for child1, child2 in zip(node1.children, node2.children):
        if not trees_equal(child1, child2, compare_attrs):
            return False

    return True


def trees_isomorphic(node1: Node, node2: Node) -> bool:
    """
    Check if two trees are isomorphic (same structure, ignoring names/values).

    Two trees are isomorphic if they have the same structure, regardless of
    node names or attributes.

    Args:
        node1: First tree root
        node2: Second tree root

    Returns:
        True if trees are isomorphic

    Example:
        >>> tree1 = Node('A', Node('B'), Node('C'))
        >>> tree2 = Node('X', Node('Y'), Node('Z'))
        >>> trees_isomorphic(tree1, tree2)
        True
    """
    # Check number of children
    if len(node1.children) != len(node2.children):
        return False

    # For isomorphism, children order doesn't matter
    # We need to find a matching between children of node1 and node2

    if not node1.children:
        return True

    # Try to find a matching
    return _has_isomorphic_matching(
        list(node1.children),
        list(node2.children)
    )


def _has_isomorphic_matching(children1: List[Node], children2: List[Node]) -> bool:
    """
    Check if there's a one-to-one matching between children lists where
    each pair is isomorphic.
    """
    if len(children1) != len(children2):
        return False

    if not children1:
        return True

    # Use backtracking to find a valid matching
    used = [False] * len(children2)

    def backtrack(idx: int) -> bool:
        if idx == len(children1):
            return True

        for i in range(len(children2)):
            if not used[i] and trees_isomorphic(children1[idx], children2[i]):
                used[i] = True
                if backtrack(idx + 1):
                    return True
                used[i] = False

        return False

    return backtrack(0)


def tree_diff(node1: Node, node2: Node) -> Dict[str, List[Tuple[str, str]]]:
    """
    Generate diff between two trees.

    Returns a dictionary with:
    - 'added': Nodes in node2 but not node1
    - 'removed': Nodes in node1 but not node2
    - 'modified': Nodes with different attributes
    - 'unchanged': Nodes that are the same

    Args:
        node1: First tree root (old)
        node2: Second tree root (new)

    Returns:
        Dictionary mapping change types to lists of (path, description) tuples

    Example:
        >>> tree1 = Node('A', Node('B'), Node('C'))
        >>> tree2 = Node('A', Node('B'), Node('D'))
        >>> diff = tree_diff(tree1, tree2)
        >>> 'removed' in diff
        True
    """
    diff_result = {
        'added': [],
        'removed': [],
        'modified': [],
        'unchanged': []
    }

    # Collect all paths in both trees
    def collect_paths(node: Node, path: str = "") -> Dict[str, Node]:
        paths = {}
        current_path = f"{path}/{node.name}" if path else node.name
        paths[current_path] = node

        for child in node.children:
            paths.update(collect_paths(child, current_path))

        return paths

    paths1 = collect_paths(node1)
    paths2 = collect_paths(node2)

    # Find added, removed, modified, and unchanged
    all_paths = set(paths1.keys()) | set(paths2.keys())

    for path in sorted(all_paths):
        if path in paths1 and path in paths2:
            n1, n2 = paths1[path], paths2[path]
            if n1.name != n2.name or n1.attrs != n2.attrs:
                changes = []
                if n1.name != n2.name:
                    changes.append(f"name: {n1.name} -> {n2.name}")
                if n1.attrs != n2.attrs:
                    changes.append(f"attrs: {n1.attrs} -> {n2.attrs}")
                diff_result['modified'].append((path, "; ".join(changes)))
            else:
                diff_result['unchanged'].append((path, "no changes"))
        elif path in paths2:
            diff_result['added'].append((path, f"added: {paths2[path].name}"))
        else:
            diff_result['removed'].append((path, f"removed: {paths1[path].name}"))

    return diff_result


def structural_diff(node1: Node, node2: Node) -> Dict[str, any]:
    """
    Compare structural properties of two trees.

    Returns a dictionary with structural comparisons:
    - 'height_diff': Difference in heights
    - 'width_diff': Difference in max widths
    - 'node_count_diff': Difference in node counts
    - 'leaf_count_diff': Difference in leaf counts

    Args:
        node1: First tree root
        node2: Second tree root

    Returns:
        Dictionary of structural differences

    Example:
        >>> tree1 = Node('A', Node('B'))
        >>> tree2 = Node('A', Node('B'), Node('C'))
        >>> diff = structural_diff(tree1, tree2)
        >>> diff['node_count_diff']
        -1
    """
    from .analysis import tree_height, tree_width

    def count_nodes(node: Node) -> int:
        return 1 + sum(count_nodes(child) for child in node.children)

    def count_leaves(node: Node) -> int:
        if not node.children:
            return 1
        return sum(count_leaves(child) for child in node.children)

    return {
        'height_diff': tree_height(node1) - tree_height(node2),
        'width_diff': tree_width(node1) - tree_width(node2),
        'node_count_diff': count_nodes(node1) - count_nodes(node2),
        'leaf_count_diff': count_leaves(node1) - count_leaves(node2),
    }


def find_common_subtrees(node1: Node, node2: Node) -> List[Tuple[str, str]]:
    """
    Find all common subtrees between two trees.

    Returns list of (path1, path2) tuples where subtrees are equal.

    Args:
        node1: First tree root
        node2: Second tree root

    Returns:
        List of matching subtree path pairs

    Example:
        >>> tree1 = Node('A', Node('B', Node('D')), Node('C'))
        >>> tree2 = Node('X', Node('Y', Node('D')), Node('Z'))
        >>> matches = find_common_subtrees(tree1, tree2)
        >>> len(matches) > 0
        True
    """
    common = []

    # Collect all subtrees with paths
    def collect_subtrees(node: Node, path: str = "") -> List[Tuple[str, Node]]:
        current_path = f"{path}/{node.name}" if path else node.name
        subtrees = [(current_path, node)]

        for child in node.children:
            subtrees.extend(collect_subtrees(child, current_path))

        return subtrees

    subtrees1 = collect_subtrees(node1)
    subtrees2 = collect_subtrees(node2)

    # Find matching subtrees
    for path1, sub1 in subtrees1:
        for path2, sub2 in subtrees2:
            if trees_equal(sub1, sub2, compare_attrs=False):
                common.append((path1, path2))

    return common


def similarity_score(node1: Node, node2: Node) -> float:
    """
    Calculate similarity score between two trees (0.0 to 1.0).

    Score is based on:
    - Structural similarity (isomorphism)
    - Name matching
    - Attribute matching

    Args:
        node1: First tree root
        node2: Second tree root

    Returns:
        Similarity score from 0.0 (completely different) to 1.0 (identical)

    Example:
        >>> tree1 = Node('A', Node('B'), Node('C'))
        >>> tree2 = Node('A', Node('B'), Node('C'))
        >>> similarity_score(tree1, tree2)
        1.0
    """
    def count_nodes(node: Node) -> int:
        return 1 + sum(count_nodes(child) for child in node.children)

    # If trees are exactly equal, score is 1.0
    if trees_equal(node1, node2):
        return 1.0

    # Count total nodes in each tree
    count1 = count_nodes(node1)
    count2 = count_nodes(node2)
    max_count = max(count1, count2)

    # Count matching nodes (by name and position)
    def count_matches(n1: Node, n2: Node) -> int:
        matches = 0

        # Check if current nodes match
        if n1.name == n2.name:
            matches += 1

        # Check children
        min_children = min(len(n1.children), len(n2.children))
        for i in range(min_children):
            matches += count_matches(n1.children[i], n2.children[i])

        return matches

    matching_nodes = count_matches(node1, node2)

    # Similarity is ratio of matching nodes to total nodes
    return matching_nodes / max_count if max_count > 0 else 0.0


def merge_trees(node1: Node, node2: Node, conflict_resolver=None) -> Node:
    """
    Merge two trees, combining their structures.

    When both trees have a node at the same path:
    - If conflict_resolver is provided, use it to decide
    - Otherwise, prefer node2's attributes

    Args:
        node1: First tree root
        node2: Second tree root
        conflict_resolver: Function(node1, node2, path) -> Node to resolve conflicts

    Returns:
        Merged tree

    Example:
        >>> tree1 = Node('A', Node('B'), attrs={'x': 1})
        >>> tree2 = Node('A', Node('C'), attrs={'y': 2})
        >>> merged = merge_trees(tree1, tree2)
        >>> len(merged.children)
        2
    """
    if conflict_resolver is None:
        # Default: prefer node2's attributes, merge children
        def default_resolver(n1, n2, path):
            return Node(n2.name, attrs=n2.attrs)
        conflict_resolver = default_resolver

    def merge_nodes(n1: Optional[Node], n2: Optional[Node], path: str = "") -> Node:
        # If one is None, return the other
        if n1 is None:
            return n2
        if n2 is None:
            return n1

        # Use conflict resolver for current node
        current_path = f"{path}/{n1.name}" if path else n1.name
        merged = conflict_resolver(n1, n2, current_path)

        # Merge children by name
        children_by_name = {}

        for child in n1.children:
            children_by_name[child.name] = (child, None)

        for child in n2.children:
            if child.name in children_by_name:
                existing = children_by_name[child.name][0]
                children_by_name[child.name] = (existing, child)
            else:
                children_by_name[child.name] = (None, child)

        # Recursively merge children
        merged_children = []
        for name, (c1, c2) in children_by_name.items():
            merged_child = merge_nodes(c1, c2, current_path)
            merged_children.append(merged_child)

        # Add all merged children
        for child in merged_children:
            merged = merged.with_child(child)

        return merged

    return merge_nodes(node1, node2)
