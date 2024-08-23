# AlgoTree Tutorial: Comprehensive Guide with Expression Trees

AlgoTree is a Python library that provides flexible and powerful tools for working with tree-like data structures. This updated tutorial will guide you through the main features of AlgoTree, including a practical application with expression trees.

## Table of Contents

1. [Installation](#1-installation)
2. [FlatForest: A Flexible Tree Structure](#2-flatforest-a-flexible-tree-structure)
3. [TreeNode: A Simple Recursive Tree Structure](#3-treenode-a-simple-recursive-tree-structure)
4. [Tree Traversal and Manipulation](#4-tree-traversal-and-manipulation)
5. [Tree Visualization](#5-tree-visualization)
6. [Tree Conversion](#6-tree-conversion)
7. [Advanced Features](#7-advanced-features)
8. [Working with FlatForest in Depth](#8-working-with-flatforest-in-depth)
9. [Algorithm Examples](#algorithm-examples)
10. [Expression Trees and Evaluation](#9-expression-trees-and-evaluation)


## 1. Installation

To install AlgoTree, you can use pip:

```bash
pip install AlgoTree
```

## 2. FlatForest: A Flexible Tree Structure

FlatForest is a core data structure in AlgoTree that represents a tree or forest using a flat dictionary structure.

### Creating a FlatForest

Let's start by creating a more complex FlatForest:

```python
from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode

data = {
    "1": { "data": 1, "parent": None},
    "2": { "parent": "1", "data": 2},
    "3": { "parent": "1", "data": 3},
    "4": { "parent": "3", "data": 4},
    "5": { "parent": "3", "data": 5},
    "A": { "data": "Data for A", "parent": None },
    "B": { "parent": "A", "data": "Data for B" },
    "C": { "parent": "A", "data": "Data for C" },
    "D": { "parent": "C", "data": "Data for D" },
    "E": { "parent": "C", "data": "Data for E" },
    "F": { "parent": "E", "data": "Data for F" },
    "G": { "parent": "E", "data": "Data for G" },
    "H": { "parent": "B", "data": "Data for H" },
    "I": { "parent": "A", "data": "Data for I" },
    "J": { "parent": "I", "data": "Data for J" },
    "K": { "parent": "G", "data": "Data for K" },
    "L": { "parent": "G", "data": "Data for L" },
    "M": { "parent": "C", "data": "Data for M" },
}

forest = FlatForest(data)

# Print the structure
for node in forest.nodes():
    print(node.name, node.payload, node.parent.name if node.parent is not None else None)
```

### Working with FlatForestNodes

```python
# Access specific nodes
node_C = forest.node("C")
print(node_C)

# Get children of a node
print(node_C.children)

# Get the logical root names
print(forest.logical_root_names())

# Get the preferred root
print(forest.preferred_root)

# Change the preferred root
forest.preferred_root = "A"
print(forest.preferred_root)
```

## 3. TreeNode: A Simple Recursive Tree Structure

TreeNode provides a more traditional recursive tree structure.

```python
from AlgoTree.treenode import TreeNode

root = TreeNode(name="root", payload=0)
A = TreeNode(name="A", parent=root, payload=1)
B = TreeNode(name="B", parent=root, payload=2)
C = TreeNode(name="C", parent=root, payload=3)
D = TreeNode(name="D", parent=C, payload=4)
E = TreeNode(name="E", parent=C, payload=5)
F = TreeNode(name="F", parent=C, payload="test")
G = TreeNode(name="G", parent=C, payload=7)
H = TreeNode(name="H", parent=C, payload=({1: 2}, [3, 4]))
I = TreeNode(name="I", parent=F, payload=9)

print(root)
```

## 4. Tree Traversal and Manipulation

AlgoTree provides various utility functions for tree traversal and manipulation:

```python
from AlgoTree import utils

# Get descendants
descendants = utils.descendants(forest.node("C"))
print([node.name for node in descendants])

# Get ancestors
ancestors = utils.ancestors(forest.node("I"))
print([node.name for node in ancestors])

# Get siblings
siblings = utils.siblings(forest.node("B"))
print([node.name for node in siblings])

# Get leaves
leaves = utils.leaves(root)
print([node.name for node in leaves])

# Get tree height
height = utils.height(root)
print(height)

# Get node depth
depth = utils.depth(forest.node("F"))
print(depth)

# Breadth-first traversal
def print_node(node, level):
    print(f"Level {level}: {node.name}")
    return False

utils.breadth_first(root, print_node)
```

## 5. Tree Visualization

AlgoTree includes a pretty printing functionality to visualize trees:

```python
from AlgoTree.pretty_tree import pretty_tree

print(pretty_tree(forest.subtree("A"), mark=["A", "G"], node_details=lambda node: node.payload['data']))
```

This will produce a nicely formatted tree representation with markers and node details.

## 6. Tree Conversion

AlgoTree allows conversion between different tree representations:

```python
from AlgoTree.tree_converter import TreeConverter

# Convert FlatForest to TreeNode
new_tree = TreeConverter.convert(forest.root, TreeNode)
print(pretty_tree(new_tree, node_details=lambda n: n.payload))

# Convert tree to dictionary
tree_dict = TreeConverter.to_dict(new_tree)
print(tree_dict)

# Convert dictionary back to TreeNode
treenode_from_dict = TreeNode.from_dict(tree_dict)
print(pretty_tree(treenode_from_dict))
```

## 7. Advanced Features

### Node Hashing

AlgoTree provides various hash functions for comparing nodes and trees:

```python
from AlgoTree.node_hash import NodeHash

# Compare nodes by name
print(NodeHash.name_hash(forest.node("A")) == NodeHash.name_hash(forest.node("B")))

# Compare nodes by name and payload
print(NodeHash.node_hash(forest.node("A")) == NodeHash.node_hash(forest.node("B")))

# Compare entire subtrees
print(NodeHash.tree_hash(forest.node("A")) == NodeHash.tree_hash(forest.node("B")))
```

## 8. Working with FlatForest in Depth

### Detaching and Reattaching Nodes

```python
# Detach a node
detached_node = forest.detach("D")
print(pretty_tree(forest.root))
print(pretty_tree(forest.detached))

# Reattach the node
detached_node.parent = forest.node("B")
print(pretty_tree(forest.root))
```

### Adding New Nodes

```python
# Add a new node
new_node = forest.node("A").add_child(name="N", data="Data for N")
print(new_node)

# Add a node with an automatically generated name
auto_named_node = forest.root.add_child(data="Auto-named node")
print(auto_named_node)
```

### Modifying Node Data

```python
# Modify node data
forest.node("A")["new_data"] = "Some new data for A"
print(forest.node("A").payload)

# Clear node data
forest.node("A").clear()
print(forest.node("A").payload)
```

## 9. Algorithm Examples

Let's explore some algorithm examples using AlgoTree:

### Finding Nodes within a Certain Distance

```python
f_nodes = utils.breadth_first_undirected(forest.node("F"), 2)
print([n.name for n in f_nodes])
```

### Creating a Subtree Rooted at a Node

```python
subtree_C = utils.subtree_rooted_at(forest.node("C"), 2)
print(pretty_tree(subtree_C, mark=["C"]))
```

### Creating a Subtree Centered at a Node

```python
center_C = utils.subtree_centered_at(forest.node("C"), 2)
print(pretty_tree(center_C, mark=["C"]))
```

### Mapping a Function Over Nodes

```python
def add_prefix(node):
    if node is None:
        return None
    elif node.name == "D":
        node.add_child(name="Q", value=41)
        node.add_child(name="R", value=42)
    elif node.name == "I" or node.name == "W":
        return None
    return node

root_mapped = utils.map(forest.root.clone(), add_prefix)
print(pretty_tree(root_mapped))
```

## 10. Expression Trees and Evaluation

Expression trees are a practical application of tree structures, particularly useful in mathematical and programming contexts. Let's explore how to create, visualize, and evaluate expression trees using AlgoTree.

### Creating an Expression Tree

First, let's create an expression tree using the TreeNode class:

```python
from AlgoTree.treenode import TreeNode

expr = TreeNode.from_dict(
    {
        "value": "+",
        "type": "op",
        "children": [
            {
                "value": "max",
                "type": "op",
                "children": [
                    {
                        "value": "+",
                        "type": "op",
                        "children": [
                            {"type": "var", "value": "x"},
                            {"type": "const", "value": 1},
                        ],
                    },
                    {"type": "const", "value": 0},
                ],
            },
            {
                "type": "op",
                "value": "+",
                "children": [
                    {
                        "type": "op",
                        "value": "max",
                        "children": [
                            {"type": "var", "value": "x"},
                            {"type": "var", "value": "y"},
                        ],
                    },
                    {"type": "const", "value": 3},
                    {"type": "var", "value": "y"},
                ],
            },
        ],
    }
)
```

### Visualizing the Expression Tree

We can use the `pretty_tree` function to visualize our expression tree:

```python
from AlgoTree.pretty_tree import pretty_tree

print(pretty_tree(expr, node_name=lambda x: x.payload["value"]))
```

This will produce a visualization like:

```
+
├───── max
│      ├───── +
│      │      ├───── x
│      │      └───── 1
│      └───── 0
└───── +
       ├───── max
       │      ├───── x
       │      └───── y
       ├───── 3
       └───── y
```

### Evaluating the Expression Tree

To evaluate the expression tree, we'll implement a simple evaluator using post-order traversal:

```python
def postorder(node, fn, ctx):
    results = []
    for child in node.children:
        result = postorder(child, fn, ctx)
        if result is not None:
            results.append(result)
    node.children = results
    return fn(node, ctx)

class Eval:
    Op = {
        "+": lambda x: sum(x),
        "max": lambda x: max(x),
    }

    Type = {
        "const": lambda node, _: node.payload["value"],
        "var": lambda node, ctx: ctx[node.payload["value"]],
        "op": lambda node, _: Eval.Op[node.payload["value"]](
            [c.payload["value"] for c in node.children]
        ),
    }

    def __init__(self, debug=True):
        self.debug = debug

    def __call__(self, expr, ctx):
        NodeType = type(expr)
        def _eval(node, ctx):
            expr_type = node.payload["type"]
            value = Eval.Type[expr_type](node, ctx)
            result = NodeType(type="const", value=value)
            if self.debug:
                print(f"Eval({node.payload}) -> {result.payload}")
            return result

        return postorder(expr.clone(), _eval, ctx)

# Evaluate the expression tree
ctx = {"x": 1, "y": 2, "z": 3}
result = Eval(debug=True)(expr, ctx)
print("Final result:", result.payload)
```

This evaluator will process the expression tree and output the intermediate steps if debug is set to True.

### Converting Between Tree Types

We can also convert our expression tree between different tree types:

```python
from AlgoTree.tree_converter import TreeConverter
from AlgoTree.flat_forest_node import FlatForestNode

# Convert TreeNode to FlatForestNode
flat_expr = TreeConverter.convert(source=expr, target_type=FlatForestNode, extract=lambda x: x.payload)
print(pretty_tree(flat_expr, node_name=lambda x: x.payload["value"]))

# Evaluate the flat forest expression
result = Eval(False)(flat_expr, ctx)
print("Result from FlatForest:", result.payload)
```

### Handling Undefined Variables

Let's see what happens when we try to evaluate the expression with undefined variables:

```python
open_ctx = {
    "x": 1,
    # 'y': 2,  # 'y' is not defined in this context
    "z": 3,
}

try:
    Eval(debug=True)(expr, open_ctx)
except KeyError as e:
    print(f"Error: {e}")
```

This will raise a KeyError for the undefined variable 'y'.

### Conclusion

Expression trees demonstrate a practical application of tree structures in AlgoTree. They show how we can represent complex expressions, visualize them, and perform operations like evaluation. This example also highlights the flexibility of AlgoTree, allowing us to work with different tree implementations (TreeNode and FlatForestNode) and convert between them seamlessly.

By understanding and working with expression trees, you can gain insights into how to use AlgoTree for other tree-based applications, such as parsing, compilers, or any domain where hierarchical data structures are useful.