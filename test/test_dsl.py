import unittest
from AlgoTree.node import Node
from AlgoTree.dsl import TreeDSL, parse_tree


class TestTreeDSL(unittest.TestCase):
    """Test TreeDSL parsing."""

    def test_parse_visual_format(self):
        """Test parsing visual tree format."""
        text = """root
├── child1
└── child2
    └── grandchild"""

        tree = TreeDSL.parse(text)

        self.assertEqual(tree.name, "root")
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(tree.children[0].name, "child1")
        self.assertEqual(tree.children[1].name, "child2")
        self.assertEqual(len(tree.children[1].children), 1)
        self.assertEqual(tree.children[1].children[0].name, "grandchild")

    def test_parse_visual_with_attributes(self):
        """Test parsing visual format with attributes."""
        text = """root[type:container]
├── child1[value:1]
└── child2[value:2]"""

        tree = TreeDSL.parse(text)

        self.assertEqual(tree.get("type"), "container")
        self.assertEqual(tree.children[0].get("value"), 1)
        self.assertEqual(tree.children[1].get("value"), 2)

    def test_parse_indent_format(self):
        """Test parsing indent-based format."""
        text = """root: {type: container}
  child1: {value: 1}
  child2: {value: 2}
    grandchild: {value: 3}"""

        tree = TreeDSL.parse(text)

        self.assertEqual(tree.name, "root")
        self.assertEqual(tree.get("type"), "container")
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(tree.children[0].get("value"), 1)
        self.assertEqual(tree.children[1].children[0].get("value"), 3)

    def test_parse_sexpr_format(self):
        """Test parsing S-expression format."""
        text = "(root :type container (child1 :value 1) (child2 :value 2))"

        tree = TreeDSL.parse(text)

        self.assertEqual(tree.name, "root")
        self.assertEqual(tree.get("type"), "container")
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(tree.children[0].name, "child1")
        self.assertEqual(tree.children[0].get("value"), 1)

    def test_parse_sexpr_nested(self):
        """Test parsing nested S-expressions."""
        text = "(root (a (b (c))))"

        tree = TreeDSL.parse(text)

        self.assertEqual(tree.name, "root")
        self.assertEqual(tree.children[0].name, "a")
        self.assertEqual(tree.children[0].children[0].name, "b")
        self.assertEqual(tree.children[0].children[0].children[0].name, "c")

    def test_auto_detect_visual(self):
        """Test auto-detecting visual format."""
        text = """root
├── child1"""

        tree = TreeDSL.parse(text)
        self.assertEqual(tree.name, "root")
        self.assertEqual(tree.children[0].name, "child1")

    def test_auto_detect_indent(self):
        """Test auto-detecting indent format."""
        text = """root
  child1
  child2"""

        tree = TreeDSL.parse(text)
        self.assertEqual(tree.name, "root")
        self.assertEqual(len(tree.children), 2)

    def test_auto_detect_sexpr(self):
        """Test auto-detecting S-expression format."""
        text = "(root (child1) (child2))"

        tree = TreeDSL.parse(text)
        self.assertEqual(tree.name, "root")
        self.assertEqual(len(tree.children), 2)

    def test_parse_empty_raises_error(self):
        """Test that empty text raises error."""
        with self.assertRaises(ValueError):
            TreeDSL.parse("")

    def test_parse_node_spec(self):
        """Test parsing node specification."""
        name, attrs = TreeDSL._parse_node_spec("node[key:value]")
        self.assertEqual(name, "node")
        self.assertEqual(attrs, {"key": "value"})

        name, attrs = TreeDSL._parse_node_spec("node[k1:v1,k2:v2]")
        self.assertEqual(name, "node")
        self.assertEqual(attrs, {"k1": "v1", "k2": "v2"})

    def test_parse_node_spec_no_attrs(self):
        """Test parsing node without attributes."""
        name, attrs = TreeDSL._parse_node_spec("simple_node")
        self.assertEqual(name, "simple_node")
        self.assertEqual(attrs, {})

    def test_parse_attrs(self):
        """Test parsing attributes."""
        attrs = TreeDSL._parse_attrs("{key: value}")
        self.assertEqual(attrs, {"key": "value"})

        attrs = TreeDSL._parse_attrs("{k1: v1, k2: v2}")
        self.assertEqual(attrs, {"k1": "v1", "k2": "v2"})

    def test_parse_attrs_empty(self):
        """Test parsing empty attributes."""
        attrs = TreeDSL._parse_attrs("{}")
        self.assertEqual(attrs, {})

        attrs = TreeDSL._parse_attrs("")
        self.assertEqual(attrs, {})

    def test_tokenize_sexpr(self):
        """Test S-expression tokenization."""
        tokens = TreeDSL._tokenize_sexpr("(a (b c) d)")
        self.assertEqual(tokens, ["(", "a", "(", "b", "c", ")", "d", ")"])

    def test_tokenize_sexpr_with_attrs(self):
        """Test S-expression tokenization with attributes."""
        tokens = TreeDSL._tokenize_sexpr("(node :key value)")
        self.assertEqual(tokens, ["(", "node", ":key", "value", ")"])


