Expression Trees and Evaluation
===============================

We are going to explore the idea of expression trees and how they relate
to our tree structures, namely ``TreeNode``, and to evaluate the
expression trees by rewriting the nodes in post-order traversal.

First, let’s define our expression tree.

.. code:: ipython3

    from AlgoTree.treenode import TreeNode
    from copy import deepcopy
    import json
    
    # Define the expression tree
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

.. code:: ipython3

    # Print the expression tree in JSON format
    print(json.dumps(expr.to_dict(), indent=4))


.. parsed-literal::

    {
        "name": "0a5c451b-cad1-48e9-9852-aec46058acda",
        "payload": {
            "value": "+",
            "type": "op"
        },
        "children": [
            {
                "name": "78baf6c2-afbd-4bb4-90a4-a08e5a3fc4e0",
                "payload": {
                    "value": "max",
                    "type": "op"
                },
                "children": [
                    {
                        "name": "fc106112-b614-467f-adff-c0c917ab03e5",
                        "payload": {
                            "value": "+",
                            "type": "op"
                        },
                        "children": [
                            {
                                "name": "30a87f4c-b4be-4217-8a24-0f0d258b2a25",
                                "payload": {
                                    "type": "var",
                                    "value": "x"
                                },
                                "children": []
                            },
                            {
                                "name": "41d8adc8-1f73-409a-ab68-ea98d53a1c56",
                                "payload": {
                                    "type": "const",
                                    "value": 1
                                },
                                "children": []
                            }
                        ]
                    },
                    {
                        "name": "5a8df89c-c833-4aae-8749-5ce307424675",
                        "payload": {
                            "type": "const",
                            "value": 0
                        },
                        "children": []
                    }
                ]
            },
            {
                "name": "1d223ec4-9daf-45f4-b2a8-9db394571b83",
                "payload": {
                    "type": "op",
                    "value": "+"
                },
                "children": [
                    {
                        "name": "dde50326-3af8-4544-9551-9aa8123ac2bd",
                        "payload": {
                            "type": "op",
                            "value": "max"
                        },
                        "children": [
                            {
                                "name": "f4057e80-3e19-477d-9b38-137b3a08d31e",
                                "payload": {
                                    "type": "var",
                                    "value": "x"
                                },
                                "children": []
                            },
                            {
                                "name": "f633d8d3-2a2e-474c-a44d-5da441854dcb",
                                "payload": {
                                    "type": "var",
                                    "value": "y"
                                },
                                "children": []
                            }
                        ]
                    },
                    {
                        "name": "1549bcb8-2ad7-45eb-a8f1-eef6aa53bbec",
                        "payload": {
                            "type": "const",
                            "value": 3
                        },
                        "children": []
                    },
                    {
                        "name": "7dc9523b-2ab5-4fef-8424-5f189f2e85f2",
                        "payload": {
                            "type": "var",
                            "value": "y"
                        },
                        "children": []
                    }
                ]
            }
        ]
    }


Visualizing the Tree Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can use the class ``PrettyTree`` (and a standalone ``pretty_tree``
function based on that class) to visualize the tree structure in a more
human-readable way.

.. code:: ipython3

    from AlgoTree.tree_converter import TreeConverter
    from AlgoTree.pretty_tree import pretty_tree

.. code:: ipython3

    print(pretty_tree(expr, node_name=lambda x: x.payload["value"]))


.. parsed-literal::

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
    


Post-order Traversal
~~~~~~~~~~~~~~~~~~~~

As a tree structure, ``TreeNode`` implements an interface that permits
tree traversal algorithms like depth-first pre-order and post-order
traversals.

We are going to implement a simple post-order traversal algorithm to
permit computation of the expression tree we defined earlier, ``expr``.
We see that it contains three operator types, ``+``, ``*``, and ``max``,
as well as numbers and variables.

We will provide a **closure** over all of these types so that when we
evaluate the expression in post-order, all of the types are defined for
the operations.

.. code:: ipython3

    def postorder(node, fn, ctx):
        """
        Applies function `fn` to the nodes in the tree using post-order traversal.
        :param fn: Function to apply to each node. Should accept one argument: the node.
        :param ctx: Context passed to the function.
        :return: The tree with the function `fn` applied to its nodes.
        """
        results = []
        for child in node.children:
            result = postorder(child, fn, ctx)
            if result is not None:
                results.append(result)
    
        node.children = results
        return fn(node, ctx)

The function ``postorder`` takes a tree node ``node``, a function
``fn``, and a context ``ctx``, and returns a rewritten tree.

