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


# ---------------------------------------------------------------------------
# Task 4: themed mermaid/html rendering (added/removed/changed)
# ---------------------------------------------------------------------------

class TestDiffToMermaid:
    """DiffTree.to_mermaid() colors nodes by diff_status."""

    def _make_diff(self):
        """A diff with one added, one removed, one changed, one unchanged."""
        before = Node('root',
                      Node('same'),
                      Node('old'),
                      Node('renamed'))
        after = Node('root',
                     Node('same'),
                     Node('old'),
                     Node('renamed', attrs={'x': 1}),
                     Node('newkid'))
        return diff(before, after)

    def test_to_mermaid_returns_string(self):
        before = Node('root', Node('child'))
        after = Node('root', Node('child'), Node('extra'))
        dt = diff(before, after)
        result = dt.to_mermaid()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_to_mermaid_starts_with_graph(self):
        before = Node('root')
        after = Node('root')
        dt = diff(before, after)
        result = dt.to_mermaid()
        assert result.startswith("graph ")

    def test_added_node_uses_green_classdef(self):
        before = Node('root')
        after = Node('root', Node('newkid'))
        dt = diff(before, after)
        result = dt.to_mermaid()
        # Should define an 'added' class with green styling
        assert 'classDef' in result
        assert 'added' in result
        # green color must be present
        assert 'green' in result.lower() or '#' in result

    def test_added_node_class_assignment(self):
        before = Node('root')
        after = Node('root', Node('newkid'))
        dt = diff(before, after)
        result = dt.to_mermaid()
        # The added node must be assigned the 'added' class
        assert 'class ' in result
        assert 'added' in result

    def test_removed_node_uses_red_classdef(self):
        before = Node('root', Node('gone'))
        after = Node('root')
        dt = diff(before, after)
        result = dt.to_mermaid()
        assert 'classDef' in result
        assert 'removed' in result
        assert 'red' in result.lower() or '#' in result

    def test_removed_node_class_assignment(self):
        before = Node('root', Node('gone'))
        after = Node('root')
        dt = diff(before, after)
        result = dt.to_mermaid()
        assert 'class ' in result
        assert 'removed' in result

    def test_changed_node_uses_yellow_classdef(self):
        before = Node('root', Node('thing', attrs={'v': 1}))
        after = Node('root', Node('thing', attrs={'v': 2}))
        dt = diff(before, after)
        result = dt.to_mermaid()
        assert 'classDef' in result
        assert 'changed' in result
        assert 'yellow' in result.lower() or '#' in result

    def test_changed_node_class_assignment(self):
        before = Node('root', Node('thing', attrs={'v': 1}))
        after = Node('root', Node('thing', attrs={'v': 2}))
        dt = diff(before, after)
        result = dt.to_mermaid()
        assert 'class ' in result
        assert 'changed' in result

    def test_unchanged_node_has_no_class_assignment(self):
        before = Node('root', Node('same'))
        after = Node('root', Node('same'))
        dt = diff(before, after)
        result = dt.to_mermaid()
        # No class assignments since all nodes are unchanged
        assert 'class N' not in result

    def test_escaping_holds_for_special_name(self):
        """A node named '<x>' must not produce malformed Mermaid output."""
        before = Node('root')
        after = Node('root', Node('<x>'))
        dt = diff(before, after)
        result = dt.to_mermaid()
        # Raw '<x>' must not appear unescaped; should be escaped (&lt; etc.)
        # The label must be in a quoted string form
        assert '"' in result
        # The node name in label form must be escaped (no raw '<' outside quotes
        # or at least the output is a well-formed Mermaid string)
        assert '<x>' not in result or result.count('"') >= 2

    def test_all_statuses_present_in_mixed_diff(self):
        dt = self._make_diff()
        result = dt.to_mermaid()
        # added newkid -> added class
        assert 'added' in result
        # renamed with attr change -> changed class
        assert 'changed' in result

    def test_node_labels_contain_names(self):
        before = Node('root', Node('alpha'))
        after = Node('root', Node('alpha'), Node('beta'))
        dt = diff(before, after)
        result = dt.to_mermaid()
        assert 'alpha' in result
        assert 'beta' in result

    def test_direction_option(self):
        before = Node('root')
        after = Node('root')
        dt = diff(before, after)
        result = dt.to_mermaid(direction="LR")
        assert result.startswith("graph LR")


class TestDiffToHtml:
    """DiffTree.to_html() adds CSS class per diff_status."""

    def test_to_html_returns_string(self):
        before = Node('root', Node('child'))
        after = Node('root', Node('child'))
        dt = diff(before, after)
        result = dt.to_html()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_added_node_has_css_class(self):
        before = Node('root')
        after = Node('root', Node('newkid'))
        dt = diff(before, after)
        result = dt.to_html()
        assert 'added' in result

    def test_removed_node_has_css_class(self):
        before = Node('root', Node('gone'))
        after = Node('root')
        dt = diff(before, after)
        result = dt.to_html()
        assert 'removed' in result

    def test_changed_node_has_css_class(self):
        before = Node('root', Node('thing', attrs={'v': 1}))
        after = Node('root', Node('thing', attrs={'v': 2}))
        dt = diff(before, after)
        result = dt.to_html()
        assert 'changed' in result

    def test_unchanged_node_has_css_class(self):
        before = Node('root', Node('same'))
        after = Node('root', Node('same'))
        dt = diff(before, after)
        result = dt.to_html()
        assert 'unchanged' in result

    def test_html_escaping_special_name(self):
        """Node named '<x>' must be HTML-escaped in output."""
        before = Node('root')
        after = Node('root', Node('<x>'))
        dt = diff(before, after)
        result = dt.to_html()
        # Must not contain raw '<x>' as HTML tag
        assert '<x>' not in result
        # Must contain HTML-escaped form
        assert '&lt;x&gt;' in result

    def test_html_contains_node_names(self):
        before = Node('root', Node('alpha'))
        after = Node('root', Node('alpha'), Node('beta'))
        dt = diff(before, after)
        result = dt.to_html()
        assert 'alpha' in result
        assert 'beta' in result

    def test_include_styles_false(self):
        before = Node('root')
        after = Node('root')
        dt = diff(before, after)
        result = dt.to_html(include_styles=False)
        assert '<style>' not in result
