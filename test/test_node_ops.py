"""
Tests for the Tree-equivalent operations added to Node (Task 1: additive).

Each test builds the same tree as both a bare Node (root) and a Tree(root),
then asserts that the Node method and the Tree method produce structurally
identical results.
"""

import unittest
from AlgoTree.node import Node
from AlgoTree.tree import Tree


def _make_tree():
    """Representative depth-3 tree with attrs for thorough testing."""
    a1 = Node("a1", attrs={"value": 10, "active": True})
    a2 = Node("a2", attrs={"value": 20, "active": False})
    a = Node("a", a1, a2, attrs={"value": 1, "active": True})
    b1 = Node("b1", attrs={"value": 30, "active": True})
    b = Node("b", b1, attrs={"value": 2, "active": False})
    c = Node("c", attrs={"value": 3, "active": True})
    return Node("root", a, b, c, attrs={"value": 0, "tag": "root"})


class TestNodeFromDict(unittest.TestCase):
    """Test Node.from_dict with children_key parameter."""

    def test_default_children_key(self):
        data = {
            "name": "root",
            "value": 1,
            "children": [
                {"name": "child1", "value": 2},
                {"name": "child2", "value": 3},
            ],
        }
        node = Node.from_dict(data)
        self.assertEqual(node.name, "root")
        self.assertEqual(node.get("value"), 1)
        self.assertEqual(len(node.children), 2)
        self.assertEqual(node.children[0].name, "child1")

    def test_custom_children_key(self):
        data = {
            "name": "root",
            "items": [
                {"name": "a"},
                {"name": "b", "items": [{"name": "c"}]},
            ],
        }
        node = Node.from_dict(data, children_key="items")
        self.assertEqual(node.name, "root")
        self.assertEqual(len(node.children), 2)
        self.assertEqual(node.children[1].children[0].name, "c")

    def test_does_not_mutate_input(self):
        data = {
            "name": "root",
            "value": 42,
            "children": [{"name": "child"}],
        }
        import copy
        original = copy.deepcopy(data)
        Node.from_dict(data)
        self.assertEqual(data, original)

    def test_matches_tree_from_dict(self):
        data = {
            "name": "root",
            "value": 1,
            "children": [
                {"name": "child1", "value": 2},
                {"name": "child2", "value": 3, "children": [
                    {"name": "grandchild", "value": 4}
                ]},
            ],
        }
        node = Node.from_dict(data)
        # Tree.from_dict uses pop so we need a fresh copy
        import copy
        tree = Tree.from_dict(copy.deepcopy(data))
        self.assertEqual(node.to_dict(), tree.to_dict())


class TestNodeFromPaths(unittest.TestCase):
    """Test Node.from_paths classmethod."""

    def test_basic_paths(self):
        paths = ["root/a/b", "root/a/c", "root/d"]
        node = Node.from_paths(paths)
        self.assertEqual(node.name, "root")
        self.assertEqual(len(node.children), 2)

    def test_matches_tree_from_paths(self):
        paths = ["root/a/b", "root/a/c", "root/d"]
        node = Node.from_paths(paths)
        tree = Tree.from_paths(paths)
        self.assertEqual(node.to_dict(), tree.root.to_dict())

    def test_empty_paths(self):
        node = Node.from_paths([])
        self.assertEqual(node.name, "root")
        self.assertEqual(len(node.children), 0)

    def test_custom_delimiter(self):
        paths = ["root.a.b", "root.a.c"]
        node = Node.from_paths(paths, delimiter=".")
        self.assertEqual(node.name, "root")
        self.assertEqual(len(node.children), 1)  # only 'a'
        self.assertEqual(node.children[0].name, "a")
        self.assertEqual(len(node.children[0].children), 2)


