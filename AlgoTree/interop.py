"""
Interoperability between AlgoTree and AlgoGraph.

Provides conversion functions between tree and graph representations.
Trees are special cases of graphs (acyclic, connected, directed from parent to child).

Note: AlgoGraph must be installed or in PYTHONPATH for interop functions to work.

Example:
    >>> from AlgoTree import Node, tree_to_graph, graph_to_tree
    >>> tree = Node('root', Node('child1'), Node('child2'))
    >>> graph = tree_to_graph(tree)  # Convert tree to graph
    >>> recovered = graph_to_tree(graph, 'root')  # Convert back
"""

from typing import Dict, Any, Optional, Set
from .node import Node

try:
    from AlgoGraph import Graph, Vertex, Edge
    ALGOGRAPH_AVAILABLE = True
except ImportError:
    ALGOGRAPH_AVAILABLE = False
    Graph = None
    Vertex = None
    Edge = None


def _require_algograph():
    """Check if AlgoGraph is available."""
    if not ALGOGRAPH_AVAILABLE:
        raise ImportError(
            "AlgoGraph is required for interop functions. "
            "Install AlgoGraph or add it to PYTHONPATH."
        )


def tree_to_graph(node: Node, directed: bool = True) -> "Graph":
    """
    Convert AlgoTree Node (and its subtree) to AlgoGraph Graph.

    Each tree node becomes a graph vertex.
    Parent-child relationships become directed edges.

    Args:
        node: Root node of tree (or Tree.root)
        directed: Whether edges should be directed (default: True)

    Returns:
        AlgoGraph Graph representation

    Example:
        >>> from AlgoTree import Node, tree_to_graph
        >>> tree = Node('root', Node('child1'), Node('child2'))
        >>> graph = tree_to_graph(tree)
        >>> graph.vertex_count
        3
        >>> graph.edge_count
        2
    """
    _require_algograph()
    vertices = set()
    edges = set()

    def traverse(n: Node, parent_id: Optional[str] = None):
        # Create vertex from node
        vertex = Vertex(n.name, attrs=n.attrs.copy())
        vertices.add(vertex)

        # Create edge from parent
        if parent_id is not None:
            edge = Edge(parent_id, n.name, directed=directed, weight=1.0)
            edges.add(edge)

        # Recurse to children
        for child in n.children:
            traverse(child, n.name)

    traverse(node)
    return Graph(vertices=vertices, edges=edges)


def graph_to_tree(graph: "Graph", root_id: str) -> Node:
    """
    Convert AlgoGraph Graph to AlgoTree Node.

    Extracts a spanning tree from the graph starting at root_id.
    Uses BFS traversal to build the tree.

    Args:
        graph: AlgoGraph Graph to convert
        root_id: Vertex ID to use as tree root

    Returns:
        AlgoTree Node representation (root of tree)

    Raises:
        ValueError: If root_id not in graph

    Example:
        >>> from AlgoGraph import Graph, Vertex, Edge
        >>> from AlgoTree import graph_to_tree
        >>> v1, v2, v3 = Vertex('A'), Vertex('B'), Vertex('C')
        >>> e1, e2 = Edge('A', 'B'), Edge('A', 'C')
        >>> graph = Graph({v1, v2, v3}, {e1, e2})
        >>> tree = graph_to_tree(graph, 'A')
        >>> tree.name
        'A'
        >>> len(tree.children)
        2
    """
    _require_algograph()

    if not graph.has_vertex(root_id):
        raise ValueError(f"Root vertex '{root_id}' not in graph")

    from collections import deque

    # BFS to build parent map
    visited: Set[str] = set()
    queue = deque([root_id])
    parent_map: Dict[str, Optional[str]] = {root_id: None}

    while queue:
        current_id = queue.popleft()

        if current_id in visited:
            continue

        visited.add(current_id)

        # Add unvisited neighbors
        for neighbor_id in graph.neighbors(current_id):
            if neighbor_id not in visited:
                parent_map[neighbor_id] = current_id
                queue.append(neighbor_id)

    # Build tree from parent map
    def build_node(vertex_id: str) -> Node:
        vertex = graph.get_vertex(vertex_id)
        if vertex is None:
            vertex = Vertex(vertex_id)

        # Find children (nodes whose parent is this vertex)
        children = []
        for vid, pid in parent_map.items():
            if pid == vertex_id:
                children.append(build_node(vid))

        return Node(vertex.id, *children, attrs=vertex.attrs.copy())

    return build_node(root_id)


