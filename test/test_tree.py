import unittest
from AlgoTree.node import Node
from AlgoTree.tree import Tree


class TestTreeCreation(unittest.TestCase):
    """Test Tree creation and factory methods."""

    def test_tree_from_node(self):
        """Test creating tree from Node."""
        node = Node("root")
        tree = Tree(node)
        self.assertEqual(tree.root.name, "root")

    def test_tree_from_string(self):
        """Test creating tree from string."""
        tree = Tree("root")
        self.assertEqual(tree.root.name, "root")
        self.assertEqual(len(tree.root.children), 0)

    def test_from_dict(self):
        """Test creating tree from dictionary."""
        data = {
            'name': 'root',
            'value': 1,
            'children': [
                {'name': 'child1', 'value': 2},
                {'name': 'child2', 'value': 3, 'children': [
                    {'name': 'grandchild', 'value': 4}
                ]}
            ]
        }
        tree = Tree.from_dict(data)

        self.assertEqual(tree.root.name, 'root')
        self.assertEqual(tree.root.get('value'), 1)
        self.assertEqual(len(tree.root.children), 2)
        self.assertEqual(tree.root.children[1].children[0].name, 'grandchild')

    def test_from_paths(self):
        """Test creating tree from paths."""
        paths = [
            'root/a/b',
            'root/a/c',
            'root/d'
        ]
        tree = Tree.from_paths(paths)

        self.assertEqual(tree.root.name, 'root')
        self.assertEqual(len(tree.root.children), 2)


class TestTreeFunctionalOps(unittest.TestCase):
    """Test Tree functional operations."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("child1", attrs={"value": 10}),
            Node("child2", attrs={"value": 20}),
            Node("child3", attrs={"value": 30})
        ))

    def test_map(self):
        """Test map operation."""
        # Map with dict return
        result = self.tree.map(lambda n: {"doubled": n.get("value", 0) * 2})
        self.assertEqual(result.root.children[0].get("doubled"), 20)

        # Map with None (no change)
        result = self.tree.map(lambda n: None)
        self.assertEqual(result.root.children[0].get("value"), 10)

    def test_filter(self):
        """Test filter operation."""
        result = self.tree.filter(lambda n: n.get("value", 0) > 15)
        # Root is kept (has matching descendants)
        self.assertEqual(result.root.name, "root")
        # Only child2 and child3 match
        self.assertEqual(len(result.root.children), 2)

    def test_reduce(self):
        """Test reduce operation."""
        total = self.tree.reduce(
            lambda acc, n: acc + n.get("value", 0),
            0
        )
        self.assertEqual(total, 60)  # 10 + 20 + 30

    def test_fold(self):
        """Test fold operation."""
        # Sum values bottom-up
        result = self.tree.fold(
            lambda node, child_results:
                node.get("value", 0) + sum(child_results)
        )
        self.assertEqual(result, 60)


class TestTreeStructureOps(unittest.TestCase):
    """Test Tree structure operations."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("keep1", attrs={"active": True}),
            Node("remove", attrs={"active": False}),
            Node("keep2", attrs={"active": True})
        ))

    def test_prune(self):
        """Test pruning nodes."""
        result = self.tree.prune(lambda n: not n.get("active", False))
        # Remove node should be gone
        self.assertEqual(len(result.root.children), 2)
        self.assertEqual(result.root.children[0].name, "keep1")

    def test_graft(self):
        """Test grafting subtree."""
        subtree = Node("grafted")
        result = self.tree.graft(lambda n: n.name == "keep1", subtree)

        # keep1 should have grafted child
        self.assertEqual(len(result.root.children[0].children), 1)
        self.assertEqual(result.root.children[0].children[0].name, "grafted")

    def test_flatten(self):
        """Test flattening tree."""
        deep_tree = Tree(Node("root",
            Node("a",
                Node("b",
                    Node("c")
                )
            )
        ))

        result = deep_tree.flatten(max_depth=1)
        # After flattening, should have fewer levels
        self.assertTrue(result.height <= 2)


