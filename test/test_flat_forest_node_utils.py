import unittest

from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode
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
    size
)


class TestTreeUtils(unittest.TestCase):
    def setUp(self):
        self.node0 = FlatForestNode(name="node0", data=0)
        self.node1 = FlatForestNode(name="node1", parent=self.node0, data=1)
        self.node2 = FlatForestNode(name="node2", parent=self.node0, data=2)
        self.node3 = FlatForestNode(name="node3", parent=self.node0, data=3)
        self.node4 = FlatForestNode(name="node4", parent=self.node3, data=4)
        self.node5 = FlatForestNode(name="node5", parent=self.node3, data=5)
        self.node6 = FlatForestNode(name="node6", parent=self.node3, data=6)
        self.node7 = FlatForestNode(name="node7", parent=self.node3, data=7)
        self.node8 = FlatForestNode(name="node8", parent=self.node3, data=8)
        self.node9 = FlatForestNode(name="node9", parent=self.node6, data=9)
        self.nodes = [
            self.node0, self.node1, self.node2, self.node3, self.node4,
            self.node5, self.node6, self.node7, self.node8, self.node9
        ]
        self.tree = self.node0.forest
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

    def test_visit_pre_order(self):
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
            lambda n: result.append(n.name) or n.name == "node6",
            order="pre",
        )
        self.assertEqual(
            result,
            ["node0", "node1", "node2", "node3", "node4", "node5", "node6"],
        )

    def test_map(self):
        def increment_data(node):
            node["data"] += 1
            return node

        map(self.node0, increment_data)
        self.assertEqual(self.node0["data"], 1)
        self.assertEqual(self.node1["data"], 2)
        self.assertEqual(self.node9["data"], 10)

    def test_descendants_node0(self):
        self.assertCountEqual(
            descendants(self.node0),
            [self.node1, self.node2, self.node3, self.node4, self.node5, self.node6, self.node7, self.node8, self.node9]
        )

    def test_descendants_root(self):
        true_descendants = [self.tree.node(n.name) for n in self.nodes[1:]]
        self.assertCountEqual(descendants(self.tree.root), true_descendants)

    def test_descendants_node3(self):
        self.assertCountEqual(
            descendants(self.node3),
            [self.node4, self.node5, self.node6, self.node9, self.node7, self.node8]
        )

    def test_ancestors(self):
        node9 = self.tree.node("node9")
        from AlgoTree.pretty_tree import pretty_tree
        print(pretty_tree(node9.parent))
        anc = [n.name for n in ancestors(node9)]
        self.assertCountEqual(anc, ["node6", "node3", "node0"])

    def test_subtree(self):
        subtree = self.tree.subtree("node3")
        self.assertEqual(subtree.name, "node3")
        self.assertEqual(subtree.root.name, "node3")
        self.assertEqual(subtree.parent, None)
        true_childs = [self.tree.subtree("node3").node("node4"),
                       self.tree.subtree("node3").node("node5"),
                       self.tree.subtree("node3").node("node6"),
                       self.tree.subtree("node3").node("node7"),
                       self.tree.subtree("node3").node("node8")]
        for n in true_childs:
            print(n)
        self.assertCountEqual(subtree.children, true_childs)

    def test_siblings(self):
        self.assertEqual(siblings(self.node6), [self.node4, self.node5, self.node7, self.node8])

    def test_leaves(self):
        self.assertEqual(
            leaves(self.node0),
            [self.node1, self.node2, self.node4, self.node5, self.node9, self.node7, self.node8]
        )

    def test_height(self):
        self.assertEqual(height(self.node0), 3)
        self.assertEqual(height(self.node3), 2)
        self.assertEqual(height(self.node9), 0)
        
    def test_height_subtree(self):
        self.assertEqual(height(self.node9.subtree()), 0)
        self.assertEqual(height(self.node9.subtree().node("node9")), 0)
        self.assertEqual(height(self.node3.subtree()), 2)
        self.assertEqual(height(self.node3.subtree().subtree("node3")), 2)
        self.assertEqual(height(self.node3.subtree().subtree().node("node3")), 2)
        self.assertEqual(height(self.node3.subtree().subtree().node("node9")), 0)
        self.assertEqual(height(self.node0.subtree()), 3)
        self.assertEqual(height(self.node0.subtree().node("node0")), 3)
        self.assertEqual(height(self.node0.subtree().node("node3")), 2)
        self.assertEqual(height(self.node0.subtree().subtree("node3").node("node9")), 0)

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
        self.assertCountEqual(
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
        nodes = find_nodes(self.node0, lambda n: n["data"] > 3)
        self.assertCountEqual(
            nodes, [self.node4, self.node5, self.node6, self.node7, self.node8, self.node9]
        )


    def test_size(self):
        self.assertEqual(size(self.node0), 10)
        self.assertEqual(size(self.tree.node("node0")), 10)
        self.assertEqual(size(self.tree.node("node0")), 10)
        self.assertEqual(size(self.node3), 7)
        self.assertEqual(size(self.node9.root), 10)
        self.assertEqual(size(self.node9), 1)
        self.assertEqual(size(self.node9.subtree().root), 1)
        self.assertEqual(size(self.node9.subtree()), 1)
        self.assertEqual(size(self.node9.forest.root), len(self.nodes))

    def test_find_node(self):
        node = find_node(self.node0, lambda n, **_: n["data"] == 7)
        self.assertEqual(node.name, "node7")


if __name__ == "__main__":
    unittest.main()