def node_to_flat_dict(node: Node) -> Dict[str, Any]:
    """
    Convert Node to flat dictionary format.

    This format is compatible with AlgoGraph's flat_dict_to_graph().

    The flat format uses:
    - Keys: node names (with path prefix if duplicates)
    - Values: dicts with .name, .children, and attributes

    Args:
        node: Root node of tree

    Returns:
        Flat dictionary representation

    Example:
        >>> from AlgoTree import Node, node_to_flat_dict
        >>> tree = Node('A', Node('B'), Node('C', attrs={'value': 10}))
        >>> flat = node_to_flat_dict(tree)
        >>> flat['A']['.children']
        ['B', 'C']
        >>> flat['C']['value']
        10
    """
    flat_dict: Dict[str, Any] = {}

    def flatten(n: Node, path_prefix: str = ""):
        # Generate unique key (use path to handle duplicate names)
        if path_prefix:
            key = f"{path_prefix}/{n.name}"
        else:
            key = n.name

        # Build node entry with dot-prefix for metadata
        node_entry: Dict[str, Any] = {
            ".name": n.name,
            ".children": [child.name for child in n.children]
        }

        # Add all attributes (skip dot-prefixed ones in attrs)
        for k, v in n.attrs.items():
            if not k.startswith('.'):
                node_entry[k] = v

        flat_dict[key] = node_entry

        # Recursively flatten children
        for child in n.children:
            flatten(child, key)

    flatten(node)
    return flat_dict


def flat_dict_to_node(flat_dict: Dict[str, Any], root_key: Optional[str] = None) -> Node:
    """
    Convert flat dictionary format to Node.

    This format is compatible with AlgoGraph's graph_to_flat_dict().

    Args:
        flat_dict: Flat dictionary representation
        root_key: Key of root node (auto-detected if not specified)

    Returns:
        AlgoTree Node representation

    Example:
        >>> flat = {
        ...     'A': {'.name': 'A', '.children': ['B', 'C'], 'value': 10},
        ...     'B': {'.name': 'B', '.children': []},
        ...     'C': {'.name': 'C', '.children': []}
        ... }
        >>> tree = flat_dict_to_node(flat, 'A')
        >>> tree.name
        'A'
        >>> len(tree.children)
        2
    """
    if not flat_dict:
        raise ValueError("Empty flat dictionary")

    # Auto-detect root if not specified (node not referenced as child)
    if root_key is None:
        all_children: Set[str] = set()
        for data in flat_dict.values():
            children = data.get('.children', data.get('.edges', []))
            for child in children:
                if isinstance(child, dict):
                    child = child.get('target', child.get('id'))
                all_children.add(child)

        roots = [k for k in flat_dict.keys() if k not in all_children]
        if len(roots) == 0:
            raise ValueError("No root found (all nodes are children of other nodes)")
        if len(roots) > 1:
            # Pick the first one alphabetically for consistency
            root_key = sorted(roots)[0]
        else:
            root_key = roots[0]

    def build_node(key: str, visited: Optional[Set[str]] = None) -> Node:
        if visited is None:
            visited = set()

        if key in visited:
            raise ValueError(f"Cycle detected at node '{key}'")
        visited.add(key)

        data = flat_dict.get(key)
        if data is None:
            # Node referenced but not in dict - create minimal node
            return Node(key)

        name = data.get('.name', key)

        # Extract attributes (non-dot-prefixed keys)
        attrs = {k: v for k, v in data.items() if not k.startswith('.')}

        # Build children
        children_refs = data.get('.children', data.get('.edges', []))
        children = []
        for child_ref in children_refs:
            if isinstance(child_ref, dict):
                child_key = child_ref.get('target', child_ref.get('id'))
            else:
                child_key = child_ref

            # Find actual key in flat_dict (may have path prefix)
            actual_key = child_key
            if child_key not in flat_dict:
                # Try with path prefix
                prefixed_key = f"{key}/{child_key}"
                if prefixed_key in flat_dict:
                    actual_key = prefixed_key

            children.append(build_node(actual_key, visited.copy()))

        return Node(name, *children, attrs=attrs)

    return build_node(root_key)


# Convenience functions for Tree objects

def tree_to_flat_dict(tree) -> Dict[str, Any]:
    """
    Convert Tree to flat dictionary format.

    Args:
        tree: AlgoTree Tree object

    Returns:
        Flat dictionary representation
    """
    return node_to_flat_dict(tree.root)


def flat_dict_to_tree(flat_dict: Dict[str, Any], root_key: Optional[str] = None):
    """
    Convert flat dictionary to Tree.

    Args:
        flat_dict: Flat dictionary representation
        root_key: Key of root node (auto-detected if not specified)

    Returns:
        AlgoTree Tree object
    """
    from .tree import Tree
    return Tree(flat_dict_to_node(flat_dict, root_key))
