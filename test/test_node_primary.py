"""
Task 3: Node is the primary type.

Assert that the full pipeline works with a bare Node, without ever constructing
a Tree.  Covers:
  - construction (Node / from_dict / from_paths)
  - transforms (prune / map / filter)
  - queries (find_all / select / locate / cursors_at / count / exists)
  - render (node.render('unicode'))
  - serialization round-trip (dumps / loads)
  - to_dict round-trip
  - interop (node_to_flat_dict / flat_dict_to_node)
  - selectors.select() works with bare Node
"""

import pytest
import json
import tempfile
import os
from AlgoTree import Node
from AlgoTree import (
    name as sel_name,
    leaf as sel_leaf,
    depth as sel_depth,
    attrs as sel_attrs,
    predicate as sel_predicate,
)
from AlgoTree.selectors import Selector
from AlgoTree.serialization import dumps, loads, save, load
from AlgoTree.interop import node_to_flat_dict, flat_dict_to_node


# ---------------------------------------------------------------------------
# Shared fixture -- representative tree with attrs and depth 3
# ---------------------------------------------------------------------------

def make_tree() -> Node:
    """Build a depth-3 tree with attrs for all tests."""
    return Node(
        "root",
        Node(
            "branch_a",
            Node("leaf_a1", attrs={"value": 10, "type": "item"}),
            Node("leaf_a2", attrs={"value": 20, "type": "item"}),
            attrs={"side": "left"},
        ),
        Node(
            "branch_b",
            Node("leaf_b1", attrs={"value": 30, "type": "item"}),
            attrs={"side": "right"},
        ),
        attrs={"root_attr": True},
    )


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestNodeConstruction:

    def test_direct_construction(self):
        root = make_tree()
        assert root.name == "root"
        assert root.get("root_attr") is True
        assert len(root.children) == 2

    def test_from_dict_round_trip(self):
        original = make_tree()
        d = original.to_dict()
        recovered = Node.from_dict(d)
        assert recovered == original

    def test_from_dict_custom_children_key(self):
        data = {
            "name": "root",
            "nodes": [
                {"name": "child1"},
                {"name": "child2"},
            ],
        }
        root = Node.from_dict(data, children_key="nodes")
        assert root.name == "root"
        assert len(root.children) == 2

    def test_from_dict_does_not_mutate_input(self):
        data = {
            "name": "root",
            "children": [{"name": "c"}],
            "extra": 42,
        }
        import copy
        original_data = copy.deepcopy(data)
        Node.from_dict(data)
        assert data == original_data

    def test_from_paths(self):
        paths = [
            "root/a/b",
            "root/a/c",
            "root/d",
        ]
        root = Node.from_paths(paths)
        assert root.name == "root"
        names = {ch.name for ch in root.children}
        assert "a" in names
        assert "d" in names

    def test_from_paths_empty(self):
        root = Node.from_paths([])
        assert root.name == "root"


# ---------------------------------------------------------------------------
# Transforms (prune / map / filter)
# ---------------------------------------------------------------------------

