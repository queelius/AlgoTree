"""
AlgoTree - A powerful, modern tree manipulation library for Python.

Primary type: Node
    Node is the single self-sufficient tree type.  Every operation that Tree
    offers (construct, transform, query, navigate, render, serialize) is
    available directly on Node.  You rarely need to construct a Tree; use it
    only for code that depends on its empty-sentinel convention or the
    Node|dict|None map() sniffing for back-compat with v1 callers.

Core components:
- Node (primary): Immutable tree nodes with the full operation set
- Tree (forwarder): Thin wrapper over Node; preserved for back-compat
- Selectors: Composable pattern matching (work with bare Node or Tree)
- Transformers: Composable tree transformations
"""

# Core classes
# Node is the primary type; Tree is a thin forwarder kept for back-compat.
from .node import Node, node
from .tree import Tree
from .cursor import Cursor, walk_cursors

# Selectors for pattern matching
from .selectors import (
    Selector,
    # Basic selectors
    NameSelector, GlobSelector, RegexSelector,
    AttrsSelector, TypeSelector, PredicateSelector,
    DepthSelector, LeafSelector, RootSelector,
    # Logical combinators
    AndSelector, OrSelector, NotSelector, XorSelector,
    # Structural combinators
    AxisSelector,
    # Factory functions
    name, glob, regex, attrs, type_, predicate, depth, leaf, root, any_, none, none_, parse
)

# Transformers for tree manipulation
from .transformers import (
    Transformer, identity,
    # Factory functions
    map_, filter_, prune, graft, flatten, normalize, annotate,
    reduce_, fold, extract, to_dict, to_paths
)

# Render engine (Theme, registry, fold-based text tree)
from . import render
from .render import (
    Theme, ASCII_THEME, UNICODE_THEME,
    render as render_tree,          # the dispatch function
    register as register_renderer,
    extension_for,
)

# Visualization and export
from .pretty_tree import PrettyTree, pretty_tree
from .exporters import TreeExporter, export_tree, save_tree

# Serialization
from .serialization import save, load, dumps, loads

# DSL support
from .dsl import parse_tree, TreeDSL

# Trace and Diff (P3)
from .trace import Trace
from .diff import diff, DiffTree

# Interoperability with AlgoGraph (optional)
from .interop import (
    tree_to_graph,
    graph_to_tree,
    node_to_flat_dict,
    flat_dict_to_node,
    tree_to_flat_dict,
    flat_dict_to_tree,
)

# Version
__version__ = "3.0.0.dev0"

# Public API
__all__ = [
    # Core
    'Node', 'node',
    'Tree',
    'Cursor', 'walk_cursors',

    # Selectors
    'Selector',
    'NameSelector', 'GlobSelector', 'RegexSelector',
    'AttrsSelector', 'TypeSelector', 'PredicateSelector',
    'DepthSelector', 'LeafSelector', 'RootSelector',
    'AndSelector', 'OrSelector', 'NotSelector', 'XorSelector',
    'AxisSelector',
    'name', 'glob', 'regex', 'attrs', 'type_', 'predicate', 'depth', 'leaf', 'root', 'any_', 'none', 'none_', 'parse',

    # Transformers
    'Transformer', 'identity',
    'map_', 'filter_', 'prune', 'graft', 'flatten', 'normalize', 'annotate',
    'reduce_', 'fold', 'extract', 'to_dict', 'to_paths',

    # Render engine
    'render',           # the module
    'render_tree',      # the dispatch function (render.render)
    'Theme', 'ASCII_THEME', 'UNICODE_THEME',
    'register_renderer', 'extension_for',

    # Visualization
    'PrettyTree', 'pretty_tree',
    'TreeExporter', 'export_tree', 'save_tree',

    # Serialization
    'save', 'load', 'dumps', 'loads',

    # DSL
    'parse_tree', 'TreeDSL',

    # Interoperability with AlgoGraph
    'tree_to_graph', 'graph_to_tree',
    'node_to_flat_dict', 'flat_dict_to_node',
    'tree_to_flat_dict', 'flat_dict_to_tree',

    # Trace and Diff (P3)
    'Trace',
    'diff', 'DiffTree',
]