At each node, ``postorder`` recursively calls ``fn`` on its children
before applying ``fn`` to the node itself. This is the essence of
post-order traversal.

Post-order is useful for problems where the children need to be
processed before the node itself. For example, evaluating an expression
tree, where typically the value of a node can only be computed after the
values of its children are known.

In contrast, pre-order traversal applies ``fn`` to the node before
applying it to the children. Pre-order may be useful for tasks such as
rewriting the tree in a different form, like algebraic simplification.

Expression Tree Evaluator
~~~~~~~~~~~~~~~~~~~~~~~~~

We will now design a simple expression tree evaluator, ``Eval``.

.. code:: ipython3

    class Eval:
        """
        An evaluator for expressions defined by operations on types, respectively
        defined by `Eval.Op` and `Eval.Type`. The operations are a
        dictionary where the keys are the operation names and the values are
        functions that take a node and a context and return the value of the
        operation in that context.
        """
    
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
            """
            :param debug: If True, print debug information
            """
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
    
            return postorder(deepcopy(expr), _eval, ctx)

To evaluate an expression tree, we need the operations to be defined for
all of the types during post-order (bottom-up) traversal. We can define
a closure over all of the types, and then use that closure to evaluate
the expression tree.

We call this closure a context. Normally, the operations and other
things are also defined in the closure, but for simplicity we will just
define the operations and provide closures over the variables.

.. code:: ipython3

    # Define the context with variable values
    ctx = {"x": 1, "y": 2, "z": 3}
    
    # Evaluate the expression tree with the context
    result = Eval(debug=True)(expr, ctx)


.. parsed-literal::

    Eval({'type': 'var', 'value': 'x'}) -> {'type': 'const', 'value': 1}
    Eval({'type': 'const', 'value': 1}) -> {'type': 'const', 'value': 1}
    Eval({'value': '+', 'type': 'op'}) -> {'type': 'const', 'value': 2}
    Eval({'type': 'const', 'value': 0}) -> {'type': 'const', 'value': 0}
    Eval({'value': 'max', 'type': 'op'}) -> {'type': 'const', 'value': 2}
    Eval({'type': 'var', 'value': 'x'}) -> {'type': 'const', 'value': 1}
    Eval({'type': 'var', 'value': 'y'}) -> {'type': 'const', 'value': 2}
    Eval({'type': 'op', 'value': 'max'}) -> {'type': 'const', 'value': 2}
    Eval({'type': 'const', 'value': 3}) -> {'type': 'const', 'value': 3}
    Eval({'type': 'var', 'value': 'y'}) -> {'type': 'const', 'value': 2}
    Eval({'type': 'op', 'value': '+'}) -> {'type': 'const', 'value': 7}
    Eval({'value': '+', 'type': 'op'}) -> {'type': 'const', 'value': 9}


Let’s print the final result of the evaluation of the expression tree.

.. code:: ipython3

    # Print the result of the evaluation
    print(result.payload)


.. parsed-literal::

    {'type': 'const', 'value': 9}


Self-Evaluating Trees
---------------------

We see that we get the expected result, ``9``. Note that it is still a
tree, but it has been transformed into a so-called self-evaluating tree
expression, which in this case is a single node with no children.

We can evaluate it again, and we see that it cannot be rewritten
further. We call this state a **normal form**. Essentially, we can think
of the tree as a program that computes a value, and the normal form is
the result of running the program.

.. code:: ipython3

    # Ensure the evaluated result is in its normal form
    assert Eval(debug=False)(result, ctx).payload == result.payload

Converting to FlatForest
~~~~~~~~~~~~~~~~~~~~~~~~

Let’s convert the tree to a ``FlatForest`` and perform the same
evaluation.

.. code:: ipython3

    from AlgoTree.flat_forest_node import FlatForestNode
    from AlgoTree.flat_forest import FlatForest
    flat_expr = TreeConverter.convert(source=expr, target_type=FlatForestNode, extract=lambda x: x.payload)
    print(pretty_tree(flat_expr, node_name=lambda x: x.payload["value"]))



.. parsed-literal::

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
    


Evaluate the flat forest expression

.. code:: ipython3

    result = Eval(False)(flat_expr, ctx)
    print(result.payload)


.. parsed-literal::

    {'type': 'const', 'value': 9}


The ``FlatForest`` structure is a different kind of structure that is
more convenient for relatively flatter data, like conversation logs. It
is a forest structure that is flattened into a dictionary of key-value
pairs, where the value is also a dictionary. This value dictionary
optionally contains the parent key, and if not then it is a root node.
If more than one root node is present, then it is a forest, but by
default it exposes a single root node (preferred root) for convenience,
which is by default the first root node encountered.

