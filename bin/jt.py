#!/usr/bin/env python3
"""
jt - JSON Tree manipulation tool

A command-line tool for querying, manipulating, and visualizing tree structures.
Uses the modern AlgoTree v1.0 API with fluent operations, pattern matching, and transformations.
"""

import argparse
import json
import sys
import os
from typing import Any, Dict, List, Optional, Union, Callable, Tuple

# Add parent directory to path to import AlgoTree
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AlgoTree.node import Node
from AlgoTree.fluent import TreeBuilder, FluentNode
from AlgoTree.dsl import parse_tree
from AlgoTree.pretty_tree import pretty_tree
from AlgoTree.pattern_matcher import dotmatch, dotpluck, dotexists, dotcount, dotfilter
from AlgoTree.tree_transformer import (
    dotmod, dotmap, dotprune as dotprune_transform, dotmerge, dotgraft,
    dotsplit, dotannotate, dotvalidate, dotnormalize, dotreduce, dotflatten
)
from AlgoTree.tree_shaper import (
    dotpipe, to_dict, to_list, to_paths, to_table,
    to_adjacency_list, to_edge_list, to_nested_lists,
    dotextract, dotcollect, dotgroup, dotpartition, dotproject
)
from AlgoTree.exporters import TreeExporter


def load_tree(input_data: str, format: str = 'auto') -> Node:
    """
    Load tree from various formats.
    
    Args:
        input_data: Input string (JSON or DSL format)
        format: Format type ('json', 'dsl', 'auto')
    
    Returns:
        Root node of loaded tree
    """
    if format == 'auto':
        # Try to detect format
        input_data = input_data.strip()
        if input_data.startswith('{') or input_data.startswith('['):
            format = 'json'
        else:
            format = 'dsl'
    
    if format == 'json':
        data = json.loads(input_data)
        if isinstance(data, list):
            # Array of nodes - build tree
            root = Node(name="root")
            for item in data:
                Node.from_dict(item, parent=root)
            return root
        else:
            return Node.from_dict(data)
    else:
        return parse_tree(input_data)


def output_tree(node: Node, format: str = 'json', **kwargs) -> str:
    """
    Output tree in various formats.
    
    Args:
        node: Root node of tree
        format: Output format
        **kwargs: Additional format-specific options
    
    Returns:
        Formatted tree string
    """
    if format == 'json':
        indent = kwargs.get('indent', 2)
        return json.dumps(node.to_dict(), indent=indent)
    elif format == 'pretty':
        # Use pretty_tree for visual output
        import io
        from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            pretty_tree(node)
        return f.getvalue()
    elif format == 'dsl':
        # Generate DSL format
        return generate_dsl(node, kwargs.get('dsl_format', 'indent'))
    elif format == 'graphviz':
        return TreeExporter.to_graphviz(node)
    elif format == 'mermaid':
        return TreeExporter.to_mermaid(node)
    elif format == 'xml':
        return TreeExporter.to_xml(node)
    elif format == 'yaml':
        return TreeExporter.to_yaml(node)
    elif format == 'html':
        return TreeExporter.to_html(node)
    elif format == 'paths':
        paths = to_paths(node)
        return '\n'.join(paths)
    elif format == 'table':
        table = to_table(node)
        # Simple table formatting
        if table:
            keys = list(table[0].keys())
            result = '\t'.join(keys) + '\n'
            for row in table:
                result += '\t'.join(str(row.get(k, '')) for k in keys) + '\n'
            return result
        return ''
    else:
        raise ValueError(f"Unknown output format: {format}")


def generate_dsl(node: Node, style: str = 'indent') -> str:
    """Generate DSL representation of tree."""
    if style == 'visual':
        return generate_visual_dsl(node)
    elif style == 'sexpr':
        return generate_sexpr_dsl(node)
    else:
        return generate_indent_dsl(node)


def generate_indent_dsl(node: Node, level: int = 0) -> str:
    """Generate indent-based DSL."""
    indent = "  " * level
    
    # Format payload
    if node.payload:
        payload_str = ", ".join(f"{k}: {v}" for k, v in node.payload.items())
        result = f"{indent}{node.name}: {{{payload_str}}}\n"
    else:
        result = f"{indent}{node.name}\n"
    
    # Add children
    for child in node.children:
        result += generate_indent_dsl(child, level + 1)
    
    return result