class TestNodeReduce(unittest.TestCase):
    """Test Node.reduce."""

    def test_sum_values(self):
        root = _make_tree()
        tree = Tree(root)
        node_result = root.reduce(lambda acc, n: acc + n.get("value", 0), 0)
        tree_result = tree.reduce(lambda acc, n: acc + n.get("value", 0), 0)
        self.assertEqual(node_result, tree_result)

    def test_preorder(self):
        root = _make_tree()
        tree = Tree(root)
        node_names = root.reduce(lambda acc, n: acc + [n.name], [], order="preorder")
        tree_names = tree.reduce(lambda acc, n: acc + [n.name], [], order="preorder")
        self.assertEqual(node_names, tree_names)

    def test_postorder(self):
        root = _make_tree()
        tree = Tree(root)
        node_names = root.reduce(lambda acc, n: acc + [n.name], [], order="postorder")
        tree_names = tree.reduce(lambda acc, n: acc + [n.name], [], order="postorder")
        self.assertEqual(node_names, tree_names)


class TestNodePrune(unittest.TestCase):
    """Test Node.prune."""

    def test_prune_inactive(self):
        root = _make_tree()
        tree = Tree(root)
        pruned_node = root.prune(lambda n: not n.get("active", False))
        pruned_tree = tree.prune(lambda n: not n.get("active", False))
        self.assertIsNotNone(pruned_node)
        # Compare structure - prune returns Optional[Node] vs Tree
        self.assertEqual(pruned_node.to_dict(), pruned_tree.root.to_dict())

    def test_prune_returns_none_when_all_pruned(self):
        root = Node("only")
        result = root.prune(lambda n: True)  # prune everything
        self.assertIsNone(result)

    def test_prune_with_selector_object(self):
        from AlgoTree.selectors import NameSelector
        root = _make_tree()
        tree = Tree(root)
        sel = NameSelector("a1")
        pruned_node = root.prune(sel)
        pruned_tree = tree.prune(sel)
        self.assertIsNotNone(pruned_node)
        self.assertEqual(pruned_node.to_dict(), pruned_tree.root.to_dict())


class TestNodeGraft(unittest.TestCase):
    """Test Node.graft."""

    def test_graft_node(self):
        root = _make_tree()
        tree = Tree(root)
        subtree = Node("grafted", attrs={"value": 99})
        grafted_node = root.graft(lambda n: n.name == "c", subtree)
        grafted_tree = tree.graft(lambda n: n.name == "c", subtree)
        self.assertEqual(grafted_node.to_dict(), grafted_tree.root.to_dict())

    def test_graft_tree_object(self):
        root = _make_tree()
        tree = Tree(root)
        subtree_node = Node("grafted")
        subtree_tree = Tree(subtree_node)
        # graft accepts both Node and Tree
        grafted_node = root.graft(lambda n: n.name == "c", subtree_tree)
        grafted_tree = tree.graft(lambda n: n.name == "c", subtree_node)
        self.assertEqual(grafted_node.to_dict(), grafted_tree.root.to_dict())

    def test_graft_by_name(self):
        root = _make_tree()
        tree = Tree(root)
        subtree = Node("new_child")
        grafted_node = root.graft("c", subtree)
        grafted_tree = tree.graft("c", subtree)
        self.assertEqual(grafted_node.to_dict(), grafted_tree.root.to_dict())


class TestNodeFlatten(unittest.TestCase):
    """Test Node.flatten."""

    def test_flatten_max_depth(self):
        root = Node("root",
            Node("a",
                Node("b",
                    Node("c")
                )
            )
        )
        tree = Tree(root)
        flattened_node = root.flatten(max_depth=1)
        flattened_tree = tree.flatten(max_depth=1)
        self.assertEqual(flattened_node.to_dict(), flattened_tree.root.to_dict())

    def test_flatten_no_depth(self):
        root = _make_tree()
        tree = Tree(root)
        # max_depth=None means full flattening
        flattened_node = root.flatten()
        flattened_tree = tree.flatten()
        self.assertEqual(flattened_node.to_dict(), flattened_tree.root.to_dict())


