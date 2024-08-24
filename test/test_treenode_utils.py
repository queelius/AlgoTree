import unittest

from AlgoTree.treenode import TreeNode
from AlgoTree.utils import (
    ancestors,
    breadth_first,
    depth,
    descendants,
    find_node,
    find_nodes,
    height,
    is_internal,
    is_leaf,
    is_root,
    leaves,
    map,
    siblings,
    visit,
)

class TestTreeNodeUtils(unittest.TestCase):
    def setUp(self):
        """
        Create a sample tree for testing

        Here is what the tree looks like::

            node0
            ├── node1
            ├── node2
            └── node3
                ├── node4
                ├── node5
                ├── node6
                │   └── node9
                ├── node7
                └── node8
        """
        self.node0 = TreeNode(name="node0", value=0)
        self.node1 = TreeNode(name="node1", parent=self.node0, value=1)
        self.node2 = TreeNode(name="node2", parent=self.node0, value=2)
        self.node3 = TreeNode(name="node3", parent=self.node0, value=3)
        self.node4 = TreeNode(name="node4", parent=self.node3, value=4)
        self.node5 = TreeNode(name="node5", parent=self.node3, value=5)
        self.node6 = TreeNode(name="node6", parent=self.node3, value=6)
        self.node7 = TreeNode(name="node7", parent=self.node3, value=7)
        self.node8 = TreeNode(name="node8", parent=self.node3, value=8)
        self.node9 = TreeNode(name="node9", parent=self.node6, value=9)

    def test_visit_pre_order(self):
        from AlgoTree.pretty_tree import pretty_tree
        from AlgoTree.treenode import TreeNode
        import json
        print("\npre-order\n")
        print(pretty_tree(self.node0))
        print("\n\n")
        print(json.dumps(self.node0.to_dict(), indent=4))
        result = []
        visit(self.node0, lambda n: result.append(n.name) or False, order="pre")
        self.assertEqual(
            result,
            [
                "node0",
                "node1",
                "node2",
                "node3",
                "node4",
                "node5",
                "node6",
                "node9",
                "node7",
                "node8",
            ],
        )

    def test_visit_level_order(self):
        result = []
        visit(
            self.node0,
            lambda n, **kwargs: result.append((n.name, kwargs["level"]))
            or False,
            order="level",
        )
        self.assertEqual(
            result,
            [
                ("node0", 0),
                ("node1", 1),
                ("node2", 1),
                ("node3", 1),
                ("node4", 2),
                ("node5", 2),
                ("node6", 2),
                ("node7", 2),
                ("node8", 2),
                ("node9", 3),
            ],
        )

    def test_visit_stop_on_match(self):
        result = []
        visit(
            self.node0,
            lambda n: result.append(n) or n.name == "node6",
            order="pre",
        )
        self.assertEqual(
            result, [self.node0, self.node1, self.node2, self.node3, self.node4, self.node5, self.node6]
        )

    def test_map(self):
        def increment_value(node):
            node.payload["value"] += 1
            return node

        map(self.node0, increment_value)
        self.assertEqual(self.node0.payload["value"], 1)
        self.assertEqual(self.node1.payload["value"], 2)
        self.assertEqual(self.node9.payload["value"], 10)

    def test_descendants_node3(self):
        self.assertCountEqual(
            descendants(self.node3),
            [self.node4, self.node5, self.node6, self.node9, self.node7, self.node8]
        )

    def test_ancestors_node9(self):
        self.assertCountEqual(ancestors(self.node9), [self.node6, self.node3, self.node0])

    def test_siblings_node6(self):
        from AlgoTree.pretty_tree import pretty_tree
        print(pretty_tree(self.node0.node("node6")))
        print(pretty_tree(self.node0.node("node6").root))
        print(siblings(self.node0.node("node6")))

        self.assertCountEqual(siblings(self.node0.node("node6")),
                              [self.node4, self.node5, self.node7, self.node8])

    def test_leaves(self):
        self.assertCountEqual(
            leaves(self.node0),
            [self.node1, self.node2, self.node4, self.node5, self.node7, self.node8, self.node9]
        )

    def test_height(self):
        """
        node0
            ├── node1
            ├── node2
            └── node3
                ├── node4
                ├── node5
                ├── node6
                │   └── node9
                ├── node7
                └── node8
        """
        self.assertEqual(height(self.node0), 3)
        self.assertEqual(height(self.node3), 2)
        self.assertEqual(height(self.node9), 0)
        self.assertEqual(height(self.node3.root), 3)


    def test_root(self):
        self.assertEqual(self.node0.root, self.node0)
        self.assertEqual(self.node3.root, self.node0)
        self.assertEqual(self.node9.root, self.node0)

    def test_depth(self):
        self.assertEqual(depth(self.node0), 0)
        self.assertEqual(depth(self.node3), 1)
        self.assertEqual(depth(self.node9), 3)

    def test_is_root(self):
        self.assertTrue(is_root(self.node0))
        self.assertFalse(is_root(self.node1))

    def test_is_leaf(self):
        self.assertTrue(is_leaf(self.node9))
        self.assertFalse(is_leaf(self.node3))

    def test_is_internal(self):
        self.assertTrue(is_internal(self.node3))
        self.assertFalse(is_internal(self.node1))

    def test_breadth_first(self):
        result = []
        breadth_first(
            self.node0,
            lambda n, **kwargs: result.append((n.name, kwargs["level"]))
            or False,
        )
        self.assertEqual(
            result,
            [
                ("node0", 0),
                ("node1", 1),
                ("node2", 1),
                ("node3", 1),
                ("node4", 2),
                ("node5", 2),
                ("node6", 2),
                ("node7", 2),
                ("node8", 2),
                ("node9", 3),
            ],
        )

    def test_find_nodes(self):
        nodes = find_nodes(self.node0, lambda n, **_: n.payload["value"] > 3)
        self.assertCountEqual(
            [n.name for n in nodes],
            ["node4", "node5", "node6", "node7", "node8", "node9"],
        )

    def test_find_node(self):
        node = find_node(self.node0, lambda n, **_: n.payload["value"] == 7)
        self.assertEqual(node.name, "node7")

    def test_get_node(self):
        node = self.node0.node("node7")
        self.assertEqual(node.name, "node7")


if __name__ == "__main__":
    unittest.main()
