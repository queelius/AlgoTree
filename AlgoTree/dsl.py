"""
DSL (Domain Specific Language) for tree definition.

Supports multiple formats:
- Visual tree format (with Unicode box characters)
- Indent-based format (YAML-like)
- S-expression format
"""
import re
from typing import List, Tuple, Dict, Any
from .node import Node


class TreeDSL:
    """Parser for various tree DSL formats."""

    @staticmethod
    def parse(text: str, format: str = 'auto') -> Node:
        """
        Parse tree from DSL text.

        Args:
            text: DSL text to parse.
            format: Format to use ('visual', 'indent', 'sexpr', 'auto').
                   'auto' tries to detect format automatically.

        Returns:
            Root node of parsed tree.
        """
        text = text.strip()

        if format == 'auto':
            format = TreeDSL._detect_format(text)

        if format == 'visual':
            return TreeDSL._parse_visual(text)
        elif format == 'indent':
            return TreeDSL._parse_indent(text)
        elif format == 'sexpr':
            return TreeDSL._parse_sexpr(text)
        else:
            raise ValueError(f"Unknown format: {format}")

    @staticmethod
    def _detect_format(text: str) -> str:
        """Detect DSL format from text."""
        # Check for visual format (tree characters)
        if any(char in text for char in ['├', '└', '│', '─']):
            return 'visual'
        # Check for S-expression format
        elif text.startswith('(') and text.endswith(')'):
            return 'sexpr'
        # Default to indent format
        else:
            return 'indent'

    @staticmethod
    def _parse_visual(text: str) -> Node:
        """
        Parse visual tree format.

        Example:
            company[type:tech]
            ├── engineering[head:Alice]
            │   ├── frontend[size:5]
            │   └── backend[size:8]
            └── sales[head:Bob]
        """
        lines = text.split('\n')
        if not lines:
            raise ValueError("Empty tree")

        # Parse all lines to get (indent, name, attrs)
        parsed_lines = []
        for line in lines:
            if not line.strip():
                continue

            # Remove tree drawing characters and count indent
            cleaned = line.replace('│', ' ').replace('├', ' ').replace('└', ' ').replace('─', ' ')
            indent = len(cleaned) - len(cleaned.lstrip())
            clean_text = cleaned.strip()

            # Parse node
            name, attrs = TreeDSL._parse_node_spec(clean_text)
            parsed_lines.append((indent, name, attrs))

        if not parsed_lines:
            raise ValueError("Empty tree")

        # Build tree using a stack-based approach (same as indent parser)
        def build_tree(lines, start_idx, parent_indent):
            """Recursively build tree from lines starting at start_idx."""
            if start_idx >= len(lines):
                return None, start_idx

            indent, name, attrs = lines[start_idx]

            # Collect all children (nodes with greater indent until we hit same/lower indent)
            children = []
            idx = start_idx + 1

            while idx < len(lines):
                child_indent = lines[idx][0]

                if child_indent <= indent:
                    # Same or lower indent - not our child
                    break

                # This is a child - recursively build it
                child_node, idx = build_tree(lines, idx, indent)
                if child_node:
                    children.append(child_node)

            node = Node(name, *children, attrs=attrs)
            return node, idx

        root, _ = build_tree(parsed_lines, 0, -1)
        return root

    @staticmethod
    def _parse_indent(text: str) -> Node:
        """
        Parse indent-based format.

        Example:
            company: {type: tech, revenue: 1M}
              engineering: {head: Alice}
                frontend: {size: 5}
                backend: {size: 8}
              sales: {head: Bob}
        """
        lines = text.split('\n')
        if not lines:
            raise ValueError("Empty tree")

        # Parse all nodes with their indent levels
        parsed_lines = []
        for line in lines:
            if not line.strip():
                continue

            # Calculate indent
            indent = len(line) - len(line.lstrip())
            line_content = line.strip()

            # Parse node - check for bracket notation first (name[attrs])
            # then for colon notation (name: {attrs})
            if '[' in line_content and ']' in line_content:
                # Bracket notation: node[key:value]
                name, attrs = TreeDSL._parse_node_spec(line_content)
            elif ':' in line_content:
                # Colon notation: node: {key: value}
                name, rest = line_content.split(':', 1)
                name = name.strip()
                attrs = TreeDSL._parse_attrs(rest.strip())
            else:
                name = line_content
                attrs = {}

            parsed_lines.append((indent, name, attrs))

        if not parsed_lines:
            raise ValueError("Empty tree")

        # Build tree using a stack-based approach
        def build_tree(lines, start_idx, parent_indent):
            """Recursively build tree from lines starting at start_idx."""
            if start_idx >= len(lines):
                return None, start_idx

            indent, name, attrs = lines[start_idx]

            # Collect all children (nodes with greater indent until we hit same/lower indent)
            children = []
            idx = start_idx + 1

            while idx < len(lines):
                child_indent = lines[idx][0]

                if child_indent <= indent:
                    # Same or lower indent - not our child
                    break

                # This is a child - recursively build it
                child_node, idx = build_tree(lines, idx, indent)
                if child_node:
                    children.append(child_node)

            node = Node(name, *children, attrs=attrs)
            return node, idx

        root, _ = build_tree(parsed_lines, 0, -1)
        return root

    @staticmethod
    def _parse_sexpr(text: str) -> Node:
        """
        Parse S-expression format.

        Example:
            (company :type tech :revenue 1M
              (engineering :head Alice
                (frontend :size 5)
                (backend :size 8))
              (sales :head Bob))
        """
        tokens = TreeDSL._tokenize_sexpr(text)
        if not tokens:
            raise ValueError("Empty tree")

        def parse_node(tokens, index):
            if index >= len(tokens) or tokens[index] != '(':
                raise ValueError("Expected '(' at start of node")

            index += 1
            if index >= len(tokens):
                raise ValueError("Unexpected end of expression")

            # Get node name
            name = tokens[index]
            index += 1

            # Parse attributes
            attrs = {}
            while index < len(tokens) and tokens[index] not in ['(', ')']:
                if tokens[index].startswith(':'):
                    key = tokens[index][1:]
                    index += 1
                    if index < len(tokens) and tokens[index] not in ['(', ')', ':']:
                        attrs[key] = TreeDSL._parse_value(tokens[index])
                        index += 1
                else:
                    index += 1

            # Parse children
            children = []
            while index < len(tokens) and tokens[index] == '(':
                child, index = parse_node(tokens, index)
                children.append(child)

            # Create node with children
            node = Node(name, *children, attrs=attrs)

            if index >= len(tokens) or tokens[index] != ')':
                raise ValueError("Expected ')' at end of node")

            return node, index + 1

        root, _ = parse_node(tokens, 0)
        return root

    @staticmethod
    def _tokenize_sexpr(text: str) -> List[str]:
        """Tokenize S-expression."""
        # Add spaces around parentheses
        text = text.replace('(', ' ( ').replace(')', ' ) ')
        # Split and filter empty tokens
        return [token for token in text.split() if token]

    @staticmethod
    def _parse_node_spec(text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse node specification like 'name[attr1:val1,attr2:val2]'.

        Returns:
            Tuple of (name, attributes_dict)
        """
        # Check for attributes in brackets
        match = re.match(r'^([^[]+)(?:\[(.*)\])?$', text.strip())
        if not match:
            return text.strip(), {}

        name = match.group(1).strip()
        attrs_str = match.group(2)

        if not attrs_str:
            return name, {}

        attrs = {}
        for pair in attrs_str.split(','):
            if ':' in pair:
                key, value = pair.split(':', 1)
                attrs[key.strip()] = TreeDSL._parse_value(value.strip())

        return name, attrs

    @staticmethod
    def _parse_attrs(text: str) -> Dict[str, Any]:
        """Parse attributes from various formats."""
        text = text.strip()

        # Handle dictionary-like format
        if text.startswith('{') and text.endswith('}'):
            text = text[1:-1]

        attrs = {}
        # Simple key:value parsing
        for pair in text.split(','):
            if ':' in pair:
                key, value = pair.split(':', 1)
                attrs[key.strip()] = TreeDSL._parse_value(value.strip())

        return attrs

    @staticmethod
    def _parse_value(value: str) -> Any:
        """Parse value string to appropriate type."""
        value = value.strip()

        # Try to parse as number
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Boolean
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False

        # String (remove quotes if present)
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        return value


def parse_tree(text: str, format: str = 'auto') -> Node:
    """
    Convenience function to parse tree from DSL text.

    Args:
        text: DSL text to parse.
        format: Format to use ('visual', 'indent', 'sexpr', 'auto').

    Returns:
        Root node of parsed tree.

    Examples:
        # Visual format
        tree = parse_tree('''
            company
            ├── engineering
            │   ├── frontend
            │   └── backend
            └── sales
        ''')

        # Indent format
        tree = parse_tree('''
            company
              engineering
                frontend
                backend
              sales
        ''')

        # S-expression format
        tree = parse_tree('''
            (company
              (engineering
                (frontend)
                (backend))
              (sales))
        ''')
    """
    return TreeDSL.parse(text, format)