class TestNodeSelect(unittest.TestCase):
    """Test Node.select (iterator)."""

    def test_select_by_predicate(self):
        root = _make_tree()
        tree = Tree(root)
        node_results = list(root.select(lambda n: n.get("active", False)))
        tree_results = list(tree.select(lambda n: n.get("active", False)))
        self.assertEqual(
            [n.name for n in node_results],
            [n.name for n in tree_results]
        )

    def test_select_with_selector(self):
        from AlgoTree.selectors import NameSelector
        root = _make_tree()
        tree = Tree(root)
        sel = NameSelector("a*")
        node_results = list(root.select(sel))
        tree_results = list(tree.select(sel))
        self.assertEqual(
            [n.name for n in node_results],
            [n.name for n in tree_results]
        )

    def test_select_by_name(self):
        root = _make_tree()
        results = list(root.select("a"))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "a")


class TestNodeExists(unittest.TestCase):
    """Test Node.exists."""

    def test_exists_found(self):
        root = _make_tree()
        tree = Tree(root)
        self.assertEqual(root.exists("a"), tree.exists("a"))
        self.assertTrue(root.exists("a"))

    def test_exists_not_found(self):
        root = _make_tree()
        tree = Tree(root)
        self.assertEqual(root.exists("zzz"), tree.exists("zzz"))
        self.assertFalse(root.exists("zzz"))

    def test_exists_predicate(self):
        root = _make_tree()
        tree = Tree(root)
        pred = lambda n: n.get("value", 0) > 25
        self.assertEqual(root.exists(pred), tree.exists(pred))


class TestNodeCount(unittest.TestCase):
    """Test Node.count."""

    def test_count_all(self):
        root = _make_tree()
        tree = Tree(root)
        self.assertEqual(root.count(), tree.count())

    def test_count_with_selector(self):
        root = _make_tree()
        tree = Tree(root)
        sel = lambda n: n.get("active", False)
        self.assertEqual(root.count(sel), tree.count(sel))

    def test_count_none(self):
        root = _make_tree()
        self.assertEqual(root.count(), root.size)


class TestNodeLocate(unittest.TestCase):
    """Test Node.locate and Node.cursors_at."""

    def test_locate_found(self):
        root = _make_tree()
        tree = Tree(root)
        cursor_node = root.locate("b1")
        cursor_tree = tree.locate("b1")
        self.assertIsNotNone(cursor_node)
        self.assertIsNotNone(cursor_tree)
        self.assertEqual(cursor_node.node.name, cursor_tree.node.name)
        self.assertEqual(cursor_node.depth, cursor_tree.depth)

    def test_locate_not_found(self):
        root = _make_tree()
        self.assertIsNone(root.locate("zzz"))

    def test_cursors_at(self):
        root = _make_tree()
        tree = Tree(root)
        sel = lambda n: n.get("active", False)
        node_cursors = root.cursors_at(sel)
        tree_cursors = tree.cursors_at(sel)
        self.assertEqual(len(node_cursors), len(tree_cursors))
        node_names = sorted(c.node.name for c in node_cursors)
        tree_names = sorted(c.node.name for c in tree_cursors)
        self.assertEqual(node_names, tree_names)

    def test_cursor_matches_static(self):
        from AlgoTree.cursor import Cursor
        root = _make_tree()
        cursor = Cursor(root)
        # _cursor_matches is a static helper
        self.assertTrue(Node._cursor_matches(cursor, "root"))
        self.assertFalse(Node._cursor_matches(cursor, "zzz"))


class TestNodeGetPath(unittest.TestCase):
    """Test Node.get_path."""

    def test_get_path_found(self):
        root = _make_tree()
        tree = Tree(root)
        node_result = root.get_path("root/a/a1")
        tree_result = tree.get_path("root/a/a1")
        self.assertIsNotNone(node_result)
        self.assertEqual(node_result.name, tree_result.name)

    def test_get_path_not_found(self):
        root = _make_tree()
        tree = Tree(root)
        self.assertIsNone(root.get_path("root/x/y"))
        self.assertIsNone(tree.get_path("root/x/y"))

    def test_get_path_root(self):
        root = _make_tree()
        result = root.get_path("root")
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "root")


