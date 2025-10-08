"""
Serialization for AlgoTree - Support for multiple formats.

Supports JSON, YAML, XML, and pickle formats for saving/loading trees.
"""

from typing import Any, Dict, Optional, Union
from pathlib import Path
import json
import gzip
import pickle
from .node import Node


def _detect_format(path: Union[str, Path]) -> str:
    """Detect format from file extension."""
    path = Path(path)
    suffix = path.suffix.lower()

    # Handle .gz compression
    if suffix == '.gz':
        suffix = path.stem.split('.')[-1].lower()
        suffix = '.' + suffix

    format_map = {
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.xml': 'xml',
        '.pkl': 'pickle',
        '.pickle': 'pickle',
    }

    return format_map.get(suffix, 'json')


def dumps(tree: Node, format: str = "json", **kwargs) -> str:
    """
    Serialize tree to string.

    Args:
        tree: Tree to serialize
        format: Output format ('json', 'yaml', 'xml')
        **kwargs: Format-specific arguments

    Returns:
        Serialized string

    Example:
        json_str = dumps(tree, format="json", indent=2)
        yaml_str = dumps(tree, format="yaml")
    """
    data = tree.to_dict()

    if format == "json":
        # Set default indent if not provided
        if 'indent' not in kwargs:
            kwargs['indent'] = 2
        return json.dumps(data, **kwargs)

    elif format == "yaml":
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML required for YAML format: pip install pyyaml")
        return yaml.dump(data, **kwargs)

    elif format == "xml":
        return _to_xml(data, **kwargs)

    else:
        raise ValueError(f"Unsupported format: {format}. Use 'json', 'yaml', or 'xml'")


def loads(string: str, format: str = "json") -> Node:
    """
    Deserialize tree from string.

    Args:
        string: Serialized string
        format: Input format ('json', 'yaml', 'xml')

    Returns:
        Root node of tree

    Example:
        tree = loads(json_str, format="json")
        tree = loads(yaml_str, format="yaml")
    """
    if format == "json":
        data = json.loads(string)

    elif format == "yaml":
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML required for YAML format: pip install pyyaml")
        data = yaml.safe_load(string)

    elif format == "xml":
        data = _from_xml(string)

    else:
        raise ValueError(f"Unsupported format: {format}. Use 'json', 'yaml', or 'xml'")

    return Node.from_dict(data)


def save(tree: Node, path: Union[str, Path], format: Optional[str] = None, compress: bool = False) -> None:
    """
    Save tree to file.

    Args:
        tree: Tree to save
        path: File path
        format: Output format (auto-detected from extension if not provided)
        compress: If True, use gzip compression

    Example:
        save(tree, "tree.json")
        save(tree, "tree.yaml", format="yaml")
        save(tree, "tree.json.gz", compress=True)
    """
    path = Path(path)

    # Auto-detect format if not provided
    if format is None:
        format = _detect_format(path)

    # Handle pickle separately (binary format)
    if format == "pickle":
        data = pickle.dumps(tree)
        if compress or path.suffix == '.gz':
            with gzip.open(path, 'wb') as f:
                f.write(data)
        else:
            with open(path, 'wb') as f:
                f.write(data)
        return

    # Text-based formats
    content = dumps(tree, format=format)

    if compress or path.suffix == '.gz':
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            f.write(content)
    else:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)


def load(path: Union[str, Path], format: Optional[str] = None) -> Node:
    """
    Load tree from file.

    Args:
        path: File path
        format: Input format (auto-detected from extension if not provided)

    Returns:
        Root node of loaded tree

    Example:
        tree = load("tree.json")
        tree = load("tree.yaml")
        tree = load("tree.json.gz")  # Auto-detects compression
    """
    path = Path(path)

    # Auto-detect format if not provided
    if format is None:
        format = _detect_format(path)

    # Handle pickle separately (binary format)
    if format == "pickle":
        if path.suffix == '.gz':
            with gzip.open(path, 'rb') as f:
                return pickle.load(f)
        else:
            with open(path, 'rb') as f:
                return pickle.load(f)

    # Text-based formats
    if path.suffix == '.gz':
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            content = f.read()
    else:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

    return loads(content, format=format)


# XML helpers

def _to_xml(data: Dict[str, Any], root_tag: str = "tree") -> str:
    """Convert dictionary to XML string."""
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        raise ImportError("xml.etree.ElementTree required for XML format")

    def dict_to_element(d: Dict[str, Any], tag: str = "node") -> ET.Element:
        """Convert dict to XML element."""
        elem = ET.Element(tag)

        # Add name as attribute
        if 'name' in d:
            elem.set('name', str(d['name']))

        # Add other attributes (except children)
        for key, value in d.items():
            if key not in ('name', 'children'):
                elem.set(key, str(value))

        # Add children
        if 'children' in d:
            for child_dict in d['children']:
                child_elem = dict_to_element(child_dict, "node")
                elem.append(child_elem)

        return elem

    root = dict_to_element(data, root_tag)
    tree = ET.ElementTree(root)

    # Convert to string with XML declaration
    import io
    output = io.StringIO()
    tree.write(output, encoding='unicode', xml_declaration=True)
    return output.getvalue()


def _from_xml(xml_string: str) -> Dict[str, Any]:
    """Convert XML string to dictionary."""
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        raise ImportError("xml.etree.ElementTree required for XML format")

    def element_to_dict(elem: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dict."""
        result = {}

        # Get name attribute
        if 'name' in elem.attrib:
            result['name'] = elem.attrib['name']

        # Get other attributes
        for key, value in elem.attrib.items():
            if key != 'name':
                # Try to convert to appropriate type
                try:
                    result[key] = int(value)
                except ValueError:
                    try:
                        result[key] = float(value)
                    except ValueError:
                        result[key] = value

        # Get children
        children = []
        for child in elem:
            children.append(element_to_dict(child))

        if children:
            result['children'] = children

        return result

    root = ET.fromstring(xml_string)
    return element_to_dict(root)


# Legacy pickle helpers for backward compatibility

def to_pickle(tree: Node) -> bytes:
    """
    Serialize tree using pickle.

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
