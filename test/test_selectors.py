import unittest
from AlgoTree.node import Node
from AlgoTree.tree import Tree
from AlgoTree.selectors import (
    Selector, NameSelector, AttrsSelector, TypeSelector, PredicateSelector,
    DepthSelector, LeafSelector, RootSelector,
    AndSelector, OrSelector, NotSelector, XorSelector,
    ChildOfSelector, ParentOfSelector, DescendantOfSelector,
    AncestorOfSelector, SiblingOfSelector,
    name, attrs, type_, predicate, depth, leaf, root, any_, none, parse
)


class TestBasicSelectors(unittest.TestCase):
    """Test basic selector types."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("file1.txt", attrs={"type": "file", "size": 100}),
            Node("dir1",
                Node("file2.py", attrs={"type": "file", "size": 200}),
                Node("file3.txt", attrs={"type": "file", "size": 150}),
                attrs={"type": "directory"}
            ),
            Node("file4.md", attrs={"type": "file", "size": 50})
        ))

    def test_name_selector_exact(self):
        """Test exact name matching."""
        selector = name("file1.txt")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "file1.txt")

    def test_name_selector_wildcard(self):
        """Test wildcard name matching."""
        selector = name("*.txt")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 2)
        names = {n.name for n in nodes}
        self.assertEqual(names, {"file1.txt", "file3.txt"})

    def test_name_selector_regex(self):
        """Test regex name matching."""
        selector = name(r"file\d+\.py")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "file2.py")

    def test_attrs_selector(self):
        """Test attribute matching."""
        selector = attrs(type="file")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 4)

        # With specific value
        selector = attrs(size=100)
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)

    def test_attrs_selector_predicate(self):
        """Test attribute with predicate function."""
        selector = attrs(size=lambda s: s and s > 100)
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 2)  # file2.py (200) and file3.txt (150)

    def test_type_selector(self):
        """Test type selector."""
        selector = type_("file")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 4)

        selector = type_("directory")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)

    def test_predicate_selector(self):
        """Test custom predicate selector."""
        selector = predicate(lambda n: n.name.endswith(".py"), name="py_files")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "file2.py")

    def test_depth_selector(self):
        """Test depth selector."""
        selector = depth(0)
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "root")

        selector = depth(2)
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 2)  # file2.py and file3.txt

    def test_depth_selector_range(self):
        """Test depth selector with range."""
        selector = depth(range(1, 3))
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 5)  # All nodes at depth 1 and 2

    def test_leaf_selector(self):
        """Test leaf selector."""
        selector = leaf()
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 4)  # All files are leaves

    def test_root_selector(self):
        """Test root selector."""
        selector = root()
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "root")


class TestLogicalCombinators(unittest.TestCase):
    """Test logical combinator selectors."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("file1.txt", attrs={"type": "file", "active": True}),
            Node("file2.txt", attrs={"type": "file", "active": False}),
            Node("dir1", attrs={"type": "directory", "active": True})
        ))

    def test_and_selector(self):
        """Test AND combinator."""
        selector = name("*.txt") & attrs(active=True)
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "file1.txt")

    def test_or_selector(self):
        """Test OR combinator."""
        selector = type_("directory") | attrs(active=True)
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 2)  # file1.txt and dir1

    def test_not_selector(self):
        """Test NOT combinator."""
        selector = ~leaf()
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "root")

    def test_xor_selector(self):
        """Test XOR combinator."""
        selector = type_("file") ^ attrs(active=True)
        nodes = list(selector.select(self.tree))
        # file2.txt (file but not active) and dir1 (active but not file)
        self.assertEqual(len(nodes), 2)

    def test_complex_logic(self):
        """Test complex logical combinations."""
        selector = (type_("file") & attrs(active=True)) | type_("directory")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 2)  # file1.txt and dir1


