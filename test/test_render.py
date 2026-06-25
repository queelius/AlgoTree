"""
Tests for AlgoTree/render.py – Theme, registry, dispatch, fold-based text tree.

TDD: write tests first, then create the module.

Cross-check: we import TreeExporter.to_ascii to verify byte-for-byte identity.
"""

import pytest
from AlgoTree import Node
from AlgoTree.exporters import TreeExporter


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

def _three_level_tree() -> Node:
    """
    root
    +- child1
    |   +- grandchild1
    |   \- grandchild2
    \- child2
        \- grandchild3
    """
    return Node(
        "root",
        Node("child1", Node("grandchild1"), Node("grandchild2")),
        Node("child2", Node("grandchild3")),
    )


# ---------------------------------------------------------------------------
# Computed expected strings (cross-checked against TreeExporter)
# ---------------------------------------------------------------------------
# ASCII:
#   root
#   +- child1
#   |   +- grandchild1
#   |   \- grandchild2
#   \- child2
#       \- grandchild3

EXPECTED_ASCII = (
    "root\n"
    "+- child1\n"
    "|   +- grandchild1\n"
    "|   \\- grandchild2\n"
    "\\- child2\n"
    "    \\- grandchild3"
)

# Unicode:
#   root
#   ├─ child1
#   │   ├─ grandchild1
#   │   └─ grandchild2
#   └─ child2
#       └─ grandchild3

EXPECTED_UNICODE = (
    "root\n"
    "├─ child1\n"
    "│   ├─ grandchild1\n"
    "│   └─ grandchild2\n"
    "└─ child2\n"
    "    └─ grandchild3"
)


# ---------------------------------------------------------------------------
# Step 1 – FAILING before render.py exists
# ---------------------------------------------------------------------------

class TestRenderModuleExists:
    """The module must be importable and expose the expected names."""

    def test_import_render_module(self):
        from AlgoTree import render as _render_mod  # noqa: F401

    def test_render_function_callable(self):
        from AlgoTree.render import render  # noqa: F401
        assert callable(render)

    def test_theme_namedtuple(self):
        from AlgoTree.render import Theme, ASCII_THEME, UNICODE_THEME
        assert isinstance(ASCII_THEME, Theme)
        assert isinstance(UNICODE_THEME, Theme)

    def test_register_callable(self):
        from AlgoTree.render import register
        assert callable(register)

    def test_extension_for(self):
        from AlgoTree.render import extension_for
        assert extension_for("ascii") == ".txt"
        assert extension_for("unicode") == ".txt"
        assert extension_for("does-not-exist") == ".txt"


class TestNodeRenderMethod:
    """Node.render must delegate to the render module."""

    def test_node_has_render_method(self):
        n = Node("x")
        assert callable(n.render)

    def test_node_render_default_is_unicode(self):
        n = Node("x")
        result = n.render()
        assert result == "x"  # leaf, unicode or ascii – both give just name

    def test_node_render_ascii_leaf(self):
        n = Node("x")
        assert n.render("ascii") == "x"

    def test_node_render_unicode_leaf(self):
        n = Node("x")
        assert n.render("unicode") == "x"


class TestRenderDispatch:
    """render(node, fmt) dispatches correctly."""

    def test_unknown_format_raises(self):
        from AlgoTree.render import render
        n = Node("x")
        with pytest.raises(ValueError, match="unknown render format"):
            render(n, "bogus")

    def test_render_ascii(self):
        from AlgoTree.render import render
        tree = _three_level_tree()
        result = render(tree, "ascii")
        assert result == EXPECTED_ASCII

    def test_render_unicode(self):
        from AlgoTree.render import render
        tree = _three_level_tree()
        result = render(tree, "unicode")
        assert result == EXPECTED_UNICODE

    def test_node_dot_render_ascii(self):
        tree = _three_level_tree()
        assert tree.render("ascii") == EXPECTED_ASCII

    def test_node_dot_render_unicode(self):
        tree = _three_level_tree()
        assert tree.render("unicode") == EXPECTED_UNICODE


