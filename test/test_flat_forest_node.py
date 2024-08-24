import unittest

from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode


class TestFlatTreeNode(unittest.TestCase):
    def setUp(self):
        self.tree_data = {
            "a": {"parent": None},
            "b": {"parent": "a"},
            "c": {"parent": "a"},
            "d": {"parent": "b"},
            "e": {"parent": "b"},
            "f": {"parent": "c"},
        }
        self.flat_tree = FlatForest(self.tree_data)
        self.node_a = FlatForestNode.proxy(self.flat_tree, "a")
        self.node_b = FlatForestNode.proxy(self.flat_tree, "b")
        self.node_c = FlatForestNode.proxy(self.flat_tree, "c")
        self.root = FlatForestNode.proxy(self.flat_tree, "a")

    def test_initialization(self):
        self.assertEqual(self.node_a.name, "a")
        self.assertEqual(self.node_b.name, "b")

    def test_parent(self):
        children = self.node_a.children
        for child in children:
            self.assertEqual(child.parent, self.node_a)

    def test_children(self):
        children_a = [child.name for child in self.node_a.children]
        self.assertCountEqual(children_a, ["b", "c"])

        children_b = [child.name for child in self.node_b.children]
        self.assertCountEqual(children_b, ["d", "e"])

    def test_payload(self):
        self.assertEqual(self.node_a.payload, {})
        self.node_a.payload = {"key1": "value1"}
        self.assertEqual(self.node_a.payload, {"key1": "value1"})

    def test_add_child(self):
        new_node = self.node_a.add_child(name="g")
        self.assertIn("g", self.flat_tree)
        self.assertEqual(self.flat_tree["g"]["parent"], "a")
        self.assertEqual(new_node.parent.name, "a")

    def test_detach(self):
        detached_node = self.node_b.detach()
        self.assertEqual(detached_node._key, "b")
        self.assertEqual(self.flat_tree["b"]["parent"], FlatForest.DETACHED_KEY)

    def test_set_parent(self):
        self.flat_tree.node("b").parent = self.node_c
        self.assertEqual(self.flat_tree["b"]["parent"], "c")

    def test_len_and_iter(self):
        self.assertEqual(len(self.node_a), 0)
        self.node_a.payload = {"data": "value"}
        self.assertEqual(self.node_a.payload, {"data": "value"})

    def test_getitem_setitem_delitem(self):
        self.node_a["key1"] = "value1"
        self.assertEqual(self.node_a["key1"], "value1")
        del self.node_a["key1"]
        with self.assertRaises(KeyError):
            _ = self.node_a["key1"]


if __name__ == "__main__":
    unittest.main()
