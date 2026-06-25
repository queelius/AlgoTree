"""
Render engine for AlgoTree: Theme, backend registry, dispatch, and the
fold-based text-tree renderer (ascii + unicode).

Usage::

    from AlgoTree.render import render, register, Theme
    print(render(node, "unicode"))
    print(render(node, "ascii"))

The text-tree backend is implemented as a catamorphism (fold) over the
tree that returns a function of *inherited* context (prefix, is_last,
is_root) — the classic "synthesized vs. inherited attributes" technique,
which avoids any mutable state while still threading parent-context
downward.

Structural backends (mermaid, graphviz/dot) use pre-order node counters
for stable IDs and route all node text through their respective escapers.
"""

from typing import Any, Callable, Dict, List, NamedTuple, Optional

from .node import Node


# ---------------------------------------------------------------------------
# Theme – charset + escaper for a render target
# ---------------------------------------------------------------------------

class Theme(NamedTuple):
    """Characters and escaper for one text-tree style."""
    vertical: str    # continuation line from a parent (│ or |)
    horizontal: str  # horizontal connector (─ or -)
    branch: str      # non-last child connector (├ or +)
    last: str        # last-child connector (└ or \\)
    escape: Callable[[str], str]  # text → safe text for the target


IDENTITY_ESCAPE: Callable[[str], str] = lambda s: s

ASCII_THEME = Theme("|", "-", "+", "\\", IDENTITY_ESCAPE)
UNICODE_THEME = Theme("│", "─", "├", "└", IDENTITY_ESCAPE)


# ---------------------------------------------------------------------------
# Backend registry
# ---------------------------------------------------------------------------

class _Backend(NamedTuple):
    render: Callable[..., str]
    ext: str


_REGISTRY: Dict[str, _Backend] = {}


def register(fmt: str, render_fn: Callable[..., str], ext: str) -> None:
    """Register a new render backend under *fmt*."""
    _REGISTRY[fmt] = _Backend(render_fn, ext)


def render(node: Node, fmt: str = "unicode", **opts: Any) -> str:
    """
    Dispatch *node* to the backend registered under *fmt*.

    Raises ValueError for unknown formats.
    """
    backend = _REGISTRY.get(fmt)
    if backend is None:
        raise ValueError(
            f"unknown render format: {fmt!r} (have {sorted(_REGISTRY)})"
        )
    return backend.render(node, **opts)


def extension_for(fmt: str) -> str:
    """Return the file extension for *fmt*, defaulting to '.txt'."""
    b = _REGISTRY.get(fmt)
    return b.ext if b else ".txt"


# ---------------------------------------------------------------------------
# Text-tree fold (synthesized + inherited attributes)
# ---------------------------------------------------------------------------
# Each node folds to a function  emit(prefix, is_last, is_root) -> List[str].
# The root call invokes emit("", True, True); child calls pass down the
# extended prefix and their own is_last flag.

def _text_tree(node: Node, theme: Theme) -> str:
    """Render *node* as a text tree using *theme*."""

    def alg(
        n: Node,
        child_fns: List[Callable[[str, bool, bool], List[str]]],
    ) -> Callable[[str, bool, bool], List[str]]:
        def emit(prefix: str, is_last: bool, is_root: bool) -> List[str]:
            if is_root:
                lines: List[str] = [theme.escape(n.name)]
            else:
                connector = theme.last if is_last else theme.branch
                lines = [f"{prefix}{connector}{theme.horizontal} {theme.escape(n.name)}"]

            for i, cf in enumerate(child_fns):
                last = i == len(child_fns) - 1
                if is_root:
                    child_prefix = ""
                else:
                    ext = "    " if is_last else f"{theme.vertical}   "
                    child_prefix = prefix + ext
                lines.extend(cf(child_prefix, last, False))

            return lines

        return emit

    return "\n".join(node.fold(alg)("", True, True))


# ---------------------------------------------------------------------------
# Register built-in backends
# ---------------------------------------------------------------------------

register("ascii",   lambda node, **o: _text_tree(node, ASCII_THEME),   ".txt")
register("unicode", lambda node, **o: _text_tree(node, UNICODE_THEME), ".txt")


# ---------------------------------------------------------------------------
# Escapers for structured formats
# ---------------------------------------------------------------------------

def _mermaid_escape(text: str) -> str:
    """Escape text for safe embedding inside a Mermaid node label."""
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "'")   # double-quote -> single (Mermaid convention)
    return text


def _dot_escape(text: str) -> str:
    """Escape text for safe embedding inside a DOT label string."""
    text = str(text)
    text = text.replace("\\", "\\\\")  # backslash first
    text = text.replace('"', '\\"')    # then double-quote
    text = text.replace("\n", "\\n")
    return text


# ---------------------------------------------------------------------------
# Mermaid backend
# ---------------------------------------------------------------------------

def _to_mermaid(
    node: Node,
    direction: str = "TD",
    node_shape: str = "round",
    **_opts: Any,
) -> str:
    """Render *node* as a Mermaid graph diagram."""
    shapes = {
        "round":   ("(", ")"),
        "square":  ("[", "]"),
        "circle":  ("((", "))"),
        "rhombus": ("{", "}"),
        "stadium": ("([", "])"),
    }
    left, right = shapes.get(node_shape, shapes["round"])

    lines: List[str] = [f"graph {direction}"]

    # Pre-order traversal to assign stable IDs and emit declarations + edges.
    counter = [0]

    def _visit(n: Node, parent_id: Optional[str]) -> None:
        node_id = f"N{counter[0]}"
        counter[0] += 1

        label = _mermaid_escape(n.name)
        lines.append(f"    {node_id}{left}{label}{right}")

        if parent_id is not None:
            lines.append(f"    {parent_id} --> {node_id}")

        for child in n.children:
            _visit(child, node_id)

    _visit(node, None)
    return "\n".join(lines)


register("mermaid", _to_mermaid, ".mmd")


# ---------------------------------------------------------------------------
# GraphViz / DOT backend
# ---------------------------------------------------------------------------

def _to_graphviz(
    node: Node,
    name: str = "Tree",
    **_opts: Any,
) -> str:
    """Render *node* as a GraphViz DOT digraph."""
    lines: List[str] = [f"digraph {name} {{"]

    # Pre-order traversal to assign stable IDs and emit nodes + edges.
    counter = [0]

    def _visit(n: Node, parent_id: Optional[str]) -> None:
        node_id = f"N{counter[0]}"
        counter[0] += 1

        label = _dot_escape(n.name)
        lines.append(f'    {node_id} [label="{label}"];')

        if parent_id is not None:
            lines.append(f"    {parent_id} -> {node_id};")

        for child in n.children:
            _visit(child, node_id)

    _visit(node, None)
    lines.append("}")
    return "\n".join(lines)


register("graphviz", _to_graphviz, ".dot")
register("dot",      _to_graphviz, ".dot")  # alias
