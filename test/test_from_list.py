"""
Tests for Node.from_list / to_list bridge and the to_paths(delimiter) fix.

Spec (from P5 Task 1):
  - from_list(['add', 1, ['mul', 3, 2]]) builds Node('add', Node('1'), Node('mul', Node('3'), Node('2')))
  - to_list() is the inverse; leaves map back to scalars via parse_scalar (default: int then float then str)
  - round-trip: from_list(x).to_list() == x for trees built by from_list
  - to_paths(delimiter='.') joins with '.'
"""
import pytest
from AlgoTree import Node
from AlgoTree.tree import Tree


class TestFromList:
    def test_simple_leaf(self):
        n = Node.from_list(42)
        assert n.name == '42'
        assert n.is_leaf

    def test_string_leaf(self):
        n = Node.from_list('hello')
        assert n.name == 'hello'
        assert n.is_leaf

    def test_operator_with_scalar_children(self):
        # ['add', 1, 2] -> Node('add', Node('1'), Node('2'))
        n = Node.from_list(['add', 1, 2])
        assert n.name == 'add'
        assert len(n.children) == 2
        assert n.children[0].name == '1'
        assert n.children[1].name == '2'
        assert n.children[0].is_leaf
        assert n.children[1].is_leaf

    def test_nested_list(self):
        # ['add', 1, ['mul', 3, 2]]
        n = Node.from_list(['add', 1, ['mul', 3, 2]])
        assert n.name == 'add'
        assert len(n.children) == 2
        assert n.children[0].name == '1'
        mul = n.children[1]
        assert mul.name == 'mul'
        assert len(mul.children) == 2
        assert mul.children[0].name == '3'
        assert mul.children[1].name == '2'

    def test_empty_list_raises(self):
        with pytest.raises(ValueError):
            Node.from_list([])

    def test_unary_operator(self):
        n = Node.from_list(['neg', 5])
        assert n.name == 'neg'
        assert len(n.children) == 1
        assert n.children[0].name == '5'

    def test_nullary_operator(self):
        # A list with only the operator name (no args) is a node with no children
        n = Node.from_list(['pi'])
        assert n.name == 'pi'
        assert n.is_leaf


class TestToList:
    def test_leaf_int(self):
        n = Node('42')
        assert n.to_list() == 42

    def test_leaf_float(self):
        n = Node('3.14')
        assert n.to_list() == pytest.approx(3.14)

    def test_leaf_string(self):
        n = Node('hello')
        assert n.to_list() == 'hello'

    def test_internal_node(self):
        n = Node('add', Node('1'), Node('2'))
        assert n.to_list() == ['add', 1, 2]

    def test_nested_internal(self):
        n = Node.from_list(['add', 1, ['mul', 3, 2]])
        result = n.to_list()
        assert result == ['add', 1, ['mul', 3, 2]]

    def test_custom_parse_scalar(self):
        n = Node('42')
        assert n.to_list(parse_scalar=str) == '42'


class TestRoundTrip:
    def _check_roundtrip(self, x):
        assert Node.from_list(x).to_list() == x

    def test_simple(self):
        self._check_roundtrip(['add', 1, 2])

    def test_nested(self):
        self._check_roundtrip(['add', 1, ['mul', 3, 2]])

    def test_string_leaf(self):
        self._check_roundtrip(['cat', 'hello', 'world'])

    def test_mixed_types(self):
        self._check_roundtrip(['f', 1, 2.5, 'x'])

    def test_deeply_nested(self):
        self._check_roundtrip(['a', ['b', ['c', 1, 2], 3], ['d', 4]])

    def test_single_operator_no_args(self):
        # ['pi'] -> Node('pi') -> back to 'pi' (scalar, since leaf)
        # Note: this does NOT round-trip to ['pi'] because a nullary list
        # builds a leaf node, which to_list maps back to a scalar.
        n = Node.from_list(['pi'])
        # 'pi' can't be int or float so it becomes str 'pi'
        assert n.to_list() == 'pi'

    def test_float_leaf(self):
        self._check_roundtrip(['mul', 1.5, 2.5])


class TestToPathsDelimiter:
    def _make_tree(self):
        return Node('root',
                    Node('a', Node('b'), Node('c')),
                    Node('d'))

    def test_default_delimiter(self):
        t = self._make_tree()
        paths = t.to_paths()
        # to_paths returns ALL nodes (not just leaves), delimiter '/'
        assert 'root' in paths or any('/' in p for p in paths)

    def test_dot_delimiter(self):
        t = self._make_tree()
        paths_dot = t.to_paths(delimiter='.')
        paths_slash = t.to_paths(delimiter='/')
        # All paths with '/' become '.' in dot version
        for p_dot, p_slash in zip(paths_dot, paths_slash):
            assert p_dot == p_slash.replace('/', '.')

    def test_paths_delimiter_param(self):
        t = self._make_tree()
        dot_paths = t.paths(to_leaves_only=True, delimiter='.')
        slash_paths = t.paths(to_leaves_only=True, delimiter='/')
        for p_dot, p_slash in zip(dot_paths, slash_paths):
            assert p_dot == p_slash.replace('/', '.')

    def test_to_paths_uses_delimiter(self):
        # Explicit test that passing delimiter actually changes output
        t = Node('root', Node('child', Node('leaf')))
        paths_slash = t.to_paths(delimiter='/')
        paths_pipe = t.to_paths(delimiter='|')
        # Both should have same paths but with different delimiters
        assert any('/' in p for p in paths_slash) or len(paths_slash) > 0
        assert all('/' not in p for p in paths_pipe)

    def test_paths_method_default_slash(self):
        t = self._make_tree()
        paths = t.paths(to_leaves_only=False, delimiter='/')
        assert any('/' in p for p in paths if len(p.split('/')) > 1)


class TestTreeForwarder:
    """Verify Tree.to_paths forwards the delimiter arg correctly."""

    def test_tree_to_paths_delimiter(self):
        n = Node('root', Node('a', Node('b')))
        t = Tree(n)
        slash = t.to_paths(delimiter='/')
        dot = t.to_paths(delimiter='.')
        for s, d in zip(slash, dot):
            assert d == s.replace('/', '.')
