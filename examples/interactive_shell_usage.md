# AlgoTree Interactive Shell - Usage Guide

**Note:** This guide covers the interactive shell, which is designed for **exploration and learning**, not for scripting or automation. For programmatic use, see the [Python API documentation](../README.rst).

## When to Use the Shell

**Use the shell for:**
- Exploring tree structures interactively
- Learning AlgoTree operations
- Quick ad-hoc queries
- Visualizing tree structure
- Terminal-based workflows

**Use the Python API for:**
- Scripts and automation
- Production code
- Complex logic
- Integration with other Python code
- Testing and CI/CD

## Starting the Shell

There are several ways to start the AlgoTree shell:

### 1. From Python

```python
from AlgoTree import Node
from AlgoTree.shell import Forest, TreeShell

# Create some trees
tree1 = Node("root",
    Node("dir1", Node("file1"), Node("file2")),
    Node("dir2", Node("file3"))
)

tree2 = Node("Company",
    Node("Engineering", Node("Alice"), Node("Bob")),
    Node("Marketing", Node("Eve"))
)

# Create forest and shell
forest = Forest({
    "filesystem": tree1,
    "organization": tree2
})

shell = TreeShell(forest)
shell.run()
```

### 2. From Command Line

```bash
# Start with a tree file
algotree shell tree.json

# Or use the dedicated shell command
algotree-shell tree.json
```

## Interactive Session Example

Here's what an interactive session looks like:

```
$ python -m AlgoTree.shell.shell
AlgoTree Shell
Type 'help' for available commands, 'exit' to quit.

/ $ help
Available commands:

  cat: Display node attributes
  cd: Change directory
  depth: Show depth of current node
  descendants: Show descendants of current node
  exit (quit, q): Exit the shell
  filter: Filter nodes by predicate
  find: Find nodes matching a pattern
  height: Show height of current subtree
  help (?): Display help information
  leaves: Show all leaf nodes in subtree
  ls: List directory contents
  map: Apply transformation to all nodes
  mkdir: Create a new child node
  mktree: Create a new tree in the forest
  pwd: Print working directory
  rmtree: Remove a tree from the forest
  select: Select nodes matching a predicate
  siblings: Show sibling nodes
  size: Count nodes in current subtree
  stat: Display detailed node information
  touch: Create a new leaf node
  tree: Display tree structure

Use 'help <command>' for detailed information.

/ $ ls
filesystem
organization

/ $ cd filesystem
/filesystem $ pwd
/filesystem

/filesystem $ ls -l
dir1/  (2 children)
dir2/  (1 children)

/filesystem $ tree
root
├───── dir1
│      ├───── file1
│      └───── file2
└───── dir2
       └───── file3

/filesystem $ cd dir1
/filesystem/dir1 $ ls
file1
file2

/filesystem/dir1 $ pwd
/filesystem/dir1

/filesystem/dir1 $ cd ..
/filesystem $ pwd
/filesystem

/filesystem $ find file.*
file1
file2
file3

/filesystem $ select n.is_leaf
file1
file2
file3

/filesystem $ cd /organization
/organization $ tree
Company
├───── Engineering
│      ├───── Alice
│      └───── Bob
└───── Marketing
       └───── Eve

/organization $ cd Engineering
/organization/Engineering $ ls
Alice
Bob

/organization/Engineering $ siblings
Marketing

/organization/Engineering $ ancestors
Company

/organization/Engineering $ descendants
Alice
Bob

/organization/Engineering $ leaves
Alice
Bob

/organization/Engineering $ depth
1

/organization/Engineering $ height
1

/organization/Engineering $ size
3

/organization/Engineering $ stat
Name: Engineering
Path: /organization/Engineering
Depth: 1
Height: 1
Is Leaf: False
Is Root: False
Children: 2
Descendants: 2
Attributes: 0

/organization/Engineering $ cd /
/ $ mktree newtree custom_root
Created tree: newtree

/ $ ls
filesystem
newtree
organization

/ $ cd newtree
/newtree $ ls

/newtree $ mkdir child1
Created node: child1

/newtree $ mkdir child2
Created node: child2

/newtree $ tree
custom_root
├───── child1
└───── child2

/newtree $ cd child1
/newtree/child1 $ touch file
Created node: file

/newtree/child1 $ ls
file

/newtree/child1 $ cd /
/ $ rmtree newtree
Removed tree: newtree

/ $ ls
filesystem
organization

/ $ exit
Goodbye!
```

## Tab Completion Examples

The shell supports intelligent tab completion:

```
/ $ cd fi<TAB>
filesystem

/filesystem $ cd d<TAB><TAB>
dir1  dir2

/filesystem $ cd dir1<TAB>
/filesystem/dir1 $

/filesystem/dir1 $ ls <TAB><TAB>
file1  file2
```

## Advanced Operations

