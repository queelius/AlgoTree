"""
Tests for the refined immutable Node class.
"""

import unittest
from AlgoTree.node import Node, node


class TestNodeCreation(unittest.TestCase):
    """Test Node creation and basic properties."""

    def test_simple_node(self):
        """Test creating a simple node."""
        n = Node("root")
        self.assertEqual(n.name, "root")
        self.assertEqual(n.attrs, {})
        self.assertEqual(len(n.children), 0)
        self.assertIsNone(n.parent)

    def test_node_with_attrs(self):
        """Test creating node with attributes."""
        n = Node("root", attrs={"type": "file", "size": 100})
        self.assertEqual(n["type"], "file")
        self.assertEqual(n.get("size"), 100)
        self.assertIsNone(n.get("missing"))
        self.assertEqual(n.get("missing", "default"), "default")

    def test_node_with_children(self):
        """Test creating node with children."""
        child1 = Node("child1")
        child2 = Node("child2")
        parent = Node("parent", child1, child2)

        self.assertEqual(len(parent.children), 2)
        self.assertEqual(parent.children[0].name, "child1")
        self.assertEqual(parent.children[1].name, "child2")

        # Check parent references
        self.assertEqual(parent.children[0].parent, parent)
        self.assertEqual(parent.children[1].parent, parent)

    def test_node_convenience_function(self):
        """Test the node() convenience function."""
        tree = node('root',
            node('child1', value=1),
            'child2',
            node('child3',
                'grandchild1',
                'grandchild2'
            )
        )

        self.assertEqual(tree.name, 'root')
        self.assertEqual(len(tree.children), 3)
        self.assertEqual(tree.children[0]['value'], 1)
        self.assertEqual(tree.children[1].name, 'child2')
        self.assertEqual(len(tree.children[2].children), 2)


class TestNodeImmutability(unittest.TestCase):
    """Test that Node operations are immutable."""

    def test_with_name(self):
        """Test with_name returns new node."""
        n1 = Node("original")
        n2 = n1.with_name("modified")

        self.assertEqual(n1.name, "original")
        self.assertEqual(n2.name, "modified")
        self.assertIsNot(n1, n2)

    def test_with_attrs(self):
        """Test with_attrs returns new node."""
        n1 = Node("node", attrs={"a": 1})
        n2 = n1.with_attrs(b=2)

        self.assertEqual(n1.attrs, {"a": 1})
        self.assertEqual(n2.attrs, {"a": 1, "b": 2})
        self.assertIsNot(n1, n2)

    def test_without_attrs(self):
        """Test without_attrs returns new node."""
        n1 = Node("node", attrs={"a": 1, "b": 2})
        n2 = n1.without_attrs("b")

        self.assertEqual(n1.attrs, {"a": 1, "b": 2})
        self.assertEqual(n2.attrs, {"a": 1})
        self.assertIsNot(n1, n2)

    def test_with_child(self):
        """Test with_child returns new node."""
        n1 = Node("parent")
        child = Node("child")
        n2 = n1.with_child(child)

        self.assertEqual(len(n1.children), 0)
        self.assertEqual(len(n2.children), 1)
        self.assertIsNot(n1, n2)

    def test_with_children(self):
        """Test with_children replaces children."""
        child1 = Node("child1")
        child2 = Node("child2")
        child3 = Node("child3")

        n1 = Node("parent", child1)
        n2 = n1.with_children(child2, child3)

        self.assertEqual(len(n1.children), 1)
        self.assertEqual(len(n2.children), 2)
        self.assertEqual(n2.children[0].name, "child2")

    def test_without_child(self):
        """Test without_child returns new node."""
        child1 = Node("child1")
        child2 = Node("child2")
        n1 = Node("parent", child1, child2)
        n2 = n1.without_child("child1")

        self.assertEqual(len(n1.children), 2)
        self.assertEqual(len(n2.children), 1)
        self.assertEqual(n2.children[0].name, "child2")


class TestNodeTransformations(unittest.TestCase):
    """Test tree-wide transformations."""

    def test_map(self):
        """Test mapping over tree nodes."""
        tree = Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2})
        )

        # Double all values
        mapped = tree.map(lambda n: n.with_attrs(value=n.get("value", 0) * 2))

        self.assertEqual(mapped.children[0]["value"], 2)
        self.assertEqual(mapped.children[1]["value"], 4)

    def test_filter(self):
        """Test filtering tree nodes."""
        tree = Node("root",
            Node("keep"),
            Node("remove"),
            Node("keep2")
        )

        filtered = tree.filter(lambda n: "keep" in n.name)

        self.assertIsNotNone(filtered)
        self.assertEqual(len(filtered.children), 2)

    def test_find(self):
        """Test finding node in tree."""
        tree = Node("root",
            Node("child1"),
            Node("child2",
                Node("grandchild")
            )
        )

        found = tree.find("grandchild")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "grandchild")

        not_found = tree.find("missing")
        self.assertIsNone(not_found)

    def test_find_all(self):
        """Test finding all matching nodes."""
        tree = Node("root",
            Node("leaf"),
            Node("branch",
                Node("leaf"),
                Node("other")
            )
        )

        leaves = tree.find_all("leaf")
        self.assertEqual(len(leaves), 2)
        self.assertTrue(all(n.name == "leaf" for n in leaves))


