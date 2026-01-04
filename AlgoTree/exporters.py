"""
Tree export functionality for various formats.

This module provides exporters to convert trees to different representations
including GraphViz, Mermaid, ASCII/Unicode trees, and more.
"""

from typing import Any, Dict, Optional, Callable
import json
from .node import Node


class TreeExporter:
    """Base class for tree exporters."""

    @staticmethod
    def to_dict(node: Node) -> Dict[str, Any]:
        """Export tree to dictionary (already implemented in Node)."""
        return node.to_dict()

    @staticmethod
    def to_json(node: Node, indent: int = 2) -> str:
        """Export tree to JSON string."""
        return json.dumps(node.to_dict(), indent=indent)

    @staticmethod
    def to_ascii(node: Node, style: str = "ascii") -> str:
        """
        Export tree to ASCII/Unicode art.

        Args:
            node: Root node of tree
            style: "ascii" for ASCII characters, "unicode" for box drawing

        Returns:
            String representation of tree
        """
        if style == "unicode":
            chars = {
                "vertical": "│",
                "horizontal": "─",
                "branch": "├",
                "last": "└"
            }
        else:
            chars = {
                "vertical": "|",
                "horizontal": "-",
                "branch": "+",
                "last": "\\"
            }

        result = []

        def render(node: Node, prefix: str = "", is_last: bool = True, is_root: bool = False):
            # Current node
            if is_root:
                result.append(node.name)
            else:
                connector = chars["last"] if is_last else chars["branch"]
                result.append(f"{prefix}{connector}{chars['horizontal']} {node.name}")

            # Render children
            for i, child in enumerate(node.children):
                is_last_child = i == len(node.children) - 1

                # Update prefix for children
                if is_root:
                    child_prefix = ""
                else:
                    extension = "    " if is_last else f"{chars['vertical']}   "
                    child_prefix = prefix + extension

                render(child, child_prefix, is_last_child, False)

        render(node, is_root=True)
        return "\n".join(result)

    @staticmethod
    def to_unicode(node: Node) -> str:
        """Export tree to Unicode box drawing (alias for to_ascii with unicode style)."""
        return TreeExporter.to_ascii(node, style="unicode")

    @staticmethod
    def to_graphviz(node: Node,
                    name: str = "Tree",
                    node_attr: Optional[Callable[[Node], Dict[str, str]]] = None,
                    edge_attr: Optional[Callable[[Node, Node], Dict[str, str]]] = None,
                    graph_attr: Optional[Dict[str, str]] = None) -> str:
        """
        Export tree to GraphViz DOT format.

        Args:
            node: Root node of tree
            name: Graph name
            node_attr: Function to generate node attributes
            edge_attr: Function to generate edge attributes
            graph_attr: Graph-level attributes

        Returns:
            DOT format string

        Example:
            dot = TreeExporter.to_graphviz(tree,
                node_attr=lambda n: {"label": f"{n.name}\\n{n.get('size', '')}"})
        """
        lines = [f"digraph {name} {{"]

        # Add graph attributes
        if graph_attr:
            for key, value in graph_attr.items():
                lines.append(f"    {key}={value};")

        # Track node IDs
        node_ids = {}
        next_id = [0]

        def get_node_id(n: Node) -> str:
            if n not in node_ids:
                node_ids[n] = f"node{next_id[0]}"
                next_id[0] += 1
            return node_ids[n]

        # Generate nodes and edges
        def process_node(n: Node):
            node_id = get_node_id(n)

            # Node declaration
            attrs = {}
            attrs["label"] = f'"{n.name}"'

            # Add custom attributes
            if node_attr:
                custom = node_attr(n)
                for key, value in custom.items():
                    if key == "label":
                        attrs[key] = f'"{value}"'
                    else:
                        attrs[key] = value

            attr_str = ", ".join(f"{k}={v}" for k, v in attrs.items())
            lines.append(f"    {node_id} [{attr_str}];")

            # Edges to children
            for child in n.children:
                child_id = get_node_id(child)
                edge_attrs = ""

                if edge_attr:
                    custom = edge_attr(n, child)
                    if custom:
                        edge_attrs = " [" + ", ".join(f"{k}={v}" for k, v in custom.items()) + "]"

                lines.append(f"    {node_id} -> {child_id}{edge_attrs};")
                process_node(child)

        process_node(node)
        lines.append("}")

        return "\n".join(lines)

    @staticmethod
    def to_mermaid(node: Node,
                   direction: str = "TD",
                   node_shape: str = "round",
                   node_text: Optional[Callable[[Node], str]] = None) -> str:
        """
        Export tree to Mermaid diagram format.

        Args:
            node: Root node of tree
            direction: Graph direction (TD, TB, BT, RL, LR)
            node_shape: Shape style ("round", "square", "circle", "rhombus", "stadium")
            node_text: Function to generate node text

        Returns:
            Mermaid format string

        Example:
            mermaid = TreeExporter.to_mermaid(tree,
                node_text=lambda n: f"{n.name}<br/>{n.get('type', '')}")
        """
        lines = [f"graph {direction}"]

        # Shape delimiters
        shapes = {
            "round": ("(", ")"),
            "square": ("[", "]"),
            "circle": ("((", "))"),
            "rhombus": ("{", "}"),
            "stadium": ("([", "])")
        }
        left, right = shapes.get(node_shape, shapes["round"])

        # Track node IDs
        node_ids = {}
        next_id = [0]

        def get_node_id(n: Node) -> str:
            if n not in node_ids:
                # Mermaid IDs must be alphanumeric
                node_ids[n] = f"N{next_id[0]}"
                next_id[0] += 1
            return node_ids[n]

        def escape_mermaid(text: str) -> str:
            """Escape special characters for Mermaid."""
            # Replace problematic characters
            text = text.replace('"', "'")
            text = text.replace("<", "&lt;")
            text = text.replace(">", "&gt;")
            return text

        def process_node(n: Node, parent_id: Optional[str] = None):
            node_id = get_node_id(n)

            # Node text
            if node_text:
                text = node_text(n)
            else:
                text = n.name
            text = escape_mermaid(text)

            # Node declaration
            lines.append(f"    {node_id}{left}{text}{right}")

            # Edge from parent
            if parent_id:
                lines.append(f"    {parent_id} --> {node_id}")

            # Process children
            for child in n.children:
                process_node(child, node_id)

        process_node(node)

        return "\n".join(lines)

    @staticmethod
    def to_yaml(node: Node, indent: int = 2) -> str:
        """
        Export tree to YAML-like indented format.

        Args:
            node: Root node of tree
            indent: Number of spaces per level

        Returns:
            YAML-like string representation
        """
        lines = []

        def render(n: Node, level: int = 0):
            prefix = " " * (level * indent)

            # Node name
            lines.append(f"{prefix}- name: {n.name}")

            # Attributes
            if n._attrs:
                for key, value in n._attrs.items():
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    lines.append(f"{prefix}  {key}: {value}")

            # Children
            if n.children:
                lines.append(f"{prefix}  children:")
                for child in n.children:
                    render(child, level + 2)

        render(node)
        return "\n".join(lines)

    @staticmethod
    def to_xml(node: Node, root_tag: str = "tree", indent: int = 2) -> str:
        """
        Export tree to XML format.

        Args:
            node: Root node of tree
            root_tag: Tag name for root element
            indent: Number of spaces per level

        Returns:
            XML string representation
        """
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']

        def escape_xml(text: str) -> str:
            """Escape special XML characters."""
            text = str(text)
            text = text.replace("&", "&amp;")
            text = text.replace("<", "&lt;")
            text = text.replace(">", "&gt;")
            text = text.replace('"', "&quot;")
            text = text.replace("'", "&apos;")
            return text

        def render(n: Node, level: int = 0):
            prefix = " " * (level * indent)

            # Open tag with name attribute
            attrs = [f'name="{escape_xml(n.name)}"']

            # Add attrs as attributes (simple values only)
            for key, value in n._attrs.items():
                if not isinstance(value, (dict, list)):
                    attrs.append(f'{key}="{escape_xml(value)}"')

            attr_str = " ".join(attrs)

            if n.children:
                lines.append(f"{prefix}<node {attr_str}>")

                # Add complex attrs as nested elements
                for key, value in n._attrs.items():
                    if isinstance(value, (dict, list)):
                        lines.append(f"{prefix}  <{key}>{escape_xml(json.dumps(value))}</{key}>")

                # Add children
                for child in n.children:
                    render(child, level + 1)

                lines.append(f"{prefix}</node>")
            else:
                # Self-closing tag for leaves
                lines.append(f"{prefix}<node {attr_str} />")

        lines.append(f"<{root_tag}>")
        render(node, 1)
        lines.append(f"</{root_tag}>")

        return "\n".join(lines)

    @staticmethod
    def to_html(node: Node,
                include_styles: bool = True,
                collapsible: bool = True) -> str:
        """
        Export tree to interactive HTML.

        Args:
            node: Root node of tree
            include_styles: Include CSS styles
            collapsible: Make tree nodes collapsible

        Returns:
            HTML string representation
        """
        html_parts = []

        if include_styles:
            html_parts.append("""
<style>
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

        html_parts.append('<div class="tree">')

        def render(n: Node) -> str:
            parts = []

            # Node content
            node_class = "node"
            toggle = ""
            if collapsible and n.children:
                toggle = '<span class="toggle">▼</span>'

            attrs_str = ""
            if n._attrs:
                items = [f"{k}: {v}" for k, v in n._attrs.items()
                         if not isinstance(v, (dict, list))]
                if items:
                    attrs_str = f'<span class="attrs">{", ".join(items)}</span>'

            parts.append(f'<li><div class="{node_class}">{toggle}{n.name}{attrs_str}</div>')

            # Children
            if n.children:
                parts.append('<ul>')
                for child in n.children:
                    parts.append(render(child))
                parts.append('</ul>')

            parts.append('</li>')

            return "".join(parts)

        html_parts.append('<ul>')
        html_parts.append(render(node))
        html_parts.append('</ul>')
        html_parts.append('</div>')

        if collapsible:
            html_parts.append("""
<script>
document.querySelectorAll('.tree .node').forEach(node => {
    if (node.querySelector('.toggle')) {
        node.addEventListener('click', function(e) {
            e.stopPropagation();
            const li = this.parentElement;
            li.classList.toggle('collapsed');
            const toggle = this.querySelector('.toggle');
            toggle.textContent = li.classList.contains('collapsed') ? '▶' : '▼';
        });
    }
});
</script>
""")

        return "".join(html_parts)

    @staticmethod
    def to_flat(node: Node, indent: int = 2) -> str:
        """
        Export tree to flat/graph format.

        Creates a flat dictionary where each node is a key mapping to a dict with:
        - .name: node name (hidden metadata)
        - .children: list of child node names (hidden metadata)
        - .color: color attribute if present (hidden metadata)
        - other attributes as regular key-value pairs

        The dot-prefix indicates hidden metadata (like Unix hidden files).

        Args:
            node: Root node of tree
            indent: JSON indentation level

        Returns:
            JSON string of flat representation
        """
        flat_dict = {}

        def flatten(n: Node, path_prefix: str = ""):
            # Generate unique key (use path to handle duplicate names)
            if path_prefix:
                key = f"{path_prefix}/{n.name}"
            else:
                key = n.name

            # Build node entry with dot-prefix for metadata
            node_entry = {
                ".name": n.name,
                ".children": [child.name for child in n.children]
            }

            # Add color if present in attrs
            if '.color' in n.attrs:
                node_entry[".color"] = n.attrs['.color']

            # Add all other attributes (skip dot-prefixed ones)
            for k, v in n.attrs.items():
                if not k.startswith('.'):
                    node_entry[k] = v

            flat_dict[key] = node_entry

            # Recursively flatten children
            for child in n.children:
                flatten(child, key)

        flatten(node)
        return json.dumps(flat_dict, indent=indent)


# Convenience functions
def export_tree(node: Node, format: str, **kwargs) -> str:
    """
    Export tree to specified format.

    Args:
        node: Root node of tree
        format: Export format (json, ascii, unicode, graphviz, mermaid, yaml, xml, html)
        **kwargs: Format-specific options

    Returns:
        String representation in specified format
    """
    exporters = {
        'json': TreeExporter.to_json,
        'flat': TreeExporter.to_flat,
        'graph': TreeExporter.to_flat,  # Alias
        'ascii': TreeExporter.to_ascii,
        'unicode': TreeExporter.to_unicode,
        'graphviz': TreeExporter.to_graphviz,
        'dot': TreeExporter.to_graphviz,  # Alias
        'mermaid': TreeExporter.to_mermaid,
        'yaml': TreeExporter.to_yaml,
        'xml': TreeExporter.to_xml,
        'html': TreeExporter.to_html,
    }

    exporter = exporters.get(format)
    if not exporter:
        raise ValueError(f"Unknown export format: {format}")

    return exporter(node, **kwargs)


def save_tree(node: Node, filepath: str, format: Optional[str] = None, **kwargs):
    """
    Save tree to file in specified format.

    Args:
        node: Root node of tree
        filepath: Output file path
        format: Export format (auto-detected from extension if not specified)
        **kwargs: Format-specific options
    """
    if format is None:
        # Auto-detect from file extension
        import os
        ext = os.path.splitext(filepath)[1].lower()
        format_map = {
            '.json': 'json',
            '.dot': 'graphviz',
            '.gv': 'graphviz',
            '.mmd': 'mermaid',
            '.mermaid': 'mermaid',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.html': 'html',
            '.txt': 'ascii',
        }
        format = format_map.get(ext, 'ascii')

    content = export_tree(node, format, **kwargs)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
