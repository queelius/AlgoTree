# Tree Construction

AlgoTree provides several ways to construct trees. The `builders.py` module was removed
in v2.0; all construction is now done through `Node`, `node()`, and class methods.

## Direct Construction with `Node`

```python
from AlgoTree import Node

tree = Node("root",
    Node("child1", attrs={"value": 1}),
    Node("child2", attrs={"value": 2})
)
```

## Convenience Function `node()`

`node()` auto-converts string arguments to leaf `Node` objects:

```python
from AlgoTree import node

tree = node("root",
    node("child1", value=1),
    "child2",           # string auto-converted to Node("child2")
    node("child3",
        "grandchild1",
        "grandchild2"
    )
)
```

## From a Dict

```python
from AlgoTree import Node

data = {
    "name": "root",
    "type": "directory",
    "children": [
        {"name": "src", "children": [
            {"name": "main.py", "type": "file", "size": 1024},
            {"name": "utils.py", "type": "file", "size": 512}
        ]},
        {"name": "docs", "children": [
            {"name": "README.md", "type": "file"}
        ]}
    ]
}

tree = Node.from_dict(data)
```

## From a List

```python
from AlgoTree import Node

# Nested list: [name, [child, child, ...]]
data = ["root", [
    ["src", [
        "main.py",
        "utils.py"
    ]],
    ["docs", [
        "README.md"
    ]]
]]

tree = Node.from_list(data)
```

## From Paths

Build a tree from a flat list of slash-delimited paths:

```python
from AlgoTree import Node

paths = [
    "project/src/main.py",
    "project/src/utils.py",
    "project/tests/test_main.py",
    "project/docs/README.md"
]

tree = Node.from_paths(paths)
```

A custom delimiter can be supplied as the second argument, e.g. `Node.from_paths(paths, ".")`.

## From DSL Text

```python
from AlgoTree import parse_tree

# Indent-based format
tree = parse_tree("""
root
  src
    main.py
    utils.py
  docs
    README.md
""", format="indent")

# S-expression format
tree = parse_tree("(root (src main.py utils.py) (docs README.md))",
                  format="sexp")
```

## Choosing an Approach

| Situation | Recommended approach |
|-----------|----------------------|
| Build by hand in code | `Node(...)` / `node(...)` |
| Load from JSON/dict | `Node.from_dict()` |
| Load from nested list | `Node.from_list()` |
| Load from file paths | `Node.from_paths()` |
| Parse from text | `parse_tree()` |
