"""
Tree generation algorithms.

Provides algorithms for generating trees with specific properties.
"""

import random
from typing import Optional, Callable
from ..node import Node


def random_tree(
    n: int,
    max_children: int = 3,
    name_generator: Optional[Callable[[int], str]] = None
) -> Node:
    """
    Generate random tree with n nodes.

    Args:
        n: Number of nodes to generate
        max_children: Maximum children per node
        name_generator: Function to generate node names (default: 'N0', 'N1', ...)

    Returns:
        Root node of random tree

    Example:
        >>> tree = random_tree(10, max_children=3)
        >>> len(list(tree.descendants())) + 1  # +1 for root
        10
    """
    if n <= 0:
        raise ValueError("n must be positive")

    if name_generator is None:
        name_generator = lambda i: f"N{i}"

    # Create all nodes
    nodes = [Node(name_generator(i)) for i in range(n)]
    root = nodes[0]

    # Track nodes that can still have children
    available_parents = [root]
    next_child_idx = 1

    while next_child_idx < n and available_parents:
        # Pick random parent
        parent_idx = random.randint(0, len(available_parents) - 1)
        parent = available_parents[parent_idx]

        # Determine how many children to add (at least 1)
        num_children = random.randint(1, min(max_children, n - next_child_idx))

        # Add children
        children = []
        for _ in range(num_children):
            if next_child_idx >= n:
                break
            children.append(nodes[next_child_idx])
            available_parents.append(nodes[next_child_idx])
            next_child_idx += 1

        # Update parent with children
        new_parent = parent
        for child in children:
            new_parent = new_parent.with_child(child)

        # Replace parent in available_parents
        available_parents[parent_idx] = new_parent

        # Remove parent if it has max_children
        if len(new_parent.children) >= max_children:
            available_parents.pop(parent_idx)

    # Rebuild tree from root with all updates
    return available_parents[0] if available_parents and available_parents[0].name == root.name else root


def balanced_tree(
    depth: int,
    branching_factor: int = 2,
    name_generator: Optional[Callable[[int, int], str]] = None
) -> Node:
    """
    Generate perfectly balanced tree.

    Args:
        depth: Depth of tree (0 = just root)
        branching_factor: Number of children per node
        name_generator: Function(level, index) to generate names

    Returns:
        Root node of balanced tree

    Example:
        >>> tree = balanced_tree(2, branching_factor=2)
        >>> tree.name
        'L0_N0'
        >>> len(tree.children)
        2
    """
    if depth < 0:
        raise ValueError("depth must be non-negative")
    if branching_factor < 1:
        raise ValueError("branching_factor must be at least 1")

    if name_generator is None:
        name_generator = lambda level, idx: f"L{level}_N{idx}"

    def build_subtree(level: int, index: int) -> Node:
        node = Node(name_generator(level, index))

        if level < depth:
            children = []
            for i in range(branching_factor):
                child_idx = index * branching_factor + i
                children.append(build_subtree(level + 1, child_idx))

            for child in children:
                node = node.with_child(child)

        return node

    return build_subtree(0, 0)


def complete_tree(
    levels: int,
    branching_factor: int = 2,
    name_generator: Optional[Callable[[int], str]] = None
) -> Node:
    """
    Generate complete tree (all levels full except possibly last).

    In a complete tree, all levels are completely filled except possibly
    the last level, which is filled from left to right.

    Args:
        levels: Number of levels (1 = just root)
        branching_factor: Number of children per node
        name_generator: Function to generate node names

    Returns:
        Root node of complete tree

    Example:
        >>> tree = complete_tree(3, branching_factor=2)
        >>> len(list(tree.descendants())) + 1
        7
    """
    if levels <= 0:
        raise ValueError("levels must be positive")
    if branching_factor < 1:
        raise ValueError("branching_factor must be at least 1")

    if name_generator is None:
        name_generator = lambda i: f"N{i}"

    # Calculate total nodes in a complete tree
    total_nodes = sum(branching_factor ** i for i in range(levels))

    # Create all nodes
    nodes = [Node(name_generator(i)) for i in range(total_nodes)]

    # Build tree level by level
    for i in range(total_nodes):
        first_child_idx = branching_factor * i + 1

        # Add children if they exist
        for j in range(branching_factor):
            child_idx = first_child_idx + j
            if child_idx < total_nodes:
                nodes[i] = nodes[i].with_child(nodes[child_idx])
            else:
                break

    return nodes[0]


