import unittest
from AlgoTree.pretty_tree import PrettyTree, pretty_tree
from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode

class TestFlatTreeNodeEq(unittest.TestCase):
    
    def setUp(self):
        """
        Create a sample tree for testing, denoted by `t`.

        Here is what the tree `t` looks like:

            a (root)
            ├── b
            │   ├── d
            │   |   ├── i
            │   |   └── j
            │   └── e
            ├── c
            |   └── f
            └── g
                └── h

        When we get a node in `t` like `t.node("d")`, it looks like:

            a (root)
            ├── b
            │   ├── d (current node)
            │   |   ├── i
            │   |   └── j
            │   └── e
            ├── c
            |   └── f
            └── g
                └── h

        So we just repositioned the current node in the tree `t`.

        When we get a subtree `t.subtree("b")`, it looks like:

            b (root, current node)
            ├── d
            │   ├── i
            │   └── j
            └── e


        When we get a node in the subtree `t.subtree("b").node("d")`, it looks like:

            b (root)
            ├── d (current node)
            │   ├── i
            │   └── j
            └── e

        So we just repositioned the current node in the subtree `t.subtree("b")`.

        When we test for equality of a node, there are many ways to define it.
        By default, we define it by path equality, i.e., the path from the root
        to the current node.
        """
        self.tree_data = {
            "a": {"parent": None},
            "b": {"parent": "a"},
            "c": {"parent": "a"},
            "d": {"parent": "b"},
            "e": {"parent": "b"},
            "f": {"parent": "c"},
            "g": {"parent": "a"},
            "h": {"parent": "g"},
            "i": {"parent": "d"},
            "j": {"parent": "d"},
        }
        self.flat_tree = FlatForest(self.tree_data)
        self.root_b_node_d = self.flat_tree.subtree("b").node("d")


    def test_eq(self):
        root_logical_node_d = self.flat_tree.node("d")
        self.assertNotEqual(root_logical_node_d, self.root_b_node_d)
        self.assertNotEqual(self.flat_tree.node("b"), self.root_b_node_d)
        self.assertNotEqual(self.flat_tree.node("e"), self.root_b_node_d)
        self.assertNotEqual(self.flat_tree.node("b"), self.flat_tree.node("d"))
        self.assertNotEqual(self.flat_tree.node("b"), self.flat_tree.node("e"))
        self.assertNotEqual(self.flat_tree.node("d"), self.flat_tree.node("e"))
        self.assertEqual(self.flat_tree.subtree("b").node("d"), self.root_b_node_d)
        self.assertEqual(self.flat_tree.subtree("b").node("i"), self.flat_tree.subtree("b").node("i"))