class TestNodePaths(unittest.TestCase):
    """Test Node.paths and Node.to_paths."""

    def test_paths_leaves_only(self):
        root = _make_tree()
        tree = Tree(root)
        node_paths = sorted(root.paths(to_leaves_only=True))
        tree_paths = sorted(tree.paths(to_leaves_only=True))
        self.assertEqual(node_paths, tree_paths)

    def test_paths_all_nodes(self):
        root = _make_tree()
        tree = Tree(root)
        node_paths = sorted(root.paths(to_leaves_only=False))
        tree_paths = sorted(tree.paths(to_leaves_only=False))
        self.assertEqual(node_paths, tree_paths)

    def test_to_paths(self):
        root = _make_tree()
        tree = Tree(root)
        node_paths = sorted(root.to_paths())
        tree_paths = sorted(tree.to_paths())
        self.assertEqual(node_paths, tree_paths)


class TestNodeNodes(unittest.TestCase):
    """Test Node.nodes() method."""

    def test_nodes_list(self):
        root = _make_tree()
        tree = Tree(root)
        node_list = root.nodes()
        tree_list = tree.nodes()
        self.assertEqual(len(node_list), len(tree_list))
        self.assertEqual(
            [n.name for n in node_list],
            [n.name for n in tree_list]
        )

    def test_nodes_returns_list(self):
        root = _make_tree()
        self.assertIsInstance(root.nodes(), list)


class TestNodeUpdateAttrs(unittest.TestCase):
    """Test Node.update_attrs."""

    def test_update_attrs_basic(self):
        n = Node("test", attrs={"a": 1})
        n2 = n.update_attrs(b=2)
        self.assertEqual(n2.attrs, {"a": 1, "b": 2})
        self.assertEqual(n.attrs, {"a": 1})  # original unchanged

    def test_update_attrs_overwrite(self):
        n = Node("test", attrs={"a": 1, "b": 2})
        n2 = n.update_attrs(b=99)
        self.assertEqual(n2.get("b"), 99)
        self.assertEqual(n.get("b"), 2)  # original unchanged

    def test_update_attrs_is_alias_of_with_attrs(self):
        n = Node("test", attrs={"x": 10})
        r1 = n.update_attrs(y=20)
        r2 = n.with_attrs(y=20)
        self.assertEqual(r1, r2)


class TestNodeOperators(unittest.TestCase):
    """Test Node pipe operators."""

    def test_pipe_operator(self):
        root = _make_tree()
        result = root | (lambda n: n.name)
        self.assertEqual(result, "root")

    def test_rshift_operator(self):
        root = _make_tree()
        result = root >> (lambda n: n.size)
        self.assertEqual(result, root.size)

    def test_pipe_chaining(self):
        root = _make_tree()
        double = lambda n: n.map(lambda x: x.with_attrs(value=x.get("value", 0) * 2))
        result = root | double
        self.assertIsInstance(result, Node)


class TestNodeFilterWithSelector(unittest.TestCase):
    """Confirm Node.filter accepts Selector objects (cursor id-membership)."""

    def test_filter_with_selector(self):
        from AlgoTree.selectors import NameSelector
        root = _make_tree()
        tree = Tree(root)
        sel = NameSelector("a*")
        # Node.filter should route Selectors via cursor id-membership
        # just like Tree.filter
        node_filtered = root.filter(sel)
        tree_filtered = tree.filter(sel)
        self.assertIsNotNone(node_filtered)
        self.assertEqual(node_filtered.to_dict(), tree_filtered.root.to_dict())

    def test_filter_depth_selector(self):
        from AlgoTree.selectors import DepthSelector
        root = _make_tree()
        tree = Tree(root)
        sel = DepthSelector(1)
        node_filtered = root.filter(sel)
        tree_filtered = tree.filter(sel)
        self.assertIsNotNone(node_filtered)
        self.assertEqual(node_filtered.to_dict(), tree_filtered.root.to_dict())


if __name__ == "__main__":
    unittest.main()
