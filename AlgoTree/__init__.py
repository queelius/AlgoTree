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
- Builders: Fluent API for tree construction
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
    NameSelector, AttrsSelector, TypeSelector, PredicateSelector,
    DepthSelector, LeafSelector, RootSelector,
    # Logical combinators
    AndSelector, OrSelector, NotSelector, XorSelector,
    # Structural combinators
    ChildOfSelector, ParentOfSelector, DescendantOfSelector,
    AncestorOfSelector, SiblingOfSelector,
    # Factory functions
    name, attrs, type_, predicate, depth, leaf, root, any_, none, parse
)

# Transformers for tree manipulation
from .transformers import (
    Transformer,
    # Tree -> Tree transformers
    TreeTransformer, MapTransformer, FilterTransformer, PruneTransformer,
    GraftTransformer, FlattenTransformer, NormalizeTransformer, AnnotateTransformer,
    # Tree -> Any transformers (shapers)
    Shaper, ReduceShaper, FoldShaper, ExtractShaper, ToDictShaper, ToPathsShaper,
    # Composite transformers
    Pipeline, ParallelTransformer, RepeatTransformer, ConditionalTransformer, DebugTransformer,
    # Factory functions
    map_, filter_, prune, graft, flatten, normalize, annotate,
    reduce_, fold, extract, to_dict, to_paths
)

# Builders for tree construction
from .builders import (
    TreeBuilder, FluentTree, TreeContext, QuickBuilder,
    tree, branch, leaf as leaf_node  # renamed to avoid collision with selectors.leaf
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
    'NameSelector', 'AttrsSelector', 'TypeSelector', 'PredicateSelector',
    'DepthSelector', 'LeafSelector', 'RootSelector',
    'AndSelector', 'OrSelector', 'NotSelector', 'XorSelector',
    'ChildOfSelector', 'ParentOfSelector', 'DescendantOfSelector',
    'AncestorOfSelector', 'SiblingOfSelector',
    'name', 'attrs', 'type_', 'predicate', 'depth', 'leaf', 'root', 'any_', 'none', 'parse',

    # Transformers
    'Transformer',
    'TreeTransformer', 'MapTransformer', 'FilterTransformer', 'PruneTransformer',
    'GraftTransformer', 'FlattenTransformer', 'NormalizeTransformer', 'AnnotateTransformer',
    'Shaper', 'ReduceShaper', 'FoldShaper', 'ExtractShaper', 'ToDictShaper', 'ToPathsShaper',
    'Pipeline', 'ParallelTransformer', 'RepeatTransformer', 'ConditionalTransformer', 'DebugTransformer',
    'map_', 'filter_', 'prune', 'graft', 'flatten', 'normalize', 'annotate',
    'reduce_', 'fold', 'extract', 'to_dict', 'to_paths',

    # Builders
    'TreeBuilder', 'FluentTree', 'TreeContext', 'QuickBuilder',
    'tree', 'branch', 'leaf_node',

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
