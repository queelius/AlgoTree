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
  - Predicates and regex matching

### Tree Transformations
- **Closed transformations** (`tree_transformer.py`):
  - `dotmod`: Modify specific nodes using dot paths
  - `dotmap`: Map transformations over matching nodes
  - `dotprune`: Remove nodes based on conditions
  - `dotmerge`, `dotgraft`, `dotsplit`, `dotannotate`, `dotvalidate`, `dotnormalize`, `dotreduce`, `dotflatten`
  
- **Open transformations** (`tree_shaper.py`):
  - `dotpipe`: Pipeline for chaining transformations
  - Conversion functions: `to_dict`, `to_list`, `to_paths`, `to_table`
  - Data extraction: `dotextract`, `dotcollect`, `dotgroup`, `dotpartition`, `dotproject`

### Export & Visualization
- **Export formats** (`exporters.py`):
  - GraphViz DOT format
  - Mermaid diagram format
  - JSON, XML, YAML
  - HTML with optional styling
  - ASCII/Unicode tree visualization

### Command-Line Tool
- **Enhanced jt tool** (`bin/jt.py`): 
  - Full integration with pattern matching
  - Support for all transformation operations
  - Multiple export formats
  - Pipeline operations for complex workflows
  - Tree navigation operations
  - Removed redundant legacy operations

### Documentation & Quality
- **Type hints**: Full typing support throughout new code
- **Comprehensive documentation**: Pattern matching, transformations, fluent API guides
- **Test coverage**: Tests for all new features

## Next Up 🎯

### Forest-level operations
- **Operations on collections of trees**:
  - `dotfilter` over multiple trees
  - `dothas` for existence checks across forests
  - Forest merging and comparison
  - Batch operations on tree collections

### Interactive REPL
- **Tree manipulation REPL**:
  - Load/save trees
  - Interactive exploration with tab completion
  - Visual feedback for operations
  - History and undo/redo
  - Live tree visualization

## Medium Priority 🟡

### Performance Optimization
- Benchmark transformation operations  
- Optimize pattern matching for large trees
- Add caching for repeated operations
- Profile and optimize hot paths

### Advanced jt Features
- `jt --diff`: Show differences between trees
- `jt --merge`: Interactive merge with conflict resolution
- `jt --watch`: Watch file and auto-update on changes
- `jt --serve`: HTTP API for tree operations

### Migration Tools
- Script to convert v0.8 code to v1.0
- Compatibility layer for gradual migration
- Documentation migration guide

## Low Priority 🟢

### Enhanced DSL Features
- Wildcards and regex patterns in DSL
- DSL for tree transformations (not just construction)
- DSL validation with better error messages
- Custom DSL definitions

### Additional Export Formats
- PlantUML diagrams
- D3.js visualization data
- LaTeX/TikZ tree diagrams
- JSON Schema generation

### Tree Analysis
- Structural similarity metrics
- Tree diff algorithms
- Pattern mining
- Statistical analysis tools

## Future Ideas 💡

### Tree Algebra
- Mathematical operations on trees (union, intersection, difference)
- Tree isomorphism detection
- Subtree mining algorithms
- Graph theory algorithms on trees

### Tree Database Backend
- Persistent tree storage with indexing
- Query optimization for large trees
- Transaction support
- Tree versioning

### Collaborative Features
- Real-time collaborative tree editing
- Conflict resolution strategies
- Change tracking and history
- Multi-user access control

### AI Integration
- Natural language to tree transformations
- Tree pattern learning
- Automated tree optimization suggestions
- Semantic tree analysis

## Breaking Changes for v2.0 🚨

- Remove legacy `TreeNode` and `FlatForest` classes completely
- Standardize all APIs on new `Node` class
- Remove all deprecated utility functions
- Clean up namespace (no more dict inheritance remnants)