def generate_visual_dsl(node: Node, prefix: str = "", is_last: bool = True) -> str:
    """Generate visual tree DSL."""
    # Node representation
    if node.payload:
        attrs = ",".join(f"{k}:{v}" for k, v in node.payload.items())
        node_str = f"{node.name}[{attrs}]"
    else:
        node_str = node.name
    
    # Add tree characters
    if prefix == "":
        result = node_str + "\n"
    else:
        connector = "└── " if is_last else "├── "
        result = prefix + connector + node_str + "\n"
    
    # Add children
    children = node.children
    for i, child in enumerate(children):
        is_last_child = i == len(children) - 1
        extension = "    " if is_last else "│   "
        new_prefix = prefix + extension if prefix else ""
        result += generate_visual_dsl(child, new_prefix, is_last_child)
    
    return result


def generate_sexpr_dsl(node: Node) -> str:
    """Generate S-expression DSL."""
    result = f"({node.name}"
    
    # Add attributes
    for key, value in node.payload.items():
        result += f" :{key} {value}"
    
    # Add children
    for child in node.children:
        result += "\n  " + generate_sexpr_dsl(child).replace("\n", "\n  ")
    
    result += ")"
    return result





def apply_transformation(tree: Node, transform_type: str, args: Any) -> Node:
    """
    Apply tree transformation.
    
    Args:
        tree: Input tree
        transform_type: Type of transformation
        args: Transformation arguments
    
    Returns:
        Transformed tree
    """
    if transform_type == 'mod':
        # Parse transformation spec
        transformations = parse_transform_spec(args)
        return dotmod(tree, transformations)
    elif transform_type == 'map':
        pattern, func_str = args.split(':', 1)
        func = eval(f"lambda n: {func_str}")
        return dotmap(tree, func, pattern)
    elif transform_type == 'prune':
        return dotprune_transform(tree, args)
    elif transform_type == 'normalize':
        return dotnormalize(tree, args)
    elif transform_type == 'flatten':
        return dotflatten(tree, args if args else None)
    elif transform_type == 'annotate':
        pattern, annotations = args.split(':', 1)
        ann_dict = json.loads(annotations)
        return dotannotate(tree, {pattern: ann_dict})
    else:
        raise ValueError(f"Unknown transformation: {transform_type}")


def parse_transform_spec(spec: str) -> Union[Dict, List[Tuple]]:
    """
    Parse transformation specification.
    
    Supported formats:
    - JSON: '{"path.to.node": {"name": "new_name"}}'
    - Simple: 'path.to.node:name=new_name,value=123'
    """
    spec = spec.strip()
    if spec.startswith('{'):
        return json.loads(spec)
    
    # Parse simple format
    transformations = {}
    for item in spec.split(';'):
        if ':' in item:
            path, changes = item.split(':', 1)
            path = path.strip()
            change_dict = {}
            for change in changes.split(','):
                if '=' in change:
                    key, value = change.split('=', 1)
                    # Try to parse value as JSON, fallback to string
                    try:
                        value = json.loads(value)
                    except:
                        pass
                    change_dict[key.strip()] = value
            transformations[path] = change_dict
    return transformations


