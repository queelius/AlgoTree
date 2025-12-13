"""
Tests for AlgoTree interoperability with AlgoGraph.

Test organization:
- TestFlatDict* classes: Do NOT require AlgoGraph
- TestTreeToGraph, TestGraphToTree, TestRoundTrip: Require AlgoGraph
- TestWithoutAlgoGraph: Tests error handling when AlgoGraph is unavailable
"""

import pytest
from AlgoTree import Node, Tree
from AlgoTree.interop import (
    tree_to_graph,
    graph_to_tree,
    node_to_flat_dict,
    flat_dict_to_node,
    tree_to_flat_dict,
    flat_dict_to_tree,
    ALGOGRAPH_AVAILABLE,
    _require_algograph,
)


# Marker for tests requiring AlgoGraph
requires_algograph = pytest.mark.skipif(
    not ALGOGRAPH_AVAILABLE,
    reason="AlgoGraph not available"
)


@requires_algograph
class TestTreeToGraph:
    """Tests for tree_to_graph conversion."""

    def test_simple_tree(self):
        """Convert simple tree to graph."""
        tree = Node('root', Node('child1'), Node('child2'))
        graph = tree_to_graph(tree)

        assert graph.vertex_count == 3
        assert graph.edge_count == 2
        assert graph.has_vertex('root')
        assert graph.has_vertex('child1')
        assert graph.has_vertex('child2')
        assert graph.has_edge('root', 'child1')
        assert graph.has_edge('root', 'child2')

    def test_deep_tree(self):
        """Convert deep tree to graph."""
        tree = Node('A',
            Node('B',
                Node('D'),
                Node('E')
            ),
            Node('C',
                Node('F')
            )
        )
        graph = tree_to_graph(tree)

        assert graph.vertex_count == 6
        assert graph.edge_count == 5
        assert graph.has_edge('A', 'B')
        assert graph.has_edge('B', 'D')
        assert graph.has_edge('B', 'E')
        assert graph.has_edge('A', 'C')
        assert graph.has_edge('C', 'F')

    def test_single_node(self):
        """Convert single node tree to graph."""
        tree = Node('only')
        graph = tree_to_graph(tree)

        assert graph.vertex_count == 1
        assert graph.edge_count == 0
        assert graph.has_vertex('only')

    def test_preserves_attributes(self):
        """Attributes are preserved in conversion."""
        tree = Node('root', attrs={'value': 42, 'label': 'test'})
        graph = tree_to_graph(tree)

        vertex = graph.get_vertex('root')
        assert vertex.get('value') == 42
        assert vertex.get('label') == 'test'

    def test_undirected_edges(self):
        """Create undirected edges when specified."""
        tree = Node('A', Node('B'))
        graph = tree_to_graph(tree, directed=False)

        # Should have edge in both directions for undirected
        edges = list(graph.edges)
        assert len(edges) == 1
        assert not edges[0].directed


@requires_algograph
class TestGraphToTree:
    """Tests for graph_to_tree conversion."""

    def test_simple_graph(self):
        """Convert simple graph to tree."""
        from AlgoGraph import Graph, Vertex, Edge

        vertices = {Vertex('A'), Vertex('B'), Vertex('C')}
        edges = {Edge('A', 'B'), Edge('A', 'C')}
        graph = Graph(vertices, edges)

        tree = graph_to_tree(graph, 'A')

        assert tree.name == 'A'
        assert len(tree.children) == 2
        child_names = {c.name for c in tree.children}
        assert child_names == {'B', 'C'}

    def test_deep_graph(self):
        """Convert deeper graph to tree."""
        from AlgoGraph import Graph, Vertex, Edge

        vertices = {Vertex('A'), Vertex('B'), Vertex('C'), Vertex('D')}
        edges = {Edge('A', 'B'), Edge('B', 'C'), Edge('C', 'D')}
        graph = Graph(vertices, edges)

        tree = graph_to_tree(graph, 'A')

        assert tree.name == 'A'
        assert len(tree.children) == 1
        assert tree.children[0].name == 'B'
        assert tree.children[0].children[0].name == 'C'
        assert tree.children[0].children[0].children[0].name == 'D'

    def test_preserves_attributes(self):
        """Attributes are preserved in conversion."""
        from AlgoGraph import Graph, Vertex, Edge

        vertices = {Vertex('A', attrs={'value': 100})}
        graph = Graph(vertices, set())

        tree = graph_to_tree(graph, 'A')

        assert tree.get('value') == 100

    def test_invalid_root(self):
        """Raise error for invalid root vertex."""
        from AlgoGraph import Graph, Vertex

        graph = Graph({Vertex('A')}, set())

        with pytest.raises(ValueError, match="not in graph"):
            graph_to_tree(graph, 'nonexistent')