class TestParseTreeFunction(unittest.TestCase):
    """Test parse_tree convenience function."""

    def test_parse_tree_visual(self):
        """Test parsing with convenience function."""
        text = """root
├── a
└── b"""

        tree = parse_tree(text)
        self.assertEqual(tree.name, "root")
        self.assertEqual(len(tree.children), 2)

    def test_parse_tree_explicit_format(self):
        """Test parsing with explicit format."""
        text = "root\n  child1\n  child2"

        tree = parse_tree(text, format="indent")
        self.assertEqual(tree.name, "root")
        self.assertEqual(len(tree.children), 2)

    def test_parse_tree_sexpr(self):
        """Test parsing S-expression with convenience function."""
        text = "(root (a) (b))"

        tree = parse_tree(text, format="sexpr")
        self.assertEqual(tree.name, "root")
        self.assertEqual(len(tree.children), 2)

    def test_parse_tree_invalid_format(self):
        """Test parsing with invalid format."""
        with self.assertRaises(ValueError):
            parse_tree("test", format="invalid")


class TestComplexTrees(unittest.TestCase):
    """Test parsing complex tree structures."""

    def test_complex_visual_tree(self):
        """Test parsing complex visual tree."""
        text = """company[type:organization]
├── engineering[dept:tech]
│   ├── frontend[team:web]
│   └── backend[team:api]
└── sales[dept:business]
    └── regional[area:west]"""

        tree = TreeDSL.parse(text)

        self.assertEqual(tree.name, "company")
        self.assertEqual(tree.get("type"), "organization")

        eng = tree.children[0]
        self.assertEqual(eng.name, "engineering")
        self.assertEqual(eng.get("dept"), "tech")
        self.assertEqual(len(eng.children), 2)

        sales = tree.children[1]
        self.assertEqual(sales.name, "sales")
        self.assertEqual(len(sales.children), 1)

    def test_complex_indent_tree(self):
        """Test parsing complex indent tree."""
        text = """root: {level: 0}
  a: {level: 1, value: 10}
    b: {level: 2, value: 20}
      c: {level: 3, value: 30}
  d: {level: 1, value: 40}"""

        tree = TreeDSL.parse(text)

        self.assertEqual(tree.get("level"), 0)
        self.assertEqual(len(tree.children), 2)

        # Deep nesting
        a = tree.children[0]
        b = a.children[0]
        c = b.children[0]
        self.assertEqual(c.get("level"), 3)
        self.assertEqual(c.get("value"), 30)

    def test_complex_sexpr_tree(self):
        """Test parsing complex S-expression."""
        text = """(company :type org
          (engineering :size 50
            (frontend :tech react)
            (backend :tech python))
          (sales :size 30))"""

        tree = TreeDSL.parse(text)

        self.assertEqual(tree.name, "company")
        self.assertEqual(tree.get("type"), "org")

        eng = tree.children[0]
        self.assertEqual(eng.name, "engineering")
        self.assertEqual(eng.get("size"), 50)
        self.assertEqual(len(eng.children), 2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_single_node(self):
        """Test parsing single node."""
        tree = TreeDSL.parse("root")
        self.assertEqual(tree.name, "root")
        self.assertEqual(len(tree.children), 0)

    def test_single_node_with_attrs(self):
        """Test parsing single node with attributes."""
        tree = TreeDSL.parse("root[key:value]")
        self.assertEqual(tree.name, "root")
        self.assertEqual(tree.get("key"), "value")

    def test_whitespace_handling(self):
        """Test handling of extra whitespace."""
        text = """root


  child1

  child2"""

        tree = TreeDSL.parse(text)
        self.assertEqual(tree.name, "root")
        self.assertEqual(len(tree.children), 2)

    def test_unicode_tree_chars(self):
        """Test various Unicode tree characters."""
        text = """root
├─ child1
└─ child2"""

        tree = TreeDSL.parse(text)
        self.assertEqual(len(tree.children), 2)

    def test_sexpr_extra_spaces(self):
        """Test S-expression with extra spaces."""
        text = "(  root   (  child1  )   (  child2  )  )"

        tree = TreeDSL.parse(text)
        self.assertEqual(tree.name, "root")
        self.assertEqual(len(tree.children), 2)


class TestAttributeParsing(unittest.TestCase):
    """Test attribute parsing edge cases."""

    def test_attribute_with_spaces(self):
        """Test attributes with spaces in values."""
        name, attrs = TreeDSL._parse_node_spec("node[desc:hello world]")
        self.assertEqual(attrs["desc"], "hello world")

    def test_attribute_with_special_chars(self):
        """Test attributes with special characters."""
        name, attrs = TreeDSL._parse_node_spec("node[path:/usr/bin]")
        self.assertEqual(attrs["path"], "/usr/bin")

    def test_multiple_colons_in_value(self):
        """Test attributes with multiple colons."""
        name, attrs = TreeDSL._parse_node_spec("node[url:http://example.com]")
        self.assertEqual(attrs["url"], "http://example.com")

    def test_dict_format_attributes(self):
        """Test dictionary format attributes."""
        attrs = TreeDSL._parse_attrs("{key1: value1, key2: value2}")
        self.assertEqual(attrs["key1"], "value1")
        self.assertEqual(attrs["key2"], "value2")


class TestSharedAssembler(unittest.TestCase):
    """Test that _parse_visual and _parse_indent both route through _assemble
    and produce structurally identical results for equivalent trees."""

    def _nodes_equal(self, a, b):
        """Recursively check that two nodes have equal names, attrs, and children."""
        if a.name != b.name:
            return False
        if dict(a.attrs) != dict(b.attrs):
            return False
        if len(a.children) != len(b.children):
            return False
        return all(self._nodes_equal(ac, bc) for ac, bc in zip(a.children, b.children))

    def test_visual_and_indent_produce_equal_nodes(self):
        """Visual and indent forms of the same structure produce equal Nodes."""
        visual_text = """root
├── a
│   ├── b
│   └── c
└── d"""

        indent_text = """root
  a
    b
    c
  d"""

        visual_tree = TreeDSL.parse(visual_text, format='visual')
        indent_tree = TreeDSL.parse(indent_text, format='indent')

        self.assertTrue(self._nodes_equal(visual_tree, indent_tree))

    def test_visual_and_indent_equal_with_attrs(self):
        """Visual and indent forms with attributes produce equal Nodes."""
        visual_text = """root[type:container]
├── child1[value:1]
└── child2[value:2]"""

        indent_text = """root[type:container]
  child1[value:1]
  child2[value:2]"""

        visual_tree = TreeDSL.parse(visual_text, format='visual')
        indent_tree = TreeDSL.parse(indent_text, format='indent')

        self.assertTrue(self._nodes_equal(visual_tree, indent_tree))

    def test_syntax_kwarg_alias(self):
        """syntax= kwarg is accepted as an alias for format=."""
        text = "root\n  child1\n  child2"

        tree_via_format = TreeDSL.parse(text, format='indent')
        tree_via_syntax = TreeDSL.parse(text, syntax='indent')

        self.assertTrue(self._nodes_equal(tree_via_format, tree_via_syntax))

    def test_parse_tree_syntax_kwarg(self):
        """parse_tree convenience function accepts syntax= kwarg."""
        text = "(root (a) (b))"

        tree_via_format = parse_tree(text, format='sexpr')
        tree_via_syntax = parse_tree(text, syntax='sexpr')

        self.assertTrue(self._nodes_equal(tree_via_format, tree_via_syntax))

    def test_syntax_overrides_format(self):
        """When both syntax= and format= are given, syntax= wins."""
        # Give format='indent' but syntax='sexpr'; sexpr should win
        text = "(root (a) (b))"
        tree = TreeDSL.parse(text, format='indent', syntax='sexpr')
        self.assertEqual(tree.name, "root")
        self.assertEqual(len(tree.children), 2)


if __name__ == "__main__":
    unittest.main()
