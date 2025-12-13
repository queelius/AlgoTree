# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AlgoTree is a powerful Python library for working with tree structures, featuring an immutable-by-default API, composable transformations, and comprehensive tree operations. Version 2.0+ provides a clean, modern architecture following functional programming principles.

**Primary Interface:** The fluent Python API (Node, Tree, transformers, selectors) is the recommended approach for all scripting, automation, and programmatic use.

**Secondary Interface:** The interactive shell (AlgoTree.shell) is designed for interactive exploration, quick queries, and terminal-based workflows - not for scripting or automation.

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
python -m pytest test/

# Run a specific test file
python -m pytest test/test_node.py

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

### Interactive Shell (For Exploration Only)
```bash
# Start interactive shell for exploration
python -m AlgoTree.shell.shell

# Start shell with a tree file
algotree-shell tree.json

# Use CLI for one-off terminal operations
algotree ls tree.json
algotree tree tree.json
algotree select 'n.depth > 2' tree.json
```

**Note:** For scripting and automation, always use the Python API below, not the shell.

## Architecture (v2.0+)

### Core Components

1. **Immutable Node API**
   - `Node` (AlgoTree/node.py): Immutable tree nodes with functional operations
     - Constructor: `Node(name, *children, attrs={})`
     - Immutable transformations: `with_name()`, `with_attrs()`, `with_child()`, etc.
     - Tree operations: `map()`, `filter()`, `find()`, `find_all()`
     - Iteration: `walk()`, `descendants()`, `ancestors()`, `leaves()`
   - `node()` convenience function for creating nodes with mixed string/Node children

2. **Selectors** (AlgoTree/selectors.py)
   - Composable pattern matching for tree nodes
   - Basic selectors: `name()`, `attrs()`, `type_()`, `predicate()`
   - Structural selectors: `depth()`, `leaf()`, `root()`
   - Logical combinators: `&` (and), `|` (or), `~` (not), `^` (xor)
   - Structural combinators: `ChildOfSelector`, `ParentOfSelector`, etc.

3. **Transformers** (AlgoTree/transformers.py)
   - Tree → Tree transformers: `map_()`, `filter_()`, `prune()`, `graft()`, etc.
   - Tree → Any shapers: `reduce_()`, `fold()`, `extract()`, `to_dict()`, `to_paths()`
   - Composite transformers: `Pipeline`, `ParallelTransformer`, `RepeatTransformer`

4. **Builders** (AlgoTree/builders.py)
   - Fluent API for tree construction
   - `TreeBuilder`, `FluentTree`, `TreeContext`, `QuickBuilder`
   - Factory functions: `tree()`, `branch()`, `leaf()`

5. **Tree Wrapper** (AlgoTree/tree.py)
   - `Tree`: Wrapper providing functional operations and consistent API
   - Factory methods: `from_dict()`, `from_paths()`
   - Fluent API with method chaining

6. **DSL Support** (AlgoTree/dsl.py)
   - `TreeDSL`: Parse trees from text formats
   - Formats: visual (Unicode tree), indent-based, S-expression
   - `parse_tree()` convenience function

7. **Export & Visualization**
   - `exporters.py`: Export to GraphViz, Mermaid, JSON, XML, YAML, HTML
   - `pretty_tree.py`: ASCII/Unicode tree visualization
   - `serialization.py`: Save/load trees to/from files

8. **Interactive Shell** (AlgoTree/shell/) - For exploration, not scripting
   - `Forest`: Collection of named trees
   - `ShellContext`: Immutable navigation state
   - `TreeShell`: Interactive REPL with prompt_toolkit
   - Built-in commands: `cd`, `ls`, `pwd`, `cat`, `tree`, `find`, `select`, etc.
   - CLI tool: `algotree` for stateless terminal operations
   - **Use case:** Interactive exploration, learning, quick queries
   - **Not for:** Scripting, automation, production code
   - See `AlgoTree/shell/README.md` for full documentation

