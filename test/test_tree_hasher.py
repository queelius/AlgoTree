import unittest
from AlgoTree.tree_hasher import TreeHasher
from AlgoTree.tree_converter import TreeConverter  # Assuming this converts trees to dictionaries
from AlgoTree.treenode import TreeNode

class Node:
    """Simple node class for testing purposes."""
    def __init__(self, name, payload=None):
        self.name = name
        self.payload = payload
        self.children = []

    def add_child(self, child):
        self.children.append(child)

class TestTreeHasher(unittest.TestCase):

    def setUp(self):
        # Create some example trees for testing
        self.tree1 = Node('Root')
        child1_1 = Node('A', payload=10)
        child1_2 = Node('B', payload=20)
        self.tree1.add_child(child1_1)
        self.tree1.add_child(child1_2)

        self.tree2 = Node('Root')
        child2_1 = Node('A', payload=10)
        child2_2 = Node('B', payload=20)
        self.tree2.add_child(child2_1)
        self.tree2.add_child(child2_2)

        self.tree3 = Node('Root')
        child3_1 = Node('A', payload=10)
        child3_2 = Node('C', payload=30)  # Different payload and name
        self.tree3.add_child(child3_1)
        self.tree3.add_child(child3_2)

        self.tree4 = TreeNode(name='Root', payload=None)
        TreeNode(name='A', payload=10, parent=self.tree4)
        TreeNode(name='B', payload=20, parent=self.tree4)


        self.non_iso_tree = TreeNode(name='Root', payload=None)
        nodeAnoniso = TreeNode(name='A', payload=10, parent=self.non_iso_tree)
        TreeNode(name='B', payload=20, parent=nodeAnoniso)


        self.tree_hasher = TreeHasher()

    def test_tree_hash_equal_trees(self):
        """Test that two identical trees have the same hash."""
        from AlgoTree.pretty_tree import pretty_tree

        self.assertEqual(self.tree_hasher(self.tree1), self.tree_hasher(self.tree2))
        self.assertEqual(self.tree_hasher(self.tree1), self.tree_hasher(self.tree4))

    def test_tree_hash_different_trees(self):
        """Test that two different trees have different hashes."""
        self.assertNotEqual(self.tree_hasher(self.tree1), self.tree_hasher(self.tree3))

    def test_tree_hash_isomorphic_trees(self):
        """Test that isomorphic trees are handled correctly (depending on the implementation)."""
        # For now, assuming the default `tree` method considers both structure and data
        self.assertNotEqual(self.tree_hasher(self.tree1), self.tree_hasher(self.tree3))

    def test_isomorphic_tree_hash(self):
        """Test that isomorphic trees hash the same if we ignore node names and payloads."""
        isomorphic_hasher = TreeHasher(TreeHasher.isomorphic)
        
        # Create isomorphic trees (structure is the same, names and payloads differ)
        tree4 = Node('X')
        child4_1 = Node('Y')
        child4_2 = Node('Z')
        tree4.add_child(child4_1)
        tree4.add_child(child4_2)

        self.assertEqual(isomorphic_hasher(self.tree1), isomorphic_hasher(tree4))

    def test_non_isomorphic_tree_hash(self):
        """Test that non-isomorphic trees hash differently if we ignore node names and payloads."""
        isomorphic_hasher = TreeHasher(TreeHasher.isomorphic)

        self.assertNotEqual(isomorphic_hasher(self.tree1), isomorphic_hasher(self.non_iso_tree))

    def test_tree_hash_with_empty_tree(self):
        """Test hashing of an empty tree (if applicable)."""
        empty_tree = Node(None)
        self.assertIsInstance(self.tree_hasher(empty_tree), int)

    def test_tree_hash_with_single_node(self):
        """Test hashing of a tree with a single node."""
        single_node_tree = Node('Single', payload=42)
        self.assertIsInstance(self.tree_hasher(single_node_tree), int)

if __name__ == '__main__':
    unittest.main()