class TestNodeTransforms:

    def test_prune_by_name_leaf(self):
        # Prune a leaf node by name - leaf has no descendants so it is removed
        root = make_tree()
        pruned = root.prune("leaf_a1")
        assert pruned is not None
        assert pruned.find("leaf_a1") is None
        assert pruned.find("leaf_a2") is not None

    def test_prune_by_predicate(self):
        # Prune all leaf items with value > 15 -- these are leaves, so they
        # have no descendants that could rescue them.
        root = make_tree()
        pruned = root.prune(lambda n: n.get("value", 0) > 15)
        assert pruned is not None
        # leaf_a2 (value=20) and leaf_b1 (value=30) should be gone
        assert pruned.find("leaf_a2") is None
        assert pruned.find("leaf_b1") is None
        # leaf_a1 (value=10) survives
        assert pruned.find("leaf_a1") is not None

    def test_prune_returns_none_when_all_pruned(self):
        root = make_tree()
        result = root.prune(lambda _: True)
        assert result is None

    def test_prune_with_selector_removes_leaf(self):
        # prune(sel_leaf()) removes leaf nodes; branches with no surviving
        # descendants become leaves themselves after the prune.
        root = make_tree()
        pruned = root.prune(sel_leaf())
        assert pruned is not None
        # All original leaf_* nodes should be gone
        assert pruned.find("leaf_a1") is None
        assert pruned.find("leaf_a2") is None
        assert pruned.find("leaf_b1") is None
        # Internal nodes still exist
        assert pruned.find("branch_a") is not None
        assert pruned.find("branch_b") is not None

    def test_map_strict(self):
        root = make_tree()
        mapped = root.map(lambda n: n.with_attrs(tagged=True))
        for node in mapped.walk():
            assert node.get("tagged") is True

    def test_filter_keeps_matching_subtree(self):
        root = make_tree()
        filtered = root.filter(lambda n: n.get("type") == "item")
        assert filtered is not None
        # All items must be present
        items = list(filtered.find_all(lambda n: n.get("type") == "item"))
        assert len(items) == 3

    def test_filter_returns_none_when_nothing_matches(self):
        root = make_tree()
        result = root.filter(lambda n: n.name == "nonexistent")
        assert result is None

    def test_filter_with_selector(self):
        root = make_tree()
        sel = sel_attrs(type="item")
        filtered = root.filter(sel)
        assert filtered is not None
        items = list(filtered.find_all(sel))
        assert len(items) == 3

    def test_graft(self):
        root = make_tree()
        new_leaf = Node("extra", attrs={"value": 99})
        grafted = root.graft("branch_a", new_leaf)
        branch_a = grafted.find("branch_a")
        assert branch_a is not None
        child_names = {c.name for c in branch_a.children}
        assert "extra" in child_names

    def test_flatten(self):
        # Build a 4-level tree so flatten(max_depth=1) actually moves things.
        # max_depth=1 means: at depth-1 nodes, collect all their descendants
        # as direct children.  For root->a->b->c, after flatten(max_depth=1),
        # 'a' should have 'c' (the deepest leaf) as its only child.
        deep_root = Node("root", Node("a", Node("b", Node("c"))))
        flat = deep_root.flatten(max_depth=1)
        a_node = flat.find("a")
        assert a_node is not None
        # 'b' should be gone; 'c' is now direct child of 'a'
        child_names = {ch.name for ch in a_node.children}
        assert "c" in child_names
        assert "b" not in child_names

    def test_reduce(self):
        root = make_tree()
        count = root.reduce(lambda acc, _n: acc + 1, 0)
        assert count == root.size


# ---------------------------------------------------------------------------
# Queries (find_all / select / locate / cursors_at / count / exists)
# ---------------------------------------------------------------------------

