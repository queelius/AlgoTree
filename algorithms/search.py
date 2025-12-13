"""
Tree search algorithms.

Provides algorithms for finding nodes, paths, and patterns in trees.
"""

from typing import List, Optional, Callable, Set
from ..node import Node


def find_path(root: Node, target: Node) -> Optional[List[Node]]:
    """
    Find path from root to target node.

    Args:
        root: Root node
        target: Target node to find

    Returns:
        List of nodes from root to target, or None if not found

    Example:
        >>> tree = Node('A', Node('B', Node('D')), Node('C'))
        >>> target = tree.children[0].children[0]  # Node D
        >>> path = find_path(tree, target)
        >>> [n.name for n in path]
        ['A', 'B', 'D']
    """
    def dfs(node: Node, path: List[Node]) -> bool:
        path.append(node)

        if node == target:
            return True

        for child in node.children:
            if dfs(child, path):
                return True

        path.pop()
        return False

    path = []
    if dfs(root, path):
        return path
    return None


def find_all_paths(root: Node, target_name: str) -> List[List[Node]]:
    """
    Find all paths to nodes with given name.

    Args:
        root: Root node
        target_name: Name to search for

    Returns:
        List of paths (each path is a list of nodes)

    Example:
        >>> tree = Node('A', Node('B', Node('X')), Node('C', Node('X')))
        >>> paths = find_all_paths(tree, 'X')
        >>> len(paths)
        2
    """
    paths = []

    def dfs(node: Node, current_path: List[Node]):
        current_path.append(node)

        if node.name == target_name:
            paths.append(current_path.copy())

        for child in node.children:
            dfs(child, current_path)

        current_path.pop()

    dfs(root, [])
    return paths


def find_lca(root: Node, node1: Node, node2: Node) -> Optional[Node]:
    """
    Find Lowest Common Ancestor (LCA) of two nodes.

    Args:
        root: Root node
        node1: First node
        node2: Second node

    Returns:
        LCA node, or None if nodes not in tree

    Example:
        >>> tree = Node('A', Node('B', Node('D'), Node('E')), Node('C'))
        >>> d = tree.children[0].children[0]
        >>> e = tree.children[0].children[1]
        >>> lca = find_lca(tree, d, e)
        >>> lca.name
        'B'
    """
    def dfs(node: Node) -> Optional[Node]:
        if node is None:
            return None

        if node == node1 or node == node2:
            return node

        matches = []
        for child in node.children:
            result = dfs(child)
            if result:
                matches.append(result)

        if len(matches) == 2:
            return node  # This is the LCA
        elif len(matches) == 1:
            return matches[0]  # Propagate up

        return None

    return dfs(root)


def find_nodes_at_distance(root: Node, distance: int) -> List[Node]:
    """
    Find all nodes at exact distance from root.

    Args:
        root: Root node
        distance: Distance from root (0 = root itself)

    Returns:
        List of nodes at given distance

    Example:
        >>> tree = Node('A', Node('B'), Node('C'))
        >>> nodes = find_nodes_at_distance(tree, 1)
        >>> [n.name for n in nodes]
        ['B', 'C']
    """
    if distance == 0:
        return [root]

    nodes = []

    def dfs(node: Node, current_distance: int):
        if current_distance == distance:
            nodes.append(node)
            return

        for child in node.children:
            dfs(child, current_distance + 1)

    for child in root.children:
        dfs(child, 1)

    return nodes


def find_by_predicate(root: Node, predicate: Callable[[Node], bool]) -> List[Node]:
    """
    Find all nodes matching a predicate.

    Args:
        root: Root node
        predicate: Function that returns True for matching nodes

    Returns:
        List of matching nodes

    Example:
        >>> tree = Node('A', Node('B', attrs={'value': 10}), Node('C', attrs={'value': 20}))
        >>> matches = find_by_predicate(tree, lambda n: n.get('value', 0) > 15)
        >>> [n.name for n in matches]
        ['C']
    """
    matches = []

    def dfs(node: Node):
        if predicate(node):
            matches.append(node)

        for child in node.children:
            dfs(child)

    dfs(root)
    return matches