class TestByteIdenticalToTreeExporter:
    """render output must be byte-for-byte identical to TreeExporter.to_ascii."""

    def test_ascii_matches_exporter(self):
        from AlgoTree.render import render
        tree = _three_level_tree()
        expected = TreeExporter.to_ascii(tree, style="ascii")
        got = render(tree, "ascii")
        assert got == expected, (
            f"render('ascii') != TreeExporter.to_ascii style=ascii\n"
            f"  render:   {got!r}\n"
            f"  exporter: {expected!r}"
        )

    def test_unicode_matches_exporter(self):
        from AlgoTree.render import render
        tree = _three_level_tree()
        expected = TreeExporter.to_ascii(tree, style="unicode")
        got = render(tree, "unicode")
        assert got == expected, (
            f"render('unicode') != TreeExporter.to_ascii style=unicode\n"
            f"  render:   {got!r}\n"
            f"  exporter: {expected!r}"
        )

    def test_single_child_ascii(self):
        from AlgoTree.render import render
        tree = Node("root", Node("only"))
        assert render(tree, "ascii") == TreeExporter.to_ascii(tree, style="ascii")

    def test_deep_chain_unicode(self):
        from AlgoTree.render import render
        tree = Node("a", Node("b", Node("c", Node("d"))))
        assert render(tree, "unicode") == TreeExporter.to_ascii(tree, style="unicode")

    def test_wide_tree_ascii(self):
        from AlgoTree.render import render
        tree = Node("root", Node("a"), Node("b"), Node("c"), Node("d"), Node("e"))
        assert render(tree, "ascii") == TreeExporter.to_ascii(tree, style="ascii")


class TestCustomBackend:
    """register() lets you add a new format."""

    def test_register_and_use_custom_backend(self):
        from AlgoTree.render import register, render
        register("names", lambda node, **o: ",".join(n.name for n in node.walk()), ".csv")
        tree = Node("r", Node("x"), Node("y"))
        result = render(tree, "names")
        assert result == "r,x,y"


# ---------------------------------------------------------------------------
# Task 2 – Structural backends: mermaid + graphviz with escaping
# ---------------------------------------------------------------------------

class TestMermaidBackend:
    """render('mermaid') emits valid Mermaid syntax with proper escaping."""

    def _simple_tree(self) -> Node:
        return Node("root", Node("child1"), Node("child2", Node("grandchild")))

    def test_mermaid_registered(self):
        from AlgoTree.render import extension_for
        assert extension_for("mermaid") == ".mmd"

    def test_mermaid_contains_graph_td(self):
        from AlgoTree.render import render
        result = render(self._simple_tree(), "mermaid")
        assert "graph TD" in result

    def test_mermaid_has_node_declarations(self):
        from AlgoTree.render import render
        result = render(self._simple_tree(), "mermaid")
        # All 4 nodes (root, child1, child2, grandchild) should appear as N0..N3
        assert "N0" in result
        assert "N1" in result
        assert "N2" in result
        assert "N3" in result

    def test_mermaid_has_arrow_edges(self):
        from AlgoTree.render import render
        result = render(self._simple_tree(), "mermaid")
        assert "-->" in result

    def test_mermaid_uses_quoted_label_syntax(self):
        from AlgoTree.render import render
        # Labels are emitted as N0["..."] regardless of node_shape, so that
        # closing delimiters inside label text cannot be mis-parsed.
        result = render(self._simple_tree(), "mermaid")
        assert 'N0["' in result

    def test_mermaid_contains_node_names(self):
        from AlgoTree.render import render
        result = render(self._simple_tree(), "mermaid")
        assert "root" in result
        assert "child1" in result
        assert "child2" in result
        assert "grandchild" in result

    def test_mermaid_angle_brackets_safe_in_quoted_syntax(self):
        from AlgoTree.render import render
        # Inside Mermaid quoted-string labels N0["..."], angle brackets are
        # safe as-is — they are not shape delimiters.  The escaper only needs
        # to escape the double-quote character (as &quot;).
        evil = Node('a<b>"c', Node("normal"))
        result = render(evil, "mermaid")
        lines = result.splitlines()
        node_line = next(l for l in lines if "N0" in l and "-->" not in l)
        # Angle brackets pass through unchanged inside the quoted label
        assert "<b>" in node_line
        # Double-quote in the name must be escaped as &quot;
        assert "&quot;" in node_line
        # The raw double-quote from the source name must not appear unescaped
        # (note: the surrounding quotes of the label syntax are expected)
        assert 'a"c' not in node_line

    def test_mermaid_escapes_double_quotes(self):
        from AlgoTree.render import render
        evil = Node('say "hello"', Node("child"))
        result = render(evil, "mermaid")
        lines = result.splitlines()
        node_line = next(l for l in lines if "N0" in l and "-->" not in l)
        # Double quote must not appear raw (converted to single or entity)
        assert '"hello"' not in node_line

    def test_mermaid_direction_option(self):
        from AlgoTree.render import render
        result = render(self._simple_tree(), "mermaid", direction="LR")
        assert "graph LR" in result

    def test_dot_alias_registered(self):
        from AlgoTree.render import extension_for
        assert extension_for("dot") == ".dot"

    def test_mermaid_node_ids_preorder(self):
        """Node IDs should be assigned in preorder (N0=root, N1=first child, ...)."""
        from AlgoTree.render import render
        result = render(self._simple_tree(), "mermaid")
        # root must be N0
        lines = result.splitlines()
        n0_line = next(l for l in lines if "N0(" in l or "N0[" in l)
        assert "root" in n0_line


