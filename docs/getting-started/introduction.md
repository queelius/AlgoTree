# Introduction

AlgoTree is a Python library for working with tree data structures. Version 2.0 introduces a modern, immutable-by-default API following functional programming principles.

## Core Principles

1. **Immutability**: All operations return new objects; nothing is mutated
2. **Composability**: Small functions that combine well using operators
3. **Functional Style**: Method chaining and pure functions
4. **Type Safety**: Full type hints for IDE support

## Core Components

### Node

The fundamental building block. Nodes are immutable - all operations return new nodes.

```python
from AlgoTree import Node

root = Node("root",
    Node("child1", attrs={"value": 1}),
    Node("child2", attrs={"value": 2})
)

# Immutable - returns new node
renamed = root.with_name("new_root")
```

### Tree

A wrapper that provides functional operations on nodes.

```python
from AlgoTree import Tree, Node

tree = Tree(Node("root", Node("a"), Node("b")))
filtered = tree.filter(lambda n: n.name != "b")
```

### Selectors

Composable pattern matching for finding nodes.

```python
from AlgoTree import name, attrs, leaf

# Combine selectors with operators
selector = name("config") & attrs(type="file")
matches = tree.find_all(selector)
```

### Transformers

Reusable, composable tree operations.

```python
from AlgoTree import map_, filter_, prune

pipeline = map_(lambda n: {"tagged": True}) >> filter_(lambda n: n.depth > 0)
result = pipeline(tree)
```

## Primary vs Secondary Interface

**Primary Interface (Recommended)**: The fluent Python API (`Node`, `Tree`, transformers, selectors) for all scripting, automation, and programmatic use.

**Secondary Interface**: The interactive shell (`AlgoTree.shell`) for exploration, quick queries, and terminal workflows - not for scripting or automation.
