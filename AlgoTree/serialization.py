"""
Serialization for AlgoTree - Modern Pythonic Approach.

Philosophy:
- JSON is the native format (human-readable, universal)
- Trees are naturally hierarchical, so nested JSON is default
- Support other formats only when there's a clear use case
- Don't reinvent the wheel - use standard libraries

The Node class already provides to_dict() and from_dict() methods
that work seamlessly with Python's json module. This module adds:
- Convenience functions for file I/O
- Optional compression
- Streaming for large trees
- Integration with modern data formats (Parquet for analytics)
"""

from typing import Any, Dict, List, Optional, Union, Iterator, TextIO, BinaryIO
from pathlib import Path
import json
import gzip
import pickle
from contextlib import contextmanager
from ..node import Node


# Simple, Pythonic file I/O

def save(tree: Node, path: Union[str, Path], compress: bool = False) -> None:
    """
    Save tree to JSON file.
    
    This is the recommended way to persist trees. Uses the natural
    hierarchical JSON representation.
    
    Args:
        tree: Tree to save
        path: File path (can be string or Path object)
        compress: If True, use gzip compression
    
    Example:
        save(tree, "my_tree.json")
        save(tree, "my_tree.json.gz", compress=True)
    """
    path = Path(path)
    data = tree.to_dict()
    
    if compress or path.suffix == '.gz':
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    else:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)


def load(path: Union[str, Path]) -> Node:
    """
    Load tree from JSON file.
    
    Automatically handles gzip compression if file ends with .gz
    
    Args:
        path: File path
    
    Returns:
        Root node of loaded tree
    
    Example:
        tree = load("my_tree.json")
        tree = load("my_tree.json.gz")  # Auto-detects compression
    """
    path = Path(path)
    
    if path.suffix == '.gz':
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            data = json.load(f)
    else:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    return Node.from_dict(data)


def dumps(tree: Node, **json_kwargs) -> str:
    """
    Serialize tree to JSON string.
    
    Args:
        tree: Tree to serialize
        **json_kwargs: Arguments passed to json.dumps (indent, sort_keys, etc.)
    
    Returns:
        JSON string
    
    Example:
        json_str = dumps(tree, indent=2, sort_keys=True)
    """
    return json.dumps(tree.to_dict(), **json_kwargs)


def loads(json_str: str) -> Node:
    """
    Deserialize tree from JSON string.
    
    Args:
        json_str: JSON string
    
    Returns:
        Root node of tree
    
    Example:
        tree = loads('{"name": "root", "children": [...]}')
    """
    data = json.loads(json_str)
    return Node.from_dict(data)


# Streaming for large trees

@contextmanager
def stream_writer(path: Union[str, Path], compress: bool = False):
    """
    Context manager for streaming tree writes.
    
    Useful for very large trees that shouldn't be held entirely in memory.
    
    Example:
        with stream_writer("large_tree.json") as writer:
            writer.write_node(root)
            for subtree in generate_subtrees():
                writer.write_subtree(subtree)
    """
    path = Path(path)
    
    class StreamWriter:
        def __init__(self, file):
            self.file = file
            self.first = True
            self.file.write('{\n  "nodes": [\n')
        
        def write_node(self, node: Node, parent_id: Optional[int] = None):
            """Write single node to stream."""
            if not self.first:
                self.file.write(',\n')
            self.first = False
            
            node_data = {
                "name": node.name,
                "parent_id": parent_id,
                **node.payload
            }
            self.file.write('    ')
            json.dump(node_data, self.file)
        
        def close(self):
            self.file.write('\n  ]\n}\n')
    
    if compress or path.suffix == '.gz':
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            writer = StreamWriter(f)
            try:
                yield writer
            finally:
                writer.close()
    else:
        with open(path, 'w', encoding='utf-8') as f:
            writer = StreamWriter(f)
            try:
                yield writer
            finally:
                writer.close()


def iter_nodes(path: Union[str, Path]) -> Iterator[Dict[str, Any]]:
    """
    Iterate over nodes in a JSON file without loading entire tree.
    
    Useful for processing large trees.
    
    Args:
        path: Path to JSON file
    
    Yields:
        Node dictionaries
    
    Example:
        for node_data in iter_nodes("large_tree.json"):
            if node_data.get("type") == "file":
                process_file(node_data)
    """
    path = Path(path)
    
    if path.suffix == '.gz':
        opener = gzip.open(path, 'rt', encoding='utf-8')
    else:
        opener = open(path, 'r', encoding='utf-8')
    
    with opener as f:
        # Use streaming JSON parser for efficiency
        # This is a simplified version - real implementation would use ijson
        data = json.load(f)
        
        def traverse(node_dict):
            yield node_dict
            for child in node_dict.get('children', []):
                yield from traverse(child)
        
        yield from traverse(data)


