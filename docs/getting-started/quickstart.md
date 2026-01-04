# Quick Start

This guide will get you up and running with AlgoTree in minutes.

## Creating Trees

### Using the Node Constructor

```python
from AlgoTree import Node

tree = Node("root",
    Node("src",
        Node("main.py", attrs={"size": 1024}),
        Node("utils.py", attrs={"size": 512})
    ),
    Node("docs",
        Node("README.md")
    )
)
```

### Using the Convenience Function

```python
from AlgoTree import node

# Strings auto-convert to nodes, kwargs become attrs
tree = node("root",
    node("src",
        node("main.py", size=1024),
        node("utils.py", size=512)
    ),
    "docs"  # Auto-converted to Node("docs")
)
```

### Parsing from Text

```python
from AlgoTree import parse_tree

# Visual format
tree = parse_tree("""
root
├── src
│   ├── main.py
│   └── utils.py
└── docs
    └── README.md
""")

# Indent format
tree = parse_tree("""
root
  src
    main.py
    utils.py
  docs
    README.md
""")

# S-expression format
tree = parse_tree("(root (src (main.py) (utils.py)) (docs (README.md)))")
```

## Traversing Trees

```python
# Walk all nodes
for node in tree.walk("preorder"):
    print(node.name)

# Just leaves
for leaf in tree.leaves():
    print(leaf.name)

# Just descendants
for desc in tree.descendants():
    print(desc.name)
```

## Finding Nodes

```python
# By name
node = tree.find("main.py")

# By predicate
large_files = tree.find_all(lambda n: n.get("size", 0) > 500)

# By pattern
py_files = tree.find_all("*.py")
```

## Transforming Trees

All transformations are immutable - they return new trees:

```python
# Add attributes
tagged = tree.map(lambda n: n.with_attrs(processed=True))

# Filter nodes
filtered = tree.filter(lambda n: n.get("size", 0) > 100)

# Remove nodes
pruned = tree.filter(lambda n: n.name != "utils.py")
```

## Visualizing Trees

```python
from AlgoTree import pretty_tree

print(pretty_tree(tree))
```

Output:
```
root
├── src
│   ├── main.py
│   └── utils.py
└── docs
    └── README.md
```

## Exporting Trees

```python
from AlgoTree import export_tree, save_tree

# To JSON string
json_str = export_tree(tree, "json")

# To GraphViz DOT
dot_str = export_tree(tree, "graphviz")

# Save to file
save_tree(tree, "tree.json")
save_tree(tree, "tree.dot")
```

## Next Steps

- [Node API](../guide/node.md) - Deep dive into Node operations
- [Selectors](../guide/selectors.md) - Pattern matching for nodes
- [Transformers](../guide/transformers.md) - Composable tree operations