@requires_algograph
class TestRoundTrip:
    """Tests for round-trip conversions."""

    def test_tree_to_graph_to_tree(self):
        """Round-trip: tree -> graph -> tree."""
        original = Node('root',
            Node('child1', attrs={'x': 1}),
            Node('child2', attrs={'x': 2})
        )

        graph = tree_to_graph(original)
        recovered = graph_to_tree(graph, 'root')

        assert recovered.name == original.name
        assert len(recovered.children) == len(original.children)

        # Check children (order may vary)
        original_child_names = {c.name for c in original.children}
        recovered_child_names = {c.name for c in recovered.children}
        assert recovered_child_names == original_child_names

    def test_complex_round_trip(self):
        """Round-trip with deeper tree."""
        original = Node('A',
            Node('B',
                Node('D', attrs={'leaf': True}),
                Node('E', attrs={'leaf': True})
            ),
            Node('C',
                Node('F', attrs={'leaf': True})
            )
        )

        graph = tree_to_graph(original)
        recovered = graph_to_tree(graph, 'A')

        # Count total nodes
        def count_nodes(n):
            return 1 + sum(count_nodes(c) for c in n.children)

        assert count_nodes(recovered) == count_nodes(original)


class TestFlatDict:
    """Tests for flat dictionary conversion."""

    def test_node_to_flat_dict(self):
        """Convert node to flat dictionary."""
        tree = Node('A',
            Node('B', attrs={'value': 1}),
            Node('C', attrs={'value': 2})
        )

        flat = node_to_flat_dict(tree)

        assert 'A' in flat
        assert flat['A']['.name'] == 'A'
        assert flat['A']['.children'] == ['B', 'C']

    def test_flat_dict_to_node_simple(self):
        """Convert flat dict to node."""
        flat = {
            'A': {'.name': 'A', '.children': ['B', 'C']},
            'B': {'.name': 'B', '.children': [], 'value': 10},
            'C': {'.name': 'C', '.children': [], 'value': 20}
        }

        tree = flat_dict_to_node(flat, 'A')

        assert tree.name == 'A'
        assert len(tree.children) == 2
        child_names = {c.name for c in tree.children}
        assert child_names == {'B', 'C'}

    def test_flat_dict_auto_root(self):
        """Auto-detect root node."""
        flat = {
            'root': {'.name': 'root', '.children': ['child']},
            'child': {'.name': 'child', '.children': []}
        }

        tree = flat_dict_to_node(flat)  # No root specified

        assert tree.name == 'root'

    def test_flat_dict_preserves_attrs(self):
        """Attributes are preserved in flat dict conversion."""
        flat = {
            'A': {'.name': 'A', '.children': [], 'value': 42, 'label': 'test'}
        }

        tree = flat_dict_to_node(flat, 'A')

        assert tree.get('value') == 42
        assert tree.get('label') == 'test'

    def test_flat_dict_round_trip(self):
        """Round-trip: node -> flat_dict -> node."""
        original = Node('root',
            Node('child1', attrs={'x': 1}),
            Node('child2', attrs={'x': 2})
        )

        flat = node_to_flat_dict(original)
        recovered = flat_dict_to_node(flat, 'root')

        assert recovered.name == original.name
        assert len(recovered.children) == len(original.children)

    def test_tree_to_flat_dict(self):
        """Convert Tree object to flat dict."""
        t = Tree(Node('root', Node('child')))
        flat = tree_to_flat_dict(t)

        assert 'root' in flat
        assert flat['root']['.children'] == ['child']

    def test_flat_dict_to_tree(self):
        """Convert flat dict to Tree object."""
        flat = {
            'root': {'.name': 'root', '.children': ['child']},
            'child': {'.name': 'child', '.children': []}
        }

        t = flat_dict_to_tree(flat, 'root')

        assert isinstance(t, Tree)
        assert t.root.name == 'root'

    def test_cycle_detection(self):
        """Detect cycles in flat dict."""
        flat = {
            'A': {'.name': 'A', '.children': ['B']},
            'B': {'.name': 'B', '.children': ['A']}  # Cycle!
        }

        with pytest.raises(ValueError, match="Cycle detected"):
            flat_dict_to_node(flat, 'A')

    def test_empty_dict(self):
        """Handle empty flat dict."""
        with pytest.raises(ValueError, match="Empty"):
            flat_dict_to_node({})


