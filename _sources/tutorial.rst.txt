AlgoTree: Comprehensive Tutorial
================================

.. contents:: Table of Contents
   :depth: 2
   :local:

1. Introduction
---------------

AlgoTree is a Python library that provides flexible and powerful tools for working with tree-like data structures. It offers various implementations of trees, along with utilities for manipulation, traversal, and visualization. The key feature of AlgoTree is its node-centric API, which provides a consistent interface across different tree implementations.

2. Installation
---------------

To install AlgoTree, use pip:

.. code-block:: bash

   pip install algotree

3. Core Concepts
----------------

Node-Centric API
^^^^^^^^^^^^^^^^

AlgoTree implements a node-centric API, which means that operations are performed from the perspective of individual nodes rather than the tree as a whole. This approach provides a consistent interface across different tree implementations and allows for intuitive navigation and manipulation of tree structures.

Tree Node Concept
^^^^^^^^^^^^^^^^^

In AlgoTree, a tree node must implement the following properties and methods:

- ``children``: A list of child nodes.
- ``parent``: The parent node (None for root nodes).
- ``node(name: str) -> NodeType``: Returns a node in the current subtree by name.
- ``root``: The root node of the current subtree.
- ``payload``: The data associated with the node.
- ``name``: An identifier for the node.
- ``contains(name) -> bool``: Checks if a node with the given name exists in the subtree.

Optional methods:

- ``subtree(name: Optional[str] = None) -> NodeType``: Returns a view of another subtree.

4. FlatForest: A Flexible Tree Structure
----------------------------------------

FlatForest represents a tree or forest using a flat dictionary structure.

.. code-block:: python

   from AlgoTree.flat_forest import FlatForest
   from AlgoTree.flat_forest_node import FlatForestNode

   data = {
       "A": {"parent": None, "data": "Root"},
       "B": {"parent": "A", "data": "Child of A"},
       "C": {"parent": "A", "data": "Another child of A"},
       "D": {"parent": "B", "data": "Child of B"}
   }

   forest = FlatForest(data)

   # Accessing nodes
   root = forest.subtree("A")
   print(root)  # FlatForestNode(name=A, parent=None, payload={'data': 'Root'}, root=A, children=['B', 'C'])

   # Adding a new node
   forest.node("C").add_child(name="E", data="Child of C")

   # Traversing the tree
   for node in forest.subtree("A").children:
       print(node.name, node.payload)

5. TreeNode: A Simple Recursive Tree Structure
----------------------------------------------

TreeNode provides a traditional recursive tree structure.

.. code-block:: python

   from AlgoTree.treenode import TreeNode

   root = TreeNode(name="root", payload={"value": 0})
   a = TreeNode(name="A", parent=root, payload={"value": 1})
   b = TreeNode(name="B", parent=root, payload={"value": 2})
   c = TreeNode(name="C", parent=a, payload={"value": 3})

   print(root.children)  # [TreeNode(name=A, ...), TreeNode(name=B, ...)]
   print(c.parent.name)  # A

   # Cloning a subtree
   cloned_a = a.clone()
   print(cloned_a)  # TreeNode(name=A, parent=None, root=A, payload={'value': 1}, len(children)=1)

6. Tree Traversal and Manipulation
----------------------------------

AlgoTree provides utility functions for tree traversal and manipulation:

.. code-block:: python

   from AlgoTree import utils

   # Get descendants
   descendants = utils.descendants(root)
   print([node.name for node in descendants])  # ['A', 'B', 'C']

   # Find leaves
   leaves = utils.leaves(root)
   print([node.name for node in leaves])  # ['C', 'B']

   # Get tree height
   height = utils.height(root)
   print(height)  # 2

   # Breadth-first traversal
   def print_node(node, level):
       print(f"Level {level}: {node.name}")
       return False

   utils.breadth_first(root, print_node)
   # Output:
   # Level 0: root
   # Level 1: A
   # Level 1: B
   # Level 2: C

