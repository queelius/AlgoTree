import unittest

from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode


class TestFlatTree(unittest.TestCase):
    def setUp(self):
        """
        Create a sample tree for testing

        Here is what the tree looks like::

          node1
          └── node3
          |   ├── node4
          |   └── node5
          └── node2

        """
        self.tree_data = {
            "node1": {
                "data": "Some data for node1",
                "more": "Some more data for node1",
            },
            "node2": {"data": "Some data for node2", "parent": "node1"},
            "node3": {
                "parent": "node1",
                "data": "Some data for node3",
                "test": "Some test data for node3",
            },
            "node4": {"parent": "node3", "data": "Some data for node4"},
            "node5": {"parent": "node3", "data": "Some data for node5"},
        }
        self.flat_tree = FlatForest(self.tree_data)

    def test_parent(self):
        #self.assertEqual(self.flat_tree.root.parent, None)
        self.assertEqual(
            self.flat_tree.node("node3").parent,
            self.flat_tree.node("node1"),
        )
        #self.assertEqual(self.flat_tree.subtree("node3").parent, None)

    def test_initialization(self):
        self.assertEqual(
            self.flat_tree["node1"]["data"], "Some data for node1"
        )
        self.assertEqual(
            self.flat_tree["node2"]["data"], "Some data for node2"
        )
        self.assertEqual(self.flat_tree["node3"]["parent"], "node1")

    def test_node_names(self):
        unique_keys = self.flat_tree.node_names()
        expected_keys = [
            "__DETACHED__",
            "node1",
            "node2",
            "node3",
            "node4",
            "node5",
        ]
        self.assertCountEqual(unique_keys, expected_keys)

    def test_child_names(self):
        self.assertCountEqual(self.flat_tree.child_names("node1"), ["node2","node3"])
        self.assertEqual(
            self.flat_tree.child_names("node3"), ["node4", "node5"]
        )
        self.assertEqual(self.flat_tree.child_names("node2"), [])

    def test_detach(self):
        detached_node = self.flat_tree.detach("node3")
        self.assertEqual(
            self.flat_tree["node3"]["parent"], FlatForest.DETACHED_KEY
        )
        self.assertEqual(detached_node._key, "node3")

    def test_purge(self):
        self.flat_tree.detach("node3")
        self.flat_tree.purge()
        self.assertNotIn("node3", self.flat_tree)
        self.assertNotIn("node4", self.flat_tree)
        self.assertNotIn("node5", self.flat_tree)

    def test_check_valid(self):
        FlatForest.check_valid(self.flat_tree)
        self.flat_tree["node1"]["parent"] = "node5"
        with self.assertRaises(ValueError):
            FlatForest.check_valid(self.flat_tree)

    def test_node(self):
        node3 = self.flat_tree.node("node3")
        self.assertEqual(node3._key, "node3")

        with self.assertRaises(KeyError):
            self.flat_tree.node("non_existing")

    def test_root(self):
        root_node = self.flat_tree.root
        self.assertEqual(root_node._key, "node1")

    def test_detached(self):
        detached_node = self.flat_tree.detached
        self.assertEqual(detached_node._key, FlatForest.DETACHED_KEY)


class TestFlatTreeNode(unittest.TestCase):
    def setUp(self):
        """
        Create a sample tree for testing

        Here is what the tree looks like::

          node1
          ├── node3
          │   ├── node4
          │   └── node5
          └── node2

        """
        self.tree_data = {
            "node1": {
                "data": "Some data for node1",
                "more": "Some more data for node1",
            },
            "node2": {"data": "Some data for node2", "parent": "node1"},
            "node3": {
                "parent": "node1",
                "data": "Some data for node3",
                "test": "Some test data for node3",
            },
            "node4": {"parent": "node3", "data": "Some data for node4"},
            "node5": {"parent": "node3", "data": "Some data for node5"},
        }
        self.flat_tree = FlatForest(self.tree_data)
        self.node1 = FlatForestNode.proxy(self.flat_tree, "node1")
        self.node3 = FlatForestNode.proxy(self.flat_tree, "node3")

    def test_initialization(self):
        self.assertEqual(self.node1.name, "node1")
        self.assertEqual(self.node3.name, "node3")

    def test_children(self):
        children_node1 = [child.name for child in self.node1.children]
        self.assertCountEqual(children_node1, ["node2", "node3"])

        children_node3 = [child.name for child in self.node3.children]
        self.assertCountEqual(children_node3, ["node4", "node5"])

    def test_add_child(self):
        new_node = self.node1.add_child(name="node6", data="data for node6")
        self.assertIn("node6", self.flat_tree)
        self.assertEqual(self.flat_tree["node6"]["parent"], "node1")
        self.assertEqual(new_node.parent.name, "node1")

    def test_detach(self):
        detached_node = self.node3.detach()
        self.assertEqual(detached_node._key, "node3")
        self.assertEqual(
            self.flat_tree["node3"]["parent"], FlatForest.DETACHED_KEY
        )

    def test_getitem_setitem_delitem(self):
        self.node1["key1"] = "value1"
        self.assertEqual(self.node1["key1"], "value1")
        del self.node1["key1"]
        with self.assertRaises(KeyError):
            _ = self.node1["key1"]

    def test_clear(self):
        self.node1.payload = {"key1": "value1", "key2": "value2"}
        self.node1.clear()
        self.assertEqual(len(self.node1), 0)
        self.assertEqual(self.node1.payload, {})

    def test_child_operations(self):
        self.node1.add_child(name="child1", data="child1 data")
        child1 = self.node1.node("child1")
        self.assertEqual(child1.parent.name, "node1")
        self.assertEqual(child1.payload["data"], "child1 data")

    def test_create_cycle(self):
        self.node3.add_child(name="node6", data="node6 data")
        node6 = self.flat_tree.node("node6")
        with self.assertRaises(ValueError):
            self.node3.parent = node6
            FlatForest.check_valid(self.flat_tree)

if __name__ == "__main__":
    unittest.main()
