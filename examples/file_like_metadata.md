# File-Like Metadata in AlgoTree Shell

The AlgoTree shell treats node attributes as "files" - you can read, write, and manipulate them using familiar command-line operations.

## Key Concepts

- **Attribute keys are filenames**: Each attribute on a node acts like a file
- **Attribute values are file contents**: The value is what's "inside" the file
- **cat** reads attributes: `cat <key>` displays the value
- **echo** writes attributes: `echo <text> > <key>` creates/overwrites
- **readfile** loads from filesystem: Load real file content into attributes

## Basic Operations

### Creating Attributes with Echo

```bash
# Create a tree and node
$ mktree docs
$ cd /docs
$ mkdir readme

# Write an attribute using echo with redirection
$ echo This is the README content > description
$ echo v1.0.0 > version
$ echo MIT License > license
```

### Reading Attributes with Cat

```bash
# Read a specific attribute (file-like)
$ cat description
This is the README content

$ cat version
v1.0.0

# Read full node info (no argument)
$ cat
name: readme
attrs:
  description: This is the README content
  version: v1.0.0
  license: MIT License
children: 0
is_leaf: True
```

### Appending to Attributes

```bash
# Append adds a newline and the new text
$ echo >> description
$ echo Additional documentation here. >> description
$ echo See docs/ for details. >> description

$ cat description
This is the README content

Additional documentation here.
See docs/ for details.
```

## Loading from Real Files

### Using readfile

The `readfile` command (alias: `load`) loads content from the filesystem into an attribute.

```bash
# Create some content on disk
$ echo "import sys\nprint('Hello')" > /tmp/script.py

# Load it into a node attribute
$ mktree project
$ cd /project
$ mkdir scripts
$ cd scripts
$ readfile /tmp/script.py code

# View it
$ cat code
import sys
print('Hello')
```

## Practical Examples

### Example 1: Documentation System

```bash
# Create a documentation tree
$ mktree docs
$ cd /docs

# Create sections with content
$ mkdir introduction
$ cd introduction
$ echo Welcome to AlgoTree! > summary
$ echo This library provides tree operations. >> summary
$ echo See examples/ for tutorials. >> summary

# Create another section
$ cd ..
$ mkdir api
$ cd api
$ echo # API Reference > content
$ echo >> content
$ echo ## Node Class >> content
$ echo The Node class is immutable. >> content

# View the structure
$ cd /docs
$ tree
docs/
├── introduction/
└── api/

$ cd introduction
$ cat summary
Welcome to AlgoTree!
This library provides tree operations.
See examples/ for tutorials.
```

### Example 2: Configuration Management

```bash
$ mktree config
$ cd /config

# Store configuration values
$ mkdir database
$ cd database
$ echo localhost > host
$ echo 5432 > port
$ echo myapp > dbname

# View all configs
$ ls -la
host  [host=localhost]
port  [port=5432]
dbname  [dbname=myapp]

# Read specific config
$ cat host
localhost
```

### Example 3: Loading Source Code

```bash
# Load Python files into tree
$ mktree codebase
$ cd /codebase

$ mkdir utils
$ cd utils
$ readfile /path/to/helpers.py source
$ echo Python utilities > description
$ echo v2.1 > version

$ mkdir core
$ cd ../core
$ readfile /path/to/main.py source
$ echo Main application logic > description
$ echo v3.0 > version

# Query by version
$ cd /codebase
$ find -a "lambda n: n.get('version', '').startswith('v3')"
/codebase/core
```

### Example 4: Note-Taking System

```bash
$ mktree notes
$ cd /notes

# Quick notes using echo
$ mkdir today
$ cd today
$ echo Attended meeting with team > meeting
$ echo Review PR #123 >> meeting
$ echo Deploy staging environment >> meeting

# Multi-line notes
$ mkdir ideas
$ cd ../ideas
$ echo New feature: tree visualization > viz
$ echo >> viz
$ echo Could use D3.js or Graphviz >> viz
$ echo Need to support large trees >> viz

# View notes
$ cat meeting
Attended meeting with team
Review PR #123
Deploy staging environment

$ cat viz
New feature: tree visualization

Could use D3.js or Graphviz
Need to support large trees
```

## Comparison with Traditional Methods

### Old Way (setattr)
```bash
$ setattr description="My description" version=1.0
```

### New Way (file-like)
```bash
$ echo My description > description
$ echo 1.0 > version
```

### Benefits
1. **More intuitive**: Familiar command-line paradigm
2. **Multi-line support**: Echo naturally handles multiple lines
3. **File integration**: Load from real files with readfile
4. **Flexibility**: Append with `>>`, overwrite with `>`

## Command Reference

| Command | Syntax | Description |
|---------|--------|-------------|
| `cat` | `cat <key>` | Read attribute value |
| `cat` | `cat` | Show full node info |
| `echo` | `echo <text>` | Print text |
| `echo >` | `echo <text> > <key>` | Write/overwrite attribute |
| `echo >>` | `echo <text> >> <key>` | Append to attribute (with newline) |
| `readfile` | `readfile <path> <key>` | Load file content into attribute |
| `load` | `load <path> <key>` | Alias for readfile |

## Tips and Tricks

1. **Multi-word text**: No quotes needed with echo
   ```bash
   $ echo This is a long description > desc
   ```

2. **Empty values**: Create empty attributes
   ```bash
   $ echo > placeholder
   ```

3. **Combining approaches**: Mix file-like and traditional methods
   ```bash
   $ mkdir node name=mynode
   $ cd node
   $ echo Additional metadata > extra
   ```

4. **Viewing in ls**: Use `-a` or `-la` to see attributes
   ```bash
   $ ls -la
   node  [name=mynode, extra=Additional metadata]
   ```

5. **Attributes as state**: Track workflow states
   ```bash
   $ echo pending > status
   $ echo in_progress > status
   $ echo completed > status
   ```

## Advanced Usage

### Scripting with Echo
```bash
# Create a template structure
$ mktree template
$ cd /template
$ for section in intro body conclusion; do
    mkdir $section
    cd $section
    echo Edit this section > content
    cd ..
  done
```

### Loading Multiple Files
```bash
$ mktree src
$ cd /src
$ for file in *.py; do
    mkdir ${file%.py}
    cd ${file%.py}
    readfile $file code
    cd ..
  done
```

### Combining with Queries
```bash
# Find all nodes with 'status' attribute
$ find -a "lambda n: 'status' in n.attrs"

# Find completed items
$ find -a "lambda n: n.get('status') == 'completed'"
```

## Summary

The file-like metadata paradigm makes AlgoTree shell feel more like a traditional Unix shell while maintaining the power of tree operations. Attributes become first-class "files" that you can read, write, and manipulate with familiar commands.

Key advantages:
- **Intuitive**: Uses familiar `cat`, `echo`, `>`, `>>` syntax
- **Powerful**: Full integration with tree navigation and queries
- **Flexible**: Mix file-like and traditional attribute operations
- **Practical**: Load real files from filesystem into your tree structures
