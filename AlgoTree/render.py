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
    """Escape text for safe embedding inside a Mermaid quoted-string label.

    Mermaid supports quoted labels of the form N0["..."], where the only
    character that needs escaping inside the double-quote delimiters is the
    double-quote itself.  Using this form avoids the closing-delimiter
    ambiguity that occurs with shape-based syntax (round/square/etc.): a
    node named 'end)', 'arr[0]', or 'f(x)' would otherwise produce malformed
    output such as 'N0(end))' or 'N0[arr[0]]'.
    """
    text = str(text)
    text = text.replace('"', "&quot;")   # only character that breaks the delimiter
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
    # node_shape is reserved for future styling; labels always use quoted ["..."] syntax.
    lines: List[str] = [f"graph {direction}"]

    # Pre-order traversal to assign stable IDs and emit declarations + edges.
    counter = [0]

    def _visit(n: Node, parent_id: Optional[str]) -> None:
        node_id = f"N{counter[0]}"
        counter[0] += 1

        label = _mermaid_escape(n.name)
        # Always use quoted-string syntax so closing delimiters inside the
        # label text cannot be mis-parsed as the end of the shape.
        # The node_shape option is retained for future use / styling but the
        # label delimiter is always a double-quoted string.
        lines.append(f'    {node_id}["{label}"]')

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
    lines: List[str] = [f'digraph "{_dot_escape(name)}" {{']

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


# ---------------------------------------------------------------------------
# JSON backend
# ---------------------------------------------------------------------------

def _to_json(node: Node, indent: int = 2, **_opts: Any) -> str:
    """Render *node* as a JSON string via node.to_dict()."""
    import json as _json
    return _json.dumps(node.to_dict(), indent=indent)


register("json", _to_json, ".json")


# ---------------------------------------------------------------------------
# YAML backend  (requires PyYAML; degrades gracefully if absent)
# ---------------------------------------------------------------------------

def _to_yaml(node: Node, **_opts: Any) -> str:
    """Render *node* as YAML via yaml.safe_dump(node.to_dict(), ...).

    Requires PyYAML.  Raises ImportError with an install hint if it is not
    available.  We deliberately do NOT hand-roll YAML: real YAML has too many
    edge cases (multi-line strings, special scalars, unicode) to emit correctly
    by string concatenation.
    """
    try:
        import yaml as _yaml  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "PyYAML is required for the 'yaml' render backend. "
            "Install it with:  pip install pyyaml"
        ) from exc
    return _yaml.safe_dump(node.to_dict(), sort_keys=False)


register("yaml", _to_yaml, ".yaml")


# ---------------------------------------------------------------------------
# XML backend  (stdlib xml.etree.ElementTree for building; never parses)
# ---------------------------------------------------------------------------

def _to_xml(node: Node, root_tag: str = "tree", **_opts: Any) -> str:
    """Render *node* as an XML document.

    Uses xml.etree.ElementTree to *construct* (not parse) the element tree,
    so there is no XXE or billion-laughs exposure.  Node names and attrs are
    set via the ElementTree API, which handles all necessary XML escaping.
    Numeric/bool attr values are coerced to str for use as XML attributes.
    Complex (dict/list) attrs are skipped as XML attributes and emitted as
    nested ``<{key}>...</{key}>`` child elements instead.
    """
    import json as _json
    import xml.etree.ElementTree as _ET
    import sys

    def _build(n: Node) -> _ET.Element:
        elem = _ET.Element("node")
        # node name as an XML attribute; ET handles escaping
        elem.set("name", n.name)
        # simple attrs → XML attributes (str-coerced); complex → child elements
        complex_attrs = {}
        for k, v in n._attrs.items():
            if isinstance(v, (dict, list)):
                complex_attrs[k] = v
            else:
                elem.set(k, str(v))
        # complex attrs as nested text elements
        # XML element tag names must be valid XML Names: sanitize the key.
        import re as _re
        for k, v in complex_attrs.items():
            safe_k = _re.sub(r"[^\w.-]", "_", k)
            if safe_k[:1].isdigit():
                safe_k = "_" + safe_k
            child_elem = _ET.SubElement(elem, safe_k)
            child_elem.text = _json.dumps(v)
        # children
        for child in n.children:
            elem.append(_build(child))
        return elem

    root_elem = _ET.Element(root_tag)
    root_elem.append(_build(node))

    # Pretty-print: ElementTree.indent() was added in Python 3.9.
    if sys.version_info >= (3, 9):
        _ET.indent(root_elem, space="  ")

    return _ET.tostring(root_elem, encoding="unicode")


register("xml", _to_xml, ".xml")


# ---------------------------------------------------------------------------
# HTML backend  (escaped; deterministic palette via zlib.crc32)
# ---------------------------------------------------------------------------

