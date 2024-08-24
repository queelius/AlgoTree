import logging
import time
import unittest

from AlgoTree.treenode import TreeNode
from AlgoTree.utils import visit

logging.basicConfig(level=logging.DEBUG)


class TestTreeNodeAdvanced(unittest.TestCase):
    def setUp(self):
        """
        Create a tree with the following structure:

        root
        ├── child1
        │   └── child1_1
        └── child2
            └── child2_1
        """
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

    def test_move_subtree(self):
        new_parent = self.child2
        subtree_root = self.child1
        subtree_root.parent = new_parent
        # Verify new structure
        self.assertEqual(subtree_root.parent, new_parent)
        self.assertIn(subtree_root, self.child2.children)

    def test_large_tree_performance(self):
        # Create a large tree
        large_root = TreeNode(name="large_root")
        current_level = [large_root]
        for _ in range(5):  # Adjust depth as needed
            next_level = []
            for node in current_level:
                for i in range(10):  # Adjust branching factor as needed
                    next_level.append(TreeNode(name=f"node_{i}", parent=node))
            current_level = next_level

        # Measure traversal time
        start_time = time.time()
        visit(large_root, lambda n: False, order="pre")
        traversal_time = time.time() - start_time

        # Assert traversal time is within acceptable limits (e.g., 1 second)
        self.assertLess(traversal_time, 1)

    def test_edge_cases(self):
        empty_tree = TreeNode()
        single_node_tree = TreeNode(name="single")

        # Empty tree checks
        self.assertEqual(len(empty_tree.children), 0)
        self.assertIsNone(empty_tree.parent)

        # Single node tree checks
        self.assertEqual(len(single_node_tree.children), 0)
        self.assertIsNone(single_node_tree.parent)
        self.assertEqual(single_node_tree.name, "single")


if __name__ == "__main__":
    unittest.main()