### Using Select

```
/organization $ select n.depth == 2
Alice
Bob
Eve

/organization $ select n.get('role', '') == 'Manager'
(assuming nodes have role attributes)
```

### Using Find

```
/filesystem $ find .*file.*
file1
file2
file3

/filesystem $ find dir.*
dir1
dir2
```

### Using Map (transforms tree)

```
/filesystem $ map n.with_name(n.name.upper())
Transformation applied

/filesystem $ tree
ROOT
├───── DIR1
│      ├───── FILE1
│      └───── FILE2
└───── DIR2
       └───── FILE3
```

### Using Filter (removes nodes)

```
/filesystem $ filter n.depth <= 1
Filter applied

/filesystem $ tree
root
├───── dir1
└───── dir2
```

## Pipeline Examples

Combine commands for more complex operations:

```
/filesystem $ find file.* | cat
(would show attributes for each matched file)

/organization $ descendants | select n.depth == 2
Alice
Bob
Eve

/filesystem $ leaves | select n.name.startswith('file')
file1
file2
file3
```

## Tips and Tricks

### 1. Navigation Shortcuts

- Use `/` to go to forest root
- Use `..` to go to parent
- Use absolute paths to jump anywhere: `cd /organization/Engineering`

### 2. Querying

- `select` for conditional filtering
- `find` for regex pattern matching
- `leaves` for leaf nodes only
- `descendants` for all descendants

### 3. Tree Inspection

- `tree` shows structure visually
- `stat` shows detailed info
- `cat` shows node attributes
- `ls -l` shows children with metadata

### 4. Creating Structures

- `mktree` creates new trees in forest
- `mkdir` creates internal nodes
- `touch` creates leaf nodes

### 5. Analysis

- `depth` shows current depth
- `height` shows subtree height
- `size` counts nodes
- `siblings` shows siblings

## Common Workflows

### Workflow 1: Exploring a Tree

```
$ algotree shell tree.json
/ $ ls                    # See available trees
/ $ cd my_tree           # Enter a tree
/my_tree $ tree          # Visualize structure
/my_tree $ size          # Count nodes
/my_tree $ find pattern  # Search for nodes
```

### Workflow 2: Building a Tree

```
/ $ mktree project
Created tree: project
/ $ cd project
/project $ mkdir src
/project $ mkdir docs
/project $ cd src
/project/src $ touch main.py
/project/src $ touch utils.py
/project/src $ cd ..
/project $ tree
```

### Workflow 3: Analyzing Structure

```
/my_tree $ depth                # Current depth
/my_tree $ height               # Subtree height
/my_tree $ size                 # Total nodes
/my_tree $ leaves               # All leaves
/my_tree $ descendants -d 2     # Limited depth
/my_tree $ select n.is_leaf     # Conditional query
```

### Workflow 4: Transforming Trees

```
/my_tree $ select n.get('value', 0) > 100
/my_tree $ map n.with_attrs(doubled=n.get('value', 0) * 2)
/my_tree $ filter n.depth <= 3
```

## Keyboard Shortcuts

- `Tab` - Complete command/path
- `Ctrl+C` - Cancel current line
- `Ctrl+D` - Exit shell
- `Ctrl+L` - Clear screen (if supported)
- `Up/Down` - Navigate command history
- `Ctrl+R` - Search command history (if supported)

## Getting Help

```
/ $ help               # List all commands
/ $ help cd            # Help for specific command
/ $ help select        # See expression syntax
```

## Exiting

```
/ $ exit              # Exit shell
/ $ quit              # Alternative
/ $ q                 # Short form
```

Or press `Ctrl+D`.

## Error Handling

When commands fail, you'll see helpful error messages:

```
/filesystem $ cd nonexistent
Error: Path not found: nonexistent

/filesystem $ select invalid.syntax
Error: Invalid expression: name 'invalid' is not defined

/ $ rmtree nonexistent
Error: Tree 'nonexistent' not found
```

## Next Steps

- Read [Shell README](../AlgoTree/shell/README.md) for full documentation
- Check out [Demo Script](shell_demo.py) for examples
- Try the [CLI tool](../AlgoTree/shell/cli.py) for one-off terminal operations

## Moving to Python API

If you find yourself wanting to automate shell operations, it's time to use the Python API:

```python
from AlgoTree import Tree, Node, load

# Load tree
tree = Tree(load('tree.json'))

# Navigate and query programmatically
node = tree.root.find('target_node')
leaves = list(tree.root.leaves())

# Full Python power
filtered = [n for n in tree.root.walk() if n.get('value', 0) > 100]

# Integration with other tools
import json
results = [{'name': n.name, 'value': n.get('value')} for n in filtered]
with open('results.json', 'w') as f:
    json.dump(results, f)
```

The Python API is more powerful, testable, and suitable for production use.