## API Examples

**Important:** These examples use the Python API, which is the recommended approach for all scripting and programmatic use. The shell is only for interactive exploration.

### Creating Trees

```python
from AlgoTree import Node, node

# Direct construction (immutable)
tree = Node("root",
    Node("child1", attrs={"value": 1}),
    Node("child2", attrs={"value": 2})
)

# Convenience function with mixed children
tree = node('root',
    node('child1', value=1),
    'child2',  # String auto-converted to Node
    node('child3',
        'grandchild1',
        'grandchild2'
    )
)
```

### Immutable Transformations

```python
# All operations return new trees
tree2 = tree.with_name("new_root")
tree3 = tree.with_attrs(status="active")
tree4 = tree.with_child(Node("new_child"))

# Map over all nodes
doubled = tree.map(lambda n: n.with_attrs(
    value=n.get("value", 0) * 2
))

# Filter nodes
filtered = tree.filter(lambda n: n.get("value", 0) > 5)
```

### Finding Nodes

```python
# Find first match
node = tree.find("child1")
node = tree.find(lambda n: n.get("value") > 5)

# Find all matches
nodes = tree.find_all("leaf*")  # Wildcard matching
nodes = tree.find_all(lambda n: n.is_leaf)
```

### Iteration

```python
# Various traversals
for node in tree.walk("preorder"):
    print(node.name)

for node in tree.walk("postorder"):
    process(node)

# Specific node types
for leaf in tree.leaves():
    print(leaf)

for ancestor in node.ancestors():
    print(ancestor)
```

### Export & Visualization

```python
from AlgoTree import export_tree, save_tree, pretty_tree

# Export to various formats
json_str = export_tree(tree, "json")
dot_str = export_tree(tree, "graphviz")
mermaid_str = export_tree(tree, "mermaid")

# Save to file
save_tree(tree, "tree.json")
save_tree(tree, "tree.dot")

# Pretty print
print(pretty_tree(tree))
```

## Testing Approach

- Unit tests in `test/` directory cover all major components
- Test files follow `test_*.py` naming convention
- Tests use pytest framework
- Run specific test methods: `python -m pytest test/test_node.py::TestNodeCreation::test_simple_node`

## API Design Principles

1. **Immutability**: All operations return new objects, never mutate existing ones
2. **Composability**: Small, focused functions that combine well
3. **Functional Style**: Prefer pure functions and method chaining
4. **Type Safety**: Full type hints for IDE support
5. **Clean Separation**: Node (data) vs Tree (operations) vs Transformers (algorithms)
6. **Python First**: The Python API is the primary interface for all programmatic use

## When to Use What

### Use Python API (Recommended for Development)

**For:**
- Scripts and automation
- Production code
- Complex transformations
- Integration with other Python code
- Testing and CI/CD
- Any programmatic usage

**Example:**
```python
from AlgoTree import Tree, Node, map_, filter_

tree = Tree(Node('root', Node('a'), Node('b')))
result = tree.filter(lambda n: n.depth > 0).map(lambda n: n.with_attrs(tagged=True))
```

### Use Shell (Interactive Exploration Only)

**For:**
- Interactive exploration of tree structures
- Quick ad-hoc queries
- Learning tree operations
- Terminal workflows
- Visualizing tree structure

**Example:**
```bash
$ algotree shell tree.json
> tree
> cd root
> find ".*"
> exit
```

**Rule of thumb:** If you're thinking about scripting shell commands, use the Python API instead.

## Migration from v1.x

The v2.0 API is a clean break from v1.x:

### Old API (v1.x)
```python
node = TreeNode(name="x", foo="bar")  # Arbitrary kwargs
node.add_child(child)  # Mutable operations
```

### New API (v2.0+)
```python
node = Node("x", attrs={"foo": "bar"})  # Explicit attrs
node = node.with_child(child)  # Immutable operations
```

## Important Reminders

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files (*.md) or README files unless explicitly requested
