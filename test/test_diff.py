"""
Tests for structural diff -> DiffTree (Task 3, P3).
"""
import pytest
from AlgoTree import Node
from AlgoTree.diff import diff, DiffTree


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_tree():
    """A small tree: root(a(x), b)."""
    return Node('root',
                Node('a', Node('x', attrs={'val': 1})),
                Node('b', attrs={'color': 'blue'}))


def _count(dt, status):
    """Count nodes in DiffTree with a given diff_status."""
    return sum(1 for n in dt.root.walk() if n['diff_status'] == status)


# ---------------------------------------------------------------------------
# Task 3: diff -> DiffTree basic correctness
# ---------------------------------------------------------------------------

class TestDiffIdentical:
    """diff(t, t) -> all nodes unchanged."""

    def test_summary_all_unchanged(self):
        t = _make_tree()
        dt = diff(t, t)
        s = dt.summary()
        assert s['unchanged'] == t.size
        assert s['added'] == 0
        assert s['removed'] == 0
        assert s['changed'] == 0

    def test_root_is_node(self):
        t = _make_tree()
        dt = diff(t, t)
        assert isinstance(dt.root, Node)

    def test_structure_preserved(self):
        t = _make_tree()
        dt = diff(t, t)
        # Same number of nodes
        assert dt.root.size == t.size


class TestDiffRemovedLeaf:
    """Removing a leaf yields exactly one 'removed' node."""

    def test_remove_leaf_count(self):
        before = Node('root', Node('child'), Node('leaf'))
        after = Node('root', Node('child'))
        dt = diff(before, after)
        s = dt.summary()
        assert s['removed'] == 1
        # root and child are unchanged
        assert s['unchanged'] == 2
        assert s['added'] == 0
        assert s['changed'] == 0

    def test_removed_node_name(self):
        before = Node('root', Node('child'), Node('leaf'))
        after = Node('root', Node('child'))
        dt = diff(before, after)
        removed = [n for n in dt.root.walk() if n['diff_status'] == 'removed']
        assert len(removed) == 1
        assert removed[0].name == 'leaf'


class TestDiffChangedAttr:
    """Changing an attribute yields one 'changed' node with the right attr_delta."""

    def test_changed_attr_count(self):
        before = Node('root', Node('child', attrs={'val': 1}))
        after = Node('root', Node('child', attrs={'val': 2}))
        dt = diff(before, after)
        s = dt.summary()
        assert s['changed'] == 1
        assert s['unchanged'] == 1  # root unchanged
        assert s['added'] == 0
        assert s['removed'] == 0

    def test_changed_attr_delta(self):
        before = Node('root', Node('child', attrs={'val': 1}))
        after = Node('root', Node('child', attrs={'val': 2}))
        dt = diff(before, after)
        changed = [n for n in dt.root.walk() if n['diff_status'] == 'changed']
        assert len(changed) == 1
        delta = changed[0]['attr_delta']
        assert 'val' in delta

    def test_changed_attr_name_change(self):
        """Renaming a node counts as 'changed'."""
        before = Node('root', Node('old_name'))
        after = Node('root', Node('new_name'))
        dt = diff(before, after)
        s = dt.summary()
        assert s['changed'] == 1
        changed = [n for n in dt.root.walk() if n['diff_status'] == 'changed']
        assert changed[0].name == 'new_name'

    def test_attr_delta_added_key(self):
        """Adding a new attr key shows up in attr_delta."""
        before = Node('root', Node('child', attrs={'x': 1}))
        after = Node('root', Node('child', attrs={'x': 1, 'y': 2}))
        dt = diff(before, after)
        changed = [n for n in dt.root.walk() if n['diff_status'] == 'changed']
        assert len(changed) == 1
        delta = changed[0]['attr_delta']
        assert 'y' in delta

    def test_attr_delta_removed_key(self):
        """Removing an attr key shows up in attr_delta."""
        before = Node('root', Node('child', attrs={'x': 1, 'y': 2}))
        after = Node('root', Node('child', attrs={'x': 1}))
        dt = diff(before, after)
        changed = [n for n in dt.root.walk() if n['diff_status'] == 'changed']
        assert len(changed) == 1
        delta = changed[0]['attr_delta']
        assert 'y' in delta


