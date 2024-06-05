import os
import unittest

from anytree import Node

from treekit.tree_viz import TreeViz


class TestTreeViz(unittest.TestCase):
    def setUp(self):
        # Create a sample tree for testing
        self.root = Node("root")
        self.child1 = Node("child1", parent=self.root)
        self.child2 = Node("child2", parent=self.root)
        self.child1_1 = Node("child1_1", parent=self.child1)
        self.child2_1 = Node("child2_1", parent=self.child2)

    def test_text_representation(self):
        # Test that text representation runs without error and returns a string
        result = TreeViz.text(self.root)
        self.assertIsInstance(result, str)
        # Basic verification of the output structure
        self.assertIn("root", result)
        self.assertIn("child1", result)
        self.assertIn("child2", result)

    def test_image_representation(self):
        # Test that image representation runs without error and creates a file
        filename = "test_tree.png"
        TreeViz.image(self.root, filename)
        self.assertTrue(os.path.exists(filename))
        # Clean up
        os.remove(filename)


if __name__ == "__main__":
    unittest.main()
