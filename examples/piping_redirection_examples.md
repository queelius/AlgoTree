# AlgoTree Shell: Piping and Redirection Guide

This document demonstrates the piping and redirection capabilities of the AlgoTree shell.

**Important:** This guide covers interactive shell features. For scripting and automation, use the [Python API](../README.rst) instead, which provides more power, type safety, and integration capabilities.

## Overview

The AlgoTree shell supports:
- **Piping** (`|`): Chain commands together, passing output from one to the next
- **Redirection** (`>`, `>>`): Redirect output to node attributes

These features enable powerful **interactive** data flows and exploration workflows.

---

## Piping

### Basic Syntax
```bash
command1 | command2 | command3
```

Each command's output becomes the input (`pipe_input` parameter) for the next command.

### Examples

#### Example 1: List and Filter
```bash
# List all nodes, then filter for those containing "test"
ls | find test
```

#### Example 2: Navigate and Query
```bash
# Change directory and list contents in one pipeline
cd src | ls
```

#### Example 3: Find Descendants with Pattern
```bash
# Get all descendants, then filter for .py files
descendants | find ".py"
```

#### Example 4: Complex Query Chain
```bash
# Multi-stage pipeline: list, get descendants, find leaves
ls | descendants | leaves
```

### Commands Supporting Piping

The following commands can receive piped input:
- `find` - Find nodes matching a pattern
- `select` - Select nodes by expression
- `descendants` - Show descendant nodes
- `leaves` - Show leaf nodes
- `ancestors` - Show ancestor nodes
- `siblings` - Show sibling nodes

Commands set `supports_piping() -> bool` to indicate pipe support.

---

## Redirection

### Basic Syntax

**Write (overwrite):**
```bash
echo text > attribute_key
```

**Append:**
```bash
echo text >> attribute_key
```

### How It Works

Redirection saves the output to a node attribute instead of displaying it:
- `>` overwrites any existing value
- `>>` appends to existing value (with newline separator)

### Examples

#### Example 1: Save a Note
```bash
# Create a note attribute on the current node
echo "This is a documentation node" > description
```

#### Example 2: Build a Log
```bash
# First entry
echo "2025-01-15: Created node" > changelog

# Add more entries
echo "2025-01-16: Updated attributes" >> changelog
echo "2025-01-17: Added children" >> changelog
```

#### Example 3: Document Configuration
```bash
# Add metadata to a node
echo "Production environment" > environment
echo "v2.1.0" > version
echo "active" > status
```

#### Example 4: Multi-line Content
```bash
# Each echo appends a new line
echo "Line 1" > content
echo "Line 2" >> content
echo "Line 3" >> content
```

### Viewing Redirected Content

Use `cat` to view attribute values:
```bash
cat description
cat changelog
```

Or use `stat` to see all attributes:
```bash
stat
```

---

## Combining Piping and Redirection

While you can't use `|` and `>` in the same command line (standard shell limitation), you can combine them in sequences:

### Example: Query and Document Results
```bash
# First, find something
find ".py"

# Then document what you found
echo "Found 5 Python files" > search_results
```

### Example: Build Documentation Workflow
```bash
# Navigate to docs directory
cd docs

# List files
ls

# Document the listing
echo "Documentation structure reviewed on 2025-01-15" > audit_log

# Check the result
cat audit_log
```

---

## Advanced Piping Patterns

### Pattern 1: Filter and Transform
```bash
# Get all descendants, filter by pattern, show only leaves
descendants | find "src" | leaves
```

### Pattern 2: Context Preservation
```bash
# Pipeline maintains context changes
cd src | ls | find ".py"
# The cd affects the context for subsequent ls
```

### Pattern 3: Long Pipelines
```bash
# You can chain many commands (tested up to 10+ stages)
ls | descendants | find "test" | leaves
```

---

## Error Handling

### Unknown Command in Pipeline
```bash
ls | unknown_cmd
# Error: Returns None, pipeline fails gracefully
```

### Failed Command in Pipeline
```bash
ls | cd /nonexistent
# Error: Pipeline stops at first failure
```

### Redirection Without Key
```bash
echo "text" >
# Error: Usage: echo <text> > <key>
```

### Redirection Outside a Tree
```bash
# At forest root (not in any tree)
echo "text" > key
# Error: Not in a tree
```