class TestNodeQueries:

    def test_find_by_name(self):
        root = make_tree()
        node = root.find("leaf_a1")
        assert node is not None
        assert node.name == "leaf_a1"

    def test_find_returns_none(self):
        root = make_tree()
        assert root.find("nonexistent") is None

    def test_find_all_by_predicate(self):
        root = make_tree()
        items = root.find_all(lambda n: n.get("type") == "item")
        assert len(items) == 3

    def test_select_returns_iterator(self):
        root = make_tree()
        sel = sel_attrs(type="item")
        results = list(root.select(sel))
        assert len(results) == 3

    def test_select_name_pattern(self):
        root = make_tree()
        results = list(root.select("leaf*"))
        assert len(results) == 3

    def test_locate_returns_cursor(self):
        root = make_tree()
        cursor = root.locate("leaf_a1")
        assert cursor is not None
        assert cursor.node.name == "leaf_a1"

    def test_locate_returns_none_when_not_found(self):
        root = make_tree()
        cursor = root.locate("nonexistent")
        assert cursor is None

    def test_cursors_at_returns_list(self):
        root = make_tree()
        cursors = root.cursors_at(sel_attrs(type="item"))
        assert len(cursors) == 3
        names = {c.node.name for c in cursors}
        assert "leaf_a1" in names
        assert "leaf_a2" in names
        assert "leaf_b1" in names

    def test_count_all_nodes(self):
        root = make_tree()
        # root + 2 branches + 3 leaves = 6
        assert root.count() == 6

    def test_count_with_selector(self):
        root = make_tree()
        assert root.count(lambda n: n.get("type") == "item") == 3

    def test_exists_true(self):
        root = make_tree()
        assert root.exists("leaf_b1") is True

    def test_exists_false(self):
        root = make_tree()
        assert root.exists("nonexistent") is False

    def test_get_path(self):
        root = make_tree()
        node = root.get_path("root/branch_a/leaf_a1")
        assert node is not None
        assert node.name == "leaf_a1"

    def test_get_path_not_found(self):
        root = make_tree()
        assert root.get_path("root/branch_x") is None

    def test_paths_to_leaves_only(self):
        root = make_tree()
        p = root.paths(to_leaves_only=True)
        assert len(p) == 3
        for path in p:
            assert path.endswith(("leaf_a1", "leaf_a2", "leaf_b1"))

    def test_paths_all(self):
        root = make_tree()
        p = root.paths(to_leaves_only=False)
        assert len(p) == 6

    def test_to_paths(self):
        root = make_tree()
        p = root.to_paths()
        assert len(p) == 6

    def test_nodes_list(self):
        root = make_tree()
        assert len(root.nodes()) == root.size

    def test_update_attrs(self):
        root = make_tree()
        updated = root.update_attrs(new_key="new_val")
        assert updated.get("new_key") == "new_val"
        assert updated.get("root_attr") is True  # original preserved

    def test_pipe_operator(self):
        root = make_tree()
        result = root | (lambda n: n.size)
        assert result == 6

    def test_rshift_operator(self):
        root = make_tree()
        result = root >> (lambda n: n.name)
        assert result == "root"


# ---------------------------------------------------------------------------
# Properties (is_leaf / height / size / walk / leaves / descendants)
# ---------------------------------------------------------------------------

class TestNodeProperties:

    def test_is_leaf(self):
        root = make_tree()
        assert not root.is_leaf
        for leaf_node in root.leaves():
            assert leaf_node.is_leaf

    def test_height(self):
        root = make_tree()
        # root -> branch -> leaf = height 2
        assert root.height == 2

    def test_size(self):
        root = make_tree()
        assert root.size == 6

    def test_walk_preorder(self):
        root = make_tree()
        nodes = list(root.walk("preorder"))
        assert nodes[0].name == "root"
        assert len(nodes) == 6

    def test_walk_postorder(self):
        root = make_tree()
        nodes = list(root.walk("postorder"))
        assert nodes[-1].name == "root"

    def test_walk_levelorder(self):
        root = make_tree()
        nodes = list(root.walk("levelorder"))
        assert nodes[0].name == "root"
        # Level 1 nodes
        level1 = {nodes[1].name, nodes[2].name}
        assert level1 == {"branch_a", "branch_b"}

    def test_leaves(self):
        root = make_tree()
        leaves = list(root.leaves())
        assert len(leaves) == 3
        leaf_names = {l.name for l in leaves}
        assert leaf_names == {"leaf_a1", "leaf_a2", "leaf_b1"}

    def test_descendants(self):
        root = make_tree()
        descs = list(root.descendants())
        assert len(descs) == 5  # all except root itself


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

class TestNodeRender:

    def test_render_unicode(self):
        root = make_tree()
        rendered = root.render("unicode")
        assert isinstance(rendered, str)
        assert "root" in rendered
        assert "branch_a" in rendered
        assert "leaf_a1" in rendered

    def test_render_ascii(self):
        root = make_tree()
        rendered = root.render("ascii")
        assert isinstance(rendered, str)
        assert "root" in rendered

    def test_fold_counts(self):
        root = make_tree()
        count = root.fold(lambda n, child_results: 1 + sum(child_results))
        assert count == 6


# ---------------------------------------------------------------------------
# Serialization round-trip (no Tree involved)
# ---------------------------------------------------------------------------

