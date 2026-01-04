# Selectors

Selectors provide composable pattern matching for finding nodes in trees.

## Basic Selectors

### Name Selector

Match nodes by name, with support for wildcards and regex:

```python
from AlgoTree import name

# Exact match
selector = name("config")

# Wildcard matching
selector = name("*.py")      # All .py files
selector = name("test_*")    # All test files

# Regex matching
selector = name(r"^test_\d+")  # test_1, test_2, etc.
```

### Attribute Selector

Match nodes by attributes:

```python
from AlgoTree import attrs

# Exact value match
selector = attrs(type="file")

# Multiple attributes
selector = attrs(type="file", size=1024)

# Predicate match
selector = attrs(size=lambda s: s > 500)

# Check existence
selector = attrs(metadata=None)  # Has metadata attr
```

### Type Selector

Match nodes by type attribute:

```python
from AlgoTree import type_

selector = type_("directory")
selector = type_("file")
```

### Predicate Selector

Custom matching logic:

```python
from AlgoTree import predicate

selector = predicate(lambda n: n.get("size", 0) > 1000)
selector = predicate(lambda n: "test" in n.name.lower())
```

### Structural Selectors

```python
from AlgoTree import depth, leaf, root

# Match by depth
selector = depth(2)           # Nodes at depth 2
selector = depth(range(1, 4)) # Depths 1, 2, or 3

# Match leaves
selector = leaf()

# Match root
selector = root()
```

## Combining Selectors

Selectors can be combined using logical operators:

### AND (`&`)

```python
from AlgoTree import name, attrs, leaf

# Python files that are leaves
selector = name("*.py") & leaf()

# Files larger than 1KB
selector = attrs(type="file") & attrs(size=lambda s: s > 1024)
```

### OR (`|`)

```python
# Python or JavaScript files
selector = name("*.py") | name("*.js")
```

### NOT (`~`)

```python
# Non-leaf nodes
selector = ~leaf()

# Not test files
selector = ~name("test_*")
```

### XOR (`^`)

```python
# Either a or b, but not both
selector = name("a") ^ name("b")
```

## Structural Combinators

### Child/Parent

```python
from AlgoTree import name, attrs

# Files that are direct children of src
selector = name("*.py").child_of(name("src"))

# Directories that contain Python files
selector = name("*").parent_of(name("*.py"))
```

### Descendant/Ancestor

```python
# Files anywhere under src
selector = name("*.py").descendant_of(name("src"))

# Directories that have any Python file descendants
selector = attrs(type="dir").ancestor_of(name("*.py"))
```

### Sibling

```python
# Nodes that have a README sibling
selector = name("*").sibling_of(name("README*"))
```

### At Depth

```python
# Python files at depth 3
selector = name("*.py").at_depth(3)
```

### Where (Add Constraints)

```python
# Files with specific attributes
selector = name("*.py").where(size=lambda s: s > 0)
```

## Using Selectors

### With Selector Methods

```python
selector = name("*.py") & leaf()

# Select all matching nodes
for node in selector.select(tree):
    print(node.name)

# Get first match
first = selector.first(tree)

# Count matches
count = selector.count(tree)

# Check existence
if selector.exists(tree):
    print("Found matching nodes")
```

### With Tree Methods

```python
from AlgoTree import Tree, name, leaf

tree = Tree(...)

# Find with selector
nodes = tree.find_all(name("*.py") & leaf())

# Filter with selector
filtered = tree.filter(name("*.py"))
```

## CSS-like Selector Parser

Parse CSS-like selector strings:

```python
from AlgoTree.selectors import parse

# By name
selector = parse("config")

# Wildcard
selector = parse("*.txt")

# Attribute
selector = parse("[type=file]")

# Direct child
selector = parse("src > main.py")

# Descendant
selector = parse("src main.py")

# Pseudo-selectors
selector = parse(":leaf")
selector = parse(":root")
```

## Selector Reference

| Selector | Description |
|----------|-------------|
| `name(pattern)` | Match by name |
| `attrs(**kw)` | Match by attributes |
| `type_(t)` | Match by type attribute |
| `predicate(fn)` | Custom predicate |
| `depth(d)` | Match by depth |
| `leaf()` | Match leaf nodes |
| `root()` | Match root node |
| `any_()` | Match all nodes |
| `none()` | Match no nodes |
