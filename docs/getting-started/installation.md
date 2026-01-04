# Installation

## From PyPI

```bash
pip install AlgoTree
```

## From Source

```bash
git clone https://github.com/queelius/AlgoTree.git
cd AlgoTree
pip install -e .
```

## Optional Dependencies

### AlgoGraph Interoperability

For converting trees to/from graph representations:

```bash
pip install AlgoGraph
```

### Development

For development and testing:

```bash
pip install AlgoTree[dev]
```

## Verifying Installation

```python
from AlgoTree import Node, pretty_tree

tree = Node("hello", Node("world"))
print(pretty_tree(tree))
```

Output:
```
hello
└── world
```