class TestAlgoGraphFlatDictCompatibility:
    """Test compatibility with AlgoGraph's flat dict format.

    These tests do NOT require AlgoGraph to be installed.
    They test the flat dict interchange format.
    """

    def test_algograph_edges_format(self):
        """Handle AlgoGraph's .edges format (vs .children)."""
        # AlgoGraph uses .edges with dict entries
        flat = {
            'A': {
                '.name': 'A',
                '.edges': [
                    {'target': 'B', 'weight': 1.0, 'directed': True},
                    {'target': 'C', 'weight': 2.0, 'directed': True}
                ]
            },
            'B': {'.name': 'B', '.edges': []},
            'C': {'.name': 'C', '.edges': []}
        }

        tree = flat_dict_to_node(flat, 'A')

        assert tree.name == 'A'
        assert len(tree.children) == 2
        child_names = {c.name for c in tree.children}
        assert child_names == {'B', 'C'}


class TestWithoutAlgoGraph:
    """Test behavior when AlgoGraph is not available."""

    def test_import_error_message(self):
        """Verify helpful error when AlgoGraph missing."""
        if ALGOGRAPH_AVAILABLE:
            pytest.skip("AlgoGraph is available")

        with pytest.raises(ImportError, match="AlgoGraph is required"):
            _require_algograph()

    def test_tree_to_graph_raises_when_unavailable(self):
        """tree_to_graph raises ImportError when AlgoGraph is missing."""
        if ALGOGRAPH_AVAILABLE:
            pytest.skip("AlgoGraph is available")

        tree = Node('root', Node('child'))
        with pytest.raises(ImportError, match="AlgoGraph is required"):
            tree_to_graph(tree)

    def test_graph_to_tree_raises_when_unavailable(self):
        """graph_to_tree raises ImportError when AlgoGraph is missing."""
        if ALGOGRAPH_AVAILABLE:
            pytest.skip("AlgoGraph is available")

        # Cannot create a real Graph without AlgoGraph, but
        # _require_algograph should fail before checking the graph
        with pytest.raises(ImportError, match="AlgoGraph is required"):
            graph_to_tree(None, 'root')


# =============================================================================
# Additional test cases for improved coverage
# =============================================================================

