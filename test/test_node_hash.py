import unittest
from AlgoTree.treenode import TreeNode
from AlgoTree.flattree import FlatTree
from AlgoTree.flattree_node import FlatTreeNode
from AlgoTree.node_hash import NodeHash

class TestNodeHash(unittest.TestCase):
    def setUp(self):
        self.node_a = FlatTreeNode(name="a", data1=1, data2=2)
        self.node_b = FlatTreeNode(name="b", parent=self.node_a, data="test")
        self.node_c = FlatTreeNode(name="c", parent=self.node_a, different_data="test2")

        self.tree_node_a = TreeNode(name="a", data1=1, data2=2)
        self.tree_node_b = TreeNode(name="b", parent=self.tree_node_a, data="test")
        self.tree_node_c = TreeNode(name="c", parent=self.tree_node_a, different_data="test2")

    def test_name_hash(self):
        # Test that the name hash of two nodes with different names is not the same
        self.assertNotEqual(NodeHash.name_hash(self.tree_node_a), NodeHash.name_hash(self.tree_node_b))

        # Test that the name hash of two nodes with the same name is the same
        root = TreeNode(name="root")
        another_a = TreeNode(name="a", parent=root)
        self.assertEqual(NodeHash.name_hash(self.tree_node_a), NodeHash.name_hash(another_a))

        # Test that the name hash of two nodes with different names is not the same
        self.assertNotEqual(NodeHash.name_hash(self.node_a), NodeHash.name_hash(self.node_b))

        # Test that the name hash of two nodes with the same name is the same
        root = FlatTreeNode(name="root")
        another_a = FlatTreeNode(name="a", parent=root)
        self.assertEqual(NodeHash.name_hash(self.node_a), NodeHash.name_hash(another_a))

        # try different tree types with same name
        self.assertEqual(NodeHash.name_hash(self.tree_node_a), NodeHash.name_hash(self.node_a))

        self.assertEqual(NodeHash.name_hash(self.node_a), NodeHash.name_hash(TreeNode(name="a")))
        self.assertNotEqual(NodeHash.name_hash(self.node_a), NodeHash.name_hash(TreeNode(name="b", data1=1, data2=2)))

    def test_payload_hash(self):
        # Test that the payload hash of two nodes with different payloads is not the same
        self.assertNotEqual(NodeHash.payload_hash(self.tree_node_a), NodeHash.payload_hash(self.tree_node_b))

        # Test that the payload hash of two nodes with the same payload is the same
        self.assertNotEqual(NodeHash.payload_hash(self.tree_node_a), NodeHash.payload_hash(TreeNode(name="a")))

        self.assertEqual(NodeHash.payload_hash(self.tree_node_a), NodeHash.payload_hash(TreeNode(name="a", data1=1, data2=2)))
        self.assertNotEqual(NodeHash.payload_hash(self.tree_node_a), NodeHash.payload_hash(TreeNode(name="a", data1=1, data2=2, more=None)))
        
        # try different tree types with same payloads
        self.assertEqual(NodeHash.payload_hash(self.tree_node_a), NodeHash.payload_hash(self.node_a))

    def test_node_hash(self):
        # Test that the node hash of two nodes with different payloads is not the same
        self.assertNotEqual(NodeHash.node_hash(self.tree_node_a), NodeHash.node_hash(self.tree_node_b))

        # Test that the node hash of two nodes with the same payload and same names are the same
        self.assertEqual(NodeHash.node_hash(self.tree_node_a), NodeHash.node_hash(TreeNode(name="a", data1=1, data2=2)))

        self.assertEqual(NodeHash.node_hash(self.tree_node_a), NodeHash.node_hash(self.node_a))

        self.assertNotEqual(NodeHash.node_hash(self.tree_node_a), NodeHash.node_hash(TreeNode(name="a", data1=1, data2=2, more=None)))

    def test_path_hash(self):
        # Test that the path hash of two nodes with different paths is not the same
        self.assertNotEqual(NodeHash.path_hash(self.tree_node_a), NodeHash.path_hash(self.tree_node_b))

        # Test that the path hash of two nodes with the same path is the same
        self.assertEqual(NodeHash.path_hash(self.tree_node_b), NodeHash.path_hash(TreeNode(name="b", parent=TreeNode(name="a",data=0), data1=10, data2=2)))

        #self.assertEqual(NodeHash.path_hash(self.tree_node_a), NodeHash.path_hash(self.node_a))

if __name__ == "__main__":
    unittest.main()