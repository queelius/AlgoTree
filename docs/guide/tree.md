# Tree API

The `Tree` class wraps a `Node` and provides additional functional operations.

## Creating Trees

```python
from AlgoTree import Tree, Node

# From Node
tree = Tree(Node("root", Node("a"), Node("b")))

# From string (creates single node)
tree = Tree("root")

# From dictionary
tree = Tree.from_dict({
    "name": "root",
    "value": 1,
    "children": [
        {"name": "a", "value": 2},
        {"name": "b", "value": 3}
    ]
})

# From paths
tree = Tree.from_paths([
    "root/src/main.py",
    "root/src/utils.py",
    "root/docs/README.md"
])
```

## Properties

```python
tree.root      # Root Node
tree.size      # Total node count
tree.height    # Tree height (max depth)
tree.leaves    # List of leaf nodes
tree.is_empty  # True if empty tree
```

## Functional Operations

### Map

```python
# Map function over all nodes
mapped = tree.map(lambda n: {"processed": True})

# Map can return:
# - dict: updates node attrs
# - Node: replaces node
# - None: keeps node unchanged
```

### Filter

```python
# Keep nodes matching predicate
# Note: preserves ancestors of matching nodes
filtered = tree.filter(lambda n: n.get("value", 0) > 5)
```

### Reduce

```python
# Reduce to single value
total = tree.reduce(
    lambda acc, node: acc + node.get("value", 0),
    initial=0,
    order="preorder"
)
```

### Fold

```python
# Bottom-up fold
sizes = tree.fold(lambda node, child_results: 1 + sum(child_results))
```

## Structure Operations

### Prune

```python
# Remove matching nodes
pruned = tree.prune("temp*")
pruned = tree.prune(lambda n: n.name.startswith("."))
```

### Graft

```python
# Add subtree to matching nodes
grafted = tree.graft("lib", Node("utils", Node("helpers")))
```

### Flatten

```python
# Flatten to max depth
flattened = tree.flatten(max_depth=2)
```

## Query Operations

```python
# Find first match
node = tree.find("config")
node = tree.find(lambda n: n.get("type") == "file")

# Find all matches
nodes = tree.find_all("*.py")
nodes = tree.find_all(lambda n: n.is_leaf)

# Check existence
if tree.exists("config"):
    pass

# Count matches
count = tree.count(lambda n: n.is_leaf)

# Select (returns iterator)
for node in tree.select("*.py"):
    print(node.name)
```

## Path Operations

```python
# Get node at path
node = tree.get_path("root/src/main.py")

# Get all paths
paths = tree.paths(to_leaves_only=True)
```

## Export

```python
# To dictionary
d = tree.to_dict()

# To paths
paths = tree.to_paths()
```

## Operators

```python
from AlgoTree import map_, filter_

# Pipe through transformer
result = tree | map_(lambda n: {"tagged": True})

# Chain transformers
result = tree >> map_(...) >> filter_(...)
```
