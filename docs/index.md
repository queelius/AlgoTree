# AlgoTree

A powerful, modern tree manipulation library for Python with an immutable-by-default API.

## Features

- **Immutable by Default**: All operations return new objects, never mutate
- **Composable**: Small functions that combine with `>>`, `|`, `&` operators
- **Type Safe**: Full type hints for IDE support
- **Multiple Formats**: Parse trees from visual, indent, or S-expression formats
- **Rich Export**: JSON, GraphViz, Mermaid, HTML, and more

## Quick Start

```python
from AlgoTree import Node, parse_tree, pretty_tree

# Create trees with constructor
tree = Node("root",
    Node("src", Node("main.py"), Node("utils.py")),
    Node("docs", Node("README.md"))
)

# Or parse from text
tree = parse_tree("""
root
├── src
│   ├── main.py
│   └── utils.py
└── docs
    └── README.md
""")

# Visualize
print(pretty_tree(tree))

# Transform (immutably)
filtered = tree.filter(lambda n: not n.name.startswith("."))
with_attrs = tree.map(lambda n: n.with_attrs(visited=True))
```

## Installation

```bash
pip install AlgoTree
```

## What's New in v2.0

- **Immutable Nodes**: All operations return new nodes; originals are never modified
- **Composable Selectors**: Pattern matching with `&`, `|`, `~` operators
- **Pipeline Transformers**: Chain transformations with `>>` or `|`
- **DSL Parsing**: Parse trees from visual, indent, or S-expression formats
- **AlgoGraph Interop**: Convert trees to/from graph representations
- **Type Safety**: Full type hints for IDE support

## License

MIT License - see [LICENSE](https://github.com/queelius/AlgoTree/blob/master/LICENSE) for details.