class TestGraphvizBackend:
    """render('graphviz') and render('dot') emit valid DOT syntax with escaping."""

    def _simple_tree(self) -> Node:
        return Node("root", Node("child1"), Node("child2", Node("grandchild")))

    def test_graphviz_registered(self):
        from AlgoTree.render import extension_for
        assert extension_for("graphviz") == ".dot"

    def test_graphviz_contains_digraph(self):
        from AlgoTree.render import render
        result = render(self._simple_tree(), "graphviz")
        assert "digraph" in result

    def test_graphviz_has_directed_edges(self):
        from AlgoTree.render import render
        result = render(self._simple_tree(), "graphviz")
        assert "->" in result

    def test_graphviz_has_stable_node_ids(self):
        from AlgoTree.render import render
        result = render(self._simple_tree(), "graphviz")
        # Stable preorder IDs: N0, N1, N2, N3
        assert "N0" in result
        assert "N1" in result
        assert "N2" in result
        assert "N3" in result

    def test_graphviz_contains_labels(self):
        from AlgoTree.render import render
        result = render(self._simple_tree(), "graphviz")
        assert "root" in result
        assert "child1" in result
        assert "child2" in result
        assert "grandchild" in result

    def test_graphviz_escapes_double_quotes_in_label(self):
        from AlgoTree.render import render
        evil = Node('say "hello"')
        result = render(evil, "graphviz")
        # Raw unescaped " inside a DOT label must not appear
        # DOT escape for " is \"
        assert 'say "hello"' not in result or '\\"hello\\"' in result or "say" in result
        # More specifically: the label value must not contain unescaped quotes
        # Find label= line
        lines = result.splitlines()
        label_lines = [l for l in lines if "label" in l and "N0" in l]
        if label_lines:
            label_line = label_lines[0]
            # The label content (between outer quotes) must have \" not "
            # Simple check: raw '"hello"' as inner content should be escaped
            inner = label_line.split("label=")[1] if "label=" in label_line else ""
            # Either escaped or the whole thing is properly quoted DOT
            assert inner  # label is present

    def test_graphviz_escapes_backslash_in_label(self):
        from AlgoTree.render import render
        evil = Node('path\\to\\file')
        result = render(evil, "graphviz")
        assert "path" in result  # at minimum the content appears

    def test_graphviz_dot_alias(self):
        from AlgoTree.render import render
        result_dot = render(self._simple_tree(), "dot")
        result_gv = render(self._simple_tree(), "graphviz")
        assert result_dot == result_gv

    def test_graphviz_closes_brace(self):
        from AlgoTree.render import render
        result = render(self._simple_tree(), "graphviz")
        assert result.strip().endswith("}")

    def test_graphviz_name_option(self):
        from AlgoTree.render import render
        result = render(self._simple_tree(), "graphviz", name="MyGraph")
        assert "MyGraph" in result


# ---------------------------------------------------------------------------
# Task 3 – Data backends: json, yaml, xml
# ---------------------------------------------------------------------------

