# Expression Trees with `TreeNode`

In this tutorial, we will explore the concept of expression trees. We will demonstrate how they relate to our tree structures, specifically the `TreeNode` class, and how to evaluate expression trees using post-order traversal.

## Defining an Expression Tree

First, let's define our expression tree.

```python
from AlgoTree.treenode import TreeNode
expr = TreeNode({
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
                    "children": [{"type": "var", "value": "x"},
                                 {"type": "const", "value": 1}]
                },
                { "type": "const", "value": 0 }
            ]
        },
        {"type": "op",
         "value": "+",
         "children": [
             {"type": "op", "value": "*",
              "children": [{"type": "var", "value": "x"},
                           {"type": "var", "value": "y"}]},
             {"type": "const", "value": 3}, 
             {"type": "var", "value": "y"}],
        }
    ]
})
```

Here is what that looks like in a more convenient form.

```python
from AlgoTree.tree_viz import TreeViz
print(TreeViz.text(expr, node_name=lambda n: n.value))
```

```
+
├── max
│   ├── +
│   │   ├── x
│   │   └── 1
│   └── 0
└── +
    ├── *
    │   ├── x
    │   └── y
    ├── 3
    └── y
```

### Understanding the Expression Tree

The given expression tree represents an arithmetic expression, visually illustrating the order of operations.

1. **Expression Tree Structure**:
   - The root node is an addition (`+`).
   - The tree branches into sub-expressions with operations like `max`, `+`, and `*`, and operands like `x`, `y`, `1`, `0`, and `3`.

2. **Post-Order Evaluation**:
   - The expression is evaluated bottom-up, meaning each node is evaluated only after its children have been processed.
   - This ensures that all necessary values are available when an operation node is evaluated.

3. **Evaluation Steps**:
   - **Variables and Constants**: Variables (`x`, `y`) are replaced by their constant values.
   - **Operations**: Each operation node computes its value based on its children’s evaluated results.
     - Example: For the subtree `+ -> x, 1`, if `x = 1`, it becomes `1 + 1 = 2`.

## Tree Traversal

The `TreeNode` class provides an interface for tree traversal algorithms, including:

- Depth-first pre-order traversal
- 
- Depth-first post-order traversal

We will implement a simple post-order traversal algorithm to compute the expression tree `expr`. It contains three operator types (`+`, `*`, and `max`), numbers, and variables.

```python
def postorder(node, fn, ctx):
    """
    Applies function `fn` to the nodes in the tree using post-order traversal.
    
    :param node: The root node of the tree or subtree.
    :param fn: Function to apply to each node. Should accept two arguments: the node and the context.
    :param ctx: Context to pass to the function `fn`.
    :return: The tree with the function `fn` applied to its nodes.
    """
    # Recursively apply post-order traversal to the children
    node[TreeNode.CHILDREN_KEY] = [postorder(child, fn, ctx) for child in node.children()]
    # Apply the function to the current node
    return fn(node, ctx)
```

## Implementing the Evaluator

Next, we design a simple expression tree evaluator, `Eval`.

```python
from functools import reduce
from copy import deepcopy

class Eval:
    """
    An evaluator for expressions defined by operations on types, respectively
    defined by `Eval.Op` and `Eval.Type`. The operations are a
    dictionary where the keys are the operation names and the values are
    functions that take a node and a context and return the value of the
    operation in that context.
    """

    Op = {
        '+': lambda x: sum(x),
        '*': lambda x: reduce(lambda a, b: a*b, x),
        'max': lambda x: max(x)
    }

    Type = {
        'const': lambda node, _: node['value'],
        'var': lambda node, ctx: ctx[node['value']],
        'op': lambda node, _: Eval.Op[node['value']]([c['value'] for c in node.children()])
    }

    def __init__(self, debug=True):
        """
        :param debug: If True, print debug information
        """
        self.debug = debug
    
    def __call__(self, expr, ctx):
        
        def _eval(node, ctx):
            node_type = Eval.Type[node['type']]
            value = Eval.Type[node['type']](node, ctx)
            result = TreeNode(type='const', value=value)
            if self.debug:
                print(f"Eval({node.get_data()} -> {result.get_data()})")
            return result

        return postorder(deepcopy(expr), _eval, ctx)
```

## Running the Evaluator

To evaluate the expression tree, we define a context with variable values and call the evaluator.

```python
ctx = {
    "x": 1,
    "y": 2,
    "z": 3  
}
result = Eval(debug=True)(expr, ctx)
```

### Debugging Output

With debugging enabled, each node's evaluation is printed:

```cpp
Eval({'type': 'var', 'value': 'x'} -> {'type': 'const', 'value': 1})
Eval({'type': 'const', 'value': 1} -> {'type': 'const', 'value': 1})
Eval({'value': '+', 'type': 'op'} -> {'type': 'const', 'value': 2})
Eval({'type': 'const', 'value': 0} -> {'type': 'const', 'value': 0})
Eval({'value': 'max', 'type': 'op'} -> {'type': 'const', 'value': 2})
Eval({'type': 'var', 'value': 'x'} -> {'type': 'const', 'value': 1})
Eval({'type': 'var', 'value': 'y'} -> {'type': 'const', 'value': 2})
Eval({'type': 'op', 'value': '*'} -> {'type': 'const', 'value': 2})
Eval({'type': 'const', 'value': 3} -> {'type': 'const', 'value': 3})
Eval({'type': 'var', 'value': 'y'} -> {'type': 'const', 'value': 2})
Eval({'type': 'op', 'value': '+'} -> {'type': 'const', 'value': 7})
Eval({'value': '+', 'type': 'op'} -> {'type': 'const', 'value': 9})
```

### Evaluator Output

Printing the final result:

```python
print(result)
```

Yields:

```python
TreeNode({'type': 'const', 'value': 9})
```

The final value is `9`. This shows the tree has been transformed into a self-evaluating expression, ultimately resulting in a single node. This state is called **normal form**.

```python
assert Eval(debug=False)(result, ctx) == result
```

### The Meaning of Closure

Grounding symbols and relations in a specific context is known as a *closure*. If a variable is undefined, an error occurs.

```python
open_ctx = {
    'x': 1,
    #'y': 2,
    'z': 3
}

try:
    Eval(debug=True)(expr, open_ctx)
except KeyError as e:
    print(f'Error: {e}')
```

```cpp
Eval({'type': 'var', 'value': 'x'} -> {'type': 'const', 'value': 1})
Eval({'type': 'const', 'value': 1} -> {'type': 'const', 'value': 1})
Eval({'value': '+', 'type': 'op'} -> {'type': 'const', 'value': 2})
Eval({'type': 'const', 'value': 0} -> {'type': 'const', 'value': 0})
Eval({'value': 'max', 'type': 'op'} -> {'type': 'const', 'value': 2})
Eval({'type': 'var', 'value': 'x'} -> {'type': 'const', 'value': 1})
Error: 'y'
```

We encounter an error because `y` is not defined in the context.

### Conclusion

Post-order traversal is effective for evaluating expressions, while pre-order traversal is useful for rewriting trees from the top down. For example, a rewrite rule can simplify the expression `x + 0` to `x`. Such rules can optimize expressions or compile them into more efficient forms.

For more details on tree traversal algorithms, refer to [this comprehensive guide](https://csanim.com/tutorials/inorder-preorder-and-postorder-tree-traversals-animated-guide).