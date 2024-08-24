import unittest
from AlgoTree.pretty_tree import PrettyTree, pretty_tree
from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode

class TestTreePrettyPrinter(unittest.TestCase):
    
    def setUp(self):
        # Create a flat tree
        #
        # Here is what the tree looks like:
        #
        #     a
        #     ├── b
        #     │   ├── d
        #     │   |   ├── i
        #     │   |   └── j
        #     │   └── e
        #     ├── c
        #     |   └── f
        #     └── g
        #         └── h
        self.tree_data = {
            "a": {"parent": None},
            "b": {"parent": "a"},
            "c": {"parent": "a"},
            "d": {"parent": "b"},
            "e": {"parent": "b"},
            "f": {"parent": "c"},
            "g": {"parent": "a"},
            "h": {"parent": "g"},
            "i": {"parent": "d"},
            "j": {"parent": "d"},
        }
        self.flat_tree = FlatForest(self.tree_data)

    def test_default_pretty_print(self):
        printer = PrettyTree()
        out = printer(self.flat_tree.subtree("a"))
        expected_output = (
            "a\n"
            "├───── b\n"
            "│      ├───── d\n"
            "│      │      ├───── i\n"
            "│      │      └───── j\n"
            "│      └───── e\n"
            "├───── c\n"
            "│      └───── f\n"
            "└───── g\n"
            "       └───── h\n"
        )
        self.assertEqual(out, expected_output, msg="Tree not displayed correctly")
    
    def test_pretty_print_marks(self):
        printer = PrettyTree()
        out = printer(self.flat_tree.subtree("a"), mark=["d", "f"], markers=["(?)"])
        expected_output = (
            "a\n"
            "├───── b\n"
            "│      ├───── d (?)\n"
            "│      │      ├───── i\n"
            "│      │      └───── j\n"
            "│      └───── e\n"
            "├───── c\n"
            "│      └───── f (?)\n"
            "└───── g\n"
            "       └───── h\n"
        )
        self.assertEqual(out, expected_output, msg="Tree not displayed correctly")

    def test_pretty_print_subtree_marks(self):
        printer = PrettyTree()
        B = self.flat_tree.subtree("b")
        out = printer(B, mark=[B.root.name], markers=["(root)"])
        expected_output = (
            "b (root)\n"
            "├───── d\n"
            "│      ├───── i\n"
            "│      └───── j\n"
            "└───── e\n"
        )
        self.assertEqual(out, expected_output, msg="Tree not displayed correctly")

if __name__ == "__main__":
    unittest.main()