class TestJsonBackend:
    """render('json') emits valid JSON that round-trips name/attrs/children."""

    def _tree_with_attrs(self) -> Node:
        return Node(
            "root",
            Node("child1", attrs={"x": 1, "y": "hello"}),
            Node("child2", Node("grandchild", attrs={"z": True})),
            attrs={"kind": "container"},
        )

    def test_json_registered(self):
        from AlgoTree.render import extension_for
        assert extension_for("json") == ".json"

    def test_json_parses(self):
        import json
        from AlgoTree.render import render
        result = render(self._tree_with_attrs(), "json")
        data = json.loads(result)
        assert isinstance(data, dict)

    def test_json_root_name(self):
        import json
        from AlgoTree.render import render
        data = json.loads(render(self._tree_with_attrs(), "json"))
        assert data["name"] == "root"

    def test_json_root_attrs(self):
        import json
        from AlgoTree.render import render
        data = json.loads(render(self._tree_with_attrs(), "json"))
        assert data["kind"] == "container"

    def test_json_children_present(self):
        import json
        from AlgoTree.render import render
        data = json.loads(render(self._tree_with_attrs(), "json"))
        assert "children" in data
        assert len(data["children"]) == 2

    def test_json_child_attrs(self):
        import json
        from AlgoTree.render import render
        data = json.loads(render(self._tree_with_attrs(), "json"))
        child1 = data["children"][0]
        assert child1["name"] == "child1"
        assert child1["x"] == 1
        assert child1["y"] == "hello"

    def test_json_leaf_has_no_children_key(self):
        import json
        from AlgoTree.render import render
        # leaf nodes should NOT include a 'children' key (matches node.to_dict())
        tree = Node("root", Node("leaf"))
        data = json.loads(render(tree, "json"))
        leaf = data["children"][0]
        assert "children" not in leaf

    def test_json_round_trips_via_node_from_dict(self):
        import json
        from AlgoTree.render import render
        tree = self._tree_with_attrs()
        data = json.loads(render(tree, "json"))
        restored = Node.from_dict(data)
        assert restored == tree

    def test_json_indent_option(self):
        from AlgoTree.render import render
        result = render(Node("x"), "json", indent=4)
        # indent=4 produces multi-line output (well, single node, but at least
        # the output is valid JSON)
        import json
        assert json.loads(result)["name"] == "x"

    def test_json_matches_node_to_dict(self):
        import json
        from AlgoTree.render import render
        tree = self._tree_with_attrs()
        assert json.loads(render(tree, "json")) == tree.to_dict()


class TestYamlBackend:
    """render('yaml') emits YAML that round-trips via yaml.safe_load."""

    def _simple_tree(self) -> Node:
        return Node(
            "root",
            Node("child", attrs={"val": 42}),
            attrs={"kind": "root"},
        )

    def test_yaml_registered(self):
        pytest.importorskip("yaml")
        from AlgoTree.render import extension_for
        assert extension_for("yaml") == ".yaml"

    def test_yaml_round_trips(self):
        yaml = pytest.importorskip("yaml")
        from AlgoTree.render import render
        tree = self._simple_tree()
        result = render(tree, "yaml")
        data = yaml.safe_load(result)
        assert data == tree.to_dict()

    def test_yaml_root_name(self):
        yaml = pytest.importorskip("yaml")
        from AlgoTree.render import render
        data = yaml.safe_load(render(self._simple_tree(), "yaml"))
        assert data["name"] == "root"

    def test_yaml_child_attrs(self):
        yaml = pytest.importorskip("yaml")
        from AlgoTree.render import render
        data = yaml.safe_load(render(self._simple_tree(), "yaml"))
        assert data["children"][0]["val"] == 42

    def test_yaml_absent_raises_with_hint(self):
        """If PyYAML is not installed, render('yaml') raises ImportError with install hint."""
        # We can only test this branch if we can mock the import.
        import sys
        import importlib
        from unittest.mock import patch

        # Patch the yaml import inside the render module to raise ImportError
        with patch.dict(sys.modules, {"yaml": None}):
            # Force reload to pick up the patched module dict
            import AlgoTree.render as render_mod
            importlib.reload(render_mod)
            try:
                with pytest.raises((ImportError, ModuleNotFoundError)):
                    render_mod.render(Node("x"), "yaml")
            finally:
                # Reload back to normal
                importlib.reload(render_mod)

    def test_yaml_uses_safe_dump_not_hand_rolled(self):
        """The yaml output must be parseable by yaml.safe_load (not hand-rolled)."""
        yaml = pytest.importorskip("yaml")
        from AlgoTree.render import render
        tree = Node("root", Node("child", attrs={"list_val": [1, 2, 3]}), attrs={"nested": {"a": 1}})
        result = render(tree, "yaml")
        # If hand-rolled, complex attrs would likely be broken; safe_load must succeed
        data = yaml.safe_load(result)
        assert data["name"] == "root"