7. Tree Visualization
---------------------

Use the ``pretty_tree`` function to visualize trees:

.. code-block:: python

   from AlgoTree.pretty_tree import pretty_tree

   print(pretty_tree(root, node_details=lambda n: n.payload['value']))

Output::

   root ◄ 0
   ├───── A ◄ 1
   │      └───── C ◄ 3
   └───── B ◄ 2

8. Tree Conversion
------------------

AlgoTree allows conversion between different tree representations:

.. code-block:: python

   from AlgoTree.tree_converter import TreeConverter

   # Convert FlatForest to TreeNode
   flat_forest_root = forest.subtree("A")
   tree_node_root = TreeConverter.convert(flat_forest_root, TreeNode)

   # Convert TreeNode to dictionary
   tree_dict = TreeConverter.to_dict(tree_node_root)
   print(tree_dict)

9. Advanced Features
--------------------

Node Hashing
^^^^^^^^^^^^

AlgoTree provides various hash functions for comparing nodes and trees:

.. code-block:: python

   from AlgoTree.node_hash import NodeHash

   # Assuming we have two nodes 'node1' and 'node2'
   print(NodeHash.name_hash(node1) == NodeHash.name_hash(node2))  # Compare nodes by name
   print(NodeHash.node_hash(node1) == NodeHash.node_hash(node2))  # Compare nodes by name and payload
   print(NodeHash.tree_hash(node1) == NodeHash.tree_hash(node2))  # Compare entire subtrees

10. Working with Subtrees
-------------------------

AlgoTree allows you to work with subtrees, maintaining consistency with the original tree:

.. code-block:: python

   # Using FlatForest
   subtree_B = forest.subtree("B")
   print(pretty_tree(subtree_B))

   # Add a child to the subtree
   subtree_B.add_child(name="F", data="Child of B")

   # The change is reflected in the original tree
   print(pretty_tree(forest.subtree("A")))

   # Using TreeNode
   subtree_A = root.node("A")
   print(pretty_tree(subtree_A))

   # Modify the subtree
   subtree_A.add_child(name="D", payload={"value": 4})

   # The change is reflected in the original tree
   print(pretty_tree(root))

11. Expression Trees and Evaluation
-----------------------------------

Let's create and evaluate an expression tree using AlgoTree:

.. code-block:: python

   expr = TreeNode.from_dict({
       "value": "+",
       "type": "op",
       "children": [
           {
               "value": "max",
               "type": "op",
               "children": [
                   {"type": "var", "value": "x"},
                   {"type": "const", "value": 1},
               ],
           },
           {
               "type": "op",
               "value": "+",
               "children": [
                   {"type": "var", "value": "y"},
                   {"type": "const", "value": 3},
               ],
           },
       ],
   })

   print(pretty_tree(expr, node_name=lambda x: x.payload["value"]))

   def evaluate(node, context):
       if node.payload["type"] == "const":
           return node.payload["value"]
       elif node.payload["type"] == "var":
           return context[node.payload["value"]]
       elif node.payload["type"] == "op":
           if node.payload["value"] == "+":
               return sum(evaluate(child, context) for child in node.children)
           elif node.payload["value"] == "max":
               return max(evaluate(child, context) for child in node.children)

   context = {"x": 2, "y": 5}
   result = evaluate(expr, context)
   print(f"Result: {result}")  # Should print: Result: 9

12. Conclusion
--------------

This tutorial has covered the main features of AlgoTree, demonstrating how to work with different tree implementations, traverse and manipulate trees, visualize tree structures, and even create and evaluate expression trees. The node-centric API provides a consistent interface across different tree types, making it easier to work with complex tree structures in Python.

Remember that AlgoTree is flexible and can be extended to suit various tree-based applications. Whether you're working on data structures, parsing, or any domain that requires hierarchical data representation, AlgoTree provides a solid foundation for your tree-related operations.