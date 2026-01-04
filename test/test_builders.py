import unittest
from AlgoTree.node import Node
from AlgoTree.tree import Tree
from AlgoTree.builders import TreeBuilder, FluentTree, TreeContext, QuickBuilder, tree, branch, leaf


class TestTreeBuilder(unittest.TestCase):
    """Test TreeBuilder class."""

    def test_simple_build(self):
        """Test building simple tree."""
        builder = TreeBuilder("root")
        result = builder.build()

        self.assertEqual(result.root.name, "root")
        self.assertEqual(len(result.root.children), 0)

    def test_with_attributes(self):
        """Test building with attributes."""
        builder = TreeBuilder("root", type="container", value=1)
        result = builder.build()

        self.assertEqual(result.root.get("type"), "container")
        self.assertEqual(result.root.get("value"), 1)

    def test_attr_method(self):
        """Test adding attributes with attr method."""
        builder = TreeBuilder("root")
        builder.attr(type="container", value=1)
        result = builder.build()

        self.assertEqual(result.root.get("type"), "container")
        self.assertEqual(result.root.get("value"), 1)

    def test_attrs_method(self):
        """Test adding attributes with attrs method."""
        builder = TreeBuilder("root")
        builder.attrs({"type": "container", "value": 1})
        result = builder.build()

        self.assertEqual(result.root.get("type"), "container")
        self.assertEqual(result.root.get("value"), 1)

    def test_add_child_with_string(self):
        """Test adding child with string name."""
        builder = TreeBuilder("root")
        builder.child("child1", type="leaf")
        result = builder.build()

        self.assertEqual(len(result.root.children), 1)
        self.assertEqual(result.root.children[0].name, "child1")
        self.assertEqual(result.root.children[0].get("type"), "leaf")

    def test_add_child_with_builder(self):
        """Test adding child with TreeBuilder."""
        child_builder = TreeBuilder("child1", value=1)
        builder = TreeBuilder("root")
        builder.child(child_builder)
        result = builder.build()

        self.assertEqual(len(result.root.children), 1)
        self.assertEqual(result.root.children[0].get("value"), 1)

    def test_add_child_with_node(self):
        """Test adding child with Node."""
        child_node = Node("child1", attrs={"value": 1})
        builder = TreeBuilder("root")
        builder.child(child_node)
        result = builder.build()

        self.assertEqual(len(result.root.children), 1)
        self.assertEqual(result.root.children[0].get("value"), 1)

    def test_children_method(self):
        """Test adding multiple children."""
        builder = TreeBuilder("root")
        builder.children("a", "b", "c")
        result = builder.build()

        self.assertEqual(len(result.root.children), 3)
        names = [c.name for c in result.root.children]
        self.assertEqual(names, ["a", "b", "c"])

    def test_chaining(self):
        """Test method chaining."""
        result = (TreeBuilder("root")
                 .attr(type="container")
                 .child("a", value=1)
                 .child("b", value=2)
                 .build())

        self.assertEqual(result.root.get("type"), "container")
        self.assertEqual(len(result.root.children), 2)

    def test_up_method(self):
        """Test up method for navigation."""
        builder = TreeBuilder("root")
        child_builder = TreeBuilder("child")
        child_builder._parent = builder

        parent = child_builder.up()
        self.assertEqual(parent, builder)

        # Root has no parent, returns self
        root_up = builder.up()
        self.assertEqual(root_up, builder)

    def test_root_method(self):
        """Test root method for navigation."""
        builder = TreeBuilder("root")
        child = TreeBuilder("child")
        grandchild = TreeBuilder("grandchild")

        child._parent = builder
        grandchild._parent = child

        root = grandchild.root()
        self.assertEqual(root, builder)

    def test_build_node(self):
        """Test building just a Node."""
        builder = TreeBuilder("root")
        builder.child("a")
        node = builder.build_node()

        self.assertIsInstance(node, Node)
        self.assertEqual(node.name, "root")
        self.assertEqual(len(node.children), 1)

    def test_lshift_operator(self):
        """Test << operator for adding children."""
        builder = TreeBuilder("root")
        builder << "a" << "b"
        result = builder.build()

        self.assertEqual(len(result.root.children), 2)

    def test_call_operator(self):
        """Test calling builder to add attributes."""
        builder = TreeBuilder("root")
        builder(type="container", value=1)
        result = builder.build()

        self.assertEqual(result.root.get("type"), "container")
        self.assertEqual(result.root.get("value"), 1)


