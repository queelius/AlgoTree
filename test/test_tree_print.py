import unittest
from AlgoTree.node import Node
from AlgoTree.pretty_tree import PrettyTree, pretty_tree


class TestTreePrettyPrinter(unittest.TestCase):

    def setUp(self):
        # Creating a sample tree structure for testing
        child1_1 = Node("child1.1")
        child1_2 = Node("child1.2")
        child1 = Node("child1", child1_1, child1_2)

        child2_1 = Node("child2.1")
        child2 = Node("child2", child2_1)

        self.root = Node("root", child1, child2)

    def test_default_pretty_print(self):
        printer = PrettyTree()
        out = printer(self.root)
        expected_output = (
            "root\n"
            "├───── child1\n"
            "│      ├───── child1.1\n"
            "│      └───── child1.2\n"
            "└───── child2\n"
            "       └───── child2.1\n"
        )
        self.assertEqual(out, expected_output, msg="Tree not displayed correctly")

    def test_mark_nodes(self):
        printer = PrettyTree()
        out = printer(self.root, mark=["child1", "child2.1"], markers=["(?)"])
        expected_output = (
            "root\n"
            "├───── child1 (?)\n"
            "│      ├───── child1.1\n"
            "│      └───── child1.2\n"
            "└───── child2\n"
            "       └───── child2.1 (?)\n"
        )
        self.assertEqual(
            out, expected_output, msg="Marked nodes are not displayed correctly"
        )


if __name__ == "__main__":
    unittest.main()
