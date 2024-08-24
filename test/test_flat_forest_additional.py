import json
import unittest
import uuid

from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode


class TestFlatTreeNodeAdditional(unittest.TestCase):
    def setUp(self):
        self.root = FlatForestNode(name="root", data=0)
        self.tree = self.root.forest

    def test_node_creation_with_uuid(self):
        # Create node without specifying a name
        unnamed_node = FlatForestNode(parent=self.root, data="data without name")
        # Verify that a UUID is assigned
        self.assertTrue(uuid.UUID(unnamed_node.name))

    def test_cycle_detection(self):
        node1 = self.root.add_child(name="node1", data=1)
        node2 = self.root.add_child(name="node2", data=2)
        node3 = node1.add_child(name="node3", data=3)

        # Attempt to create a cycle: making node1 a child of node3
        with self.assertRaises(ValueError):
            node1.parent = node3
            FlatForest.check_valid(node1.tree)

    def test_serialization_and_deserialization(self):
        node1 = self.root.add_child(name="node1", data="data1")
        self.root.add_child(name="node2", data="data2")
        node1.add_child(name="node3", data="data3")

        # Serialize to JSON
        tree_json = json.dumps(self.tree, indent=2)
        # Deserialize back to FlatTree
        deserialized_tree_data = json.loads(tree_json)
        deserialized_tree = FlatForest(deserialized_tree_data)

        # Verify structure is the same
        self.assertEqual(self.tree, deserialized_tree)

    def test_handling_non_serializable_data(self):
        # Create a tree with non-serializable data (function)
        non_serializable_data = {"node1": {"data": lambda x: x}}
        non_serializable_tree = FlatForest(non_serializable_data)

        # Verify serialization fails
        with self.assertRaises(TypeError):
            json.dumps(non_serializable_tree)

    def test_tree_visualization(self):
        node1 = self.root.add_child(name="node1", data=1)
        node2 = self.root.add_child(name="node2", data=2)
        node3 = node1.add_child(name="node3", data=3)

        def pretty_print(node, depth=0):
            result = ""
            if depth != 0:
                result += "    " * depth + "|\n"
                result += "    " * depth + "+ " + "-" * depth + " "
            result += node.name + "\n"
            for child in node.children:
                result += pretty_print(child, depth + 1)
            return result

        expected_output = """root
    |
    + - node1
        |
        + -- node3
    |
    + - node2
"""
        actual_output = pretty_print(self.root)
        self.assertEqual(expected_output, actual_output)


if __name__ == "__main__":
    unittest.main()
