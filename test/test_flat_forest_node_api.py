import unittest

from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode


class TestFlatTreeNodeAPI(unittest.TestCase):
    def setUp(self):
        self.root = FlatForestNode(name="root", data=0)
        self.tree = self.root.forest

    def test_create_and_add_nodes(self):
        # Create nodes
        node1 = FlatForestNode(name="node1", parent=self.root, data=1)
        node2 = FlatForestNode(name="node2", parent=self.root, data=2)
        node3 = self.root.add_child(name="node3", data=3)

        # Verify creation
        self.assertIn("node1", self.tree)
        self.assertIn("node2", self.tree)
        self.assertIn("node3", self.tree)
        self.assertEqual(self.tree["node1"]["data"], 1)
        self.assertEqual(self.tree["node2"]["data"], 2)
        self.assertEqual(self.tree["node3"]["data"], 3)
        self.assertEqual(self.tree["node3"]["parent"], "root")

    def test_retrieve_and_manipulate_children(self):
        # Create nodes
        node1 = self.root.add_child(name="node1", data=1)
        node3 = self.root.add_child(name="node3", data=3)
        node4 = node3.add_child(name="node4", data=4)
        node5 = node3.add_child(name="node5", data=5)
        node6 = node3.add_child(name="node6", data=6)

        # Retrieve node3 and verify children
        retrieved_node3 = self.tree.node("node3")
        children_names = [child.name for child in retrieved_node3.children]
        self.assertCountEqual(children_names, ["node4", "node5", "node6"])

        # Update children
        node7 = FlatForestNode(name="node7", data=7, parent=node3)
        node3.children = [node4, node5, node7]
        updated_children_names = [child.name for child in node3.children]
        self.assertCountEqual(
            updated_children_names, ["node4", "node5", "node7"]
        )

    def test_detach_and_purge(self):
        # Create nodes
        node1 = self.root.add_child(name="node1", data=1)
        node3 = self.root.add_child(name="node3", data=3)
        node4 = node3.add_child(name="node4", data=4)
        node5 = node3.add_child(name="node5", data=5)

        # Detach node3
        detached_node3 = node3.detach()
        self.assertEqual(self.tree["node3"]["parent"], FlatForest.DETACHED_KEY)
        detached_children_names = [
            child.name for child in detached_node3.children
        ]
        self.assertCountEqual(detached_children_names, ["node4", "node5"])

        # Prune detached node3
        self.tree.purge()
        self.assertNotIn("node3", self.tree)
        self.assertNotIn("node4", self.tree)
        self.assertNotIn("node5", self.tree)

    def test_payload_manipulation(self):
        # Create node
        node1 = self.root.add_child(name="node1", data=1)

        # Manipulate payload
        node1.payload = {"new_key": "new_value"}
        self.assertEqual(node1.payload, {"new_key": "new_value"})

        node1["another_key"] = "another_value"
        self.assertEqual(node1["another_key"], "another_value")

        del node1["new_key"]
        self.assertNotIn("new_key", node1.payload)

    def test_clear_children(self):
        # Create nodes
        node3 = self.root.add_child(name="node3", data=3)
        node4 = node3.add_child(name="node4", data=4)
        node5 = node3.add_child(name="node5", data=5)

        # Clear children of node3
        node3.children = []
        self.assertEqual(node3.children, [])


if __name__ == "__main__":
    unittest.main()
