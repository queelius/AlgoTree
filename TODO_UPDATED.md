# TODO

## Recently Completed ✅

### Core Architecture
- **New Node class** (`node.py`): Modern OOP design with proper attributes instead of dict inheritance
- **Fluent API** (`fluent.py`): 
  - TreeBuilder for intuitive tree construction with method chaining
  - FluentNode for chainable tree operations (filter/map/prune/sort)
- **Tree DSL** (`dsl.py`): Parse trees from three formats:
  - Visual format with Unicode tree characters
  - Indent-based format (YAML-like)  
  - S-expression format

### Pattern Matching (dotsuite-inspired)
- **Advanced pattern matching** (`pattern_matcher.py`):
  - Dot notation paths with escaping (`\.` for literal dots)
  - Wildcards: `*` (single), `**` (deep), `*.txt` (with suffix)
  - Attribute filters: `[type=file]`, `[size]` (existence)
  - Predicates: `[?(@.size > 1000)]`
  - Regex: `~pattern`, Fuzzy: `%match:threshold`
- **Pattern functions**: `dotmatch`, `dotpluck`, `dotexists`, `dotcount`, `dotfilter`

### Tree Transformations
- **Closed transformations** (`tree_transformer.py`):
  - `dotmod`: Modify specific nodes using dot paths
  - `dotmap`: Map transformations over matching nodes
  - `dotprune`: Remove nodes based on conditions
  - `dotmerge`: Merge trees with multiple strategies
  - `dotgraft`, `dotsplit`, `dotannotate`, `dotvalidate`, `dotnormalize`, `dotreduce`, `dotflatten`
  
- **Open transformations** (`tree_shaper.py`):
  - `dotpipe`: Pipeline for chaining transformations
  - Conversion functions: `to_dict`, `to_list`, `to_paths`, `to_table`, etc.
  - Data extraction: `dotextract`, `dotcollect`, `dotgroup`, `dotpartition`, `dotproject`

### Export & Visualization
- **Export formats** (`exporters.py`):
  - GraphViz DOT format
  - Mermaid diagram format
  - JSON, XML, YAML
  - HTML with optional styling
  - ASCII/Unicode tree visualization

### Documentation & Quality
- **Complete type hints**: Full typing support throughout the codebase
- **Comprehensive documentation**:
  - Pattern matching guide
  - Transformations guide
  - API reference
  - Cookbook with practical examples
- **Test coverage**: Full test suites for all new features

### Command-Line Tool
- **Enhanced jt tool**: Rewritten with fluent API (basic integration complete)

## In Progress 🚧

- **Update jt CLI tool**: Add new transformation functionality (dotmod, dotpipe, etc.)
  - Add --transform flag for dotmod operations
  - Add --pipe flag for dotpipe operations
  - Add --export-format for new export types

## High Priority 🔴

- **Forest-level operations**: Operations on collections of trees
  - `dotfilter` over multiple trees
  - `dothas` for existence checks across forests
  - Forest merging and comparison
  
- **Interactive REPL**: Tree manipulation REPL
  - Load/save trees
  - Interactive exploration with tab completion
  - Visual feedback for operations
  - History and undo/redo

## Medium Priority 🟡

- **Performance optimization**:
  - Benchmark transformation operations
  - Optimize pattern matching for large trees
  - Add caching for repeated operations
  
- **Advanced jt features**:
  - `jt --diff`: Show differences between trees
  - `jt --merge`: Interactive merge with conflict resolution
  - `jt --watch`: Watch file and auto-update on changes

## Low Priority 🟢

- **Enhanced DSL features**:
  - DSL for tree transformations (not just construction)
  - DSL validation with better error messages
  - Custom DSL definitions
  
- **Additional export formats**:
  - PlantUML diagrams
  - D3.js visualization data
  - LaTeX/TikZ tree diagrams

## Future Ideas 💡

- **Tree algebra**: Mathematical operations on trees
  - Union, intersection, difference
  - Tree isomorphism detection
  - Subtree mining algorithms
  
- **Tree database backend**: 
  - Persistent tree storage with indexing
  - Query optimization for large trees
  - Transaction support
  
- **Collaborative features**:
  - Real-time collaborative tree editing
  - Conflict resolution strategies
  - Change tracking and versioning
  
- **AI Integration**:
  - Natural language to tree transformations
  - Tree pattern learning
  - Automated tree optimization suggestions

## Breaking Changes for v2.0 🚨

- Remove legacy `TreeNode` and `FlatForest` classes
- Remove dict inheritance completely
- Standardize all APIs on new `Node` class
- Remove deprecated utility functions