# Marker palette for node icons.  We use zlib.crc32(name.encode()) — which is
# fully deterministic across Python versions and PYTHONHASHSEED values — to
# pick a marker from a fixed list, so the same name always gets the same icon.
_MARKERS = [
    "&#x25CF;",  # ● BLACK CIRCLE
    "&#x25A0;",  # ■ BLACK SQUARE
    "&#x25B2;",  # ▲ BLACK UP-POINTING TRIANGLE
    "&#x25C6;",  # ◆ BLACK DIAMOND
    "&#x2605;",  # ★ BLACK STAR
    "&#x25D7;",  # ◗ RIGHT HALF BLACK CIRCLE
    "&#x29BF;",  # ⦿ CIRCLED BULLET
    "&#x2756;",  # ❖ BLACK DIAMOND MINUS WHITE X
]


def _stable_marker(name: str) -> str:
    """Return a deterministic marker for *name* (zlib.crc32, not builtin hash)."""
    import zlib as _zlib
    idx = _zlib.crc32(name.encode("utf-8")) % len(_MARKERS)
    return _MARKERS[idx]


def _html_escape(text: str) -> str:
    """Escape *text* for safe embedding in HTML (text nodes and attribute values)."""
    import html as _html
    return _html.escape(str(text), quote=True)


def _to_html(
    node: "Node",
    include_styles: bool = True,
    collapsible: bool = True,
    **_opts: Any,
) -> str:
    """Render *node* as an interactive HTML tree.

    All node names and attribute values are routed through :func:`_html_escape`
    (stdlib ``html.escape``), closing the HTML-injection hole present in the
    old hand-rolled exporter.  The marker palette is keyed by
    ``zlib.crc32(name.encode())`` — deterministic across runs and
    PYTHONHASHSEED values, unlike Python's builtin ``hash()``.
    """
    parts: List[str] = []

    if include_styles:
        parts.append("""<style>
    .tree { font-family: monospace; }
    .tree ul { list-style-type: none; position: relative; padding-left: 20px; }
    .tree li { position: relative; padding: 5px 0; }
    .tree li::before {
        content: ''; position: absolute; top: 0; left: -15px;
        width: 10px; height: 50%; border-left: 1px solid #ccc;
        border-bottom: 1px solid #ccc;
    }
    .tree li::after {
        content: ''; position: absolute; left: -15px; bottom: 50%;
        width: 10px; height: 50%; border-left: 1px solid #ccc;
    }
    .tree li:last-child::after { display: none; }
    .tree .node {
        display: inline-block; padding: 3px 8px;
        border: 1px solid #ddd; border-radius: 3px;
        background: #f5f5f5; cursor: pointer;
    }
    .tree .attrs {
        font-size: 0.9em; color: #666;
        margin-left: 10px; font-style: italic;
    }
    .collapsed > ul { display: none; }
    .tree .toggle { margin-right: 5px; }
</style>
""")

    parts.append('<div class="tree">')

    def _render_node(n: "Node") -> str:
        node_parts: List[str] = []

        # Toggle arrow (only for non-leaf nodes in collapsible mode)
        toggle = ""
        if collapsible and n.children:
            toggle = '<span class="toggle">&#x25BC;</span>'  # ▼

        # Safe name (HTML-escaped)
        safe_name = _html_escape(n.name)

        # Marker from stable palette
        marker = _stable_marker(n.name)

        # Safe attribute display (HTML-escaped)
        attrs_str = ""
        if n._attrs:
            items = []
            for k, v in n._attrs.items():
                if not isinstance(v, (dict, list)):
                    items.append(f"{_html_escape(str(k))}: {_html_escape(str(v))}")
            if items:
                attrs_str = (
                    '<span class="attrs">'
                    + ", ".join(items)
                    + "</span>"
                )

        node_parts.append(
            f'<li><div class="node">'
            f'{toggle}{marker} {safe_name}'
            f"{attrs_str}"
            f"</div>"
        )

        if n.children:
            node_parts.append("<ul>")
            for child in n.children:
                node_parts.append(_render_node(child))
            node_parts.append("</ul>")

        node_parts.append("</li>")
        return "".join(node_parts)

    parts.append("<ul>")
    parts.append(_render_node(node))
    parts.append("</ul>")
    parts.append("</div>")

    if collapsible:
        parts.append("""<script>
document.querySelectorAll('.tree .node').forEach(node => {
    if (node.querySelector('.toggle')) {
        node.addEventListener('click', function(e) {
            e.stopPropagation();
            const li = this.parentElement;
            li.classList.toggle('collapsed');
            const toggle = this.querySelector('.toggle');
            toggle.textContent = li.classList.contains('collapsed') ? '\\u25B6' : '\\u25BC';
        });
    }
});
</script>
""")

    return "".join(parts)


register("html", _to_html, ".html")