class TestTreeQuery(unittest.TestCase):
    """Test Tree query operations."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("child1", attrs={"type": "a"}),
            Node("child2", attrs={"type": "b"}),
            Node("child3", attrs={"type": "a"})
        ))

    def test_find(self):
        """Test finding first match."""
        node = self.tree.find("child2")
        self.assertEqual(node.name, "child2")

        node = self.tree.find(lambda n: n.get("type") == "b")
        self.assertEqual(node.name, "child2")

    def test_find_all(self):
        """Test finding all matches."""
        nodes = self.tree.find_all(lambda n: n.get("type") == "a")
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0].name, "child1")
        self.assertEqual(nodes[1].name, "child3")

    def test_exists(self):
        """Test checking existence."""
        self.assertTrue(self.tree.exists("child1"))
        self.assertFalse(self.tree.exists("nonexistent"))

    def test_count(self):
        """Test counting nodes."""
        # Count all
        self.assertEqual(self.tree.count(), 4)  # root + 3 children

        # Count matching
        self.assertEqual(self.tree.count(lambda n: n.get("type") == "a"), 2)

    def test_select(self):
        """Test selecting nodes (iterator)."""
        nodes = list(self.tree.select(lambda n: n.get("type") == "a"))
        self.assertEqual(len(nodes), 2)


class TestTreePaths(unittest.TestCase):
    """Test Tree path operations."""

    def test_get_path(self):
        """Test getting node at path."""
        tree = Tree(Node("root",
            Node("a",
                Node("b")
            )
        ))

        node = tree.get_path("root/a/b")
        self.assertEqual(node.name, "b")

        # Non-existent path
        node = tree.get_path("root/x/y")
        self.assertIsNone(node)

    def test_paths(self):
        """Test getting all paths."""
        tree = Tree(Node("root",
            Node("a"),
            Node("b",
                Node("c")
            )
        ))

        # Leaves only
        paths = tree.paths(to_leaves_only=True)
        self.assertEqual(len(paths), 2)
        self.assertIn("root/a", paths)
        self.assertIn("root/b/c", paths)

        # All nodes
        paths = tree.paths(to_leaves_only=False)
        self.assertEqual(len(paths), 4)  # root, a, b, c

    def test_to_dict(self):
        """Test converting to dictionary."""
        tree = Tree(Node("root",
            Node("child", attrs={"value": 1})
        ))

        d = tree.to_dict()
        self.assertEqual(d['name'], 'root')
        self.assertEqual(d['children'][0]['name'], 'child')
        self.assertEqual(d['children'][0]['value'], 1)


class TestTreeProperties(unittest.TestCase):
    """Test Tree properties."""

    def test_size(self):
        """Test tree size."""
        tree = Tree(Node("root",
            Node("a"),
            Node("b")
        ))
        self.assertEqual(tree.size, 3)

    def test_height(self):
        """Test tree height."""
        tree = Tree(Node("root",
            Node("a",
                Node("b",
                    Node("c")
                )
            )
        ))
        self.assertEqual(tree.height, 3)

    def test_leaves(self):
        """Test getting leaves."""
        tree = Tree(Node("root",
            Node("a"),
            Node("b",
                Node("c")
            )
        ))
        leaves = tree.leaves
        self.assertEqual(len(leaves), 2)
        names = {leaf.name for leaf in leaves}
        self.assertEqual(names, {"a", "c"})

    def test_is_empty(self):
        """Test empty tree check."""
        tree = Tree(Node("<empty>"))
        self.assertTrue(tree.is_empty)

        tree = Tree(Node("root"))
        self.assertFalse(tree.is_empty)


class TestTreeIteration(unittest.TestCase):
    """Test Tree iteration."""

    def test_walk_orders(self):
        """Test different traversal orders."""
        tree = Tree(Node("root",
            Node("a"),
            Node("b")
        ))

        # Preorder
        nodes = list(tree.walk("preorder"))
        names = [n.name for n in nodes]
        self.assertEqual(names, ["root", "a", "b"])

        # Postorder
        nodes = list(tree.walk("postorder"))
        names = [n.name for n in nodes]
        self.assertEqual(names, ["a", "b", "root"])

        # Levelorder
        nodes = list(tree.walk("levelorder"))
        names = [n.name for n in nodes]
        self.assertEqual(names, ["root", "a", "b"])

    def test_nodes(self):
        """Test getting all nodes as list."""
        tree = Tree(Node("root",
            Node("a"),
            Node("b")
        ))
        nodes = tree.nodes()
        self.assertEqual(len(nodes), 3)


class TestTreeOperators(unittest.TestCase):
    """Test Tree operator overloading."""

    def test_pipe_operator(self):
        """Test | operator for transformation."""
        tree = Tree(Node("root", attrs={"value": 1}))

        def double_values(t):
            return t.map(lambda n: {"value": n.get("value", 0) * 2})

        result = tree | double_values
        self.assertEqual(result.root.get("value"), 2)

    def test_rshift_operator(self):
        """Test >> operator for transformation."""
        tree = Tree(Node("root",
            Node("a"),
            Node("b")
        ))

        # Can change type
        result = tree >> (lambda t: t.size)
        self.assertEqual(result, 3)


class TestTreeRepresentations(unittest.TestCase):
    """Test Tree string representations."""

    def test_repr(self):
        """Test repr output."""
        tree = Tree(Node("root",
            Node("a"),
            Node("b")
        ))
        repr_str = repr(tree)
        self.assertIn("Tree", repr_str)
        self.assertIn("root", repr_str)
        self.assertIn("size=3", repr_str)

    def test_str(self):
        """Test str output (ASCII tree)."""
        tree = Tree(Node("root",
            Node("a"),
            Node("b")
        ))
        str_output = str(tree)
        self.assertIn("root", str_output)
        self.assertIn("a", str_output)
        self.assertIn("b", str_output)


if __name__ == "__main__":
    unittest.main()