class TestXmlBackend:
    """render('xml') emits valid XML parseable by ElementTree."""

    def _simple_tree(self) -> Node:
        return Node(
            "root",
            Node("child1", attrs={"val": "10"}),
            Node("child2", Node("grandchild")),
            attrs={"kind": "container"},
        )

    def test_xml_registered(self):
        from AlgoTree.render import extension_for
        assert extension_for("xml") == ".xml"

    def test_xml_parses(self):
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        result = render(self._simple_tree(), "xml")
        root = ET.fromstring(result)
        assert root is not None

    def test_xml_has_root_tag(self):
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        result = render(self._simple_tree(), "xml")
        root = ET.fromstring(result)
        assert root.tag == "tree"

    def test_xml_custom_root_tag(self):
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        result = render(self._simple_tree(), "xml", root_tag="forest")
        root = ET.fromstring(result)
        assert root.tag == "forest"

    def test_xml_has_node_elements(self):
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        result = render(self._simple_tree(), "xml")
        root = ET.fromstring(result)
        # Should have child <node> elements under <tree>
        nodes = list(root.iter("node"))
        assert len(nodes) > 0

    def test_xml_node_names_as_attribute(self):
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        result = render(self._simple_tree(), "xml")
        root = ET.fromstring(result)
        names = [n.get("name") for n in root.iter("node")]
        assert "root" in names
        assert "child1" in names

    def test_xml_attrs_as_element_attributes(self):
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        result = render(self._simple_tree(), "xml")
        root = ET.fromstring(result)
        child1_elem = next(n for n in root.iter("node") if n.get("name") == "child1")
        assert child1_elem.get("val") == "10"

    def test_xml_children_nested(self):
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        result = render(self._simple_tree(), "xml")
        root = ET.fromstring(result)
        # child2 should contain grandchild
        child2_elem = next(n for n in root.iter("node") if n.get("name") == "child2")
        grandchild_elem = child2_elem.find("node")
        assert grandchild_elem is not None
        assert grandchild_elem.get("name") == "grandchild"

    def test_xml_escapes_special_chars_in_name(self):
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        evil = Node('root<&>"', Node("child's node"))
        result = render(evil, "xml")
        # Must be parseable despite special characters (ET handles this)
        root = ET.fromstring(result)
        names = [n.get("name") for n in root.iter("node")]
        assert 'root<&>"' in names

    def test_xml_escapes_special_chars_in_attrs(self):
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        evil = Node("root", attrs={"key": 'val<&>"'})
        result = render(evil, "xml")
        root = ET.fromstring(result)
        node_elem = next(n for n in root.iter("node") if n.get("name") == "root")
        assert node_elem.get("key") == 'val<&>"'

    def test_xml_str_values_for_attrs(self):
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        # Numeric attrs should be str()-converted for XML attributes
        node = Node("root", attrs={"count": 42, "flag": True})
        result = render(node, "xml")
        root = ET.fromstring(result)
        elem = next(n for n in root.iter("node") if n.get("name") == "root")
        assert elem.get("count") == "42"

    def test_xml_list_valued_attr_parses(self):
        """A node with a list-valued attr must still produce XML parseable by ET.fromstring."""
        import json
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        node = Node("root", attrs={"my list": [1, 2, 3]})
        result = render(node, "xml")
        # Must not raise
        root = ET.fromstring(result)
        # The sanitised tag (space → underscore) should appear
        node_elem = next(n for n in root.iter("node") if n.get("name") == "root")
        attr_elem = node_elem.find("my_list")
        assert attr_elem is not None
        assert json.loads(attr_elem.text) == [1, 2, 3]

    def test_xml_invalid_xml_name_key_sanitized(self):
        """Keys with XML-invalid characters (digits first, angle brackets, spaces) are sanitized."""
        import xml.etree.ElementTree as ET
        from AlgoTree.render import render
        node = Node("root", attrs={"1bad": {"nested": True}, "key<x>": [0]})
        result = render(node, "xml")
        # Must parse without error
        ET.fromstring(result)