class TestFluentTree(unittest.TestCase):
    """Test FluentTree class."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2})
        ))

    def test_create_from_tree(self):
        """Test creating from Tree."""
        fluent = FluentTree(self.tree)
        self.assertEqual(fluent.root.name, "root")

    def test_create_from_node(self):
        """Test creating from Node."""
        node = Node("root")
        fluent = FluentTree(node)
        self.assertEqual(fluent.root.name, "root")

    def test_create_from_string(self):
        """Test creating from string."""
        fluent = FluentTree("root")
        self.assertEqual(fluent.root.name, "root")

    def test_map(self):
        """Test map operation."""
        fluent = FluentTree(self.tree)
        result = fluent.map(lambda n: {"doubled": n.get("value", 0) * 2})

        self.assertIsInstance(result, FluentTree)
        self.assertEqual(result.root.children[0].get("doubled"), 2)

    def test_filter(self):
        """Test filter operation."""
        fluent = FluentTree(self.tree)
        result = fluent.filter(lambda n: n.get("value", 0) > 1)

        self.assertIsInstance(result, FluentTree)
        self.assertEqual(len(result.root.children), 1)

    def test_prune(self):
        """Test prune operation."""
        fluent = FluentTree(self.tree)
        result = fluent.prune(lambda n: n.name == "a")

        self.assertIsInstance(result, FluentTree)
        names = [c.name for c in result.root.children]
        self.assertNotIn("a", names)

    def test_graft(self):
        """Test graft operation."""
        fluent = FluentTree(self.tree)
        subtree = Node("new")
        result = fluent.graft(lambda n: n.name == "a", subtree)

        self.assertIsInstance(result, FluentTree)
        self.assertEqual(len(result.root.children[0].children), 1)

    def test_flatten(self):
        """Test flatten operation."""
        deep_tree = Tree(Node("root",
            Node("a",
                Node("b")
            )
        ))
        fluent = FluentTree(deep_tree)
        result = fluent.flatten(max_depth=1)

        self.assertIsInstance(result, FluentTree)

    def test_transform(self):
        """Test custom transform."""
        fluent = FluentTree(self.tree)
        result = fluent.transform(lambda t: t.map(lambda n: {"transformed": True}))

        self.assertIsInstance(result, FluentTree)
        self.assertTrue(result.root.get("transformed"))

    def test_terminal_operations(self):
        """Test terminal operations (don't return FluentTree)."""
        fluent = FluentTree(self.tree)

        # find
        node = fluent.find("a")
        self.assertIsInstance(node, Node)

        # find_all
        nodes = fluent.find_all(lambda n: True)
        self.assertIsInstance(nodes, list)

        # reduce
        total = fluent.reduce(lambda acc, n: acc + n.get("value", 0), 0)
        self.assertEqual(total, 3)

        # to_dict
        d = fluent.to_dict()
        self.assertIsInstance(d, dict)

        # to_paths
        paths = fluent.to_paths()
        self.assertIsInstance(paths, list)

    def test_or_operator(self):
        """Test | operator."""
        fluent = FluentTree(self.tree)
        result = fluent | (lambda t: t.map(lambda n: {"piped": True}))

        self.assertIsInstance(result, FluentTree)
        self.assertTrue(result.root.get("piped"))

    def test_rshift_operator(self):
        """Test >> operator."""
        fluent = FluentTree(self.tree)
        result = fluent >> (lambda t: t.size)

        self.assertEqual(result, 3)  # Not a FluentTree


class TestDSLFunctions(unittest.TestCase):
    """Test DSL-style builder functions."""

    def test_tree_function(self):
        """Test tree() function."""
        result = tree("root",
            tree("child1", value=1),
            tree("child2", value=2)
        ).build()

        self.assertEqual(result.root.name, "root")
        self.assertEqual(len(result.root.children), 2)
        self.assertEqual(result.root.children[0].get("value"), 1)

    def test_tree_with_node_children(self):
        """Test tree() with Node children."""
        node = Node("child")
        result = tree("root", node).build()

        self.assertEqual(len(result.root.children), 1)
        self.assertEqual(result.root.children[0].name, "child")

    def test_tree_with_string_children(self):
        """Test tree() with string children."""
        result = tree("root", "child1", "child2").build()

        self.assertEqual(len(result.root.children), 2)
        names = [c.name for c in result.root.children]
        self.assertEqual(names, ["child1", "child2"])

    def test_branch_function(self):
        """Test branch() function (alias for tree)."""
        result = branch("root",
            leaf("child1"),
            leaf("child2")
        ).build()

        self.assertEqual(result.root.name, "root")
        self.assertEqual(len(result.root.children), 2)

    def test_leaf_function(self):
        """Test leaf() function."""
        builder = leaf("my_leaf", value=1)
        result = builder.build()

        self.assertEqual(result.root.name, "my_leaf")
        self.assertEqual(result.root.get("value"), 1)
        self.assertEqual(len(result.root.children), 0)


class TestTreeContext(unittest.TestCase):
    """Test TreeContext class."""

    def test_basic_context(self):
        """Test basic context usage."""
        with TreeContext("root") as ctx:
            with ctx.child("a") as a:
                a.add_child("a1")  # add_child for leaf nodes
            with ctx.child("b") as b:
                b.add_child("b1")

        result = ctx.build()

        self.assertEqual(result.root.name, "root")
        self.assertEqual(len(result.root.children), 2)
        self.assertEqual(result.root.children[0].children[0].name, "a1")

    def test_context_with_attributes(self):
        """Test context with attributes."""
        with TreeContext("root", type="container") as ctx:
            with ctx.child("a", value=1) as a:
                pass

        result = ctx.build()

        self.assertEqual(result.root.get("type"), "container")
        self.assertEqual(result.root.children[0].get("value"), 1)

    def test_nested_context(self):
        """Test deeply nested context."""
        with TreeContext("root") as ctx:
            with ctx.child("a") as a:
                with a.child("b") as b:
                    with b.child("c"):
                        pass

        result = ctx.build()

        # Navigate to deeply nested node
        c = result.root.children[0].children[0].children[0]
        self.assertEqual(c.name, "c")


class TestQuickBuilder(unittest.TestCase):
    """Test QuickBuilder class."""

    def test_simple_build(self):
        """Test simple quick build."""
        builder = QuickBuilder()
        result = builder.root("myroot").build()

        self.assertEqual(result.root.name, "myroot")

    def test_add_paths(self):
        """Test adding paths."""
        result = (QuickBuilder()
                 .root("root")
                 .add("src/main.py", type="file")
                 .add("src/utils.py", type="file")
                 .add("docs/README.md", type="file")
                 .build())

        # Should have hierarchical structure
        self.assertEqual(len(result.root.children), 2)  # src and docs

        # Check that src has children
        src = next(c for c in result.root.children if c.name == "src")
        self.assertEqual(len(src.children), 2)

    def test_shared_paths(self):
        """Test paths that share prefixes."""
        result = (QuickBuilder()
                 .root("root")
                 .add("a/b/c")
                 .add("a/b/d")
                 .add("a/e")
                 .build())

        # a should have b and e as children
        a = result.root.children[0]
        self.assertEqual(len(a.children), 2)

        # b should have c and d
        b = next(c for c in a.children if c.name == "b")
        self.assertEqual(len(b.children), 2)

    def test_default_root(self):
        """Test with default root."""
        result = (QuickBuilder()
                 .add("a/b")
                 .build())

        # Should create default 'root' node
        self.assertEqual(result.root.name, "root")

    def test_custom_delimiter(self):
        """Test custom path delimiter."""
        result = (QuickBuilder()
                 .root("root")
                 .add("a.b.c")
                 .build(delimiter="."))

        # Should parse with dot delimiter
        a = result.root.children[0]
        self.assertEqual(a.name, "a")
        self.assertEqual(a.children[0].name, "b")


class TestBuilderRepresentations(unittest.TestCase):
    """Test builder string representations."""

    def test_tree_builder_repr(self):
        """Test TreeBuilder repr."""
        builder = TreeBuilder("root", type="test")
        builder.child("a")

        repr_str = repr(builder)
        self.assertIn("TreeBuilder", repr_str)
        self.assertIn("root", repr_str)
        self.assertIn("children=1", repr_str)

    def test_fluent_tree_repr(self):
        """Test FluentTree repr."""
        fluent = FluentTree("root")
        repr_str = repr(fluent)
        self.assertIn("FluentTree", repr_str)

    def test_fluent_tree_str(self):
        """Test FluentTree str."""
        fluent = FluentTree(Tree(Node("root",
            Node("a")
        )))
        str_output = str(fluent)
        self.assertIn("root", str_output)
        self.assertIn("a", str_output)


if __name__ == "__main__":
    unittest.main()
