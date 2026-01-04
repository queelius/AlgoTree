# Node API

The `Node` class is the core building block of AlgoTree. Nodes are immutable - all operations return new nodes.

## Creating Nodes

### Basic Construction

```python
from AlgoTree import Node

# Simple node
node = Node("root")

# With children
node = Node("root",
    Node("child1"),
    Node("child2")
)

# With attributes
node = Node("root",
    Node("child1", attrs={"value": 1}),
    attrs={"type": "container"}
)
```

### Using the Convenience Function

```python
from AlgoTree import node

# kwargs become attrs, strings become nodes
tree = node("root",
    node("child1", value=1),
    "child2",  # String auto-converted
    type="container"
)
```

## Node Properties

```python
node.name        # Node name (str)
node.children    # Child nodes (tuple)
node.attrs       # Attributes (dict)
node.is_leaf     # True if no children
node.is_root     # True (nodes don't track parents)
node.size        # Total nodes in subtree
node.height      # Max depth of subtree
node.depth       # Always 0 for standalone nodes
node.path        # Path string from root
```

## Accessing Attributes

```python
# Get with default
value = node.get("key", default=0)

# Check existence
if "key" in node.attrs:
    pass
```

## Immutable Transformations

All methods return new nodes - the original is never modified:

```python
original = Node("root", attrs={"x": 1})

# Rename
renamed = original.with_name("new_name")

# Add/update attributes
with_attrs = original.with_attrs(y=2, z=3)

# Remove attribute
without = original.without_attr("x")

# Add child
with_child = original.with_child(Node("child"))

# Replace children
new_children = original.with_children(Node("a"), Node("b"))

# Remove child
without_child = original.without_child("child")
# or by index: original.without_child(0)
```

## Traversal

```python
# Walk tree (preorder, postorder, levelorder)
for n in node.walk("preorder"):
    print(n.name)

# Iterate children
for child in node.children:
    print(child.name)

# Get leaves
for leaf in node.leaves():
    print(leaf.name)

# Get all descendants
for desc in node.descendants():
    print(desc.name)
```

## Finding Nodes

```python
# Find first match
found = node.find("child_name")
found = node.find(lambda n: n.get("value") > 5)

# Find all matches
all_matches = node.find_all("pattern*")
all_matches = node.find_all(lambda n: n.is_leaf)
```

## Map and Filter

```python
# Map function over all nodes
doubled = node.map(lambda n: n.with_attrs(
    value=n.get("value", 0) * 2
))

# Filter (keeps ancestors of matching nodes)
filtered = node.filter(lambda n: n.get("value", 0) > 5)
```

## Conversion

```python
# To dictionary
d = node.to_dict()
# {'name': 'root', 'children': [...], ...attrs}

# From dictionary (use Tree.from_dict)
from AlgoTree import Tree
tree = Tree.from_dict({"name": "root", "children": [...]})
```
