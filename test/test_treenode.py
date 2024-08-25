import unittest

from AlgoTree.treenode import TreeNode

class TestTreeNode(unittest.TestCase):
    def test_constructor_with_name_and_value(self):
        node = TreeNode(name="root", value=10)
        self.assertEqual(node.name, "root")
        self.assertEqual(node.payload["value"], 10)
        self.assertEqual(node.children, [])

    def test_add_child(self):
        root = TreeNode(name="root", value=10)
        child = root.add_child(name="child1", value=1)
        self.assertEqual(len(root.children), 1)
        self.assertEqual(root.children[0].name, "child1")
        self.assertEqual(root.children[0].payload["value"], 1)
        self.assertEqual(child.name, "child1")
        self.assertEqual(child.payload["value"], 1)

    def test_set_get_children(self):
        root = TreeNode(name="root", value=10)
        child1 = TreeNode(name="child1", value=1)
        child2 = TreeNode(name="child2", value=2)
        root.children = [child1, child2]
        self.assertEqual(len(root.children), 2)
        self.assertEqual(root.children[0].name, "child1")
        self.assertEqual(root.children[1].name, "child2")

    def test_set_get_payload(self):
        root = TreeNode(name="root", value=10, extra="extra_data")
        self.assertEqual(root.payload, {"value": 10, "extra": "extra_data"})
        root.payload = {"value": 20, "new_data": "new_value"}
        self.assertEqual(root.payload["value"], 20)
        self.assertEqual(root.payload["new_data"], "new_value")
        self.assertNotIn("extra", root)

    def test_node_method(self):
        root = TreeNode(name="root", value=10)
        with self.assertRaises(KeyError):
            root.node("non_existent")

if __name__ == "__main__":
    unittest.main()
