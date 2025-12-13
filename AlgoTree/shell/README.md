# AlgoTree Shell

A Linux-like command-line interface for **interactive exploration** of tree structures.

## Overview

The AlgoTree Shell provides a familiar shell environment for **interactively exploring and experimenting** with tree structures. It's designed for human interaction, quick queries, and learning tree structures - not for scripting or automation.

**When to use the shell:**
- Interactive exploration of tree structures
- Quick queries and visualization
- Learning and experimenting with tree operations
- Terminal-based workflows
- Ad-hoc analysis

**When NOT to use the shell (use the Python API instead):**
- Automation and scripting
- Production code
- Complex logic and transformations
- Integration with other Python code
- Testing and CI/CD pipelines
- Any programmatic usage

Navigate using `cd`, list contents with `ls`, query with `find`, and transform trees using powerful commands - all with tab completion and command history.

## Features

- **Forest Management**: Work with multiple named trees in a single session
- **Familiar Commands**: `cd`, `ls`, `pwd`, `cat`, `stat`, `tree`, `find`, and more
- **Tree Operations**: `map`, `filter`, `select` for transforming trees
- **Query Commands**: `ancestors`, `descendants`, `leaves`, `siblings`
- **Analysis**: `depth`, `height`, `size` for tree metrics
- **Pipeline Support**: Compose commands with `|` for complex operations
- **Tab Completion**: Auto-complete commands, paths, and tree names
- **Interactive REPL**: Built with prompt_toolkit for a great user experience
- **CLI Tool**: Stateless operations on tree files

## Quick Start

### Interactive Shell (Start Empty)

```python
from AlgoTree.shell import TreeShell

# Start with empty forest - build trees interactively!
shell = TreeShell()
shell.run()

# In the shell:
# $ mktree myproject
# $ cd myproject
# $ mkdir src
# $ mkdir docs
# $ tree
```

### Interactive Shell (With Existing Tree)

```python
from AlgoTree import Node
from AlgoTree.shell import Forest, TreeShell

# Create a tree
tree = Node("root",
    Node("dir1", Node("file1"), Node("file2")),
    Node("dir2", Node("file3"))
)

# Create forest and shell
forest = Forest({"my_tree": tree})
shell = TreeShell(forest)

# Run interactive shell
shell.run()
```

### Programmatic API

```python
from AlgoTree.shell import Forest, ShellContext
from AlgoTree.shell.builtins import LsCommand, CdCommand

# Create context
forest = Forest({"my_tree": tree})
ctx = ShellContext(forest)

# Navigate
ctx = ctx.cd("my_tree")
ctx = ctx.cd("dir1")

# Execute commands
ls = LsCommand()
result = ls.execute(ctx, [])
print(result.output)  # file1\nfile2
```

### CLI Tool

```bash
# Start empty shell - build trees from scratch!
algotree shell

# Or start with a tree file loaded
algotree shell tree.json

# One-off operations on tree files
algotree ls tree.json
algotree ls tree.json:/root/child1
algotree tree tree.json
algotree find ".*pattern.*" tree.json
algotree select 'n.depth > 2' tree.json
```

## Commands

### Navigation

- `pwd` - Print working directory
- `cd <path>` - Change directory
- `ls [path] [-l]` - List directory contents

### Read Operations

- `cat [path]` - Display node attributes
- `stat [path]` - Show detailed node information
- `tree [path] [-d depth]` - Display tree structure

### Write Operations

- `mkdir <name> [key=value ...]` - Create new child node with optional attributes
- `touch <name> [key=value ...]` - Create new leaf node with optional attributes
- `mktree <name> [root_name]` - Create new tree in forest
- `rmtree <name>` - Remove tree from forest
- `setattr <key>=<value> [...]` - Set or update node attributes
- `rmattr <key> [...]` - Remove node attributes

### Query Operations

- `find <pattern>` - Find nodes matching pattern (regex)
- `ancestors` - Show ancestors of current node
- `descendants [-d depth]` - Show descendants
- `leaves` - Show all leaf nodes
- `siblings` - Show sibling nodes

### Analysis

- `depth` - Show depth of current node
- `height` - Show height of subtree
- `size` - Count nodes in subtree

### Tree Operations

- `select <expression>` - Select nodes matching predicate
- `map <expression>` - Apply transformation to all nodes
- `filter <expression>` - Filter nodes by predicate

### Utilities

- `help [command]` - Show help information
- `exit` - Exit shell (aliases: `quit`, `q`)

## Path Syntax

Paths follow Unix-like conventions:

- `/` - Forest root (container of trees)
- `/tree_name` - Tree root
- `/tree_name/child1/child2` - Absolute path within tree
- `child1/child2` - Relative path
- `.` - Current directory
- `..` - Parent directory

## Expression Language

For `select`, `map`, and `filter` commands, use Python expressions with access to:

- `n` or `node` - The current node
- `n.name` - Node name
- `n.depth` - Depth in tree
- `n.height` - Height of subtree
- `n.is_leaf` - Whether node is a leaf
- `n.is_root` - Whether node is root
- `n.attrs` - Node attributes dict
- `n.get(key, default)` - Get attribute value
- `n.children` - List of child nodes

### Examples