class TestNodeIteration(unittest.TestCase):
    """Test node iteration methods."""

    def test_walk_preorder(self):
        """Test preorder traversal."""
        tree = Node("root",
            Node("a"),
            Node("b",
                Node("c")
            )
        )

        names = [n.name for n in tree.walk("preorder")]
        self.assertEqual(names, ["root", "a", "b", "c"])

    def test_walk_postorder(self):
        """Test postorder traversal."""
        tree = Node("root",
            Node("a"),
            Node("b",
                Node("c")
            )
        )

        names = [n.name for n in tree.walk("postorder")]
        self.assertEqual(names, ["a", "c", "b", "root"])

    def test_descendants(self):
        """Test descendants iteration."""
        tree = Node("root",
            Node("a"),
            Node("b",
                Node("c")
            )
        )

        desc_names = [n.name for n in tree.descendants()]
        self.assertEqual(desc_names, ["a", "b", "c"])

    def test_leaves(self):
        """Test leaves iteration."""
        tree = Node("root",
            Node("leaf1"),
            Node("branch",
                Node("leaf2"),
                Node("leaf3")
            )
        )

        leaf_names = [n.name for n in tree.leaves()]
        self.assertEqual(set(leaf_names), {"leaf1", "leaf2", "leaf3"})


class TestNodeProperties(unittest.TestCase):
    """Test node query properties."""

    def test_is_root(self):
        """Test is_root property."""
        parent = Node("parent")
        child = Node("child")
        parent = parent.with_child(child)

        self.assertTrue(parent.is_root)
        self.assertFalse(parent.children[0].is_root)

    def test_is_leaf(self):
        """Test is_leaf property."""
        parent = Node("parent")
        child = Node("child")
        parent = parent.with_child(child)

        self.assertFalse(parent.is_leaf)
        self.assertTrue(parent.children[0].is_leaf)

    def test_depth(self):
        """Test depth property."""
        tree = Node("root",
            Node("child",
                Node("grandchild")
            )
        )

        self.assertEqual(tree.depth, 0)
        self.assertEqual(tree.children[0].depth, 1)
        self.assertEqual(tree.children[0].children[0].depth, 2)

    def test_height(self):
        """Test height property."""
        tree = Node("root",
            Node("child1"),
            Node("child2",
                Node("grandchild")
            )
        )

        self.assertEqual(tree.height, 2)
        self.assertEqual(tree.children[0].height, 0)
        self.assertEqual(tree.children[1].height, 1)

    def test_size(self):
        """Test size property."""
        tree = Node("root",
            Node("child1"),
            Node("child2",
                Node("grandchild")
            )
        )

        self.assertEqual(tree.size, 4)


class TestNodeConversion(unittest.TestCase):
    """Test node conversion methods."""

    def test_to_dict(self):
        """Test to_dict conversion."""
        child = Node("child", attrs={"value": 1})
        tree = Node("root", child, attrs={"type": "file"})

        d = tree.to_dict()

        self.assertEqual(d["name"], "root")
        self.assertEqual(d["type"], "file")
        self.assertEqual(len(d["children"]), 1)
        self.assertEqual(d["children"][0]["name"], "child")
        self.assertEqual(d["children"][0]["value"], 1)


class TestNodeEquality(unittest.TestCase):
    """Test node equality and hashing."""

    def test_equality(self):
        """Test node equality."""
        n1 = Node("root", attrs={"a": 1})
        n2 = Node("root", attrs={"a": 1})
        n3 = Node("root", attrs={"a": 2})

        self.assertEqual(n1, n2)
        self.assertNotEqual(n1, n3)

    def test_hash(self):
        """Test node hashing."""
        n1 = Node("root", attrs={"a": 1})
        n2 = Node("root", attrs={"a": 1})

        # Same nodes should have same hash
        self.assertEqual(hash(n1), hash(n2))

        # Can be used in sets
        s = {n1, n2}
        self.assertEqual(len(s), 1)


if __name__ == "__main__":
    unittest.main()