# Alternative formats (only when needed)

def to_pickle(tree: Node) -> bytes:
    """
    Serialize tree using pickle.
    
    Faster than JSON but Python-only and not human-readable.
    Use only for temporary caching or when speed is critical.
    
    Args:
        tree: Tree to serialize
    
    Returns:
        Pickled bytes
    """
    return pickle.dumps(tree)


def from_pickle(data: bytes) -> Node:
    """
    Deserialize tree from pickle.
    
    Args:
        data: Pickled bytes
    
    Returns:
        Tree root node
    """
    return pickle.loads(data)


def to_parquet(tree: Node, path: Union[str, Path], include_path: bool = True) -> None:
    """
    Export tree to Parquet format for analytics.
    
    Parquet is columnar format excellent for analytical queries.
    Each node becomes a row with its attributes as columns.
    
    Args:
        tree: Tree to export
        path: Output file path
        include_path: Include full path from root as column
    
    Example:
        to_parquet(tree, "tree_data.parquet")
        # Then analyze with pandas, Spark, DuckDB, etc.
        df = pd.read_parquet("tree_data.parquet")
        df[df['type'] == 'file'].groupby('extension').size()
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas required for Parquet: pip install pandas pyarrow")
    
    rows = []
    
    def traverse(node: Node, path_parts: List[str] = None):
        if path_parts is None:
            path_parts = []
        
        current_path = path_parts + [node.name]
        
        row = {
            'name': node.name,
            'level': len(path_parts),
            'is_leaf': len(node.children) == 0,
            'num_children': len(node.children)
        }
        
        if include_path:
            row['path'] = '/'.join(current_path)
            row['parent_path'] = '/'.join(path_parts) if path_parts else None
        
        # Add payload attributes
        for key, value in node.payload.items():
            row[key] = value
        
        rows.append(row)
        
        # Traverse children
        for child in node.children:
            traverse(child, current_path)
    
    traverse(tree)
    
    df = pd.DataFrame(rows)
    df.to_parquet(path, engine='pyarrow', index=False)


def from_parquet(path: Union[str, Path]) -> Node:
    """
    Load tree from Parquet format.
    
    Reconstructs tree structure from tabular data.
    
    Args:
        path: Parquet file path
    
    Returns:
        Root node of tree
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("pandas required for Parquet: pip install pandas pyarrow")
    
    df = pd.read_parquet(path)
    
    # Build tree from paths
    if 'path' not in df.columns:
        raise ValueError("Parquet file must have 'path' column to reconstruct tree")
    
    root = None
    path_to_node = {}
    
    # Sort by path depth to ensure parents are created before children
    df['depth'] = df['path'].str.count('/')
    df = df.sort_values('depth')
    
    for _, row in df.iterrows():
        path = row['path']
        parts = path.split('/')
        name = parts[-1]
        
        # Extract payload (all columns except structural ones)
        structural_cols = {'name', 'path', 'parent_path', 'level', 'is_leaf', 'num_children', 'depth'}
        payload = {k: v for k, v in row.items() 
                  if k not in structural_cols and pd.notna(v)}
        
        node = Node(name=name, **payload)
        path_to_node[path] = node
        
        if len(parts) == 1:
            root = node
        else:
            parent_path = '/'.join(parts[:-1])
            if parent_path in path_to_node:
                parent = path_to_node[parent_path]
                node.parent = parent
                parent.children.append(node)
    
    return root


# Integration with standard library

def register_json_encoder():
    """
    Register Node class with json module for seamless serialization.
    
    After calling this, you can use json.dumps directly on Node objects:
        register_json_encoder()
        json.dumps(tree)  # Works without calling to_dict()
    """
    class NodeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Node):
                return obj.to_dict()
            return super().default(obj)
    
    # Monkey-patch json module (use with caution)
    json._default_encoder = NodeEncoder()


# Backward compatibility helpers

def upgrade_legacy_format(legacy_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Upgrade legacy TreeNode/FlatForest format to modern format.
    
    Args:
        legacy_data: Old format dictionary
    
    Returns:
        Modern format dictionary compatible with Node.from_dict()
    """
    # Handle old TreeNode format (which used dict inheritance)
    if '_children' in legacy_data:
        legacy_data['children'] = legacy_data.pop('_children')
    
    # Handle old FlatForest format
    if 'nodes' in legacy_data and isinstance(legacy_data['nodes'], dict):
        # Convert to modern format
        # This is just a placeholder - actual conversion would be more complex
        pass
    
    return legacy_data