class TestFlatDictEdgeCases:
    """Edge cases and error handling for flat dict conversions.

    These tests do NOT require AlgoGraph.
    """

    def test_node_to_flat_dict_with_deep_nesting(self):
        """Verify path prefix handling for deeply nested trees."""
        tree = Node('root',
            Node('A',
                Node('B',
                    Node('C', attrs={'depth': 3})
                )
            )
        )

        flat = node_to_flat_dict(tree)

        # Root should have no prefix
        assert 'root' in flat
        # Children use path prefix
        assert 'root/A' in flat
        assert 'root/A/B' in flat
        assert 'root/A/B/C' in flat

        # Verify attributes preserved at all levels
        assert flat['root/A/B/C']['depth'] == 3

    def test_node_to_flat_dict_filters_dot_prefixed_attrs(self):
        """Dot-prefixed attributes in attrs dict should be filtered."""
        tree = Node('root', attrs={
            'value': 10,
            '.internal': 'should_be_filtered',
            'normal': 'kept'
        })

        flat = node_to_flat_dict(tree)

        assert flat['root']['value'] == 10
        assert flat['root']['normal'] == 'kept'
        # .internal should NOT be in the output (it would conflict with metadata)
        assert '.internal' not in flat['root']

    def test_flat_dict_to_node_with_missing_child_reference(self):
        """Handle child references that don't exist in flat_dict."""
        flat = {
            'root': {'.name': 'root', '.children': ['missing_child']}
        }

        # Should create minimal node for missing references
        tree = flat_dict_to_node(flat, 'root')

        assert tree.name == 'root'
        assert len(tree.children) == 1
        # Child is created with just the name
        assert tree.children[0].name == 'missing_child'

    def test_flat_dict_to_node_with_multiple_roots_selects_first_alphabetically(self):
        """When multiple roots exist, select first alphabetically."""
        flat = {
            'Z': {'.name': 'Z', '.children': []},
            'A': {'.name': 'A', '.children': []},
            'M': {'.name': 'M', '.children': []}
        }

        tree = flat_dict_to_node(flat)

        # 'A' should be selected as root (first alphabetically)
        assert tree.name == 'A'

    def test_flat_dict_to_node_with_complex_attribute_values(self):
        """Attributes can contain complex types like lists and dicts."""
        flat = {
            'root': {
                '.name': 'root',
                '.children': [],
                'list_attr': [1, 2, 3],
                'dict_attr': {'nested': 'value'},
                'none_attr': None,
                'bool_attr': True
            }
        }

        tree = flat_dict_to_node(flat, 'root')

        assert tree.get('list_attr') == [1, 2, 3]
        assert tree.get('dict_attr') == {'nested': 'value'}
        assert tree.get('none_attr') is None
        assert tree.get('bool_attr') is True

    def test_flat_dict_to_node_with_name_from_key_when_dotname_missing(self):
        """Use dict key as name when .name is missing."""
        flat = {
            'root': {'.children': ['child']},
            'child': {'.children': []}  # No .name field
        }

        tree = flat_dict_to_node(flat, 'root')

        assert tree.name == 'root'
        assert tree.children[0].name == 'child'

    def test_flat_dict_round_trip_with_deep_nesting(self):
        """Round-trip preserves structure for deeply nested trees."""
        original = Node('root',
            Node('level1',
                Node('level2',
                    Node('level3', attrs={'value': 'deep'})
                )
            )
        )

        flat = node_to_flat_dict(original)
        recovered = flat_dict_to_node(flat, 'root')

        # Navigate to deepest node
        deep_node = recovered.children[0].children[0].children[0]
        assert deep_node.name == 'level3'
        assert deep_node.get('value') == 'deep'

    def test_flat_dict_with_edges_using_id_key(self):
        """Support .edges entries with 'id' key instead of 'target'."""
        flat = {
            'A': {
                '.name': 'A',
                '.edges': [
                    {'id': 'B'},
                    {'id': 'C'}
                ]
            },
            'B': {'.name': 'B', '.edges': []},
            'C': {'.name': 'C', '.edges': []}
        }

        tree = flat_dict_to_node(flat, 'A')

        assert tree.name == 'A'
        assert len(tree.children) == 2
        child_names = {c.name for c in tree.children}
        assert child_names == {'B', 'C'}

    def test_flat_dict_to_node_no_root_found_raises_error(self):
        """Raise error when all nodes are children of other nodes."""
        flat = {
            'A': {'.name': 'A', '.children': ['B']},
            'B': {'.name': 'B', '.children': ['C']},
            'C': {'.name': 'C', '.children': ['A']}  # Forms a cycle, no root
        }

        with pytest.raises(ValueError, match="No root found"):
            flat_dict_to_node(flat)

    def test_flat_dict_auto_root_with_edges_dict_format(self):
        """Auto-detect root when children are in dict format with target/id."""
        flat = {
            'root': {
                '.name': 'root',
                '.edges': [
                    {'target': 'child1'},
                    {'target': 'child2'}
                ]
            },
            'child1': {'.name': 'child1', '.edges': []},
            'child2': {'.name': 'child2', '.edges': []}
        }

        # Auto-detect root (root is not a child of any other node)
        tree = flat_dict_to_node(flat)

        assert tree.name == 'root'
        assert len(tree.children) == 2

    def test_flat_dict_with_path_prefixed_child_lookup(self):
        """Verify path prefix lookup when child key has prefix."""
        flat = {
            'root': {'.name': 'root', '.children': ['child']},
            'root/child': {'.name': 'child', '.children': [], 'value': 42}
        }

        tree = flat_dict_to_node(flat, 'root')

        assert tree.name == 'root'
        assert len(tree.children) == 1
        assert tree.children[0].name == 'child'
        assert tree.children[0].get('value') == 42