def full_tree(
    depth: int,
    branching_factor: int = 2,
    name_generator: Optional[Callable[[int, int], str]] = None
) -> Node:
    """
    Generate full tree (all internal nodes have same number of children).

    A full tree is one where every node has either 0 or branching_factor children.
    This is identical to a perfect/complete balanced tree.

    Args:
        depth: Depth of tree (0 = just root)
        branching_factor: Number of children per internal node
        name_generator: Function(level, index) to generate names

    Returns:
        Root node of full tree

    Example:
        >>> tree = full_tree(2, branching_factor=2)
        >>> all(len(n.children) in [0, 2] for n in tree.walk())
        True
    """
    # A full tree is the same as a balanced tree in our implementation
    return balanced_tree(depth, branching_factor, name_generator)


def binary_search_tree(values: list) -> Node:
    """
    Generate binary search tree from values.

    Creates a BST where left child < parent < right child.

    Args:
        values: List of comparable values

    Returns:
        Root node of BST

    Example:
        >>> tree = binary_search_tree([5, 3, 7, 1, 9])
        >>> tree.name
        '5'
        >>> tree.children[0].name  # Left child
        '3'
    """
    if not values:
        raise ValueError("values cannot be empty")

    def insert(node: Optional[Node], value) -> Node:
        if node is None:
            return Node(str(value), attrs={'value': value})

        node_value = node.attrs.get('value', node.name)

        if value < node_value:
            # Insert into left subtree (first child)
            if len(node.children) == 0:
                return node.with_child(Node(str(value), attrs={'value': value}))
            else:
                left = insert(node.children[0], value)
                new_children = [left] + list(node.children[1:])
                return Node(node.name, *new_children, attrs=node.attrs)
        else:
            # Insert into right subtree (second child)
            if len(node.children) <= 1:
                left = node.children[0] if node.children else None
                right = Node(str(value), attrs={'value': value})
                children = [left, right] if left else [right]
                return Node(node.name, *children, attrs=node.attrs)
            else:
                right = insert(node.children[1], value)
                new_children = [node.children[0], right] + list(node.children[2:])
                return Node(node.name, *new_children, attrs=node.attrs)

    root = None
    for value in values:
        root = insert(root, value)

    return root


def tree_from_edges(edges: list, root_name: str = None) -> Node:
    """
    Generate tree from edge list.

    Args:
        edges: List of (parent, child) tuples
        root_name: Name of root node (auto-detected if None)

    Returns:
        Root node of tree

    Example:
        >>> edges = [('A', 'B'), ('A', 'C'), ('B', 'D')]
        >>> tree = tree_from_edges(edges, 'A')
        >>> tree.name
        'A'
    """
    if not edges:
        raise ValueError("edges cannot be empty")

    # Find root if not specified
    if root_name is None:
        parents = {parent for parent, _ in edges}
        children = {child for _, child in edges}
        roots = parents - children
        if not roots:
            raise ValueError("No root node found (cyclic graph?)")
        if len(roots) > 1:
            raise ValueError(f"Multiple potential roots: {roots}")
        root_name = roots.pop()

    # Build adjacency list
    adj = {}
    for parent, child in edges:
        if parent not in adj:
            adj[parent] = []
        adj[parent].append(child)

    # Build tree recursively
    def build(name: str) -> Node:
        node = Node(name)
        if name in adj:
            for child_name in adj[name]:
                node = node.with_child(build(child_name))
        return node

    return build(root_name)
