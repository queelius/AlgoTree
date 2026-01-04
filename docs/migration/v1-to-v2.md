# Migration Guide: v1.x to v2.0

AlgoTree v2.0 introduces a modern, immutable-by-default API. This guide helps you migrate from v1.x.

## Key Changes

### 1. Immutability

**v1.x (Mutable)**:
```python
# Nodes were mutable
node = TreeNode(name="x")
node.add_child(child)  # Modified node in place
node.foo = "bar"       # Direct attribute assignment
```

**v2.0 (Immutable)**:
```python
# All operations return new nodes
node = Node("x")
node = node.with_child(child)       # Returns new node
node = node.with_attrs(foo="bar")   # Returns new node
```

### 2. Node Construction

**v1.x**:
```python
node = TreeNode(name="x", foo="bar", baz=123)
```

**v2.0**:
```python
# Attributes go in explicit attrs dict
node = Node("x", attrs={"foo": "bar", "baz": 123})

# Or use convenience function
node = node("x", foo="bar", baz=123)
```

### 3. Adding Children

**v1.x**:
```python
parent.add_child(child)
parent.children.append(child)
```

**v2.0**:
```python
parent = parent.with_child(child)
parent = parent.with_children(child1, child2, child3)
```

### 4. Removing Children

**v1.x**:
```python
parent.remove_child(child)
del parent.children[0]
```

**v2.0**:
```python
parent = parent.without_child("child_name")
parent = parent.without_child(0)  # By index
```

### 5. Modifying Attributes

**v1.x**:
```python
node.value = 10
node.type = "file"
del node.some_attr
```

**v2.0**:
```python
node = node.with_attrs(value=10, type="file")
node = node.without_attr("some_attr")
```

### 6. Renaming Nodes

**v1.x**:
```python
node.name = "new_name"
```

**v2.0**:
```python
node = node.with_name("new_name")
```

## API Mapping

| v1.x | v2.0 |
|------|------|
| `TreeNode(name, **kwargs)` | `Node(name, attrs={...})` |
| `node.add_child(child)` | `node.with_child(child)` |
| `node.remove_child(child)` | `node.without_child(child)` |
| `node.name = x` | `node.with_name(x)` |
| `node.foo = x` | `node.with_attrs(foo=x)` |
| `del node.foo` | `node.without_attr("foo")` |
| `node.children.append(x)` | `node.with_child(x)` |
| `node.foo` | `node.get("foo")` |

## Tree Class Changes

### v1.x Tree

```python
from AlgoTree import FlatForest

forest = FlatForest()
forest.add_node("root")
forest.add_node("child", parent="root")
```

### v2.0 Tree

```python
from AlgoTree import Tree, Node

tree = Tree(Node("root", Node("child")))

# Factory methods
tree = Tree.from_dict({"name": "root", "children": [...]})
tree = Tree.from_paths(["a/b/c", "a/b/d"])
```

## New Features in v2.0

### Selectors

Composable pattern matching:

```python
from AlgoTree import name, attrs, leaf

# Combine with operators
selector = name("*.py") & leaf()
nodes = tree.find_all(selector)
```

### Transformers

Reusable tree operations:

```python
from AlgoTree import map_, filter_, prune

pipeline = map_(fn) >> filter_(pred) >> prune(selector)
result = pipeline(tree)
```

### Pipe Operators

```python
result = tree | map_(fn)
result = tree >> map_(fn) >> filter_(pred)
```

### DSL Parsing

```python
from AlgoTree import parse_tree

tree = parse_tree("""
root
├── child1
└── child2
""")
```

### Export Formats

```python
from AlgoTree import export_tree, save_tree

dot = export_tree(tree, "graphviz")
save_tree(tree, "tree.json")
```

## Migration Patterns

### Pattern 1: Building Trees

**Before**:
```python
root = TreeNode("root")
child1 = TreeNode("child1", value=10)
child2 = TreeNode("child2", value=20)
root.add_child(child1)
root.add_child(child2)
```

**After**:
```python
root = Node("root",
    Node("child1", attrs={"value": 10}),
    Node("child2", attrs={"value": 20})
)
```

### Pattern 2: Modifying Trees

**Before**:
```python
for node in tree.walk():
    node.visited = True
```

**After**:
```python
tree = tree.map(lambda n: n.with_attrs(visited=True))
```

### Pattern 3: Filtering

**Before**:
```python
result = []
for node in tree.walk():
    if node.value > 10:
        result.append(node)
```

**After**:
```python
result = tree.find_all(lambda n: n.get("value", 0) > 10)
# Or
result = tree.filter(lambda n: n.get("value", 0) > 10)
```

### Pattern 4: Transformations

**Before**:
```python
def transform(node):
    node.value = node.value * 2
    for child in node.children:
        transform(child)
```

**After**:
```python
tree = tree.map(lambda n: n.with_attrs(
    value=n.get("value", 0) * 2
))
```

## Compatibility Layer

If you need to maintain v1.x compatibility during migration, you can create wrapper functions:

```python
def add_child(parent, child):
    """v1.x-style add_child as function."""
    return parent.with_child(child)

def set_attr(node, key, value):
    """v1.x-style attribute setting."""
    return node.with_attrs(**{key: value})
```

## Benefits of v2.0

1. **Predictability**: Immutable data is easier to reason about
2. **Thread Safety**: No shared mutable state
3. **Functional Composition**: Pipeline operators for clean code
4. **Better Testing**: Pure functions are easy to test
5. **Undo/History**: Keep old versions for free
6. **Type Safety**: Better IDE support with type hints

## Getting Help

- [Full API Documentation](../guide/node.md)
- [GitHub Issues](https://github.com/queelius/AlgoTree/issues)
