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
