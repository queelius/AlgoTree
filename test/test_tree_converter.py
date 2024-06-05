import unittest

from anytree import Node

from treekit.flattree_node import FlatTreeNode
from treekit.tree_converter import TreeConverter
from treekit.treenode import TreeNode


class TestTreeConverter(unittest.TestCase):
    def setUp(self):
        # Setup a sample tree for testing
        self.root = TreeNode(name="root", value="root_value")
        self.child1 = TreeNode(
            name="child1", parent=self.root, value="child1_value"
        )
        self.child2 = TreeNode(
            name="child2", parent=self.root, value="child2_value"
        )
        self.child1_1 = TreeNode(
            name="child1_1", parent=self.child1, value="child1_1_value"
        )
        self.child2_1 = TreeNode(
            name="child2_1", parent=self.child2, value="child2_1_value"
        )

    def test_copy_under(self):
        # Test copying a subtree under another node
        new_root = TreeNode(name="new_root", value="new_root_value")
        TreeConverter.copy_under(self.root, new_root)

        # Verify the structure
        self.assertEqual(len(new_root.children), 1)
        copied_root = new_root.children[0]
        self.assertEqual(copied_root.name, "root")
        self.assertEqual(copied_root["value"], "root_value")
        self.assertEqual(len(copied_root.children), 2)
        self.assertEqual(copied_root.children[0].name, "child1")
        self.assertEqual(copied_root.children[1].name, "child2")

    def test_convert_to_treenode(self):
        # Test converting TreeNode to TreeNode (identity transformation)
        new_tree = TreeConverter.convert(self.root, TreeNode)

        # logging.debug(json.dumps(new_tree, indent=2))
        self.assertIsInstance(new_tree, TreeNode)
        self.assertEqual(new_tree.name, "root")
        self.assertEqual(new_tree["value"], "root_value")

        # Verify the structure
        self.assertEqual(len(new_tree.children), 2)
        self.assertEqual(new_tree.children[0].name, "child1")
        self.assertEqual(new_tree.children[1].name, "child2")

    def test_convert_to_anytree(self):
        # Test converting TreeNode to anytree Node
        new_tree = TreeConverter.convert(self.root, Node)
        self.assertIsInstance(new_tree, Node)
        self.assertEqual(new_tree.name, "root")
        self.assertEqual(new_tree.value, "root_value")

        # Verify the structure
        self.assertEqual(len(new_tree.children), 2)
        self.assertEqual(new_tree.children[0].name, "child1")
        self.assertEqual(new_tree.children[1].name, "child2")

    def test_convert_to_flattreenode(self):
        # Test converting TreeNode to FlatTreeNode
        new_tree = TreeConverter.convert(self.root, FlatTreeNode)
        self.assertIsInstance(new_tree, FlatTreeNode)
        self.assertEqual(new_tree.name, "root")
        self.assertEqual(new_tree["value"], "root_value")

        # Verify the structure
        self.assertEqual(len(new_tree.children), 2)
        self.assertEqual(new_tree.children[0].name, "child1")
        self.assertEqual(new_tree.children[1].name, "child2")


if __name__ == "__main__":
    unittest.main()
