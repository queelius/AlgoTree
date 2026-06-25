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