Handling Undefined Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What happens when we change the context so that not every variable is
defined?

.. code:: ipython3

    # Define an incomplete context with missing variable values
    open_ctx = {
        "x": 1,
        # 'y': 2,  # 'y' is not defined in this context
        "z": 3,
    }
    
    # Try evaluating the expression tree with the incomplete context
    try:
        Eval(debug=True)(expr, open_ctx)
    except KeyError as e:
        print(f"Error: {e}")


.. parsed-literal::

    Eval({'type': 'var', 'value': 'x'}) -> {'type': 'const', 'value': 1}
    Eval({'type': 'const', 'value': 1}) -> {'type': 'const', 'value': 1}
    Eval({'value': '+', 'type': 'op'}) -> {'type': 'const', 'value': 2}
    Eval({'type': 'const', 'value': 0}) -> {'type': 'const', 'value': 0}
    Eval({'value': 'max', 'type': 'op'}) -> {'type': 'const', 'value': 2}
    Eval({'type': 'var', 'value': 'x'}) -> {'type': 'const', 'value': 1}
    Error: 'y'


We see that we get an error. Our operations in ``Eval.Op`` are not
defined over undefined variables.

We would run into a similar problem if we used pre-order traversal
instead of post-order. In pre-order traversal, we would try to evaluate
the parent node (say, an operation) before we had evaluated its
children, which would result in an error. Our defined operations only
work over numbers (type ``const``), so we need to evaluate the
non-``const`` expressions first in order for our operations to be
defined for them.

Post-order vs. Pre-order Traversal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Post-order traversal is good for things like evaluating expressions,
where you need to evaluate the children before you can evaluate the
parent.

Pre-order traversal is good for things like rewriting trees from the top
down, but your rewrite rules need to be defined in terms of
sub-expression trees. So, for example, you might have a complex
expression and seek to rewrite it into a simpler form. This is an
example of a **rewrite system**. A rewrite system is a set of rules that
transform expressions into other expressions. For instance, suppose that
we add a ``0`` to a variable ``x`` in the expression tree. We know that
``x + 0`` is the same as ``x``, so we could add a rewrite rule that maps
the sub-tree ``(+ x 0)`` to ``x``. We could add many rewrite rules to
implement, for instance, algebraic simplification (``simplify``), or
implement a compiler (``compile``) that translates the tree into a
different form that could be evaluated by a different set of rewrite
rules. Or, the compiler could be an optimizing compiler that rewrites
the tree into a form that is more efficient to evaluate, like replacing
a multiplication by a power of two with a shift or getting rid of no-op
operations like adding zero.

Alternative Way To Construct Expression Trees
---------------------------------------------

We imported from a ``dict`` (or JSON) representation of the expression
tree. This is a common way to construct trees from data, and it is also
a common way to serialize trees to disk or to send them over the
network.

Howerver, we can also construct the tree directly using the ``TreeNode``
class.

.. code:: ipython3

    root = TreeNode(name="+", value="+", type="op")
    root_1 = TreeNode(name="max", value="max", type="op", parent=root)
    root_2 = TreeNode(name="+", value="+", type="op", parent=root)
    root_1_1 = TreeNode(name="+", value="+", type="op", parent=root_1)
    root_1_1_1 = TreeNode(name="var", value="x", type="var", parent=root_1_1)
    root_1_1_2 = TreeNode(name="const", value=1, type="const", parent=root_1_1)
    root_2_1 = TreeNode(name="max", value="max", type="op", parent=root_2)
    root_2_1_1 = TreeNode(name="var", value="x", type="var", parent=root_2_1)
    root_2_1_2 = TreeNode(name="var", value="y", type="var", parent=root_2_1)
    root_2_2 = TreeNode(name="const", value=3, type="const", parent=root_2)
    root_2_3 = TreeNode(name="var", value="y", type="var", parent=root_2)

Let’s evaluate this tree to see if it gives the same result as the
previous expression tree.

.. code:: ipython3

    result = Eval(False)(flat_expr, ctx)
    print(result.payload)


.. parsed-literal::

    {'type': 'const', 'value': 9}


Conclusion
----------

We have explored the idea of expression trees and how they relate to our
tree structures, namely ``TreeNode`` and ``FlatForestNode``, and how to
evaluate the expression trees by rewriting the nodes in post-order
traversal.

The ``TreeNode`` structure is a general-purpose tree structure that is
fast and efficient for these kinds of operations. The ``FlatForestNode``
structure is a more specialized structure that is more convenient for
relatively flatter data, like conversation logs.