---

## Edge Cases and Gotchas

### 1. Quoted Arguments in Pipelines
```bash
# Use quotes for multi-word arguments
echo "hello world" | cat
```

### 2. Whitespace in Pipelines
```bash
# Extra whitespace is handled gracefully
ls   |   find test  |  leaves
```

### 3. Empty Pipeline Segments
```bash
# Trailing pipes are handled
ls |
# Treated as just 'ls'
```

### 4. Special Characters in Redirection
```bash
# Special characters work fine
echo "Hello! @#$%" > special_note
```

### 5. Empty String Redirection
```bash
# Redirecting empty string creates empty attribute
echo > empty_field
```

---

## Interactive Use Cases

These features enable powerful **interactive** command sequences. For scripting, use the Python API:

### Use Case 1: Build and Annotate Tree
```bash
# Create tree
mktree project

# Navigate in
cd project

# Build structure
mkdir src
mkdir docs
mkdir tests

# Document each directory
cd src
echo "Source code directory" > description

cd /project/docs
echo "Documentation directory" > description

cd /project/tests
echo "Test suite directory" > description
```

### Use Case 2: Query and Report
```bash
# Find all Python files
cd project
find ".py" | leaves

# Document the search
echo "Searched for Python files on 2025-01-15" > search_history
```

### Use Case 3: Bulk Operations
```bash
# Get all descendants and filter
descendants | find "old" | select 'n.depth > 2'

# Document the operation
echo "Identified nodes for cleanup" > cleanup_log
```

---

## Implementation Details

### Piping Infrastructure
- Defined in `AlgoTree/shell/commands.py`
- `Pipeline` class parses and executes command chains
- Uses `shlex` for proper quote handling
- Each command receives `pipe_input` parameter

### Redirection Implementation
- Implemented in `EchoCommand` (`AlgoTree/shell/builtins.py`)
- Writes to node attributes (not files)
- Uses immutable operations (`with_attrs()`)
- Properly updates tree structure

### Tested Features
- ✓ Basic piping (2-stage)
- ✓ Multi-stage pipelines (3-4+ stages)
- ✓ Error handling in pipelines
- ✓ Context preservation across pipes
- ✓ Basic redirection (>, >>)
- ✓ Append vs overwrite
- ✓ Special characters
- ✓ Edge cases

All features verified with 73 passing tests across:
- `test/test_shell_commands.py` (47 tests)
- `test/test_piping_redirection.py` (26 tests)

---

## For Scripting: Use the Python API

If you need scripting capabilities, use the Python API instead:

```python
from AlgoTree import Tree, load, save

# Load tree
tree = Tree(load('tree.json'))

# Complex transformations
result = (tree
    .filter(lambda n: not n.get('skip', False))
    .map(lambda n: n.with_attrs(processed=True))
    .prune(lambda n: n.name.startswith('test_')))

# Save result
save(result.root, 'output.json')

# Full error handling, logging, etc.
```

The Python API provides:
- Full Python language features
- Type safety and IDE support
- Error handling and logging
- Integration with Python ecosystem
- Testability and reproducibility

## Future Shell Enhancements

Potential additions for **interactive** use:

1. **Input redirection** (`<`): Read from attribute
2. **File I/O**: Redirect to actual files
3. **Background jobs**: `&`

**Note:** The shell is intentionally focused on interactive exploration, not scripting. For automation, use the Python API.

---

## Summary

The AlgoTree shell provides robust piping and redirection:

| Feature | Syntax | Status |
|---------|--------|--------|
| Basic piping | `cmd1 \| cmd2` | ✓ Implemented |
| Multi-stage piping | `cmd1 \| cmd2 \| cmd3 \| ...` | ✓ Implemented |
| Overwrite redirection | `echo text > key` | ✓ Implemented |
| Append redirection | `echo text >> key` | ✓ Implemented |
| Quoted arguments | `"multi word"` | ✓ Implemented |
| Error handling | Pipeline failures | ✓ Implemented |

These features provide a solid foundation for:
- Interactive tree navigation and querying
- Building documentation and metadata
- Complex multi-step operations
- Integration with external scripts

For scripting needs beyond the shell, use Python or Bash to orchestrate shell commands!
