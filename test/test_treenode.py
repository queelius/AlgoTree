import unittest

from AlgoTree.treenode import TreeNode


class TestTreeNode(unittest.TestCase):
    def test_constructor_with_name_and_value(self):
        node = TreeNode(name="root", value=10)
        self.assertEqual(node.name, "root")
        self.assertEqual(node["value"], 10)
        self.assertEqual(node.children, [])

    def test_constructor_with_children(self):
        children = [{"value": 1}, {"value": 2}]
        root = TreeNode(name="root", value=10, children=children)
        self.assertEqual(root.name, "root")
        self.assertEqual(root["value"], 10)
        self.assertEqual(len(root.children), 2)
        self.assertEqual(root.children[0]["value"], 1)
        self.assertEqual(root.children[1]["value"], 2)

    def test_add_child(self):
        root = TreeNode(name="root", value=10)
        child = root.add_child(name="child1", value=1)
        self.assertEqual(len(root.children), 1)
        self.assertEqual(root.children[0].name, "child1")
        self.assertEqual(root.children[0]["value"], 1)
        self.assertEqual(child.name, "child1")
        self.assertEqual(child["value"], 1)

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
        self.assertEqual(root["value"], 20)
        self.assertEqual(root["new_data"], "new_value")
        self.assertNotIn("extra", root)

    def test_node_method(self):
        children = [
            {TreeNode.NAME_KEY: "child1", "value": 1},
            {TreeNode.NAME_KEY: "child2", "value": 2},
        ]
        root = TreeNode(name="root", value=10, children=children)
        child1 = root.node("child1")
        self.assertEqual(child1.name, "child1")
        self.assertEqual(child1["value"], 1)
        with self.assertRaises(KeyError):
            root.node("non_existent")

    def test_setitem(self):
        root = TreeNode(name="root", value=10)
        root["new_key"] = "new_value"
        self.assertEqual(root["new_key"], "new_value")

    def test_repr(self):
        treenode = TreeNode({
            "__name__": "A",
            "value": 1,
            "children": [
                {"__name__": "B", "value": 2},
                {"__name__": "C", "value": 3, "children": [
                    {"__name__": "D", "value": 4},
                    {"__name__": "E", "value": 5}
                ]}
            ]})
        recreated_node = eval(repr(treenode))
        self.assertEqual(treenode, recreated_node)

if __name__ == "__main__":
    unittest.main()
