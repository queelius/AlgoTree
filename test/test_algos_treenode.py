import unittest
from AlgoTree.utils import node_to_leaf_paths, prune
from AlgoTree.treenode import TreeNode
from AlgoTree.flat_forest_node import FlatForestNode

class TestUtils(unittest.TestCase):

    def setUp(self):
        """
        Create a sample tree for testing
        
        Here is what the tree looks like:
        
            A
            ├── B
            │   ├── E
            │   └── F
            |       └── H
            ├── C
            │   └── G
            └── D            
        """

        # Create a sample tree for testing
        self.node_a = TreeNode(name="A")
        self.node_b = TreeNode(name="B", parent=self.node_a)
        self.node_c = TreeNode(name="C", parent=self.node_a)
        self.node_d = TreeNode(name="D", parent=self.node_a)
        self.node_e = TreeNode(name="E", parent=self.node_b)
        self.node_f = TreeNode(name="F", parent=self.node_b)
        self.node_g = TreeNode(name="G", parent=self.node_c)
        self.node_h = TreeNode(name="H", parent=self.node_f)

    def test_node_to_leaf_paths(self):
        """
        Test the root_to_leaf_paths function

        See the setUp method for the tree structure.

        Expected paths:
        [
            [A, B, E],
            [A, B, F, H]
            [A, C, G],
            [A, D]
        ]
        """
        expected_paths = [
            [self.node_a, self.node_b, self.node_e],
            [self.node_a, self.node_b, self.node_f, self.node_h],
            [self.node_a, self.node_c, self.node_g],
            [self.node_a, self.node_d]
        ]
        result = node_to_leaf_paths(self.node_a)
        self.assertEqual(result, expected_paths)


    def test_prune(self):
        def pred(node):
            # let's just prune sub-trees rooted at B and D
            return node.name in ["B", "D"]

        pruned_tree = prune(self.node_a, pred)
        self.assertEqual(pruned_tree.name, "A")
        self.assertEqual(len(pruned_tree.children), 1)
        self.assertEqual(pruned_tree.children[0].name, "C")
        self.assertEqual(len(pruned_tree.children[0].children), 1)
        self.assertEqual(pruned_tree.children[0].children[0].name, "G")

if __name__ == "__main__":
    unittest.main()
