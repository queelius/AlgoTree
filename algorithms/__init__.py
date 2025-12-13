"""
Tree algorithms organized by category.

This package provides a comprehensive collection of tree algorithms including:
- Traversal algorithms (DFS, BFS, level-order, etc.)
- Search algorithms (path finding, pattern matching)
- Analysis algorithms (LCA, diameter, balance, centrality)
- Generation algorithms (random trees, balanced trees)
- Comparison algorithms (equality, isomorphism, diff)
"""

from .traversal import (
    preorder_traversal,
    postorder_traversal,
    level_order_traversal,
    inorder_traversal_binary,
    zigzag_traversal,
    boundary_traversal,
)

from .search import (
    find_path,
    find_all_paths,
    find_lca,
    find_nodes_at_distance,
    find_by_predicate,
)

from .analysis import (
    tree_diameter,
    tree_height,
    tree_width,
    is_balanced,
    node_centrality,
    subtree_sizes,
)

from .generation import (
    random_tree,
    balanced_tree,
    complete_tree,
    full_tree,
    binary_search_tree,
    tree_from_edges,
)

from .comparison import (
    trees_equal,
    trees_isomorphic,
    tree_diff,
    structural_diff,
    find_common_subtrees,
    similarity_score,
    merge_trees,
)

__all__ = [
    # Traversal
    'preorder_traversal',
    'postorder_traversal',
    'level_order_traversal',
    'inorder_traversal_binary',
    'zigzag_traversal',
    'boundary_traversal',
    # Search
    'find_path',
    'find_all_paths',
    'find_lca',
    'find_nodes_at_distance',
    'find_by_predicate',
    # Analysis
    'tree_diameter',
    'tree_height',
    'tree_width',
    'is_balanced',
    'node_centrality',
    'subtree_sizes',
    # Generation
    'random_tree',
    'balanced_tree',
    'complete_tree',
    'full_tree',
    'binary_search_tree',
    'tree_from_edges',
    # Comparison
    'trees_equal',
    'trees_isomorphic',
    'tree_diff',
    'structural_diff',
    'find_common_subtrees',
    'similarity_score',
    'merge_trees',
]
