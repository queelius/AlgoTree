"""
Tree traversal algorithms.

Provides various methods for traversing trees including:
- Depth-first traversals (preorder, postorder, inorder for binary trees)
- Breadth-first traversals (level-order, zigzag)
- Specialized traversals (boundary, spiral)
"""

from typing import Iterator, List, Callable, Any
from collections import deque
from ..node import Node


def preorder_traversal(node: Node) -> Iterator[Node]:
    """
    Preorder traversal: root, left subtree, right subtree.

    Args:
        node: Root node of tree

    Yields:
        Nodes in preorder

    Example:
        >>> tree = Node('A', Node('B'), Node('C'))
        >>> [n.name for n in preorder_traversal(tree)]
        ['A', 'B', 'C']
    """
    yield node
    for child in node.children:
        yield from preorder_traversal(child)


def postorder_traversal(node: Node) -> Iterator[Node]:
    """
    Postorder traversal: left subtree, right subtree, root.

    Args:
        node: Root node of tree

    Yields:
        Nodes in postorder

    Example:
        >>> tree = Node('A', Node('B'), Node('C'))
        >>> [n.name for n in postorder_traversal(tree)]
        ['B', 'C', 'A']
    """
    for child in node.children:
        yield from postorder_traversal(child)
    yield node


def level_order_traversal(node: Node) -> Iterator[List[Node]]:
    """
    Level-order (BFS) traversal - yields nodes level by level.

    Args:
        node: Root node of tree

    Yields:
        Lists of nodes at each level

    Example:
        >>> tree = Node('A', Node('B'), Node('C'))
        >>> [[n.name for n in level] for level in level_order_traversal(tree)]
        [['A'], ['B', 'C']]
    """
    if not node:
        return

    queue = deque([node])

    while queue:
        level_size = len(queue)
        level_nodes = []

        for _ in range(level_size):
            current = queue.popleft()
            level_nodes.append(current)

            for child in current.children:
                queue.append(child)

        yield level_nodes


def inorder_traversal_binary(node: Node) -> Iterator[Node]:
    """
    Inorder traversal for binary trees: left, root, right.

    Assumes first child is left, second child is right.

    Args:
        node: Root node of binary tree

    Yields:
        Nodes in inorder

    Example:
        >>> tree = Node('A', Node('B'), Node('C'))
        >>> [n.name for n in inorder_traversal_binary(tree)]
        ['B', 'A', 'C']
    """
    children = list(node.children)

    # Left subtree
    if len(children) > 0:
        yield from inorder_traversal_binary(children[0])

    # Root
    yield node

    # Right subtree
    if len(children) > 1:
        yield from inorder_traversal_binary(children[1])


def zigzag_traversal(node: Node) -> Iterator[List[Node]]:
    """
    Zigzag (spiral) level-order traversal.

    Alternates direction at each level: left-to-right, then right-to-left.

    Args:
        node: Root node of tree

    Yields:
        Lists of nodes at each level (alternating direction)

    Example:
        >>> tree = Node('A', Node('B', Node('D'), Node('E')), Node('C'))
        >>> [[n.name for n in level] for level in zigzag_traversal(tree)]
        [['A'], ['C', 'B'], ['D', 'E']]
    """
    if not node:
        return

    left_to_right = True
    queue = deque([node])

    while queue:
        level_size = len(queue)
        level_nodes = []

        for _ in range(level_size):
            current = queue.popleft()
            level_nodes.append(current)

            for child in current.children:
                queue.append(child)

        # Reverse if going right to left
        if not left_to_right:
            level_nodes.reverse()

        yield level_nodes
        left_to_right = not left_to_right


def boundary_traversal(node: Node) -> Iterator[Node]:
    """
    Boundary traversal: left boundary, leaves, right boundary.

    Args:
        node: Root node of tree

    Yields:
        Nodes on the boundary
    """
    if not node:
        return

    # Root
    yield node

    # Left boundary (excluding leaves)
    def left_boundary(n: Node):
        if n and n.children:
            if not n.is_leaf:
                yield n
            if n.children:
                yield from left_boundary(n.children[0])

    # Leaves
    def leaves(n: Node):
        if n.is_leaf:
            yield n
        for child in n.children:
            yield from leaves(child)

    # Right boundary (excluding leaves, in reverse)
    def right_boundary(n: Node):
        if n and n.children:
            if len(n.children) > 1:
                yield from right_boundary(n.children[-1])
            if not n.is_leaf:
                yield n

    # Traverse
    if node.children:
        yield from left_boundary(node.children[0] if node.children else node)

        for child in node.children:
            yield from leaves(child)

        if len(node.children) > 1:
            yield from right_boundary(node.children[-1])