```bash
# Select nodes at depth > 2
select n.depth > 2

# Select nodes with specific attribute
select n.get('value', 0) > 100

# Select leaf nodes
select n.is_leaf

# Select by name pattern
select n.name.startswith('test')

# Combine conditions
select n.depth > 1 and n.get('status') == 'active'
```

## Pipeline Support

Compose commands using pipes:

```bash
# Find all "test" nodes and show their attributes
find test.* | cat

# Get descendants and filter by depth
descendants | select n.depth == 2

# List and count
ls | wc -l
```

## Tab Completion

The shell provides intelligent tab completion for:

- Command names and aliases
- Tree names at forest root
- Child node names within trees
- Special paths like `..`

Press `Tab` to see suggestions, `Tab Tab` to cycle through options.

## Examples

### Example 1: File System Navigation

```python
from AlgoTree import Node
from AlgoTree.shell import Forest, TreeShell

# Create a file system-like tree
fs = Node("root",
    Node("home",
        Node("alice", Node("documents"), Node("photos")),
        Node("bob", Node("projects"))
    ),
    Node("var",
        Node("log"),
        Node("tmp")
    )
)

forest = Forest({"filesystem": fs})
shell = TreeShell(forest)

# In the shell:
# >>> ls
# filesystem
# >>> cd filesystem
# >>> tree
# >>> cd home/alice
# >>> ls
# documents
# photos
```

### Example 2: Organization Tree

```python
org = Node("Company",
    Node("Engineering",
        Node("Alice", attrs={"role": "Senior Dev"}),
        Node("Bob", attrs={"role": "Junior Dev"}),
    ),
    Node("Marketing",
        Node("Eve", attrs={"role": "Manager"}),
    )
)

# Query examples:
# >>> select n.get('role', '').startswith('Senior')
# Alice
# >>> descendants
# Engineering
# Alice
# Bob
# Marketing
# Eve
```

### Example 3: Tree Transformation

```python
tree = Node("root",
    Node("a", attrs={"value": 10}),
    Node("b", attrs={"value": 20}),
    Node("c", attrs={"value": 30}),
)

# In the shell:
# >>> select n.get('value', 0) > 15
# b
# c
# >>> map n.with_attrs(value=n.get('value', 0) * 2)
# Transformation applied
```

## Architecture

### Core Components

1. **Forest** - Collection of named trees
2. **TreePath** - Path parsing and resolution
3. **ShellContext** - Navigation state (immutable)
4. **Command** - Base class for all commands
5. **CommandRegistry** - Command management
6. **Pipeline** - Command composition
7. **TreeShell** - Interactive REPL
8. **CLI** - Stateless command-line tool

### Design Principles

- **Immutability**: All operations return new objects
- **Composability**: Small, focused commands that combine well
- **Familiarity**: Unix-like interface that feels natural
- **Type Safety**: Full type hints for IDE support
- **Extensibility**: Easy to add custom commands

## Adding Custom Commands

```python
from AlgoTree.shell.commands import Command, CommandResult

class MyCommand(Command):
    @property
    def name(self) -> str:
        return "mycommand"

    @property
    def description(self) -> str:
        return "My custom command"

    def execute(self, context, args, pipe_input=None):
        # Your logic here
        return CommandResult.ok(output="Hello!", context=context)

# Register and use
registry = create_builtin_registry()
registry.register(MyCommand())
shell = TreeShell(registry=registry)
```

## Integration with AlgoTree

The shell integrates seamlessly with AlgoTree's core functionality:

- Uses `Node` for immutable tree structures
- Uses `Tree` wrapper for operations
- Compatible with all exporters and serializers
- Works with trees created via builders, DSL, or `from_dict`

### From Shell to Python API

If you find yourself wanting to script shell operations, that's a sign you should use the Python API instead:

**Shell (Interactive):**
```bash
$ algotree shell data.json
> cd project
> find "*.py"
> select "n.get('lines', 0) > 100"
> tree
```

**Python API (Scripting):**
```python
from AlgoTree import Tree, load, name

# Same operations, but programmatic
tree = Tree(load('data.json'))
project = tree.root.find('project')

# More powerful with full Python
py_files = [n for n in project.walk() if n.name.endswith('.py')]
large_files = [f for f in py_files if f.get('lines', 0) > 100]

# Generate reports, integrate with other systems, etc.
for f in large_files:
    print(f"Large file: {f.path} ({f.get('lines')} lines)")
```

The Python API provides:
- Full Python language features
- Type safety and IDE support
- Error handling and logging
- Integration with Python ecosystem
- Testability and reproducibility

## Performance

- Navigation is O(1) for most operations
- Tree operations depend on tree size
- Path resolution is O(depth)
- Command execution is optimized for interactive use

## Limitations

- Expression evaluation uses `eval()` with restricted globals
- Large trees may be slow to display with `tree` command
- Pipeline support is basic (no advanced shell features like redirection)

## Future Enhancements

Potential additions for interactive use:

- More file operation commands (`cp`, `mv`, `rm`)
- Output redirection to files
- History search and navigation
- Undo/redo support
- Session saving and loading
- More sophisticated expression language
- Tree comparison and diff commands
- Export commands for various formats

**Note:** For scripting needs, use the Python API. The shell is intentionally focused on interactive use, not scripting automation.

## See Also

- [AlgoTree Documentation](../../README.md)
- [Examples](../../examples/shell_demo.py)
- [Tests](../../test/test_shell_core.py)
