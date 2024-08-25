import unittest
from AlgoTree.treenode import TreeNode
from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode
from AlgoTree.node_hasher import NodeHasher

class TestNodeHash(unittest.TestCase):
    def setUp(self):
        """
        Create a sample tree for testing

        Here is what the tree looks like::
            
                a
                |
                +-- b
                |   |
                |   +-- d
                |   |   |
                |   |   +-- f
                |   |
                |   +-- e
                |
                +-- c
        """
        self.node_a = FlatForestNode(name="a", data1=1, data2=2)
        self.node_b = FlatForestNode(name="b", parent=self.node_a, data="test")
        self.node_c = FlatForestNode(name="c", parent=self.node_a, different_data="test2")
        self.node_d = FlatForestNode(name="d", parent=self.node_b, data="test")
        self.node_e = FlatForestNode(name="e", parent=self.node_b, different_data="test2")
        self.node_f = FlatForestNode(name="f", parent=self.node_d, data="test")

        self.tree_node_a = TreeNode(name="a", data1=1, data2=2)
        self.tree_node_b = TreeNode(name="b", parent=self.tree_node_a, data="test")
        self.tree_node_c = TreeNode(name="c", parent=self.tree_node_a, different_data="test2")
        self.tree_node_d = TreeNode(name="d", parent=self.tree_node_b, data="test")
        self.tree_node_e = TreeNode(name="e", parent=self.tree_node_b, different_data="test2")
        self.tree_node_f = TreeNode(name="f", parent=self.tree_node_d, data="test")

    def test_name_hash(self):
        # Test that the name hash of two nodes with different names is not the same
        self.assertNotEqual(NodeHasher.name(self.tree_node_a), NodeHasher.name(self.tree_node_b))

        # Test that the name hash of two nodes with the same name is the same
        root = TreeNode(name="root")
        another_a = TreeNode(name="a", parent=root)
        self.assertEqual(NodeHasher.name(self.tree_node_a), NodeHasher.name(another_a))

        # Test that the name hash of two nodes with different names is not the same
        self.assertNotEqual(NodeHasher.name(self.node_a), NodeHasher.name(self.node_b))

        # Test that the name hash of two nodes with the same name is the same
        root = FlatForestNode(name="root")
        another_a = FlatForestNode(name="a", parent=root)
        self.assertEqual(NodeHasher.name(self.node_a), NodeHasher.name(another_a))

        # try different tree types with same name
        self.assertEqual(NodeHasher.name(self.tree_node_a), NodeHasher.name(self.node_a))

        self.assertEqual(NodeHasher.name(self.node_a), NodeHasher.name(TreeNode(name="a")))
        self.assertNotEqual(NodeHasher.name(self.node_a), NodeHasher.name(TreeNode(name="b", data1=1, data2=2)))

    def test_payload_hash(self):
        # Test that the payload hash of two nodes with different payloads is not the same
        self.assertNotEqual(NodeHasher.payload(self.tree_node_a), NodeHasher.payload(self.tree_node_b))

        # Test that the payload hash of two nodes with the same payload is the same
        self.assertNotEqual(NodeHasher.payload(self.tree_node_a), NodeHasher.payload(TreeNode(name="a")))

        self.assertEqual(NodeHasher.payload(self.tree_node_a), NodeHasher.payload(TreeNode(name="a", data1=1, data2=2)))
        self.assertNotEqual(NodeHasher.payload(self.tree_node_a), NodeHasher.payload(TreeNode(name="a", data1=1, data2=2, more=None)))
        
        # try different tree types with same payloads
        self.assertEqual(NodeHasher.payload(self.tree_node_a), NodeHasher.payload(self.node_a))

    def test_node_hash(self):
        # Test that the node hash of two nodes with different payloads is not the same
        self.assertNotEqual(NodeHasher.node(self.tree_node_a), NodeHasher.node(self.tree_node_b))

        # Test that the node hash of two nodes with the same payload and same names are the same
        self.assertEqual(NodeHasher.node(self.tree_node_a), NodeHasher.node(TreeNode(name="a", data1=1, data2=2)))

        self.assertEqual(NodeHasher.node(self.tree_node_a), NodeHasher.node(self.node_a))

        self.assertNotEqual(NodeHasher.node(self.tree_node_a), NodeHasher.node(TreeNode(name="a", data1=1, data2=2, more=None)))

    def test_path_hash(self):
        # Test that the path hash of two nodes with different paths is not the same
        self.assertNotEqual(NodeHasher.path(self.tree_node_a), NodeHasher.path(self.tree_node_b))
        self.assertEqual(NodeHasher.path(self.tree_node_b), NodeHasher.path(TreeNode(name="b", parent=TreeNode(name="a",data=0), data1=10, data2=2)))
        self.assertEqual(NodeHasher.path(self.tree_node_a), NodeHasher.path(self.node_a))

if __name__ == "__main__":
    unittest.main()