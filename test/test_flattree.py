import unittest
from treekit.flattree_newer import FlatTree

class TestFlatTree(unittest.TestCase):

    def test_create_tree(self):
        node = FlatTree.ProxyNode.create(name="root", value=1)
        self.assertIsInstance(node, FlatTree.ProxyNode)
        self.assertEqual(node.payload["name"], "root")
        self.assertEqual(node.payload["value"], 1)

    def test_create_tree_with_children(self):
        root = FlatTree.ProxyNode.create(name="root")
        child = FlatTree.ProxyNode.create(name="child")
        root.add_child(child)
        self.assertEqual(child.parent, root)

    def test_initialize_existing_tree(self):
        tree = FlatTree({"root": {"name": "root"}})
        node = FlatTree.ProxyNode("root", tree)
        self.assertEqual(node.payload["name"], "root")

    def test_add_child(self):
        root = FlatTree.ProxyNode.create(name="root")
        child = root.add_child(name="child")
        self.assertEqual(child.payload["name"], "child")
        self.assertEqual(child.parent, root)

    def test_clone_node(self):
        root = FlatTree.ProxyNode.create(name="root")
        child = root.add_child(name="child")
        clone = FlatTree.ProxyNode.clone(root, clone_children=True)
        self.assertEqual(clone.payload["name"], "root")
        self.assertEqual(clone.children[0].payload["name"], "child")

    def test_detach_node(self):
        root = FlatTree.ProxyNode.create(name="root")
        child = root.add_child(name="child")
        child.detach()
        self.assertEqual(child.parent_key, FlatTree.DETACHED_KEY)

    def test_prune_node(self):
        root = FlatTree.ProxyNode.create(name="root")
        child = root.add_child(name="child")
        grandchild = child.add_child(name="grandchild")
        root._tree.prune(child)
        self.assertNotIn("child", root._tree)
        self.assertNotIn("grandchild", root._tree)

    def test_check_valid(self):
        tree = FlatTree({
            "root": {"name": "root"},
            "child": {"name": "child", "parent": "root"}
        })
        tree.check_valid()  # Should not raise

        # Create a cycle
        tree["root"]["parent"] = "child"
        with self.assertRaises(ValueError):
            tree.check_valid()

    def test_get_node(self):
        tree = FlatTree({"root": {"name": "root"}})
        node = tree.get_node("root")
        self.assertEqual(node.payload["name"], "root")


if __name__ == "__main__":
    unittest.main()