class TestFlatDictTreeWrappers:
    """Tests for Tree-level flat dict wrapper functions.

    These tests do NOT require AlgoGraph.
    """

    def test_tree_to_flat_dict_with_nested_tree(self):
        """tree_to_flat_dict delegates to node_to_flat_dict correctly."""
        t = Tree(Node('root',
            Node('child', attrs={'x': 1})
        ))

        flat = tree_to_flat_dict(t)

        assert 'root' in flat
        assert 'root/child' in flat
        assert flat['root/child']['x'] == 1

    def test_flat_dict_to_tree_with_auto_root(self):
        """flat_dict_to_tree auto-detects root."""
        flat = {
            'only_root': {'.name': 'only_root', '.children': []}
        }

        t = flat_dict_to_tree(flat)

        assert isinstance(t, Tree)
        assert t.root.name == 'only_root'

    def test_flat_dict_to_tree_preserves_attributes(self):
        """flat_dict_to_tree preserves all node attributes."""
        flat = {
            'root': {'.name': 'root', '.children': ['child'], 'root_attr': 'rv'},
            'child': {'.name': 'child', '.children': [], 'child_attr': 'cv'}
        }

        t = flat_dict_to_tree(flat, 'root')

        assert t.root.get('root_attr') == 'rv'
        assert t.root.children[0].get('child_attr') == 'cv'


@requires_algograph
class TestGraphConversionEdgeCases:
    """Additional edge cases for graph conversions.

    These tests require AlgoGraph.
    """

    def test_tree_to_graph_with_deep_attributes(self):
        """Attributes at all tree levels are preserved in graph."""
        tree = Node('root',
            Node('child', attrs={'child_attr': 'cv'}),
            attrs={'root_attr': 'rv'}
        )

        graph = tree_to_graph(tree)

        root_vertex = graph.get_vertex('root')
        child_vertex = graph.get_vertex('child')

        assert root_vertex.get('root_attr') == 'rv'
        assert child_vertex.get('child_attr') == 'cv'

    def test_tree_to_graph_with_wide_tree(self):
        """Handle wide trees (many children per node)."""
        children = [Node(f'child{i}') for i in range(10)]
        tree = Node('root', *children)

        graph = tree_to_graph(tree)

        assert graph.vertex_count == 11
        assert graph.edge_count == 10
        for i in range(10):
            assert graph.has_edge('root', f'child{i}')

    def test_graph_to_tree_with_disconnected_vertices(self):
        """Disconnected vertices are not included in tree."""
        from AlgoGraph import Graph, Vertex, Edge

        vertices = {
            Vertex('A'),
            Vertex('B'),
            Vertex('C'),  # Disconnected
        }
        edges = {Edge('A', 'B')}
        graph = Graph(vertices, edges)

        tree = graph_to_tree(graph, 'A')

        # Tree should only contain connected nodes
        def get_all_names(n):
            names = {n.name}
            for c in n.children:
                names.update(get_all_names(c))
            return names

        names = get_all_names(tree)
        assert names == {'A', 'B'}
        # 'C' is not in the tree since it's disconnected

    def test_round_trip_preserves_leaf_attributes(self):
        """Round-trip preserves attributes on leaf nodes."""
        original = Node('root',
            Node('leaf1', attrs={'type': 'leaf', 'value': 1}),
            Node('leaf2', attrs={'type': 'leaf', 'value': 2})
        )

        graph = tree_to_graph(original)
        recovered = graph_to_tree(graph, 'root')

        # Find leaves and check attributes
        leaf_attrs = {}
        for child in recovered.children:
            leaf_attrs[child.name] = child.get('value')

        assert leaf_attrs.get('leaf1') == 1
        assert leaf_attrs.get('leaf2') == 2