class TestNodeSerializationRoundTrip:

    def test_dumps_loads_json(self):
        root = make_tree()
        json_str = dumps(root)
        recovered = loads(json_str)
        assert isinstance(recovered, Node)
        assert recovered == root

    def test_dumps_loads_yaml(self):
        yaml = pytest.importorskip("yaml")  # skip if pyyaml not installed
        root = make_tree()
        yaml_str = dumps(root, format="yaml")
        recovered = loads(yaml_str, format="yaml")
        assert isinstance(recovered, Node)
        assert recovered == root

    def test_dumps_loads_xml(self):
        root = make_tree()
        xml_str = dumps(root, format="xml")
        recovered = loads(xml_str, format="xml")
        assert isinstance(recovered, Node)
        # XML round-trip: names and structure preserved
        assert recovered.name == root.name
        assert len(recovered.children) == len(root.children)

    def test_save_load_json_file(self):
        root = make_tree()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "tree.json")
            save(root, path)
            recovered = load(path)
        assert isinstance(recovered, Node)
        assert recovered == root

    def test_save_load_pickle_file(self):
        root = make_tree()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "tree.pkl")
            save(root, path)
            recovered = load(path)
        assert isinstance(recovered, Node)
        assert recovered == root

    def test_to_dict_round_trip(self):
        root = make_tree()
        d = root.to_dict()
        recovered = Node.from_dict(d)
        assert recovered == root

    def test_to_dict_custom_children_key_round_trip(self):
        root = make_tree()
        d = root.to_dict(children_key="nodes")
        recovered = Node.from_dict(d, children_key="nodes")
        assert recovered == root


# ---------------------------------------------------------------------------
# Interop (node_to_flat_dict / flat_dict_to_node) -- no Tree
# ---------------------------------------------------------------------------

class TestNodeInteropRoundTrip:

    def test_node_to_flat_dict_and_back(self):
        root = make_tree()
        flat = node_to_flat_dict(root)
        assert "root" in flat
        recovered = flat_dict_to_node(flat, "root")
        assert isinstance(recovered, Node)
        assert recovered.name == root.name
        assert len(recovered.children) == len(root.children)

    def test_flat_dict_preserves_attrs(self):
        root = make_tree()
        flat = node_to_flat_dict(root)
        recovered = flat_dict_to_node(flat, "root")
        branch_a = recovered.find("branch_a")
        assert branch_a is not None
        assert branch_a.get("side") == "left"

    def test_flat_dict_preserves_leaf_attrs(self):
        root = make_tree()
        flat = node_to_flat_dict(root)
        recovered = flat_dict_to_node(flat, "root")
        leaf_a1 = recovered.find("leaf_a1")
        assert leaf_a1 is not None
        assert leaf_a1.get("value") == 10
        assert leaf_a1.get("type") == "item"


# ---------------------------------------------------------------------------
# Selectors work with bare Node
# ---------------------------------------------------------------------------

class TestSelectorWithBareNode:

    def test_name_selector_select(self):
        root = make_tree()
        sel = sel_name("leaf_a1")
        results = list(sel.select(root))  # passes Node, not Tree
        assert len(results) == 1
        assert results[0].name == "leaf_a1"

    def test_leaf_selector_select(self):
        root = make_tree()
        sel = sel_leaf()
        results = list(sel.select(root))
        assert len(results) == 3

    def test_depth_selector_select(self):
        root = make_tree()
        sel = sel_depth(2)
        results = list(sel.select(root))
        names = {n.name for n in results}
        assert names == {"leaf_a1", "leaf_a2", "leaf_b1"}

    def test_attrs_selector_select(self):
        root = make_tree()
        sel = sel_attrs(type="item")
        results = list(sel.select(root))
        assert len(results) == 3

    def test_combined_selector(self):
        root = make_tree()
        sel = sel_attrs(type="item") & sel_predicate(lambda n: n.get("value", 0) > 15)
        results = list(sel.select(root))
        assert len(results) == 2
        values = {n.get("value") for n in results}
        assert values == {20, 30}

    def test_selector_count_with_bare_node(self):
        root = make_tree()
        sel = sel_attrs(type="item")
        assert sel.count(root) == 3

    def test_selector_exists_with_bare_node(self):
        root = make_tree()
        assert sel_name("leaf_b1").exists(root) is True
        assert sel_name("nonexistent").exists(root) is False

    def test_selector_first_with_bare_node(self):
        root = make_tree()
        first = sel_attrs(side="left").first(root)
        assert first is not None
        assert first.name == "branch_a"
