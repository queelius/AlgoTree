# Changelog

All notable changes to AlgoTree will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-18

### ⚠️ BREAKING CHANGES

This is a complete rewrite of AlgoTree with a modern, fluent API. The old dict-based 
`TreeNode` and `FlatForest` classes have been removed in favor of a cleaner design.

**To use the old API, install version 0.8.x:**
```bash
pip install "AlgoTree<1.0.0"
```

### Added

#### New Core Features
- **`Node` class**: Modern OOP tree node with clean API
  - Properties: `parent`, `children`, `is_root`, `is_leaf`, `level`, `siblings`
  - Traversal: `traverse_preorder()`, `traverse_postorder()`, `traverse_levelorder()`
  - Search: `find()`, `find_all()` with predicates
  - Conversion: `to_dict()`, `from_dict()` for JSON compatibility

- **`TreeBuilder` fluent API**: Intuitive tree construction
  ```python
  tree = (TreeBuilder()
      .root("company")
      .child("engineering")
          .child("frontend")
          .sibling("backend")
      .build())
  ```

- **`FluentNode` chainable operations**: Functional-style tree manipulation
  ```python
  FluentNode(tree)
      .descendants()
      .filter(lambda n: n.level > 2)
      .map(lambda n: {"size": n.payload.get("size", 0) * 2})
      .prune(lambda n: n.is_leaf)
  ```

- **Tree DSL parser**: Parse trees from text in multiple formats
  - Visual format with Unicode tree characters
  - Indent-based format (YAML-like)
  - S-expression format
  - Auto-detection of format

#### Pattern Matching (dotsuite-inspired)
- **Dot notation paths**: Navigate trees with intuitive syntax
- **Escaped dots**: Use `\.` for literal dots in node names
- **Pattern types**:
  - Wildcards: `*` (single), `**` (deep)
  - Attributes: `[type=file]`, `[size]` (existence)
  - Predicates: `[?(@.size > 1000)]`
  - Regex: `~pattern`
  - Fuzzy: `%match:threshold`
- **Functions**: `dotmatch`, `dotpluck`, `dotexists`, `dotcount`, `dotfilter`

#### Tree Transformations (Closed: Tree → Tree)
- **`dotmod`**: Modify specific nodes using dot paths
- **`dotmap`**: Map transformations over matching nodes
- **`dotprune`**: Remove nodes based on conditions
- **`dotmerge`**: Merge trees with multiple strategies
- **`dotgraft`**: Graft subtrees at specific points
- **`dotsplit`**: Split tree extracting subtrees
- **`dotannotate`**: Add metadata annotations
- **`dotvalidate`**: Validate tree constraints
- **`dotnormalize`**: Normalize node names
- **`dotreduce`**: Reduce tree to aggregate value
- **`dotflatten`**: Flatten tree structure

#### Tree Shaping (Open: Tree → Any)
- **`dotpipe`**: Pipeline for chaining transformations
- **Conversion functions**:
  - `to_dict`: Nested dictionary
  - `to_list`: Flat list
  - `to_paths`: Path strings
  - `to_table`: Tabular/DataFrame format
  - `to_adjacency_list`, `to_edge_list`: Graph representations
  - `to_nested_lists`: S-expression style
- **Data extraction**:
  - `dotextract`: Extract with custom functions
  - `dotcollect`: Collect/aggregate data
  - `dotgroup`: Group nodes by keys
  - `dotpartition`: Split into groups
  - `dotproject`: SQL-like projection

#### Export Formats
- **GraphViz**: DOT format for visualization
- **Mermaid**: Diagram generation
- **Data formats**: JSON, XML, YAML
- **Web**: HTML with optional styling
- **Text**: ASCII/Unicode tree visualization

#### Type Hints
- Complete type annotations throughout codebase
- Improved IDE support and type checking

#### Documentation
- Comprehensive fluent API guide (`source/fluent_api.rst`)
- Pattern matching guide (`source/pattern_matching.rst`)
- Transformations guide (`source/transformations.rst`)
- API reference (`source/api_reference.rst`)
- Cookbook with practical examples (`source/cookbook.rst`)
- Updated examples using modern API
- Migration warnings in README

#### Development
- Enhanced Makefile with:
  - Virtual environment management (`make venv`, `make venv-clean`)
  - Documentation serving (`make docs-serve`, `make docs-open`)
  - GitHub Pages deployment (`make docs-deploy-gh-pages`)
- Full test coverage for new features

### Removed
- **`TreeNode` class** (dict-based implementation)
- **`FlatForest` class** (dict-based implementation)
- **`FlatForestNode` class** (proxy pattern)
- All dict inheritance in tree structures

### Changed
- Complete API redesign focusing on clarity and usability
- Tree nodes are now proper objects, not dictionaries
- Simplified tree construction and manipulation
- More Pythonic and intuitive method names

## [0.8.0] - Previous Release

The last release with the original dict-based API. This version is still available for projects requiring backward compatibility.

### Features in 0.8.0
- `TreeNode`: Dict-based recursive tree structure
- `FlatForest`: Dict-based flat tree with parent pointers
- `FlatForestNode`: Proxy for node-centric API
- Tree conversion utilities
- Pretty printing
- `jt` command-line tool

---

## Migration Guide

### From 0.8.x to 1.0.0

#### Old API (0.8.x)
```python
from AlgoTree import TreeNode

# Dict-based node creation
root = TreeNode(name="root", data={"value": 100})
child = TreeNode(name="child", parent=root, data={"value": 50})

# Accessing data
print(root["data"]["value"])
```

#### New API (1.0.0)
```python
from AlgoTree import Node, TreeBuilder

# Object-based node creation
root = Node(name="root", value=100)
child = root.add_child(name="child", value=50)

# Accessing data
print(root.payload["value"])

# Or use TreeBuilder
tree = (TreeBuilder()
    .root("root", value=100)
    .child("child", value=50)
    .build())
```

### Key Differences

1. **No dict inheritance**: Nodes are proper objects with attributes
2. **Cleaner API**: `node.parent` instead of `node['parent']`
3. **Built-in methods**: Traversal, search, and manipulation methods
4. **Fluent interfaces**: Chainable operations for complex tasks
5. **DSL support**: Parse trees from text representations