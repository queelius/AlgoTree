# API Reference

Complete API documentation for AlgoTree.

## Core Components

- [Node](node.md) - Immutable tree nodes
- [Tree](tree.md) - Tree wrapper with functional operations
- [Selectors](selectors.md) - Pattern matching for nodes
- [Transformers](transformers.md) - Composable tree operations

## Quick Import Reference

```python
from AlgoTree import (
    # Core
    Node, node, Tree,

    # Selectors
    name, attrs, type_, predicate,
    depth, leaf, root, any_, none,

    # Transformers
    map_, filter_, prune, graft,
    flatten, normalize, annotate,
    reduce_, fold, extract, to_dict, to_paths,

    # Builders
    TreeBuilder, FluentTree, TreeContext, QuickBuilder,
    tree, branch, leaf_node,

    # DSL
    parse_tree, TreeDSL,

    # Export
    export_tree, save_tree, pretty_tree,

    # Interop
    tree_to_graph, graph_to_tree,
    node_to_flat_dict, flat_dict_to_node,
)
```
