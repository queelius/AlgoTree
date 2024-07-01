import unittest
from AlgoTree.pretty_tree import PrettyTree, pretty_tree

class TestTreePrettyPrinter(unittest.TestCase):
    
    class Node:
        def __init__(self, name, children=None, payload=None):
            self.name = name
            self.payload = payload
            self.children = children or []
            for child in self.children:
                child.parent = self
            self.parent = None

        @property
        def root(self):
            node = self
            while node.parent:
                node = node.parent
            return node
    
    def setUp(self):
        # Creating a sample tree structure for testing
        self.root = self.Node('root', [
            self.Node('child1', [
                self.Node('child1.1'),
                self.Node('child1.2')
            ]),
            self.Node('child2', [
                self.Node('child2.1')
            ])
        ])
    
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
        out = printer(self.root, mark=['child1', 'child2.1'], markers=['(?)'])
        expected_output = (
            "root\n"
            "├───── child1 (?)\n"
            "│      ├───── child1.1\n"
            "│      └───── child1.2\n"
            "└───── child2\n"
            "       └───── child2.1 (?)\n"
        )
        self.assertEqual(out, expected_output, msg="Marked nodes are not displayed correctly")

if __name__ == "__main__":
    unittest.main()