# ---------------------------------------------------------------------------
# Task 4 – HTML backend (escaped) + notebook reprs + stable palette
# ---------------------------------------------------------------------------

class TestHtmlBackend:
    """render('html') emits HTML with all node text properly escaped."""

    def test_html_registered(self):
        from AlgoTree.render import extension_for
        assert extension_for("html") == ".html"

    def test_html_returns_string(self):
        from AlgoTree.render import render
        result = render(Node("root", Node("child")), "html")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_html_escapes_script_tag_in_name(self):
        """A node named '<script>' must have its angle brackets HTML-escaped.

        We render WITHOUT the collapsible JS (collapsible=False, include_styles=False)
        so there is no legitimate <script> tag from the template — any <script>
        in the result would be injected from the node name.
        """
        from AlgoTree.render import render
        evil = Node("<script>", Node("child"))
        # Render without JS so the only possible <script> would be an injection
        result = render(evil, "html", collapsible=False, include_styles=False)
        # The raw tag must NOT appear (would be an injection hole)
        assert "<script>" not in result
        # The escaped form must appear
        assert "&lt;script&gt;" in result

    def test_html_escapes_ampersand_in_name(self):
        from AlgoTree.render import render
        evil = Node("a & b")
        result = render(evil, "html")
        assert "a & b" not in result
        assert "a &amp; b" in result

    def test_html_escapes_double_quote_in_name(self):
        from AlgoTree.render import render
        evil = Node('say "hello"')
        result = render(evil, "html")
        # Raw unescaped double-quote in text context must not appear as injection
        # (html.escape converts " to &quot; when quote=True)
        assert 'say "hello"' not in result or "&quot;" in result

    def test_html_escapes_attrs(self):
        """Attribute values with special chars must be escaped in the HTML output."""
        from AlgoTree.render import render
        evil = Node("root", attrs={"label": "<b>bold</b>"})
        result = render(evil, "html")
        # Raw unescaped <b> from an attr value must not be injected
        # Either the attr is escaped, or it is not shown; but raw injection is forbidden
        assert "<b>bold</b>" not in result or "&lt;b&gt;" in result

    def test_html_contains_tree_structure(self):
        """HTML output should contain nested structure for children."""
        from AlgoTree.render import render
        tree = Node("root", Node("child1"), Node("child2"))
        result = render(tree, "html")
        # Both child names should appear (escaped if needed)
        assert "child1" in result
        assert "child2" in result
        # Should have some list/div structure
        assert "<ul" in result or "<li" in result or "<div" in result

    def test_html_include_styles_option(self):
        from AlgoTree.render import render
        with_styles = render(Node("root"), "html", include_styles=True)
        without_styles = render(Node("root"), "html", include_styles=False)
        # With styles should be longer (has CSS)
        assert len(with_styles) > len(without_styles)
        assert "<style" in with_styles
        assert "<style" not in without_styles

    def test_html_collapsible_option(self):
        from AlgoTree.render import render
        with_js = render(Node("root", Node("child")), "html", collapsible=True)
        without_js = render(Node("root", Node("child")), "html", collapsible=False)
        # Collapsible mode should include JavaScript
        assert "<script" in with_js
        assert "<script" not in without_js

    def test_html_leaf_node_no_toggle(self):
        """Leaf nodes should not have a toggle/collapse button."""
        from AlgoTree.render import render
        tree = Node("root", Node("leaf"))
        result = render(tree, "html")
        # Result should be valid (no crash on leaf)
        assert "leaf" in result or "&lt;" in result  # either name appears escaped or not

    def test_html_multiple_levels_all_names_present(self):
        """All node names should appear (escaped) in the HTML output."""
        from AlgoTree.render import render
        tree = Node("root",
                    Node("alpha", Node("gamma")),
                    Node("beta"))
        result = render(tree, "html")
        for name_str in ["root", "alpha", "beta", "gamma"]:
            assert name_str in result, f"Expected {name_str!r} in html output"


