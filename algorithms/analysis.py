"""
Tree analysis algorithms.

Provides algorithms for analyzing tree structure and properties.
"""

from typing import Dict, Tuple
from ..node import Node


def tree_diameter(root: Node) -> int:
    """
    Calculate tree diameter (longest path between any two nodes).

    Args:
        root: Root node

    Returns:
        Length of longest path

    Example:
        >>> tree = Node('A', Node('B', Node('D'), Node('E')), Node('C'))
        >>> tree_diameter(tree)
        3
    """
    max_diameter = [0]  # Use list to allow modification in nested function

    def height(node: Node) -> int:
        if not node or not node.children:
            return 0

        # Get heights of all children
        heights = [height(child) for child in node.children]

        # Diameter through this node is sum of two largest heights
        if len(heights) >= 2:
            heights_sorted = sorted(heights, reverse=True)
            diameter_through_node = heights_sorted[0] + heights_sorted[1] + 2
            max_diameter[0] = max(max_diameter[0], diameter_through_node)
        elif len(heights) == 1:
            max_diameter[0] = max(max_diameter[0], heights[0] + 1)

        return max(heights) + 1 if heights else 0

    height(root)
    return max_diameter[0]


def tree_height(root: Node) -> int:
    """
    Calculate height of tree (longest path from root to leaf).

    Args:
        root: Root node

    Returns:
        Height of tree

    Example:
        >>> tree = Node('A', Node('B', Node('D')), Node('C'))
        >>> tree_height(tree)
        2
    """
    if not root or not root.children:
        return 0

    return max(tree_height(child) for child in root.children) + 1


def tree_width(root: Node) -> int:
    """
    Calculate maximum width of tree (max nodes at any level).

    Args:
        root: Root node

    Returns:
        Maximum width

    Example:
        >>> tree = Node('A', Node('B'), Node('C'), Node('D'))
        >>> tree_width(tree)
        3
    """
    from collections import deque

    if not root:
        return 0

    max_width = 0
    queue = deque([root])

    while queue:
        level_width = len(queue)
        max_width = max(max_width, level_width)

        for _ in range(level_width):
            node = queue.popleft()
            queue.extend(node.children)

    return max_width


def is_balanced(root: Node, threshold: int = 1) -> bool:
    """
    Check if tree is balanced (heights of subtrees differ by at most threshold).

    Args:
        root: Root node
        threshold: Maximum allowed height difference

    Returns:
        True if balanced

    Example:
        >>> tree = Node('A', Node('B'), Node('C'))
        >>> is_balanced(tree)
        True
    """
    def check_height(node: Node) -> Tuple[bool, int]:
        if not node or not node.children:
            return True, 0

        # Check all children
        children_balanced = True
        children_heights = []

        for child in node.children:
            is_child_balanced, child_height = check_height(child)
            if not is_child_balanced:
                children_balanced = False
            children_heights.append(child_height)

        if not children_balanced:
            return False, 0

        # Check if current node is balanced
        if children_heights:
            max_height = max(children_heights)
            min_height = min(children_heights)

            if max_height - min_height > threshold:
                return False, 0

        current_height = max(children_heights) + 1 if children_heights else 0
        return True, current_height

    balanced, _ = check_height(root)
    return balanced


def node_centrality(root: Node) -> Dict[str, float]:
    """
    Calculate centrality scores for all nodes.

    Centrality = 1 / (average distance to all other nodes)

    Args:
        root: Root node

    Returns:
        Dictionary mapping node names to centrality scores

    Example:
        >>> tree = Node('A', Node('B'), Node('C'))
        >>> scores = node_centrality(tree)
        >>> scores['A'] > scores['B']
        True
    """
    # Collect all nodes
    nodes = []

    def collect(node: Node):
        nodes.append(node)
        for child in node.children:
            collect(child)

    collect(root)

    # Calculate distances between all pairs
    def distance_to_all(start: Node) -> int:
        total_distance = 0

        for target in nodes:
            if start == target:
                continue

            # Find path from root to both nodes
            def find_node_path(node: Node, target: Node, path: list) -> bool:
                path.append(node)
                if node == target:
                    return True
                for child in node.children:
                    if find_node_path(child, target, path):
                        return True
                path.pop()
                return False

            start_path = []
            target_path = []
            find_node_path(root, start, start_path)
            find_node_path(root, target, target_path)

            # Find LCA
            lca_idx = 0
            for i in range(min(len(start_path), len(target_path))):
                if start_path[i] == target_path[i]:
                    lca_idx = i
                else:
                    break

            # Distance = distance to LCA + distance from LCA
            dist = (len(start_path) - lca_idx - 1) + (len(target_path) - lca_idx - 1)
            total_distance += dist

        return total_distance

    # Calculate centrality for each node
    centrality_scores = {}
    for node in nodes:
        avg_distance = distance_to_all(node) / (len(nodes) - 1) if len(nodes) > 1 else 1
        centrality_scores[node.name] = 1.0 / avg_distance if avg_distance > 0 else float('inf')

    return centrality_scores


def subtree_sizes(root: Node) -> Dict[str, int]:
    """
    Calculate size of subtree rooted at each node.

    Args:
        root: Root node

    Returns:
        Dictionary mapping node names to subtree sizes

    Example:
        >>> tree = Node('A', Node('B', Node('D')), Node('C'))
        >>> sizes = subtree_sizes(tree)
        >>> sizes['A']
        4
        >>> sizes['B']
        2
    """
    sizes = {}

    def calculate_size(node: Node) -> int:
        size = 1  # Count self

        for child in node.children:
            size += calculate_size(child)

        sizes[node.name] = size
        return size

    calculate_size(root)
    return sizes
