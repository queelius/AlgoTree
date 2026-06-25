"""
Tree export functionality - thin delegates to the render registry.

All rendering is now performed by :mod:`AlgoTree.render`.  This module
exists for backwards compatibility: the public names ``TreeExporter``,
``export_tree``, and ``save_tree`` continue to work unchanged.

The ``flat`` / ``graph`` formats are special cases that produce a
path-keyed flat dictionary via :mod:`AlgoTree.interop`; they are NOT
registered in the render backend (they don't produce text output).
"""

from typing import Any, Dict, Optional, Callable
import json
import os
from .node import Node
from . import render as _render


class TreeExporter:
    """Tree exporter - thin delegates to the render registry."""

    @staticmethod
    def to_dict(node: Node) -> Dict[str, Any]:
        """Export tree to dictionary (already implemented in Node)."""
        return node.to_dict()

    @staticmethod
    def to_json(node: Node, indent: int = 2) -> str:
        """Export tree to JSON string."""
        return _render.render(node, "json", indent=indent)

    @staticmethod
    def to_ascii(node: Node, style: str = "ascii") -> str:
        """
        Export tree to ASCII/Unicode art.

        Args:
            node: Root node of tree
            style: ``"ascii"`` for ASCII characters, ``"unicode"`` for box drawing.

        Returns:
            String representation of tree.
        """
        fmt = "unicode" if style == "unicode" else "ascii"
        return _render.render(node, fmt)

    @staticmethod
    def to_unicode(node: Node) -> str:
        """Export tree to Unicode box drawing (alias for to_ascii with unicode style)."""
        return _render.render(node, "unicode")

    @staticmethod
    def to_graphviz(
        node: Node,
        name: str = "Tree",
        node_attr: Optional[Callable[[Node], Dict[str, str]]] = None,
        edge_attr: Optional[Callable[[Node, Node], Dict[str, str]]] = None,
        graph_attr: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Export tree to GraphViz DOT format.

        The base output is produced by ``render(node, 'graphviz', name=name)``.
        Optional *node_attr*, *edge_attr*, and *graph_attr* callbacks extend it
        with additional DOT attributes (kept for backwards compatibility).

        For the common case (no callbacks), output is identical to
        ``render(node, 'graphviz', name=name)``.
        """
        if node_attr is None and edge_attr is None and graph_attr is None:
            return _render.render(node, "graphviz", name=name)

        # Legacy path: callbacks requested – build DOT with extra attributes.
        from ._utils import make_predicate as _mp  # noqa: F401 (import guard only)
        from . import render as _r
        from .render import _dot_escape

        lines = [f'digraph "{_dot_escape(name)}" {{']

        if graph_attr:
            for key, value in graph_attr.items():
                lines.append(f"    {key}={value};")

        counter = [0]

        def _visit(n: Node, parent_id: Optional[str]) -> None:
            node_id = f"N{counter[0]}"
            counter[0] += 1

            label = _dot_escape(n.name)
            attrs: Dict[str, str] = {f'label': f'"{label}"'}

            if node_attr:
                custom = node_attr(n)
                for k, v in custom.items():
                    if k == "label":
                        attrs[k] = f'"{v}"'
                    else:
                        attrs[k] = str(v)

            attr_str = ", ".join(f"{k}={v}" for k, v in attrs.items())
            lines.append(f"    {node_id} [{attr_str}];")

            if parent_id is not None:
                edge_extra = ""
                if edge_attr:
                    custom = edge_attr(
                        next(
                            nd
                            for nd in node.walk()
                            if nd.name == n.name
                            or id(nd) == id(n)
                        ),
                        n,
                    )
                    if custom:
                        edge_extra = " [" + ", ".join(
                            f"{k}={v}" for k, v in custom.items()
                        ) + "]"
                lines.append(f"    {parent_id} -> {node_id}{edge_extra};")

            for child in n.children:
                _visit(child, node_id)

        _visit(node, None)
        lines.append("}")
        return "\n".join(lines)

    @staticmethod
    def to_mermaid(
        node: Node,
        direction: str = "TD",
        node_shape: str = "round",
        node_text: Optional[Callable[[Node], str]] = None,
    ) -> str:
        """
        Export tree to Mermaid diagram format.

        Delegates to ``render(node, 'mermaid', direction=direction)``.
        The *node_text* callback is a legacy option; when provided the output
        uses the quoted-label syntax with the custom text substituted.
        The *node_shape* option is accepted for API compatibility but the new
        backend always uses Mermaid's double-quoted label syntax ``N0["..."]``
        (which avoids mis-parsing of closing delimiters in node names).
        """
        if node_text is None:
            return _render.render(node, "mermaid", direction=direction, node_shape=node_shape)

        # Legacy path: custom node_text callback.
        from typing import List, Optional as Opt
        from .render import _mermaid_escape

        lines: List[str] = [f"graph {direction}"]
        counter = [0]

        def _visit(n: Node, parent_id: Opt[str]) -> None:
            node_id = f"N{counter[0]}"
            counter[0] += 1

            text = _mermaid_escape(node_text(n))
            lines.append(f'    {node_id}["{text}"]')

            if parent_id is not None:
                lines.append(f"    {parent_id} --> {node_id}")

            for child in n.children:
                _visit(child, node_id)

        _visit(node, None)
        return "\n".join(lines)

    @staticmethod
    def to_yaml(node: Node, indent: int = 2) -> str:
        """
        Export tree to YAML.

        Delegates to ``render(node, 'yaml')``, which uses PyYAML's
        ``safe_dump``.  Raises ``ImportError`` if PyYAML is not installed.

        Note: The *indent* parameter is accepted for API compatibility but
        PyYAML's ``safe_dump`` manages indentation internally.
        """
        return _render.render(node, "yaml")

    @staticmethod
    def to_xml(node: Node, root_tag: str = "tree", indent: int = 2) -> str:
        """
        Export tree to XML format.

        Delegates to ``render(node, 'xml', root_tag=root_tag)``.

        Note: The *indent* parameter is accepted for API compatibility; the
        actual indentation is controlled by the render backend (two spaces
        on Python 3.9+, compact on 3.8).
        """
        return _render.render(node, "xml", root_tag=root_tag)

    @staticmethod
    def to_html(
        node: Node,
        include_styles: bool = True,
        collapsible: bool = True,
    ) -> str:
        """Export tree to interactive HTML."""
        return _render.render(
            node, "html",
            include_styles=include_styles,
            collapsible=collapsible,
        )

    @staticmethod
    def to_flat(node: Node, indent: int = 2) -> str:
        """
        Export tree to flat/graph format (path-keyed JSON dictionary).

        This format is not in the render registry (it produces a structured
        dict, not a linear text layout).  Kept as a direct implementation.
        """
        flat_dict: Dict[str, Any] = {}

        def _flatten(n: Node, path_prefix: str = "") -> None:
            key = f"{path_prefix}/{n.name}" if path_prefix else n.name
            node_entry: Dict[str, Any] = {
                ".name": n.name,
                ".children": [child.name for child in n.children],
            }
            if ".color" in n.attrs:
                node_entry[".color"] = n.attrs[".color"]
            for k, v in n.attrs.items():
                if not k.startswith("."):
                    node_entry[k] = v
            flat_dict[key] = node_entry
            for child in n.children:
                _flatten(child, key)

        _flatten(node)
        return json.dumps(flat_dict, indent=indent)


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

def export_tree(node: Node, format: str, **kwargs) -> str:
    """
    Export tree to the specified format.

    Delegates to the render registry for all standard formats.
    ``"flat"`` / ``"graph"`` use :meth:`TreeExporter.to_flat`.

    Args:
        node: Root node of tree.
        format: One of ``json``, ``ascii``, ``unicode``, ``graphviz``,
            ``dot``, ``mermaid``, ``yaml``, ``xml``, ``html``, ``flat``,
            ``graph``.
        **kwargs: Format-specific options forwarded to the backend.

    Returns:
        String representation in the requested format.

    Raises:
        ValueError: For unknown format strings.
    """
    # flat / graph are not in the render registry
    if format in ("flat", "graph"):
        return TreeExporter.to_flat(node, **kwargs)

    # TreeExporter shim methods handle legacy kwargs (node_attr, node_text, …)
    # but for the simple cases we can go directly to render.
    _shim = {
        "json": TreeExporter.to_json,
        "ascii": TreeExporter.to_ascii,
        "unicode": TreeExporter.to_unicode,
        "graphviz": TreeExporter.to_graphviz,
        "dot": TreeExporter.to_graphviz,
        "mermaid": TreeExporter.to_mermaid,
        "yaml": TreeExporter.to_yaml,
        "xml": TreeExporter.to_xml,
        "html": TreeExporter.to_html,
    }
    shim_fn = _shim.get(format)
    if shim_fn is None:
        raise ValueError(f"Unknown export format: {format!r}")
    return shim_fn(node, **kwargs)


def save_tree(
    node: Node,
    filepath: str,
    format: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Save tree to file in the specified format.

    Args:
        node: Root node of tree.
        filepath: Output file path.
        format: Export format; auto-detected from file extension if not given.
        **kwargs: Format-specific options forwarded to the backend.
    """
    if format is None:
        ext = os.path.splitext(filepath)[1].lower()
        format_map = {
            ".json": "json",
            ".dot": "graphviz",
            ".gv": "graphviz",
            ".mmd": "mermaid",
            ".mermaid": "mermaid",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".xml": "xml",
            ".html": "html",
            ".txt": "ascii",
        }
        format = format_map.get(ext, "ascii")

    content = export_tree(node, format, **kwargs)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