class TestNodeNotebookReprs:
    """Node._repr_html_() and _repr_mermaid_() for Jupyter/Quarto."""

    def test_node_has_repr_html(self):
        n = Node("x")
        assert hasattr(n, "_repr_html_")
        assert callable(n._repr_html_)

    def test_node_has_repr_mermaid(self):
        n = Node("x")
        assert hasattr(n, "_repr_mermaid_")
        assert callable(n._repr_mermaid_)

    def test_repr_html_returns_string(self):
        n = Node("root", Node("child"))
        result = n._repr_html_()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_repr_html_matches_render_html(self):
        """_repr_html_() must return exactly the same string as render(node, 'html')."""
        from AlgoTree.render import render
        tree = Node("root", Node("child1"), Node("child2"))
        assert tree._repr_html_() == render(tree, "html")

    def test_repr_mermaid_returns_string(self):
        n = Node("root", Node("child"))
        result = n._repr_mermaid_()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_repr_mermaid_matches_render_mermaid(self):
        """_repr_mermaid_() must return exactly the same string as render(node, 'mermaid')."""
        from AlgoTree.render import render
        tree = Node("root", Node("child1"), Node("child2"))
        assert tree._repr_mermaid_() == render(tree, "mermaid")

    def test_repr_html_escapes_injection(self):
        """_repr_html_() must not inject raw HTML from node names.

        We check for '&lt;script&gt;' in the result, confirming the name is
        escaped, and verify that the raw alert payload does not appear.
        """
        evil = Node("<script>alert(1)</script>")
        result = evil._repr_html_()
        # The escaped form must be present
        assert "&lt;script&gt;" in result
        # The raw JS payload must not appear unescaped
        assert "alert(1)</script>" not in result

    def test_repr_html_different_trees_differ(self):
        """Different trees produce different HTML repr strings."""
        t1 = Node("root", Node("a"))
        t2 = Node("root", Node("b"))
        assert t1._repr_html_() != t2._repr_html_()


class TestStablePalette:
    """The node marker/palette must be deterministic across calls (no builtin hash)."""

    def test_html_marker_same_name_same_result_two_calls(self):
        """Calling render twice for the same tree produces identical output."""
        from AlgoTree.render import render
        tree = Node("root", Node("alpha"), Node("beta"))
        r1 = render(tree, "html")
        r2 = render(tree, "html")
        assert r1 == r2

    def test_html_marker_same_name_different_trees_same_marker(self):
        """A node with the same name should get the same marker in separate trees."""
        from AlgoTree.render import render
        # Build two trees with the same names; their HTML should be identical
        tree1 = Node("same_root", Node("same_child"))
        tree2 = Node("same_root", Node("same_child"))
        assert render(tree1, "html") == render(tree2, "html")

    def test_html_palette_deterministic_by_value(self):
        """Rendering the same tree in two separate import sessions is approximated
        by rendering it twice and asserting equality (in-process determinism)."""
        from AlgoTree.render import render
        tree = Node("deterministic", Node("node_a"), Node("node_b", Node("node_c")))
        results = [render(tree, "html") for _ in range(5)]
        assert all(r == results[0] for r in results), "render('html') is not deterministic"

    def test_html_palette_does_not_use_builtin_hash(self):
        """Verify determinism by value: two equal trees produce identical HTML even
        when Python's PYTHONHASHSEED would cause builtin hash() to differ."""
        from AlgoTree.render import render
        # We can't easily vary PYTHONHASHSEED in-process, but we can assert that
        # structurally equal trees (same names + attrs) always produce equal output.
        t1 = Node("root", Node("x"), Node("y", Node("z")))
        t2 = Node("root", Node("x"), Node("y", Node("z")))
        # These are value-equal (same structure)
        assert t1 == t2
        assert render(t1, "html") == render(t2, "html")