def main():
    parser = argparse.ArgumentParser(
        description="jt - JSON Tree manipulation tool (v1.0)",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  # Pretty print a tree
  jt tree.json --pretty
  
  # Pattern matching with dot notation
  jt tree.json --match "files.*.txt"
  jt tree.json --match "**[type=file]"
  jt tree.json --match "docs.report\\.pdf"  # Escaped dot for literal dot
  
  # Tree navigation
  jt tree.json --children "src"         # Show children of 'src' node
  jt tree.json --ancestors "main.py"    # Show ancestors up to root
  jt tree.json --descendants "docs"     # Show entire subtree
  
  # Transformations
  jt tree.json --transform mod "files.old:name=new"
  jt tree.json --transform map "**[size]:n.payload['size'] * 2"
  jt tree.json --transform prune "**[temp]"
  
  # Export formats
  jt tree.json --output graphviz > tree.dot
  jt tree.json --output mermaid
  jt tree.json --output yaml
  
  # Pipeline operations
  jt tree.json --pipe "match:**/*.txt" --pipe "extract:name,size"
  jt tree.json --pipe "match:**[type=file]" --pipe "group:extension"
""")
    
    # Input/Output options
    parser.add_argument(
        "file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Input file (reads from stdin if not provided)"
    )
    
    parser.add_argument(
        "--input-format", "-i",
        choices=["json", "dsl", "auto"],
        default="auto",
        help="Input format (default: auto-detect)"
    )
    
    parser.add_argument(
        "--output", "-o",
        choices=["json", "pretty", "dsl", "graphviz", "mermaid", "xml", "yaml", "html", "paths", "table"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--dsl-format",
        choices=["indent", "visual", "sexpr"],
        default="indent",
        help="DSL format style (for --output dsl)"
    )
    
    # Pattern matching operations
    parser.add_argument(
        "--match",
        metavar="PATTERN",
        help="Match nodes using dot notation (e.g., 'files.*.txt', '**[type=file]')"
    )
    
    parser.add_argument(
        "--pluck",
        metavar="PATTERN",
        help="Extract values using dot notation"
    )
    
    parser.add_argument(
        "--exists",
        metavar="PATTERN",
        help="Check if pattern exists in tree"
    )
    
    parser.add_argument(
        "--count",
        metavar="PATTERN",
        help="Count matching nodes"
    )
    
    # Transformation operations
    parser.add_argument(
        "--transform", "-t",
        nargs=2,
        metavar=('TYPE', 'SPEC'),
        help="Apply transformation (mod, map, prune, normalize, flatten, annotate)"
    )
    
    parser.add_argument(
        "--merge",
        metavar="FILE",
        help="Merge with another tree file"
    )
    
    parser.add_argument(
        "--graft",
        nargs=2,
        metavar=('PATTERN', 'FILE'),
        help="Graft subtree from file at pattern location"
    )
    
    # Shaping operations
    parser.add_argument(
        "--pipe",
        action="append",
        metavar="OPERATION",
        help="Pipeline operation (can be used multiple times)"
    )
    
    parser.add_argument(
        "--extract",
        metavar="FIELDS",
        help="Extract specific fields (comma-separated)"
    )
    
    parser.add_argument(
        "--group",
        metavar="KEY",
        help="Group nodes by key"
    )
    
    
    # Tree operations
    parser.add_argument(
        "--children",
        metavar="NODE",
        help="Show children of node"
    )
    
    parser.add_argument(
        "--parent",
        metavar="NODE",
        help="Show parent of node"
    )
    
    parser.add_argument(
        "--siblings",
        metavar="NODE",
        help="Show siblings of node"
    )
    
    parser.add_argument(
        "--ancestors",
        metavar="NODE",
        help="Show ancestors of node"
    )
    
    parser.add_argument(
        "--descendants",
        metavar="NODE",
        help="Show descendants of node"
    )
    
    parser.add_argument(
        "--path",
        metavar="NODE",
        help="Show path from root to node"
    )
    
    # Analysis operations
    parser.add_argument(
        "--size",
        action="store_true",
        help="Print tree size (total nodes)"
    )
    
    parser.add_argument(
        "--height",
        action="store_true",
        help="Print tree height"
    )
    
    parser.add_argument(
        "--leaves",
        action="store_true",
        help="Show all leaf nodes"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show tree statistics"
    )
    
    # Display options
    parser.add_argument(
        "--pretty", "-p",
        action="store_true",
        help="Pretty print tree (shortcut for --output pretty)"
    )
    
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indent level (default: 2)"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 1.0.0 (AlgoTree v1.0)"
    )
    
    args = parser.parse_args()
    
    try:
        # Read input
        input_data = args.file.read()
        
        # Load tree
        tree = load_tree(input_data, args.input_format)
        
        # Create fluent wrapper
        fluent = FluentNode(tree)
        
        # Apply operations
        result = tree
        
        # Pattern matching operations
        if args.match:
            matches = dotmatch(result, args.match)
            if not matches:
                print(f"No nodes match pattern '{args.match}'", file=sys.stderr)
                sys.exit(1)
            if len(matches) == 1:
                result = matches[0]
            else:
                # Create a new tree with matched nodes
                new_root = Node(name="matched_nodes")
                for node in matches:
                    new_root.add_child(name=node.name, **node.payload)
                result = new_root
        
        if args.pluck:
            values = dotpluck(result, args.pluck)
            print(json.dumps(values, indent=2))
            return
        
        if args.exists:
            exists = dotexists(result, args.exists)
            print("true" if exists else "false")
            return
        
        if args.count:
            count = dotcount(result, args.count)
            print(count)
            return
        
        # Transformation operations
        if args.transform:
            transform_type, spec = args.transform
            result = apply_transformation(result, transform_type, spec)
        
        if args.merge:
            with open(args.merge, 'r') as f:
                other_tree = load_tree(f.read())
            result = dotmerge(result, other_tree)
        
        if args.graft:
            pattern, file_path = args.graft
            with open(file_path, 'r') as f:
                subtree = load_tree(f.read())
            result = dotgraft(result, pattern, subtree)
        
        # Pipeline operations
        if args.pipe:
            current = result
            for pipe_op in args.pipe:
                if ':' in pipe_op:
                    op_name, op_args = pipe_op.split(':', 1)
                else:
                    op_name = pipe_op
                    op_args = None
                
                if op_name == 'match':
                    current = dotmatch(current, op_args)
                elif op_name == 'extract':
                    fields = op_args.split(',') if op_args else []
                    current = dotextract(current, lambda n: {f: n.payload.get(f) for f in fields})
                elif op_name == 'group':
                    current = dotgroup([current], op_args)
                elif op_name == 'collect':
                    current = dotcollect(current, op_args if op_args else 'name')
                elif op_name == 'to_dict':
                    current = to_dict(current)
                elif op_name == 'to_list':
                    current = to_list(current)
                elif op_name == 'to_paths':
                    current = to_paths(current)
                else:
                    print(f"Unknown pipe operation: {op_name}", file=sys.stderr)
                    sys.exit(1)
            
            # Output pipeline result
            if isinstance(current, (dict, list)):
                print(json.dumps(current, indent=2))
            elif isinstance(current, Node):
                result = current
            else:
                print(current)
                return
        
        # Shaping operations
        if args.extract:
            fields = args.extract.split(',')
            extracted = dotextract(result, lambda n: {f: n.payload.get(f) for f in fields})
            print(json.dumps(extracted, indent=2))
            return
        
        if args.group:
            grouped = dotgroup([result], args.group)
            print(json.dumps(grouped, indent=2))
            return
        
        
        # Navigation operations
        if args.children:
            node = result.find(lambda n: n.name == args.children)
            if node:
                new_root = Node(name=f"children_of_{args.children}")
                for child in node.children:
                    new_root.add_child(name=child.name, **child.payload)
                result = new_root
        
        if args.parent:
            node = result.find(lambda n: n.name == args.parent)
            if node and node.parent:
                result = node.parent
        
        if args.siblings:
            node = result.find(lambda n: n.name == args.siblings)
            if node:
                new_root = Node(name=f"siblings_of_{args.siblings}")
                for sibling in node.siblings:
                    new_root.add_child(name=sibling.name, **sibling.payload)
                result = new_root
        
        if args.ancestors:
            node = result.find(lambda n: n.name == args.ancestors)
            if node:
                new_root = Node(name=f"ancestors_of_{args.ancestors}")
                current = node.parent
                while current:
                    new_root.add_child(name=current.name, **current.payload)
                    current = current.parent
                result = new_root
        
        if args.descendants:
            node = result.find(lambda n: n.name == args.descendants)
            if node:
                result = node
        
        if args.path:
            node = result.find(lambda n: n.name == args.path)
            if node:
                new_root = Node(name=f"path_to_{args.path}")
                for n in node.get_path():
                    new_root.add_child(name=n.name, **n.payload)
                result = new_root
        
        # Analysis operations
        if args.size:
            print(len(list(result.traverse_preorder())))
            return
        
        if args.height:
            def get_height(node):
                if not node.children:
                    return 0
                return 1 + max(get_height(child) for child in node.children)
            print(get_height(result))
            return
        
        if args.leaves:
            leaves = FluentNode(result).leaves().to_list()
            new_root = Node(name="leaf_nodes")
            for leaf in leaves:
                new_root.add_child(name=leaf.name, **leaf.payload)
            result = new_root
        
        if args.stats:
            total = len(list(result.traverse_preorder()))
            leaves = len(FluentNode(result).leaves().to_list())
            internal = total - leaves
            def get_height(node):
                if not node.children:
                    return 0
                return 1 + max(get_height(child) for child in node.children)
            height = get_height(result)
            
            stats = {
                "total_nodes": total,
                "leaf_nodes": leaves,
                "internal_nodes": internal,
                "height": height,
                "root": result.name
            }
            print(json.dumps(stats, indent=2))
            return
        
        # Output
        if args.pretty:
            output = output_tree(result, 'pretty')
        else:
            output = output_tree(result, args.output, 
                               indent=args.indent,
                               dsl_format=args.dsl_format)
        
        print(output, end='')
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()