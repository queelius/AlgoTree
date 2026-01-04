"""
AlgoTree - A powerful, modern tree manipulation library for Python.

Core components:
- Node: Immutable tree nodes with functional operations
- Tree: Tree wrapper with consistent API
- Selectors: Composable pattern matching
- Transformers: Composable tree transformations
- Builders: Fluent API for tree construction
"""

# Core classes
from .node import Node, node
from .tree import Tree

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

# Visualization and export
from .pretty_tree import PrettyTree, pretty_tree
from .exporters import TreeExporter, export_tree, save_tree

# Serialization
from .serialization import save, load, dumps, loads

# DSL support
from .dsl import parse_tree, TreeDSL

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
__version__ = "2.0.0"

# Public API
__all__ = [
    # Core
    'Node', 'node',
    'Tree',

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
]
