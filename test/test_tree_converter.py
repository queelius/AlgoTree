import unittest

from anytree import Node

from AlgoTree.flattree_node import FlatTreeNode
from AlgoTree.tree_converter import TreeConverter
from AlgoTree.treenode import TreeNode


class TestTreeConverter(unittest.TestCase):
    def setUp(self):
        """
        Create a sample tree for testing

        Here is what the tree looks like::

            root
            ├── child1
            │   └── child1_1
            │       └── child2_1 (child1_1_1 value)
            │   
            └── child2
                ├── child2_1
                └── child2_2

        Notice that child2_1 is not unique in the tree. It appears under both
        child1_1 and child2. This is fine for `TreeNode`, but for `FlatTreeNode`
        it will be an issue -- it will have to either rename one of the nodes
        (child_2_1_0, for example) or raise an error, depending on whether
        renaming is set to true or false.
        """
        self.root = TreeNode(name="root", value="root_value")
        self.child1 = TreeNode(
            name="child1", parent=self.root, value="child1_value"
        )
        self.child1_1 = TreeNode(
            name="child1_1", parent=self.child1, value="child1_1_value"
        )
        self.child1_1_1 = TreeNode(
            name="child2_1", parent=self.child1_1, value="child1_1_1_value"
        )

        self.child2 = TreeNode(
            name="child2", parent=self.root, value="child2_value"
        )
        self.child2_1 = TreeNode(
            name="child2_1", parent=self.child2, value="child2_1_value"
        )
        self.child2_2 = TreeNode(
            name="child2_2", parent=self.child2, value="child2_2_value"
        )

    def verify_tree_structure(self, root):
        self.assertEqual(root["name"], "root")
        self.assertEqual(root["payload"], { "value" : "root_value"})
        self.assertEqual(len(root["children"]), 2)
        child1 = root["children"][0]
        child2 = root["children"][1]
        self.assertEqual(child1["name"], "child1")
        self.assertEqual(child1["payload"], { "value" : "child1_value"})
        self.assertEqual(child2["name"], "child2")
        self.assertEqual(child2["payload"], { "value" : "child2_value"})

        self.assertEqual(len(child1["children"]), 1)
        child1_1 = child1["children"][0]
        self.assertEqual(child1_1["name"], "child1_1")
        self.assertEqual(child1_1["payload"], { "value" : "child1_1_value"})

        self.assertEqual(len(child1_1["children"]), 1)
        child1_1_1 = child1_1["children"][0]
        self.assertEqual(child1_1_1["name"], "child2_1")
        self.assertEqual(child1_1_1["payload"], { "value" : "child1_1_1_value"})
        self.assertEqual(len(child1_1_1["children"]), 0)

        self.assertEqual(len(child2["children"]), 2)
        child2_1 = child2["children"][0]
        child2_2 = child2["children"][1]
        self.assertEqual(child2_1["name"], "child2_1")
        self.assertEqual(child2_1["payload"], { "value" : "child2_1_value"})
        self.assertEqual(len(child2_1["children"]), 0)

        self.assertEqual(child2_2["name"], "child2_2")
        self.assertEqual(child2_2["payload"], { "value" : "child2_2_value"})
        self.assertEqual(len(child2_2["children"]), 0)

    def test_to_dict(self):
        """
            root
            ├── child1
            │   └── child1_1
            │       └── child2_1 (child1_1_1 value)
            └── child2
                ├── child2_1
                └── child2_2
        """
        
        # Test converting TreeNode to dict
        tree_dict = TreeConverter.to_dict(self.root)
        # logging.debug(json.dumps(tree_dict, indent=2))
        self.verify_tree_structure(tree_dict)

    def test_copy_under(self):
        # Test copying a subtree under another node
        new_root = TreeNode(name="new_root", value="new_root_value")
        TreeConverter.copy_under(self.root, new_root)
        print(new_root)
        # Verify the structure
        self.assertEqual(len(new_root.children), 1)
        #root = new_root.children[0]
        #tree_dict = TreeConverter.to_dict(root)
        #self.verify_tree_structure(tree_dict)

    def test_convert_to_treenode(self):
        # Test converting TreeNode to TreeNode (identity transformation)
        new_tree = TreeConverter.convert(self.root, TreeNode)

        # logging.debug(json.dumps(new_tree, indent=2))
        self.assertIsInstance(new_tree, TreeNode)
        tree_dict = TreeConverter.to_dict(new_tree)
        self.verify_tree_structure(tree_dict)

    def test_convert_to_anytree(self):
        # Test converting TreeNode to anytree Node
        new_tree = TreeConverter.convert(self.root, Node)
        self.assertIsInstance(new_tree, Node)
        tree_dict = TreeConverter.to_dict(new_tree)
        self.verify_tree_structure(tree_dict)
        
    def test_convert_to_flattreenode(self):
        # Test converting TreeNode to FlatTreeNode
        new_tree = TreeConverter.convert(self.root, FlatTreeNode)
        self.assertIsInstance(new_tree, FlatTreeNode)
        tree_dict = TreeConverter.to_dict(new_tree)
        self.verify_tree_structure(tree_dict)


    def test_convert_to_flattreenode_to_anynode_to_treenode(self):
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