class TestDiffAddedChild:
    """Adding a child yields one 'added' node."""

    def test_added_child_count(self):
        before = Node('root', Node('child'))
        after = Node('root', Node('child'), Node('new_child'))
        dt = diff(before, after)
        s = dt.summary()
        assert s['added'] == 1
        assert s['unchanged'] == 2  # root + child
        assert s['removed'] == 0
        assert s['changed'] == 0

    def test_added_node_name(self):
        before = Node('root', Node('child'))
        after = Node('root', Node('child'), Node('new_child'))
        dt = diff(before, after)
        added = [n for n in dt.root.walk() if n['diff_status'] == 'added']
        assert len(added) == 1
        assert added[0].name == 'new_child'


class TestDiffSummaryOracle:
    """summary() counts match a brute-force oracle."""

    def test_mixed_changes(self):
        before = Node('root',
                      Node('a', Node('x')),
                      Node('b', attrs={'color': 'red'}))
        after = Node('root',
                     Node('a', Node('x'), Node('y')),  # added 'y'
                     Node('b', attrs={'color': 'blue'}))  # attr changed

        dt = diff(before, after)
        s = dt.summary()

        # Brute force count using _count helper
        assert _count(dt, 'added') == s['added']
        assert _count(dt, 'removed') == s['removed']
        assert _count(dt, 'changed') == s['changed']
        assert _count(dt, 'unchanged') == s['unchanged']

        # Specific expectations:
        # root: unchanged
        # a: unchanged (same name, no attrs changed)
        # x: unchanged (same)
        # y: added
        # b: changed (attr color changed)
        assert s['unchanged'] == 3   # root, a, x
        assert s['added'] == 1       # y
        assert s['changed'] == 1     # b
        assert s['removed'] == 0

    def test_total_size(self):
        before = Node('root', Node('a'), Node('b'), Node('c'))
        after = Node('root', Node('a'), Node('d'))
        dt = diff(before, after)
        s = dt.summary()
        total = s['added'] + s['removed'] + s['changed'] + s['unchanged']
        # diff tree size = max(before.size, after.size) where children are position-aligned
        # root + max(3,2) = 1 + 3 = 4 (b->d changed at pos 1, c removed at pos 2)
        assert total == dt.root.size


class TestDiffTreeInterface:
    """DiffTree has .root, .summary(), .changed_nodes()."""

    def test_is_difftree(self):
        t = _make_tree()
        dt = diff(t, t)
        assert isinstance(dt, DiffTree)

    def test_root_is_node(self):
        t = _make_tree()
        dt = diff(t, t)
        assert isinstance(dt.root, Node)

    def test_summary_keys(self):
        t = _make_tree()
        dt = diff(t, t)
        s = dt.summary()
        assert set(s.keys()) == {'added', 'removed', 'changed', 'unchanged'}

    def test_changed_nodes_returns_list(self):
        before = Node('root', Node('a'))
        after = Node('root', Node('b'))
        dt = diff(before, after)
        cn = dt.changed_nodes()
        assert isinstance(cn, list)

    def test_changed_nodes_excludes_unchanged(self):
        before = _make_tree()
        after = _make_tree()
        dt = diff(before, after)
        cn = dt.changed_nodes()
        # All nodes are unchanged, so changed_nodes should be empty
        assert cn == []

    def test_changed_nodes_includes_changed(self):
        before = Node('root', Node('a'))
        after = Node('root', Node('b'))
        dt = diff(before, after)
        cn = dt.changed_nodes()
        assert len(cn) == 1
        assert cn[0].name == 'b'

    def test_changed_nodes_includes_added_and_removed(self):
        before = Node('root', Node('a'), Node('b'))
        after = Node('root', Node('a'))
        dt = diff(before, after)
        cn = dt.changed_nodes()
        # 'b' was removed
        names = [n.name for n in cn]
        assert 'b' in names


class TestDiffAttrDelta:
    """_attr_delta computes correct diff on attrs dicts."""

    def test_unchanged_attrs_have_empty_delta(self):
        before = Node('root', attrs={'x': 1, 'y': 2})
        after = Node('root', attrs={'x': 1, 'y': 2})
        dt = diff(before, after)
        root_node = dt.root
        # Root should be unchanged
        assert root_node['diff_status'] == 'unchanged'
        assert root_node['attr_delta'] == {}

    def test_added_node_has_empty_delta(self):
        before = Node('root')
        after = Node('root', Node('child'))
        dt = diff(before, after)
        added = [n for n in dt.root.walk() if n['diff_status'] == 'added']
        assert len(added) == 1
        assert added[0]['attr_delta'] == {}

    def test_removed_node_has_empty_delta(self):
        before = Node('root', Node('child'))
        after = Node('root')
        dt = diff(before, after)
        removed = [n for n in dt.root.walk() if n['diff_status'] == 'removed']
        assert len(removed) == 1
        assert removed[0]['attr_delta'] == {}
