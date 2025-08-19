# AlgoTree v1.0 - Modern Tree Manipulation Library
# 
# Primary API (v1.0+)
from .node import Node
from .fluent import TreeBuilder, FluentNode
from .dsl import parse_tree, TreeDSL
from .pattern_matcher import (
    Pattern, PatternMatcher, MatchType, 
    pattern_match, dotmatch, dotpluck, 
    dotexists, dotcount, dotfilter
)
from .tree_transformer import (
    dotmod, dotmap, dotprune, dotmerge,
    dotgraft, dotsplit, dotflatten, dotreduce,
    dotannotate, dotvalidate, dotnormalize
)
from .tree_shaper import (
    dotpipe, to_dict, to_list, to_paths,
    to_adjacency_list, to_edge_list, to_nested_lists,
    to_table, dotextract, dotcollect, dotgroup,
    dotpartition, dotproject, to_graphviz_data, to_json_schema
)

# Utilities (still compatible)
from .pretty_tree import PrettyTree, pretty_tree
from .exporters import TreeExporter, export_tree, save_tree

# Serialization
from .serialization import save, load, dumps, loads

# Legacy imports (deprecated - will be removed in v2.0)
# These are kept for minimal compatibility but should not be used in new code
try:
    from .flat_forest import FlatForest
    from .flat_forest_node import FlatForestNode
    from .treenode import TreeNode
    from .tree_converter import TreeConverter
    from .treenode_api import TreeNodeApi
    from .node_hasher import NodeHasher
    from .tree_hasher import TreeHasher
    from .utils import (
        map,
        visit,
        descendants,
        ancestors,
        siblings,
        leaves,
        height,
        depth,
        is_root,
        is_leaf,
        is_internal,
        breadth_first,
        find_nodes,
        find_node,
        find_path,
        node_stats,
        size,
        prune,
        lca,
        breadth_first_undirected,
        node_to_leaf_paths,
        distance,
        subtree_centered_at,
        subtree_rooted_at,
        paths_to_tree,
        is_isomorphic,
    )
    
    import warnings
    warnings.warn(
        "Legacy AlgoTree APIs (TreeNode, FlatForest) are deprecated and will be removed in v2.0. "
        "Please migrate to the new Node/TreeBuilder/FluentNode API. "
        "See https://github.com/queelius/AlgoTree/blob/main/CHANGELOG.md for migration guide.",
        DeprecationWarning,
        stacklevel=2
    )
except ImportError:
    # Legacy modules not available - this is fine for new installations
    pass

__version__ = "1.0.0"
__all__ = [
    # Primary API
    "Node",
    "TreeBuilder", 
    "FluentNode",
    "parse_tree",
    "TreeDSL",
    # Pattern Matching
    "Pattern",
    "PatternMatcher",
    "MatchType",
    "pattern_match",
    # Dot Notation (dotsuite-inspired)
    "dotmatch",
    "dotpluck",
    "dotexists",
    "dotcount",
    "dotfilter",
    # Tree Transformations (dotmod family - closed)
    "dotmod",
    "dotmap",
    "dotprune",
    "dotmerge",
    "dotgraft",
    "dotsplit",
    "dotflatten",
    "dotreduce",
    "dotannotate",
    "dotvalidate",
    "dotnormalize",
    # Tree Shaping (dotpipe family - open)
    "dotpipe",
    "to_dict",
    "to_list",
    "to_paths",
    "to_adjacency_list",
    "to_edge_list",
    "to_nested_lists",
    "to_table",
    "dotextract",
    "dotcollect",
    "dotgroup",
    "dotpartition",
    "dotproject",
    "to_graphviz_data",
    "to_json_schema",
    # Utilities
    "pretty_tree",
    "PrettyTree",
    # Export
    "TreeExporter",
    "export_tree",
    "save_tree",
    # Serialization
    "save",
    "load",
    "dumps",
    "loads",
]