class TestStructuralCombinators(unittest.TestCase):
    """Test structural combinator selectors."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("parent1",
                Node("child1", attrs={"type": "child"}),
                Node("child2", attrs={"type": "child"}),
                attrs={"type": "parent"}
            ),
            Node("parent2",
                Node("child3", attrs={"type": "child"}),
                attrs={"type": "parent"}
            )
        ))

    def test_child_of_selector(self):
        """Test child_of combinator."""
        selector = type_("child").child_of(name("parent1"))
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 2)
        names = {n.name for n in nodes}
        self.assertEqual(names, {"child1", "child2"})

    def test_parent_of_selector(self):
        """Test parent_of combinator."""
        selector = type_("parent").parent_of(name("child1"))
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "parent1")

    def test_descendant_of_selector(self):
        """Test descendant_of combinator."""
        selector = type_("child").descendant_of(name("root"))
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 3)  # All children

    def test_ancestor_of_selector(self):
        """Test ancestor_of combinator."""
        selector = any_().ancestor_of(name("child1"))
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 2)  # root and parent1

    def test_sibling_of_selector(self):
        """Test sibling_of combinator."""
        selector = type_("child").sibling_of(name("child1"))
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "child2")


class TestSelectorMethods(unittest.TestCase):
    """Test selector helper methods."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2}),
            Node("c", attrs={"value": 3})
        ))

    def test_first(self):
        """Test getting first match."""
        selector = attrs(value=lambda v: v and v > 1)
        node = selector.first(self.tree)
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "b")

    def test_first_none(self):
        """Test first returns None when no match."""
        selector = name("nonexistent")
        node = selector.first(self.tree)
        self.assertIsNone(node)

    def test_count(self):
        """Test counting matches."""
        selector = attrs(value=lambda v: v and v > 1)
        count = selector.count(self.tree)
        self.assertEqual(count, 2)

    def test_exists(self):
        """Test checking existence."""
        selector = name("b")
        self.assertTrue(selector.exists(self.tree))

        selector = name("z")
        self.assertFalse(selector.exists(self.tree))

    def test_where(self):
        """Test where method for adding attributes."""
        selector = type_("file").where(size=100)
        # This is equivalent to type_("file") & attrs(size=100)
        self.assertIsInstance(selector, AndSelector)

    def test_at_depth(self):
        """Test at_depth convenience method."""
        selector = leaf().at_depth(1)
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 3)  # All children at depth 1


class TestSelectorParsing(unittest.TestCase):
    """Test selector parsing from strings."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("file.txt", attrs={"type": "file"}),
            Node("parent",
                Node("child")
            )
        ))

    def test_parse_name(self):
        """Test parsing simple name selector."""
        selector = parse("file.txt")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)

    def test_parse_wildcard(self):
        """Test parsing wildcard selector."""
        selector = parse("*.txt")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)

    def test_parse_attribute(self):
        """Test parsing attribute selector."""
        selector = parse("[type=file]")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)

    def test_parse_pseudo_leaf(self):
        """Test parsing :leaf pseudo-selector."""
        selector = parse(":leaf")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 2)  # file.txt and child

    def test_parse_pseudo_root(self):
        """Test parsing :root pseudo-selector."""
        selector = parse(":root")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "root")

    def test_parse_direct_child(self):
        """Test parsing direct child selector."""
        selector = parse("parent > child")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "child")

    def test_parse_descendant(self):
        """Test parsing descendant selector."""
        selector = parse("root child")
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].name, "child")


class TestSelectorRepresentations(unittest.TestCase):
    """Test selector string representations."""

    def test_name_selector_repr(self):
        """Test NameSelector repr."""
        selector = name("test")
        self.assertIn("NameSelector", repr(selector))
        self.assertIn("test", repr(selector))

    def test_attrs_selector_repr(self):
        """Test AttrsSelector repr."""
        selector = attrs(type="file", size=100)
        repr_str = repr(selector)
        self.assertIn("AttrsSelector", repr_str)

    def test_logical_selector_repr(self):
        """Test logical selector repr."""
        selector = name("a") & name("b")
        repr_str = repr(selector)
        self.assertIn("&", repr_str)

        selector = ~name("a")
        repr_str = repr(selector)
        self.assertIn("~", repr_str)


class TestAnyNoneSelectors(unittest.TestCase):
    """Test any and none selectors."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("a"),
            Node("b")
        ))

    def test_any_selector(self):
        """Test any selector matches all nodes."""
        selector = any_()
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 3)  # All nodes

    def test_none_selector(self):
        """Test none selector matches no nodes."""
        selector = none()
        nodes = list(selector.select(self.tree))
        self.assertEqual(len(nodes), 0)


if __name__ == "__main__":
    unittest.main()
