# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AlgoTree is a powerful Python library for working with tree structures, featuring a modern fluent API, advanced pattern matching, and comprehensive tree transformations inspired by dotsuite. Version 1.0+ provides a complete redesign with clean OOP architecture.

## Key Commands

### Development Setup
```bash
# Install dependencies
make install
# or
pip install -r requirements.txt
```

### Testing
```bash
# Run all tests
make test
# or
python -m unittest discover -s test

# Run a specific test file
python -m unittest test.test_treenode

# Run with coverage
make coverage
```

### Linting
```bash
make lint
# or
python -m flake8 AlgoTree test
```

### Documentation
```bash
# Generate documentation
make docs
```

### Building and Distribution
```bash
# Build package
python setup.py sdist bdist_wheel

# Upload to PyPI
make pypi
```

## Architecture

### Core Components (v1.0+)

1. **Modern Tree API**
   - `Node` (AlgoTree/node.py): Clean OOP tree node class
   - `TreeBuilder` (AlgoTree/fluent.py): Fluent API for tree construction
   - `FluentNode` (AlgoTree/fluent.py): Chainable operations on trees
   - `TreeDSL` (AlgoTree/dsl.py): Parse trees from text formats

2. **Pattern Matching** (dotsuite-inspired)
   - `Pattern` & `PatternMatcher` (AlgoTree/pattern_matcher.py): Advanced pattern matching
   - Dot notation with escaping: `files.report\.pdf` for literal dots
   - Wildcards: `*` (single), `**` (deep), `*.txt` (with suffix)
   - Attributes: `[type=file]`, `[size]` (existence check)
   - Functions: `dotmatch`, `dotpluck`, `dotexists`, `dotcount`, `dotfilter`

3. **Tree Transformations**
   - `tree_transformer.py`: Closed transformations (tree→tree)
     - `dotmod`, `dotmap`, `dotprune`, `dotmerge`, `dotannotate`, etc.
   - `tree_shaper.py`: Open transformations (tree→any)
     - `dotpipe`, `to_dict`, `to_list`, `to_paths`, `dotextract`, etc.

4. **Export & Visualization**
   - `exporters.py`: Export to GraphViz, Mermaid, JSON, XML, YAML, HTML
   - `pretty_tree.py`: ASCII/Unicode tree visualization

5. **Legacy Components** (deprecated - will be removed in v2.0)
   - `FlatForest` (AlgoTree/flat_forest.py): Flat tree structure
   - `FlatForestNode` (AlgoTree/flat_forest_node.py): Node-centric proxy
   - `TreeNode` (AlgoTree/treenode.py): Dict-based recursive tree

6. **Utilities**
   - `utils.py`: Tree algorithms (traversal, search, LCA, pruning, etc.)
   - `tree_converter.py`: Convert between tree representations
   - `tree_hasher.py` & `node_hasher.py`: Tree hashing

7. **Command-Line Tool**
   - `jt` (bin/jt.py): Tree manipulation CLI tool
   - Supports queries, visualization, transformations
   - Usage: `jt [file] [options]`

## Testing Approach

- Unit tests in `test/` directory cover all major components
- Test files follow `test_*.py` naming convention
- Tests use Python's unittest framework
- Run specific test methods: `python -m unittest test.TestClass.test_method`