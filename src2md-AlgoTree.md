# Project Directory: AlgoTree

## Documentation Files


### README.rst


'''markdown
AlgoTree
========

.. image:: https://img.shields.io/pypi/v/AlgoTree.svg
   :target: https://pypi.org/project/AlgoTree/

.. image:: https://img.shields.io/pypi/l/AlgoTree.svg
   :target: https://pypi.org/project/AlgoTree/

``AlgoTree`` is a Python package for working with tree structures, including
FlatForest and TreeNode representations.


Introduction
------------

Welcome to the documentation for the ``AlgoTree`` package. This package provides a
suite of utilities for working with tree-like data structures in Python. It
supports various tree representations, including:

- ``FlatForest`` and ``FlatForestNode`` for working with flat forest and tree structures
- ``TreeNode`` for recursive tree structures
- Conversion utilities to convert between different tree representations
- Utility functions for common tree operations

It also comes with a command-line tool ``jt`` that exposes most of the functionality:

- Can be used to create, manipulate, query, and visualize trees
- It's like ``jq`` but for trees
- Uses piping and redirection to make it easy to compose commands

Getting Started
---------------

To install the ``AlgoTree`` package, you can use pip:

.. code-block:: shell

   pip install AlgoTree

Once installed, you can start using the various tree structures and utilities
provided by the package. Here is a quick example to get you started:

.. code-block:: python

   from AlgoTree.flat_forest_node import FlatForestNode
   from AlgoTree.pretty_tree import pretty_tree
   root = FlatForestNode(name="root", data=0)
   node1 = FlatForestNode(name="node1", parent=root, data=1)
   node2 = FlatForestNode(name="node2", parent=root, data=2)
   node3 = FlatForestNode(name="node3", parent=node2, data=3)
   node4 = FlatForestNode(name="node4", parent=node3, data=4)

   pretty_tree(root)

This produces the output::

   root
   ├── node1
   └── node2
       └── node3
           └── node4

This code creates a simple tree with a root node and two child nodes. It then
pretty-prints the tree.

The ``AlgoTree`` package provides a wide range of tree structures and utilities
to help you work with tree-like data structures in Python. You can explore the
documentation to learn more about the available features and how to use them.

Features
--------

- Flexible tree structures with ``FlatForest``, ``FlatForestNode``, and ``TreeNode``
- Utility functions for common tree operations such as traversal, searching, and manipulation
- Conversion utilities to easily convert between different tree representations
- Integration with visualization tools to visualize tree structures


Node-Centric API
----------------

We implement two tree data structures:

- ``FlatForest`` for working with flat tree structures with
      "pointers" to parent nodes. It uses a proxy object ``FlatForestNode`` to
      provide a node-centric API.
- ``TreeNode`` for recursive tree structures, in which each node is a dictionary
      with an optional list of child nodes.

Each representation has its own strengths and weaknesses. The key design point
for ``FlatForest`` and ``TreeNode`` is that they are both also ``dict`` objects, i.e.,
they provide a *view* of dictionaries as tree-like structures, as long as the
dictionaries are structured in a certain way. We document that structure
elsewhere.

Each tree data structure models the *concept* of a tree node so that the
underlying implementations can be decoupled from any algorithms
or operations that we may want to perform on the tree.

The tree node concept is defined as follows:

- **children** property

      Represents a list of child nodes for the current node that can be
      accessed and modified[1_].

- **parent** property

      Represents the parent node of the current node that can be accessed
      and modified[2_]. 
      
      Suppose we have the subtree ``G`` at node ``G``::

            B (root)
            ├── D
            └── E (parent)
                └── G (current node)

      Then, ``G.parent`` should refer node ``E``. ``G.root.parent`` should be None
      since ``root`` is the root node of subtree ``G`` and the root node has no parent.
      This is true even if subtree ``G`` is a subtree view of a larger tree.

      If we set ``G.parent = D``, then the tree structure changes to::

            B (root)
            ├── D
            │   └── G (current node)
            └── E
      
      This also changes the view of the sub-tree, since we changed the
      underlying tree structure. However, the same nodes are still accessible
      from the sub-tree.

      If we had set ``G.parent = X`` where ``X`` is not in the subtree ``G``, then
      we would have an invalid subtree view even if is is a well-defined
      operation on the underlying tree structure. It is undefined
      behavior to set a parent that is not in the subtree, but leave it
      up to each implementation to decide how to handle such cases.

- **node(name: str) -> NodeType** method.

      Returns a node in the current subtree that the
      current node belongs to. The returned node should be the node with the
      given name, if it exists. If the node does not exist, it should raise
      a ``KeyError``.

      The node-centric view of the returned node should be consistent with the
      view of the current node, i.e., if the current node belongs to a specific sub-tree
      rooted at some other node, the returned node should also belong to the
      same sub-tree (i.e., with the same root), just pointing to the new node,
      but it should be possible to use ``parent`` and ``children`` to go up and down
      the sub-tree to reach the same nodes. Any node that is an ancestor of the
      root of the sub-tree remains inaccessible.

      Example: Suppose we have the sub-tree ``t`` rooted at ``A`` and the current node
      is ``B``::

            A (root)
            ├── B (current node)
            │   ├── D
            │   └── E
            |       └── G
            └── C
                └── F
      
      If we get node ``F``, ``t.node(F)``, then the sub-tree ``t`` remains the same,
      but the current node is now ``F``::
    
            A (root)
            ├── B
            │   ├── D
            │   └── E
            |       └── G
            └── C
                └── F (current node)

- **subtree(name: Optional[str] = None) -> NodeType** method.

      This is an optional method that may not be implemented by all tree
      structures. ``FlatForestNode`` implements this method, but ``TreeNode`` does
      not.

      Returns a view of another sub-tree rooted at ``node`` where ``node`` is
      contained in the original sub-tree view. If ``node`` is ``None``, the method
      will return the sub-tree rooted at the current node.

      As a view, the subtree represents a way of looking at the tree structure
      from a different perspective. If you modify the sub-tree, you are also
      modifying the underlying tree structure. The sub-tree should be a
      consistent view of the tree, i.e., it should be possible to use ``parent``
      and ``children`` to navigate between the nodes in the sub-tree and the
      nodes in the original tree.
      
      ``subtree`` is a *partial function* over the the nodes in the sub-tree,
      which means it is only well-defined when ``node`` is a descendant of
      the root of the sub-tree. We do not specify how to deal with the case
      when this condition is not met, but one approach would be to raise an
      exception.

      Example: Suppose we have the sub-tree `t` rooted at `A` and the current node
      is `C`::

            A (root)
            ├── B
            │   ├── D
            │   └── E
            |       └── G
            └── C (current node)
                └── F

      The subtree `t.subtree(B)` returns a new subtree::

            B (root, current node)
            ├── D
            └── E
                └── G

- **root** property

      An immutable property that represents the root node of the (sub)tree.
      
      Suppose we have the subtree ``G`` at node ``G``::

            B (root)
            ├── D
            └── E
                └── G (current node)

      Then, `G.root` should refer node `B`.

- **payload** property

      Returns the payload of the current node. The payload
      is the data associated with the node but not with the structure of the
      tree, e.g., it does not include the ``parent`` or ``children`` of the node.

- **name** property

      Returns the name of the current node. The name is
      an identifier for the node within the tree. It is not necessarily unique,
      and nor is it necessarily even a meaningful identifier, e.g., a random
      UUID.
      
      In ``TreeNode``, for instance, if the name is not set, a UUID is generated.

.. [1] Modifying this property may change the **parent** property of other nodes.

.. [2] Modifying this property may change the **children** property of other nodes.
'''

### TODO.md


'''markdown
# TODO

- `TreeDot`: I may want to create a tree structure called `TreeDot` that wraps any tree-like structure that models the node-centric API, and is specialized for visualization. But, no compelling reason to do this yet, so I'll leave it as a TODO.

- `jsontree.py` command line tool should be expanded. It is based mostly on piping and redirection. For any operation that modifies
the tree, it will output the modified tree as a JSON string. This also allows it to be used with other tools, like `jq` for filtering and selecting.
Since it also has a nice looking unicode tree output, it can be used to visualize trees in the
terminal as well. I have something like this in mind:

      - `jsontree --edit` - edit a JSON tree

      - `jsontree --merge` - merge two JSON trees using `TreeConverter`.

      - `json-tree --filter` - filter a JSON tree 

      - `json-tree --query` - query a JSON tree.maybe this one can use JMESPath for querying and also be able to output node paths (search orders) and subtrees.
'''

### source/index.rst


'''markdown
.. Treekit documentation master file, created by
   sphinx-quickstart on Thu Jun  3 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to AlgoTree's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   introduction
   flat_forest
   treenode
   tutorial
   flat_forest_nb
   expr_trees_nb
   identity
   jt

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
'''

### source/tutorial.rst


'''markdown
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

Remember that AlgoTree is flexible and can be extended to suit various tree-based applications. Whether you're working on data structures, parsing, or any domain that requires hierarchical data representation, AlgoTree provides a solid foundation for your tree-related operations.'''

### source/flat_forest.rst


'''markdown
FlatForest
==========

The `FlatForest` class represents a forest (set of tree-like objects) using a
flat dictionary structure where each node has a unique key and an optional
'parent' key to reference its parent node. This class provides a view adapter
for dict/JSON data of a particular format.

Tree Data Format
----------------

A `FlatForest` is represented using a dictionary, where each key is a unique
node identifier, and the value is another dictionary containing node data and
an optional 'parent' key indicating the parent node.

.. code-block:: python

    {
      "<node_key>": {
          "parent": "<parent_node_key>",  # Parent node key (optional)
          "<key>": "<value>", # Node payload (optional key-value pairs)
          "...": "...",
          "<key>": "<value>"
      },
      "...": "...",
      "<node_key>": {
          "parent": "<parent_node_key>",
          "<key>": "<value>",
          "...": "...",
          "<key>": "<value>"
      }      
      # ... more node key-value pairs
    }

Example Forest Data:

.. code-block:: json

    {
      "node1": {
        "data": "Some data for node1"
      },
      "node2": {
        "data": "Some data for node2"
      },
      "node3": {
        "parent": "node1",
        "data": "Some data for node3"
      },
      "node4": {
        "parent": "node3",
        "data": "Some data for node4"
      },
      "node5": {
        "parent": "node3",
        "data": "Some data for node5"
      }
    }

Theoretical Background
----------------------

Trees are hierarchical data structures consisting of nodes, where
each node has a parent and potentially many children. Trees are used in various
domains such as databases, file systems, and network routing. They are
particularly useful for representing data with a nested or hierarchical nature.

Tree Terminology

- **Node:** A structure that contains data and references to its parent. A tree is a collection of nodes related by parent-child relationships.
- **Root:** The top node of a tree.
- **Leaf:** A node with no children.

Proxy Objects and Views
^^^^^^^^^^^^^^^^^^^^^^^

In computer science, a proxy object is an object that acts as an intermediary
for another object. The proxy can control access to the original object,
providing additional functionality such as validation, lazy loading, or caching.
This is a common design pattern used to create a level of indirection.

A view in this context is an abstraction that provides a different perspective
or representation of the underlying data. For example, a view can present a flat
dictionary as a hierarchical tree structure.

`FlatForestNode` Proxies
""""""""""""""""""""""""

The `FlatForestNode` is a proxy class for providing a node-centric view of `FlatForest`
objects. It allows you to treat nodes as first-class objects while maintaining
the underlying flat dictionary structure. You do not even need to be aware
of `FlatForest` objects, since you can create and manipulate nodes directly,
but these operations are reflected in the underlying `FlatForest`, which may
be accessed if needed using the `forest` attribute.

Key Features:

- **Encapsulation:** Provides methods to manipulate individual nodes.
- **Abstraction:** Hides the complexity of the flat dictionary structure, presenting a more intuitive tree-like interface.
- **Flexibility:** Allows you to work with sub-trees and individual nodes seamlessly.

Root Node
^^^^^^^^^

In `FlatForest`, there can be multiple roots (multiple trees). These roots are
the nodes that have no parent. They can be accessed with the `roots` and
`root_names` attributes.

`FlatForest` also exposes itself as a tree-like structure, where the
default behavior is to treat the first root node found as the tree. This may
be overridden by changing the `preferred_root` attribute.
 
We also provide an `as_tree` method to merge all of the trees in the forest
under a new root node, which can be useful if a tree-like structure is needed
for all nodes in the forest.

`FlatForest` Class
------------------

The `FlatForest` class provides a flexible way to work with tree structures
using a flat dictionary format. It offers various methods for manipulating and visualizing trees.

Initializing a FlatTree
^^^^^^^^^^^^^^^^^^^^^^^

You can initialize a `FlatForest` with a dictionary representing the tree data.

.. code-block:: python

    import AlgoTree

    tree_data = {
        "node1": {
            "data": "Some data for node1"
        },
        "node2": {
            "parent": "node1",
            "data": "Some data for node2"
        },
        "node3": {
            "parent": "node1",
            "data": "Some data for node3"
        },
        "node4": {
            "parent": "node3",
            "data": "Some data for node4"
        },
        "node5": {
            "parent": "node3",
            "data": "Some data for node5"
        }
    }

    tree = AlgoTree.FlatForest(tree_data)
    print(json.dumps(tree, indent=2))

Expected Output:

.. code-block:: json

    {
      "node1": {
        "data": "Some data for node1"
      },
      "node2": {
        "parent": "node1",
        "data": "Some data for node2"
      },
      "node3": {
        "parent": "node1",
        "data": "Some data for node3"
      },
      "node4": {
        "parent": "node3",
        "data": "Some data for node4"
      },
      "node5": {
        "parent": "node3",
        "data": "Some data for node5"
      }
    }

Visualizing the Tree
^^^^^^^^^^^^^^^^^^^^

You can visualize the tree using the `PrettyTree` class.

Text Visualization
""""""""""""""""""

.. code-block:: python

    from AlgoTree.pretty_print import pretty_print
    print(pretty_print(tree))

Expected Output:

.. code-block:: text

    node1
    ├── node3
    │   ├── node4
    │   └── node5
    └── node2

Manipulating the Tree
^^^^^^^^^^^^^^^^^^^^^

Adding a Child Node
"""""""""""""""""""

.. code-block:: python

    child = tree.root.add_child(name="node36", data="Some data for node36")
    print(child)

Expected Output:

.. code-block:: text

    FlatForestNode(name=node36, parent=node1, data="Some data for node36"})

Viewing Sub-Trees
^^^^^^^^^^^^^^^^^

You can work with sub-trees rooted at any node.

.. code-block:: python

    print(pretty_tree(tree.node("node3")))

Expected Output:

.. code-block:: text

    node3
    ├── node4
    └── node5

Validating the Tree
^^^^^^^^^^^^^^^^^^^

Ensures that all keys are unique and that parent references are valid.

.. code-block:: python

    tree.check_valid()

Detaching and Purging Nodes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can detach nodes, which sets their parent to a special key indicating they
are detached, and purge detached nodes to remove them from the underlying
dictionary.

Purging Detached Nodes
""""""""""""""""""""""

.. code-block:: python

    tree.purge()

Handling Errors
^^^^^^^^^^^^^^^

Invalid Parent Reference
""""""""""""""""""""""""

Attempting to create a tree with an invalid parent reference will raise an error.

.. code-block:: python

    try:
        invalid_tree = AlgoTree.FlatForest({
            "node1": {
                "parent": "non_existent_parent",
                "data": "Some data for node1"
            }})
        invalid_tree.check_valid()
    except KeyError as e:
        print(e)

Expected Output:

.. code-block:: text

    Parent node non-existent: 'non_existent_parent'

Cycle Detection
"""""""""""""""

The `FlatForest` class checks for cycles in the forest and raises an error if a cycle is detected.

.. code-block:: python

    try:
        cycle_tree_data = {
            "node0": { "data": "Some data for node0"},
            "node1": {"parent": "node2", "data": "Some data for node1"},
            "node2": {"parent": "node3", "data": "Some data for node2"},
            "node3": {"parent": "node1", "data": "Some data for node3"},
            "node4": {"parent": "node0", "data": "Some data for node4"}
        }
        cycle_tree = AlgoTree.FlatForest(cycle_tree_data)
        cycle_tree.check_valid()
    except ValueError as e:
        print(e)

Expected Output:

.. code-block:: text

    Cycle detected: {'node2', 'node3', 'node1'}

Tree Conversions
----------------

You can convert between different tree representations, as long as they
expose an API like `children` property or `parent`. We provide a
`TreeConverter` class to facilitate these conversions.

Converting to `TreeNode`
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import AlgoTree.tree_converter as tc
    new_tree = tc.TreeConverter.convert(tree, target_type=AlgoTree.TreeNode)
    print(type(new_tree))

Expected Output:

.. code-block:: text

    <class 'AlgoTree.treenode.TreeNode'>

Conclusion
----------

The `FlatForest` class provides a flexible and powerful way to represent and
manipulate tree structures using a flat dictionary format. With methods for
adding, detaching, pruning, and visualizing nodes, `FlatForest` can handle
various tree-related tasks efficiently. This tutorial has covered the basic and
advanced usage of the class, demonstrating its capabilities and versatility.

For more detailed information and code implementation, refer to the
[GitHub repository](https://github.com/queelius/AlgoTree).
'''

### source/jt.rst


'''markdown
jt Command-Line Tool
====================

`jt` is a command-line tool for querying and manipulating tree structures represented in JSON format. It supports various operations such as finding nodes, calculating distances, pruning, and converting tree structures.

Overview
--------

The `jt` program processes trees represented in JSON, supporting multiple tree formats such as `FlatForest` and `TreeNode`. It allows you to perform operations like finding the lowest common ancestor (LCA), calculating tree size, marking nodes, and more.

Usage
-----

The basic usage is as follows:

.. code-block:: bash

    jt [OPTIONS] [FILE]

Where `FILE` is the path to a JSON file containing the tree structure. If no file is provided, `jt` reads from standard input.

### Example Commands

Here are a few example commands:

- **Check if a node exists:**
  
  .. code-block:: bash

      jt ./example.json --has-node nodeName

- **Get specific node details:**

  .. code-block:: bash

      jt ./example.json --node nodeKey

- **Show siblings of a node:**

  .. code-block:: bash

      jt ./example.json --siblings nodeName

Arguments
---------

The following arguments are supported by the `jt` tool:

- **file**: The path to the JSON file representing the tree. If not provided, the program reads from standard input.

- **--node-name LAMBDA_EXPRESSION**: Lambda expression to generate node names from a node. Defaults to `lambda node: node.name`.

- **--lca NODE_KEY1 NODE_KEY2**: Get the lowest common ancestor (LCA) of two nodes.

- **--depth NODE_KEY**: Get the depth of a specific node in the tree.

- **--mark-nodes NODE_KEY [NODE_KEY ...]**: Mark nodes in the tree by specifying their keys.

- **--distance NODE_KEY1 NODE_KEY2**: Get the distance between two nodes.

- **--version**: Show the program version.

- **--size**: Print the size of the tree (i.e., the number of nodes).

- **--siblings NODE_KEY**: Show the siblings of a specific node.

- **--children NODE_KEY**: Show the children of a specific node.

- **--parent NODE_KEY**: Show the parent of a specific node.

- **--ancestors NODE_KEY**: Show the ancestors of a specific node.

- **--descendants NODE_KEY**: Show the descendants of a specific node.

- **--has-node NODE_KEY**: Check if a specific node exists in the tree.

- **--subtree NODE_KEY**: Get the subtree rooted at a specific node.

- **--node NODE_KEY**: Get a node by its key.

- **--root**: Get the root node of the tree.

- **--root-to-leaves**: Get a list of paths from the root to the leaves of the tree.

- **--leaves**: Get the leaf nodes of the tree.

- **--height**: Get the height of the tree.

- **--nodes**: Get all nodes in the tree.

- **--pretty**: Print the tree in a pretty format.

- **--prune LAMBDA_EXPRESSION**: Prune the tree by a predicate function.

- **--subtree-rooted-at NODE_KEY**: Get the subtree rooted at a specific node.

- **--find-nodes LAMBDA_EXPRESSION**: Find nodes by a predicate function.

- **--json**: Output the tree in JSON format.

- **--convert TARGET_FORMAT**: Convert the tree to a different format (e.g., `FlatForest`, `TreeNode`).

- **--type**: Print the type of the tree.

- **--merge-forest NODE_KEY**: Merge a forest into a single tree under a new node named `NODE_KEY`.

- **--set-root NODE_KEY**: Set the root node of the tree to the node with the given key.

- **--epilog**: Show example usage.

### Example Usage
In addition to the commands listed above, here are more examples to help you understand how `jt` can be used:

.. code-block:: bash

    # Merge a forest into a single tree
    jt ./forest.json --merge-forest NewRootNode

    # Prune the tree based on a custom lambda expression
    jt ./example.json --prune 'lambda node: node.payload > 10'

    # Pretty print the tree structure
    jt ./example.json --pretty

    # Convert the tree to a different format
    jt ./example.json --convert FlatForest

License
-------

This program is distributed under the MIT License. See the LICENSE file for more details.

'''

### source/modules.rst


'''markdown
AlgoTree
========

.. toctree::
   :maxdepth: 4

   AlgoTree
'''

### source/treenode.rst


'''markdown
TreeNode
========

The `TreeNode` class is a recursive representation of a tree.

TreeNode Structure
------------------

Each node is a `TreeNode` object.

Example Structure:

We can import JSON data into a `TreeNode` object as follows:

.. code-block:: python

  TreeNode.from_dict(
    {
      "name": "root",
      "value": "root_value",
      "children": [
        {
          "name": "child1",
          "value": "child1_value",
          "children": [
            {
              "name": "child1_1",
              "value": "child1_1_value"
            }
          ]
        },
        {
          "name": "child2",
          "value": "child2_value",
          "children": [
            {
              "name": "child2_1",
              "value": "child2_1_value"
            }
          ]
        }
      ]
    })

Where:

- `name` (optional) is a key that maps to the name of the node. If not
  provided, the name defaults to a UUID.
- `children` is a list of child nodes, each of which is a `TreeNode` object.
- Other key-value pairs can be stored in the node as needed, which in total
  form the `payload` of the node, which can be accessed using the `payload` property.

Attributes and Methods
----------------------

Initialization
~~~~~~~~~~~~~~

Each `TreeNode` can be initialized with an optional parent, name, and additional key-value pairs.

.. code-block:: python

    def __init__(self, *args, parent: Optional['TreeNode'] = None, name: Optional[str] = None,
                 payload: Optional[Any], *args, **kwargs):
        # Initialization code here

If the `payload` argument is provided, that is used as payload. However, we
also allow for the payload to be specified by arguments and key-word arguments,
`*args` and `**kwargs`. If the `name` argument is provided, it is stored as the
name of the node, otherwise a UUID is generated. If the `parent` argument is
provided, the node is added as a child of the parent node.

Properties
~~~~~~~~~~

- `name`: Returns the name of the node.
- `children`: Returns the list of children of the node.
- `payload`: Returns the data stored in the node.

Methods
~~~~~~~

- `node(name: str) -> 'TreeNode'`: Retrieves the node with the given name.
- `add_child(name: Optional[str] = None, payload: Optional[Any], *args, **kwargs) -> 'TreeNode'`: Adds a child node to the tree.
- `root`: Returns the root of the tree.

Tree API
--------

The `TreeNode` class also provides a tree API that allows manipulation and
construction of tree. Unlike the `FlatForestNode` class, it is not backed by
a dictionary. It is a recursive representation of a tree that has fewer
restrictions on what kind of objects can be stored in, for instance, the
`payload`.

Example Usage
-------------

.. code-block:: python

    root = TreeNode(name='root', value='root_value')
    child1 = root.add_child(name='child1', value='child1_value')
    child1_1 = child1.add_child(name='child1_1', value='child1_1_value')
    child2 = root.add_child(name='child2', value='child2_value')
    child2_1 = child2.add_child(name='child2_1', value='child2_1_value')

    other = TreeNode(name="other", value="other_value", parent=child1_1)
    TreeNode(name="other2", value="other2_value", parent=other)

    print(root.node('child1').value)  # Output: 'child1_value'
    print(child1_1.root.name)         # Output: 'root'
'''

### source/flat_forest_nb.rst


'''markdown
FlatForest Notebook
===================

.. contents:: Table of Contents
    :backlinks: none

Introduction
------------

In this notebook, we explore the ``FlatForest`` data structure, which is
a forest structure with a flat (non-nested) data structure. It is a
``dict`` with special methods to access the root nodes and other
tree-like operations.

The main implementation detail is the proxy class ``FlatForestNode``,
which allows us to access the ``dict`` with a node-centric abstraction.
This allows us to implement tree-like operations in a flat data
structure. As a proxy, it also modifies the ``dict`` in place, so it is
a mutable data structure.

Creating a ``FlatForest``
-------------------------

Let’s load the required libraries and create a ``FlatForest`` data
structure using the node interface.

.. code:: ipython3

    from AlgoTree.flat_forest_node import FlatForestNode
    from AlgoTree.flat_forest import FlatForest
    from AlgoTree.tree_converter import TreeConverter
    from IPython.display import display, Markdown
    from AlgoTree.pretty_tree import pretty_tree
    import json
    #from AlgoTree.treenode import TreeNode
    from copy import deepcopy
    
    
    def monotext(txt):
        display(Markdown(f"<pre>{txt}</pre>"))
    
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
    
    forest = FlatForest()
    nodes = []
    for key, value in data.items():
        par_key = value.pop("parent", None)
        nodes.append(FlatForestNode(name=key, parent=par_key, forest=forest, data=value["data"]))
    
    for node in nodes:
        try:
            print(node.name, node.payload, node.parent.name if node.parent is not None else None)
        except ValueError as e:
            print(f"ValueError: {e}")
        except KeyError as e:
            print(f"KeyError: {e}")
        print()


Output
^^^^^^

.. parsed-literal::

    1 {'data': 1} None
    
    2 {'data': 2} 1
    
    3 {'data': 3} 1
    
    4 {'data': 4} 3
    
    5 {'data': 5} 3
    
    A {'data': 'Data for A'} None
    
    B {'data': 'Data for B'} A
    
    C {'data': 'Data for C'} A
    
    D {'data': 'Data for D'} C
    
    E {'data': 'Data for E'} C
    
    F {'data': 'Data for F'} E
    
    G {'data': 'Data for G'} E
    
    H {'data': 'Data for H'} B
    
    I {'data': 'Data for I'} A
    
    J {'data': 'Data for J'} I
    
    K {'data': 'Data for K'} G
    
    L {'data': 'Data for L'} G
    
    M {'data': 'Data for M'} C
    

Storing and Transmitting Trees
------------------------------

It’s easy to regenerate any JSON files that may have been used to
generate the ``FlatForest`` object. So, JSON is a good format for
storing and transmitting trees. And, of course, ``FlatForest`` *is* a
dictionary.

Note that when we load a dictionary, the tree is providing a *view* of it
in-place. So, if we modify the dictionary, we modify the tree, and vice versa.

Creating a `FlatForest` from a JSON
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: ipython3

    # load a forest from data
    forest2 = FlatForest(deepcopy(data))
    # load a forest from a forest
    forest3 = FlatForest(forest)
    
    print(forest == forest2)
    
    print(json.dumps(dict(forest), indent=2, sort_keys=True) == json.dumps(dict(forest2), indent=2, sort_keys=True))
    print(json.dumps(dict(forest), indent=2, sort_keys=True) == json.dumps(dict(forest3), indent=2, sort_keys=True))
    print(json.dumps(dict(forest2), indent=2, sort_keys=True) == json.dumps(dict(forest3), indent=2, sort_keys=True))


.. parsed-literal::

    False
    False
    True
    False


.. code:: ipython3

    forest.logical_root_names()




.. parsed-literal::

    [None, None, '__DETACHED__']



.. code:: ipython3

    print(forest.detached)


.. parsed-literal::

    FlatForestNode(name=__DETACHED__, parent=None, payload={}, root=__DETACHED__, children=[])


.. code:: ipython3

    from copy import deepcopy
    new_forest = deepcopy(forest)
    new_forest.detach("1")




.. parsed-literal::

    FlatForestNode(name=1, parent=None, payload={'data': 1}, root=1, children=['2', '3'])



If we try to detach a node that was already detached, we get a
``KeyError``. Note that this can happen in two ways:

1. The node was detached and then we try to detach it again.
2. The node was detached and then we try to detach a child of it.

Any child of a detached node is also detached, so we can’t detach a
child of a detached node.

.. code:: ipython3

    try:
        new_forest.detach("2")
    except KeyError as e:
        print(f"KeyError: {e}")

.. code:: ipython3

    forest.as_tree()




.. parsed-literal::

    FlatForestNode(name=__ROOT__, parent=None, payload={}, root=__ROOT__, children=['1', 'A'])



.. code:: ipython3

    forest.preferred_root = "1"
    print(pretty_tree(forest.subtree()))
    forest.preferred_root = "A"
    print(pretty_tree(forest.subtree()))
    print(pretty_tree(forest.subtree("C")))


.. parsed-literal::

    1
    ├───── 2
    └───── 3
           ├───── 4
           └───── 5
    
    A
    ├───── B
    │      └───── H
    ├───── C
    │      ├───── D
    │      ├───── E
    │      │      ├───── F
    │      │      └───── G
    │      │             ├───── K
    │      │             └───── L
    │      └───── M
    └───── I
           └───── J
    
    C
    ├───── D
    ├───── E
    │      ├───── F
    │      └───── G
    │             ├───── K
    │             └───── L
    └───── M
    


For visualizing trees, we can use the ``PrettyTree`` class and the
``pretty_tree`` function. The ``PrettyTree`` class is a simple tree data
structure that can be used to visualize trees in pretty text format,
optionally with the ability to mark nodes for highlighting.

.. code:: ipython3

    monotext(pretty_tree(forest.subtree("A"), mark=["A", "G"], node_details=lambda node: node.payload['data']))



.. raw:: html

   <pre>A ◄ Data for A 🔵
   ├───── B ◄ Data for B
   │      └───── H ◄ Data for H
   ├───── C ◄ Data for C
   │      ├───── D ◄ Data for D
   │      ├───── E ◄ Data for E
   │      │      ├───── F ◄ Data for F
   │      │      └───── G ◄ Data for G 🟣
   │      │             ├───── K ◄ Data for K
   │      │             └───── L ◄ Data for L
   │      └───── M ◄ Data for M
   └───── I ◄ Data for I
          └───── J ◄ Data for J
   </pre>


.. code:: ipython3

    monotext(pretty_tree(forest.subtree("A"), mark=["H", "D"]))



.. raw:: html

   <pre>A
   ├───── B
   │      └───── H 🟡
   ├───── C
   │      ├───── D ⭕
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   └───── I
          └───── J
   </pre>


.. code:: ipython3

    from pprint import pprint
    from AlgoTree import utils
    pprint(utils.node_stats(forest.subtree("C")))


.. parsed-literal::

    {'node_info': {'ancestors': [],
                   'children': ['D', 'E', 'M'],
                   'depth': 0,
                   'descendants': ['D', 'E', 'F', 'G', 'K', 'L', 'M'],
                   'is_internal': True,
                   'is_leaf': False,
                   'is_root': True,
                   'leaves_under': ['D', 'F', 'K', 'L', 'M'],
                   'name': 'C',
                   'parent': None,
                   'path': ['C'],
                   'payload': {'data': 'Data for C'},
                   'root_distance': 0,
                   'siblings': [],
                   'type': "<class 'AlgoTree.flat_forest_node.FlatForestNode'>"},
     'subtree_info': {'height': 3,
                      'leaves': ['D', 'F', 'K', 'L', 'M'],
                      'root': 'C',
                      'size': 8}}


The ``FlatForest`` class provides a **view** of a ``dict`` object as a
forest. We do not modify the ``dict`` passed into it (and you can create
a dict through the ``FlatForest`` API). Since it’s just a view of a
``dict`` we have all the normal operations on it that we would have on a
``dict`` object.

``FlatForest`` also implements the concept of a node, which is a view of
a particular node in our node-centric API. In order to do this, we
specify a preferred root node, which by default is the first root node
in the forest. This is the node that will be used as the root node in
the ``FlatForestNode`` API. If you want to change the root node, you can
do so by calling ``FlatForest.preferred_root`` with the name of the node
you want to be the preferred root.

We also provide as ``as_tree`` method that unifies any ``dict`` object
representing a flat forest structure into a flat forest structure with
just a single root node, where all the root nodes are children of this
root node. This is no longer a view, however, as we return a new
``dict`` object.

.. code:: ipython3

    print(forest["C"])
    C = forest.subtree("C")
    print(C)
    print(C["parent"])
    print(C.children)


.. parsed-literal::

    {'data': 'Data for C', 'parent': 'A'}
    FlatForestNode(name=C, parent=None, payload={'data': 'Data for C'}, root=C, children=['D', 'E', 'M'])
    A
    [FlatForestNode(name=D, parent=C, payload={'data': 'Data for D'}, root=C, children=[]), FlatForestNode(name=E, parent=C, payload={'data': 'Data for E'}, root=C, children=['F', 'G']), FlatForestNode(name=M, parent=C, payload={'data': 'Data for M'}, root=C, children=[])]


.. code:: ipython3

    N = forest.root.add_child(name="N", data="Data for N")
    print(N)
    forest.subtree("A").add_child(name="O", data="Data for O")
    monotext(pretty_tree(forest.root.node("A"), mark=["O"]))


.. parsed-literal::

    FlatForestNode(name=N, parent=A, payload={'data': 'Data for N'}, root=A, children=[])



.. raw:: html

   <pre>A
   ├───── B
   │      └───── H
   ├───── C
   │      ├───── D
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   └───── O 🟡
   </pre>


If we try too add a non-unique node key to the tree, we will get a
``KeyError``.

.. code:: ipython3

    try:
        forest.subtree("A").add_child(name="B")
    except KeyError as e:
        print(e)


.. parsed-literal::

    'key already exists in the tree: B'


Let’s add some more nodes.

.. code:: ipython3

    P = N.add_child(name="P", data="Data for P")
    N.add_child(name="Q", data="Data for Q")
    P.add_child(name="R", data="Data for R").add_child(
        name="S", data="Data for S"
    )
    monotext(pretty_tree(forest.root, mark=["N", "P", "Q", "R", "S"]))
    
    print(forest.root.node("A"))
    print(forest.root.node("A").parent)



.. raw:: html

   <pre>A
   ├───── B
   │      └───── H
   ├───── C
   │      ├───── D
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N ⭕
   │      ├───── P 🟤
   │      │      └───── R 🔵
   │      │             └───── S 🟤
   │      └───── Q 🔘
   └───── O
   </pre>


.. parsed-literal::

    FlatForestNode(name=A, parent=None, payload={'data': 'Data for A'}, root=A, children=['B', 'C', 'I', 'N', 'O'])
    None


.. code:: ipython3

    f_nodes = utils.breadth_first_undirected(forest.node("F"), 2)
    print([n.name for n in f_nodes])



.. parsed-literal::

    ['F', 'E', 'G', 'C']


.. code:: ipython3

    
    monotext(pretty_tree(utils.subtree_rooted_at(forest.node("C"), 2), mark=["C"]))



.. raw:: html

   <pre>C ⭕
   ├───── D
   ├───── E
   │      ├───── F
   │      └───── G
   └───── M
   </pre>


.. code:: ipython3

    center_C = utils.subtree_centered_at(forest.node("C"), 2)
    monotext(pretty_tree(center_C, mark=["C"]))
    monotext(pretty_tree(forest.root, mark=["C"]))



.. raw:: html

   <pre>A
   ├───── B
   ├───── C ⭕
   │      ├───── D
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      └───── M
   ├───── I
   ├───── N
   └───── O
   </pre>



.. raw:: html

   <pre>A
   ├───── B
   │      └───── H
   ├───── C ⭕
   │      ├───── D
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   └───── O
   </pre>


We also support conversions to and from any tree-like structure that
supports the node-centric API, including ``FlatForest`` and a simple
(but far more flexible) ``TreeNode`` class that we also provide for
illustrative purposes.

The function is called ``TreeConverter.copy_under`` which accepts a
``source`` and ``target`` object, and copies the ``source`` object under
the ``target`` object. The source is normally a node of some kind, and
the target is another node, and the result is the tree structure under
the source node is copied under the target node. The source node is not
modified in any way.

.. code:: ipython3

    from AlgoTree.treenode import TreeNode
    treeNodeMe = TreeNode(name="treenode", payload={"data": "Data for treenode"})
    treeNodeMe.add_child(name="child1", payload={"data": "Data for child1"})
    treeNodeMe.add_child(name="child2", payload={"data": "Data for child2"})
    tree1 = TreeConverter.copy_under(forest.subtree("C"), treeNodeMe.children[0])
    print(pretty_tree(tree1.root, mark=["child1"]))



.. parsed-literal::

    treenode
    ├───── child1 🟡
    │      └───── C
    │             ├───── D
    │             ├───── E
    │             │      ├───── F
    │             │      └───── G
    │             │             ├───── K
    │             │             └───── L
    │             └───── M
    └───── child2
    


.. code:: ipython3

    tree2 = TreeConverter.copy_under(tree1.root, forest.subtree("D"), node_name=lambda n: n.name + "_2")
    monotext(pretty_tree(tree2.forest.root))




.. raw:: html

   <pre>A
   ├───── B
   │      └───── H
   ├───── C
   │      ├───── D
   │      │      └───── treenode_2
   │      │             ├───── child1_2
   │      │             │      └───── C_2
   │      │             │             ├───── D_2
   │      │             │             ├───── E_2
   │      │             │             │      ├───── F_2
   │      │             │             │      └───── G_2
   │      │             │             │             ├───── K_2
   │      │             │             │             └───── L_2
   │      │             │             └───── M_2
   │      │             └───── child2_2
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   └───── O
   </pre>


We can iterate over the items of the child and we can modify/delete its
data.

.. code:: ipython3

    for k, v in forest.subtree("N").items():
        print(k, "<--", v)
    
    N["new_data"] = "Some new data for G"
    print(N)
    
    del N["new_data"]
    N["other_new_data"] = "Some other data for G"
    print(N)


.. parsed-literal::

    data <-- Data for N
    parent <-- A
    FlatForestNode(name=N, parent=A, payload={'data': 'Data for N', 'new_data': 'Some new data for G'}, root=A, children=['P', 'Q'])
    FlatForestNode(name=N, parent=A, payload={'data': 'Data for N', 'other_new_data': 'Some other data for G'}, root=A, children=['P', 'Q'])


Let’s create a tree from a dictionary that refers to a non-existent
parent.

.. code:: ipython3

    try:
        non_existent_parent_tree = FlatForest(
            {
                "A": {
                    "parent": "non_existent_parent",
                    "data": "Data for A",
                }
            }
        )
        FlatForest.check_valid(non_existent_parent_tree)
    except KeyError as e:
        print(e)


.. parsed-literal::

    "Parent 'non_existent_parent' not in forest for node 'A'"


We see that the node is disconnected from the logical root, since it
refers to a non-existent parent.

.. code:: ipython3

    try:
        cycle_tree = FlatForest(
            {
                "x": {"parent": None, "data": "Data for x"},
                "A": {"parent": "C", "data": "Data for A"},
                "B": {"parent": "A", "data": "Data for B"},
                "C": {"parent": "B", "data": "Data for C"},
                "D": {"parent": "x", "data": "Data for D"},
            }
        )
    
        monotext(pretty_tree(cycle_tree.root))
        FlatForest.check_valid(cycle_tree)
    except ValueError as e:
        print(e)



.. raw:: html

   <pre>x
   └───── D
   </pre>


.. parsed-literal::

    Cycle detected: {'C', 'A', 'B'}


We see that the tree was in an invalid state. In particular, nodes 1, 2,
and 3 are from any root and in a cycle. We can fix this by breaking the
cycle and setting the parent of node 3 to, for instance, to ``x``.
However, we can also fix it by setting the parent to ``None``, so that
it is a seperate tree in the forest.

.. code:: ipython3

    cycle_tree["C"]["parent"] = None
    FlatForest.check_valid(cycle_tree)
    monotext(pretty_tree(cycle_tree.subtree("C"), mark=["C"]))
    print(cycle_tree.root_names)



.. raw:: html

   <pre>C ⭕
   └───── A
          └───── B
   </pre>


.. parsed-literal::

    ['x', 'C', None, None, '__DETACHED__']


Let’s look at the tree again, and see about creating a cycle.

We will make node 1 the parent of node 5, to create a cycle:

.. code:: ipython3

    try:
        new_tree = deepcopy(forest.root)
        new_tree.node("A")["parent"] = "E"
        FlatForest.check_valid(new_tree)
    except ValueError as e:
        print(e)


.. parsed-literal::

    Data is not a dictionary: data=FlatForestNode(name=A, parent=None, payload={'data': 'Data for A'}, root=A, children=['B', 'C', 'I', 'N', 'O'])


Notice that we use ``deepcopy`` to avoid modifying the original tree
with these invalid operations. We chose to do it this way so as to not
incur the overhead of reverting the tree to a valid state after an
invalid operation. This way, we can keep the tree in an invalid state
for as long as we want, and only revert it to a valid state when we want
to.

Each node is a key-value pair in the ``FlatForest``. We have the
``FlatForestNode`` so that we can have an API focused on the nodes and
not the underlying dictionary. However, we stiill permit access to the
underlying dictionary. When you modify the tree in this way, we still
maintain the integrity of the tree.

Since the ``FlatForest`` represents nodes as key-value pairs, and the
value may have a parent key, along with any other arbitrary data, each
value for a node must be a dictionary.

Below, we see that trying to add a ``test`` node with a non-dictionary
value generates an error.

.. code:: ipython3

    try:
        error_tree = deepcopy(forest)
        # this will raise a ValueError because the node with key `test` maps to
        # string instead of a dict.
        error_tree["test"] = "Some test data"
        FlatForest.check_valid(error_tree)
    except ValueError as e:
        print(e)


.. parsed-literal::

    Node 'test' does not have a payload dictionary: 'Some test data'


Let’s manipulate the tree a bit more using the ``dict`` API. We’re just
going to add a ``new_node`` with some data.

.. code:: ipython3

    forest["T"] = {
        "parent": "B",
        "data": "Data for T"
    }
    
    print(forest.node("T"))
    print(pretty_tree(forest.subtree("B"), mark=["T"]))



.. parsed-literal::

    FlatForestNode(name=T, parent=B, payload={'data': 'Data for T'}, root=A, children=[])
    B
    ├───── H
    └───── T 🔵
    


Logical roots are not a part of the underlying dictionary, so we can’t
access it through the ``dict`` API. It’s non-children data are also
immutable through the ``FlatForestNode`` API. Right now, we use
``FlatForest.DETACHED_KEY`` as a logical root for detached nodes.

.. code:: ipython3

    print(forest.detached)


.. parsed-literal::

    FlatForestNode(name=__DETACHED__, parent=None, payload={}, root=__DETACHED__, children=[])


We see that there are no detached nodes in the forest right now.

.. code:: ipython3

    try:
        forest.detached["data"] = "Some new data for root node"
    except TypeError as e:
        print(e)
    
    try:
        forest.detached["parent"] = None
    except TypeError as e:
        print(e)


.. parsed-literal::

    __DETACHED__ is an immutable logical root
    __DETACHED__ is an immutable logical root


We can *detach* nodes. Let’s first view the full tree, pre-detachment.

.. code:: ipython3

    monotext(pretty_tree(forest.root))



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      └───── T
   ├───── C
   │      ├───── D
   │      │      └───── treenode_2
   │      │             ├───── child1_2
   │      │             │      └───── C_2
   │      │             │             ├───── D_2
   │      │             │             ├───── E_2
   │      │             │             │      ├───── F_2
   │      │             │             │      └───── G_2
   │      │             │             │             ├───── K_2
   │      │             │             │             └───── L_2
   │      │             │             └───── M_2
   │      │             └───── child2_2
   │      ├───── E
   │      │      ├───── F
   │      │      └───── G
   │      │             ├───── K
   │      │             └───── L
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   └───── O
   </pre>


.. code:: ipython3

    forest.node("D").detach()
    forest.detach("G")
    monotext(pretty_tree(forest.root))




.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      └───── T
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   └───── O
   </pre>


Let’s view the detached tree.

.. code:: ipython3

    monotext(pretty_tree(forest.detached, mark=["B", "C"]))




.. raw:: html

   <pre>__DETACHED__
   ├───── D
   │      └───── treenode_2
   │             ├───── child1_2
   │             │      └───── C_2
   │             │             ├───── D_2
   │             │             ├───── E_2
   │             │             │      ├───── F_2
   │             │             │      └───── G_2
   │             │             │             ├───── K_2
   │             │             │             └───── L_2
   │             │             └───── M_2
   │             └───── child2_2
   └───── G
          ├───── K
          └───── L
   </pre>


We can purge detached nodes (and their descendants) from the tree with
the ``purge`` method. Let’s purge the detached nodes. Note that when we
do this, through the node-centric API, nothing will seem different
(unless we look at the tree rooted at the detached logical root).
However, if we look at the underlying dictionary, we will see that the
detached nodes are gone.

.. code:: ipython3

    forest.purge()
    print(json.dumps(forest, indent=2))


.. parsed-literal::

    {
      "1": {
        "data": 1,
        "parent": null
      },
      "2": {
        "data": 2,
        "parent": "1"
      },
      "3": {
        "data": 3,
        "parent": "1"
      },
      "4": {
        "data": 4,
        "parent": "3"
      },
      "5": {
        "data": 5,
        "parent": "3"
      },
      "A": {
        "data": "Data for A",
        "parent": null
      },
      "B": {
        "data": "Data for B",
        "parent": "A"
      },
      "C": {
        "data": "Data for C",
        "parent": "A"
      },
      "E": {
        "data": "Data for E",
        "parent": "C"
      },
      "F": {
        "data": "Data for F",
        "parent": "E"
      },
      "H": {
        "data": "Data for H",
        "parent": "B"
      },
      "I": {
        "data": "Data for I",
        "parent": "A"
      },
      "J": {
        "data": "Data for J",
        "parent": "I"
      },
      "M": {
        "data": "Data for M",
        "parent": "C"
      },
      "N": {
        "data": "Data for N",
        "parent": "A",
        "other_new_data": "Some other data for G"
      },
      "O": {
        "data": "Data for O",
        "parent": "A"
      },
      "P": {
        "data": "Data for P",
        "parent": "N"
      },
      "Q": {
        "data": "Data for Q",
        "parent": "N"
      },
      "R": {
        "data": "Data for R",
        "parent": "P"
      },
      "S": {
        "data": "Data for S",
        "parent": "R"
      },
      "T": {
        "parent": "B",
        "data": "Data for T"
      }
    }


We have a fairly complete API for manipulating the forest. Let’s explore
some additional methods. Let’s first create a node itrator to node A,
and then access or modify the payload data for node A. Since payload
data is mutable, and it must be a dictionary, we can access or modify it
using the dict API.

.. code:: ipython3

    forest.node("A").clear()
    forest.node("A")["new_data"] = "Some new data for A"
    forest.node("A")["other_new_data"] = "Some other data for A"
    print(forest["A"])


.. parsed-literal::

    {'new_data': 'Some new data for A', 'other_new_data': 'Some other data for A'}


This is fairly self-expalanatory.

Let’s add some more nodes without specifying a key name for them, since
often we don’t care about the key name and it’s only for bookkeeping
purposes.

.. code:: ipython3

    forest.root.add_child(whatever=3).add_child(
        name="U", whatever=4).add_child(whatever=5)




.. parsed-literal::

    FlatForestNode(name=779cc759-36a9-4dae-a1c9-e021d65aa1d4, parent=U, payload={'whatever': 5}, root=A, children=[])



.. code:: ipython3

    FlatForestNode(whatever=1000, parent=forest.root.children[0])
    FlatForestNode(name="V", whatever=2000, parent=forest.root.children[0].children[1])
    FlatForestNode(whatever=3000, more_data="yes", parent=forest.node("V"))
    FlatForestNode(name="W", parent=forest.root, whatever=200)




.. parsed-literal::

    FlatForestNode(name=W, parent=A, payload={'whatever': 200}, root=A, children=[])



.. code:: ipython3

    forest.node("V").parent = forest.node("W")
    monotext(pretty_tree(forest.root, mark=["U", "V", "W"], node_details=lambda n: n.payload))



.. raw:: html

   <pre>A ◄ {'new_data': 'Some new data for A', 'other_new_data': 'Some other data for A'}
   ├───── B ◄ {'data': 'Data for B'}
   │      ├───── H ◄ {'data': 'Data for H'}
   │      ├───── T ◄ {'data': 'Data for T'}
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978 ◄ {'whatever': 1000}
   ├───── C ◄ {'data': 'Data for C'}
   │      ├───── E ◄ {'data': 'Data for E'}
   │      │      └───── F ◄ {'data': 'Data for F'}
   │      └───── M ◄ {'data': 'Data for M'}
   ├───── I ◄ {'data': 'Data for I'}
   │      └───── J ◄ {'data': 'Data for J'}
   ├───── N ◄ {'data': 'Data for N', 'other_new_data': 'Some other data for G'}
   │      ├───── P ◄ {'data': 'Data for P'}
   │      │      └───── R ◄ {'data': 'Data for R'}
   │      │             └───── S ◄ {'data': 'Data for S'}
   │      └───── Q ◄ {'data': 'Data for Q'}
   ├───── O ◄ {'data': 'Data for O'}
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e ◄ {'whatever': 3}
   │      └───── U ◄ {'whatever': 4} 🔴
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4 ◄ {'whatever': 5}
   └───── W ◄ {'whatever': 200} ⚫
          └───── V ◄ {'whatever': 2000} 🔘
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8 ◄ {'whatever': 3000, 'more_data': 'yes'}
   </pre>


Let’s look at some tree conversions. We can convert between different
tree representations and data structures.

.. code:: ipython3

    new_tree = TreeConverter.convert(forest.root, TreeNode)
    monotext(pretty_tree(new_tree, node_details=lambda n: n.payload))



.. raw:: html

   <pre>A ◄ {'new_data': 'Some new data for A', 'other_new_data': 'Some other data for A'}
   ├───── B ◄ None
   │      ├───── H ◄ None
   │      ├───── T ◄ None
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978 ◄ None
   ├───── C ◄ None
   │      ├───── E ◄ None
   │      │      └───── F ◄ None
   │      └───── M ◄ None
   ├───── I ◄ None
   │      └───── J ◄ None
   ├───── N ◄ None
   │      ├───── P ◄ None
   │      │      └───── R ◄ None
   │      │             └───── S ◄ None
   │      └───── Q ◄ None
   ├───── O ◄ None
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e ◄ None
   │      └───── U ◄ None
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4 ◄ None
   └───── W ◄ None
          └───── V ◄ None
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8 ◄ None
   </pre>


We see that it’s a different type of tree, a ``TreeNode``, which is a
recursive data structure. It models the same tree data, but in a
different way. This one is also more flexible, so that it doesn’t
require unique names or the payload data to be a dictionary - it can be
any object or value. This simplicity comes at the cost of not being a
dictionary (or view of a dictionary), as FlatForest does.

We see that it has a very different structure. However, when we
pretty-print it using ``TreeViz``, we see that it’s the same tree.

.. code:: ipython3

    monotext(pretty_tree(forest.root))
    monotext(pretty_tree(new_tree))



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   ├───── O
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e
   │      └───── U
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4
   └───── W
          └───── V
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8
   </pre>



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   ├───── O
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e
   │      └───── U
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4
   └───── W
          └───── V
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8
   </pre>


.. code:: ipython3

    result = TreeConverter.copy_under(new_tree, FlatForestNode(name="new_root"))
    monotext(pretty_tree(result))
    result2 = TreeConverter.copy_under(result, new_tree)
    monotext(pretty_tree(result2))



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   ├───── O
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e
   │      └───── U
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4
   └───── W
          └───── V
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8
   </pre>



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   ├───── O
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e
   │      └───── U
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4
   └───── W
          └───── V
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8
   </pre>


The ``TreeNode`` is a bit more useful for operations that require
recursion, but any tree can support the sae operations. The ``TreeNode``
is a bit more specialized for this purpose, and the ``FlatTree`` is a
bit more specialized for more general storage and manipulation of data
that is tree-like, such as configuration data or log data. See
``TreeNode.md`` for more information on the ``TreeNode`` class.

.. code:: ipython3

    root = TreeNode(name="root", payload= {"value":0}, parent=None)
    A = TreeNode(name="A", payload={"value":1}, parent=root)
    print(root.children)



.. parsed-literal::

    [TreeNode(name=A, parent=root, root=root, payload={'value': 1}, len(children)=0)]


.. code:: ipython3

    root2 = TreeNode(name="root", payload=0)
    A2 = TreeNode(name="A", parent=root2, payload=1)
    B2 = TreeNode(name="B", parent=root2, payload=2)
    C2 = TreeNode(name="C", parent=root2, payload=3)
    D2 = TreeNode(name="D", parent=C2, payload=4)
    E2 = TreeNode(name="E", parent=C2, payload=5)
    F2 = TreeNode(name="F", parent=C2, payload="test")
    G2 = TreeNode(name="G", parent=C2, payload=7)
    H2 = TreeNode(name="H", parent=C2, payload=({1: 2}, [3, 4]))
    I2 = TreeNode(name="I", parent=F2, payload=9)
    monotext(pretty_tree(root2, node_details=lambda n: n.payload))



.. raw:: html

   <pre>root ◄ 0
   ├───── A ◄ 1
   ├───── B ◄ 2
   └───── C ◄ 3
          ├───── D ◄ 4
          ├───── E ◄ 5
          ├───── F ◄ test
          │      └───── I ◄ 9
          ├───── G ◄ 7
          └───── H ◄ ({1: 2}, [3, 4])
   </pre>


Algorithm Examples
------------------

Using utility algorithms with ``FlatTree`` and ``FlatTreeNode``:

Finding descendants of a node:

.. code:: ipython3

    from AlgoTree.utils import *
    from pprint import pprint
    pprint(descendants(C))


.. parsed-literal::

    [FlatForestNode(name=E, parent=C, payload={'data': 'Data for E'}, root=C, children=['F']),
     FlatForestNode(name=F, parent=E, payload={'data': 'Data for F'}, root=C, children=[]),
     FlatForestNode(name=M, parent=C, payload={'data': 'Data for M'}, root=C, children=[])]


Finding ancestors of a node:

.. code:: ipython3

    pprint(ancestors(I2))


.. parsed-literal::

    [TreeNode(name=F, parent=C, root=root, payload=test, len(children)=1),
     TreeNode(name=C, parent=root, root=root, payload=3, len(children)=5),
     TreeNode(name=root, root=root, payload=0, len(children)=3)]


Finding siblings of a node:

.. code:: ipython3

    pprint(siblings(E2))


.. parsed-literal::

    []


Finding leaves of a node:

.. code:: ipython3

    pprint(leaves(root2))


.. parsed-literal::

    [TreeNode(name=A, parent=root, root=root, payload=1, len(children)=0),
     TreeNode(name=B, parent=root, root=root, payload=2, len(children)=0),
     TreeNode(name=D, parent=C, root=root, payload=4, len(children)=0),
     TreeNode(name=E, parent=C, root=root, payload=5, len(children)=0),
     TreeNode(name=I, parent=F, root=root, payload=9, len(children)=0),
     TreeNode(name=G, parent=C, root=root, payload=7, len(children)=0),
     TreeNode(name=H, parent=C, root=root, payload=({1: 2}, [3, 4]), len(children)=0)]


Finding the height of a tree:

.. code:: ipython3

    pprint(height(root2))


.. parsed-literal::

    3


Finding the depth of a node:

.. code:: ipython3

    pprint(depth(F2))


.. parsed-literal::

    2


Breadth-first traversal:

.. code:: ipython3

    def print_node(node, level):
        print(f"Level {level}: {node.name}")
        return False
    
    breadth_first(root2, print_node)


.. parsed-literal::

    Level 0: root
    Level 1: A
    Level 1: B
    Level 1: C
    Level 2: D
    Level 2: E
    Level 2: F
    Level 2: G
    Level 2: H
    Level 3: I




.. parsed-literal::

    False



.. code:: ipython3

    print(json.dumps(utils.node_stats(forest.node("N")), indent=2))


.. parsed-literal::

    {
      "node_info": {
        "type": "<class 'AlgoTree.flat_forest_node.FlatForestNode'>",
        "name": "N",
        "payload": {
          "data": "Data for N",
          "other_new_data": "Some other data for G"
        },
        "children": [
          "P",
          "Q"
        ],
        "parent": "A",
        "depth": 1,
        "is_root": false,
        "is_leaf": false,
        "is_internal": true,
        "ancestors": [
          "A"
        ],
        "siblings": [
          "B",
          "C",
          "I",
          "O",
          "945ef525-fece-45f0-a499-b5449d28ef1e",
          "W"
        ],
        "descendants": [
          "P",
          "R",
          "S",
          "Q"
        ],
        "path": [
          "A",
          "N"
        ],
        "root_distance": 1,
        "leaves_under": [
          "S",
          "Q"
        ]
      },
      "subtree_info": {
        "leaves": [
          "H",
          "T",
          "d433395a-27bc-457d-b6d9-c7034d020978",
          "F",
          "M",
          "J",
          "S",
          "Q",
          "O",
          "779cc759-36a9-4dae-a1c9-e021d65aa1d4",
          "14e057df-8004-47c3-9415-b7c7235ea4d8"
        ],
        "height": 3,
        "root": "A",
        "size": 5
      }
    }


Mapping a function over the nodes:

.. code:: ipython3

    def add_prefix(node):
        if node is None:
            return None
        elif node.name == "D":
            # add Q and R as children of D
            node.add_child(name="Q", value=41)
            node.add_child(name="R", value=42)
        elif node.name == "I" or node.name == "W":
            # delete I by returning None (i.e. don't add it to the new tree)
            return None
        elif "U" in [child.name for child in node.children]:
            return None
        return node
    
    root_mapped = map(deepcopy(forest.root), add_prefix)
    
    monotext(pretty_tree(root_mapped))
    
    monotext(pretty_tree(forest.root))



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   └───── O
   </pre>



.. raw:: html

   <pre>A
   ├───── B
   │      ├───── H
   │      ├───── T
   │      └───── d433395a-27bc-457d-b6d9-c7034d020978
   ├───── C
   │      ├───── E
   │      │      └───── F
   │      └───── M
   ├───── I
   │      └───── J
   ├───── N
   │      ├───── P
   │      │      └───── R
   │      │             └───── S
   │      └───── Q
   ├───── O
   ├───── 945ef525-fece-45f0-a499-b5449d28ef1e
   │      └───── U
   │             └───── 779cc759-36a9-4dae-a1c9-e021d65aa1d4
   └───── W
          └───── V
                 └───── 14e057df-8004-47c3-9415-b7c7235ea4d8
   </pre>


Pruning nodes based on a predicate:

.. code:: ipython3

    
    def should_prune(node):
        return node.name == "A"
    
    monotext(pretty_tree(root2))
    pruned_tree = prune(root2, should_prune)
    monotext(pretty_tree(pruned_tree))



.. raw:: html

   <pre>root
   ├───── A
   ├───── B
   └───── C
          ├───── D
          ├───── E
          ├───── F
          │      └───── I
          ├───── G
          └───── H
   </pre>



.. raw:: html

   <pre>root
   ├───── B
   └───── C
          ├───── D
          ├───── E
          ├───── F
          │      └───── I
          ├───── G
          └───── H
   </pre>


Finding root-to-leaf paths:

.. code:: ipython3

    from pprint import pprint
    paths = node_to_leaf_paths(root)
    # print max path length from root to leaf
    pprint(max(paths, key=len))
    print(utils.height(root) == len(max(paths, key=len)) - 1)



.. parsed-literal::

    [TreeNode(name=root, root=root, payload={'value': 0}, len(children)=1),
     TreeNode(name=A, parent=root, root=root, payload={'value': 1}, len(children)=0)]
    True


Converting paths to a tree:

.. code:: ipython3

    rooter = paths_to_tree([["a", "b", "c"], ["a", "b", "d"], ["a", "e", "d"],
                            ["a", "f", "d"], ["a", "e", "g" ], ["a", "e", "h"],
                            ["a", "i", "j", "b"], ["a", "i", "j", "b", "m"],
                            ["a", "i", "j", "l", "b", "b", "b", "b", "b", "b", "t", "u", "v", "w", "x", "y", "b"]],
                            FlatForestNode)
    monotext(pretty_tree(rooter))



.. raw:: html

   <pre>a
   ├───── b
   │      ├───── c
   │      └───── d
   ├───── e
   │      ├───── d_0
   │      ├───── g
   │      └───── h
   ├───── f
   │      └───── d_1
   └───── i
          └───── j
                 ├───── b_0
                 │      └───── m
                 └───── l
                        └───── b_1
                               └───── b_2
                                      └───── b_3
                                             └───── b_4
                                                    └───── b_5
                                                           └───── b_6
                                                                  └───── t
                                                                         └───── u
                                                                                └───── v
                                                                                       └───── w
                                                                                              └───── x
                                                                                                     └───── y
                                                                                                            └───── b_7
   </pre>


.. code:: ipython3

    from AlgoTree.utils import depth, path, ancestors, siblings, is_root
    A = rooter.node("i")
    pretty_tree(A)
    print(depth(A.children[0]))
    print([n.name for n in path(A.children[0].children[0])])
    print([n.name for n in ancestors(A.children[0].children[0])])
    print(siblings(A.children[0]))
    print(is_root(A))


.. parsed-literal::

    2
    ['a', 'i', 'j', 'b_0']
    ['j', 'i', 'a']
    []
    False


.. code:: ipython3

    treenode = TreeNode(name="A")
    TreeNode(name="B", parent=treenode)
    C = TreeNode(name="C", parent=treenode)
    TreeNode(name="D", parent=C)
    TreeNode(name="E", parent=C)
    
    monotext(pretty_tree(treenode))



.. raw:: html

   <pre>A
   ├───── B
   └───── C
          ├───── D
          └───── E
   </pre>


.. code:: ipython3

    treenode_dict = {
        "name": "A",
        "value": 1,
        "children": [
            {"name": "B"},
            {"name": "C", "children": [
                {"name": "D"},
                {"name": "E"}
            ]}
        ]}
    
    print(json.dumps(treenode_dict, indent=2))
    print(json.dumps(treenode.to_dict(), indent=2))


.. parsed-literal::

    {
      "name": "A",
      "value": 1,
      "children": [
        {
          "name": "B"
        },
        {
          "name": "C",
          "children": [
            {
              "name": "D"
            },
            {
              "name": "E"
            }
          ]
        }
      ]
    }
    {
      "name": "A",
      "payload": null,
      "children": [
        {
          "name": "B",
          "payload": null,
          "children": []
        },
        {
          "name": "C",
          "payload": null,
          "children": [
            {
              "name": "D",
              "payload": null,
              "children": []
            },
            {
              "name": "E",
              "payload": null,
              "children": []
            }
          ]
        }
      ]
    }


.. code:: ipython3

    treenode_from_dict = TreeNode.from_dict(treenode_dict)
    monotext(pretty_tree(treenode_from_dict))
    print(treenode_from_dict == treenode)



.. raw:: html

   <pre>A
   ├───── B
   └───── C
          ├───── D
          └───── E
   </pre>


.. parsed-literal::

    True


Conclusion
----------

The ``FlatForest`` class provides a powerful and flexible way to work
with tree-like and forest-like data structures using a flat dictionary
structure. It supports a wide range of operations, including node
manipulation, tree traversal, detachment, pruning, and conversion
between different tree representations.

Explore the ``AlgoTree`` package further to discover more features and
utilities for working with trees in Python.
'''

### source/introduction.rst


'''markdown
Introduction
============

Welcome to the documentation for the `AlgoTree` package. This package provides a
suite of utilities for working with tree-like data structures in Python. It
supports various tree representations, including:

- `FlatForest` and `FlatForestNode` for working with flat tree structures
- `TreeNode` for recursive tree structures
- Conversion utilities to convert between different tree representations
- Utility functions for common tree operations

Getting Started
---------------

To install the `AlgoTree` package, you can use pip:

.. code-block:: shell

   pip install AlgoTree

Once installed, you can start using the various tree structures and utilities
provided by the package. Here is a quick example to get you started:

.. code-block:: python

   from AlgoTree.flat_forest_node import FlatForestNode
   from AlgoTree.print_tree import print_tree
   root = FlatForestNode(name="root", data=0)
   node1 = FlatForestNode(name="node1", parent=root, data=1)
   node2 = FlatForestNode(name="node2", parent=root, data=2)
   node3 = FlatForestNode(name="node3", parent=node2, data=3)
   node4 = FlatForestNode(name="node4", parent=node3, data=4)

   print_tree(root)

This produces the output::

   root
   ├── node1
   └── node2
       └── node3
           └── node4

This code creates a simple tree with a root node and two child nodes. It then
pretty-prints the tree.

The `AlgoTree` package provides a wide range of tree structures and utilities
to help you work with tree-like data structures in Python. You can explore the
documentation to learn more about the available features and how to use them.

Features
--------

- Flexible tree structures with `FlatForest`, `FlatForestNode`, and `TreeNode`
- Utility functions for common tree operations such as traversal, searching, and manipulation
- Conversion utilities to easily convert between different tree representations
- Integration with visualization tools to visualize tree structures


Node-Centric API
----------------

We implement two tree data structures:

- `FlatForest` for working with flat tree and forest structures with
      "pointers" to parent nodes. It uses a proxy object `FlatForestNode` to
      provide a node-centric API.
- `TreeNode` for recursive tree structures, in which each node is a dictionary
      with an optional list of child nodes.

Each representation has its own strengths and weaknesses. The key design point
for `FlatForest` is that it is a flat forest structure that is also a `dict`, i.e.,
it provides a view of dictionaries as forest-like structures, as long as the
dictionaries are structured in a certain way. We document that structure
elsewhere. The `TreeNode` structure is a recursive tree structure that is in
most ways more flexible than the `FlatForest` structure, but it is not provide
a view of dictionaries as trees.

Each tree data structure models the *concept* of a tree node so that the
underlying implementations can be decoupled from any algorithms
or operations that we may want to perform on the tree.

The tree node concept is defined as follows:

- **children** property

      Represents a list of child nodes for the current node that can be
      accessed and modified [1]_.

- **parent** property

      Represents the parent node of the current node that can be accessed
      and modified [2]_. 
      
      Suppose we have the subtree `G` at node `G`::

            B (root)
            ├── D
            └── E (parent)
                └── G (current node)

      Then, `G.parent` should refer node `E`. `G.root.parent` should be None
      since `root` is the root node of subtree `G` and the root node has no parent.
      This is true even if subtree `G` is a subtree view of a larger tree.

      If we set `G.parent = D`, then the tree structure changes to::

            B (root)
            ├── D
            │   └── G (current node)
            └── E
      
      This also changes the view of the sub-tree, since we changed the
      underlying tree structure. However, the same nodes are still accessible
      from the sub-tree.

      If we had set `G.parent = X` where `X` is not in the subtree `G`, then
      we would have an invalid subtree view even if is is a well-defined
      operation on the underlying tree structure. It is undefined
      behavior to set a parent that is not in the subtree, but leave it
      up to each implementation to decide how to handle such cases.

- **node(name: str) -> NodeType** method.

      Returns a node in the current subtree that the
      current node belongs to. The returned node should be the node with the
      given name, if it exists. If the node does not exist, it should raise
      a `KeyError`.

      The node-centric view of the returned node should be consistent with the
      view of the current node, i.e., if the current node belongs to a specific sub-tree
      rooted at some other node, the returned node should also belong to the
      same sub-tree (i.e., with the same root), just pointing to the new node,
      but it should be possible to use `parent` and `children` to go up and down
      the sub-tree to reach the same nodes. Any node that is an ancestor of the
      root of the sub-tree remains inaccessible.

      Example: Suppose we have the sub-tree `t` rooted at `A` and the current node
      is `B`::

            A (root)
            ├── B (current node)
            │   ├── D
            │   └── E
            |       └── G
            └── C
                └── F
      
      If we get node `F`, `t.node(F)`, then the sub-tree `t` remains the same,
      but the current node is now `F`::
    
            A (root)
            ├── B
            │   ├── D
            │   └── E
            |       └── G
            └── C
                └── F (current node)

- **subtree(name: Optional[str] = None) -> NodeType** method.

      This is an optional method that may not be implemented by all tree
      structures. `FlatForestNode` implements this method, but `TreeNode` does
      not.

      Returns a view of another sub-tree rooted at `node` where `node` is
      contained in the original sub-tree view. If `node` is `None`, the method
      will return the sub-tree rooted at the current node.

      As a view, the subtree represents a way of looking at the tree structure
      from a different perspective. If you modify the sub-tree, you are also
      modifying the underlying tree structure. The sub-tree should be a
      consistent view of the tree, i.e., it should be possible to use `parent`
      and `children` to navigate between the nodes in the sub-tree and the
      nodes in the original tree.
      
      `subtree` is a *partial function* over the the nodes in the sub-tree,
      which means it is only well-defined when `node` is a descendant of
      the root of the sub-tree. We do not specify how to deal with the case
      when this condition is not met, but one approach would be to raise an
      exception.

      Example: Suppose we have the sub-tree `t` rooted at `A` and the current node
      is `C`::

            A (root)
            ├── B
            │   ├── D
            │   └── E
            |       └── G
            └── C (current node)
                └── F

      The subtree `t.subtree(B)` returns a new subtree::

            B (root, current node)
            ├── D
            └── E
                └── G

- **root** property

      An immutable property that represents the root node of the (sub)tree.
      
      Suppose we have the subtree `G` at node `G`::

            B (root)
            ├── D
            └── E
                └── G (current node)

      Then, `G.root` should refer node `B`.

- **payload** property

      Returns the payload of the current node. The payload
      is the data associated with the node but not with the structure of the
      tree, e.g., it does not include the `parent` or `children` of the node.

- **name** property

      Returns the name of the current node. The name is
      an identifier for the node within the tree. It is not necessarily unique,
      and nor is it necessarily even a meaningful identifier, e.g., a random
      UUID.
      
      In `TreeNode`, for instance, if the name is not set, it is a hash of the
      tree structure and the current node. Assuming hash collisions are
      negligible, two nodes with the same name are the same node in the same
      tree.

.. [1] Modifying this property may change the **parent** property of other nodes.

.. [2] Modifying this property may change the **children** property of other nodes.
'''

### source/AlgoTree.rst


'''markdown
AlgoTree package
================

Submodules
----------

AlgoTree.flat\_forest module
----------------------------

.. automodule:: AlgoTree.flat_forest
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.flat\_forest\_node module
----------------------------------

.. automodule:: AlgoTree.flat_forest_node
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.node\_hasher module
----------------------------

.. automodule:: AlgoTree.node_hasher
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.tree\_hasher module
----------------------------

.. automodule:: AlgoTree.tree_hasher
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.pretty\_tree module
----------------------------

.. automodule:: AlgoTree.pretty_tree
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.tree\_converter module
-------------------------------

.. automodule:: AlgoTree.tree_converter
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.treenode module
------------------------

.. automodule:: AlgoTree.treenode
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.treenode\_api module
-----------------------------

.. automodule:: AlgoTree.treenode_api
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.utils module
---------------------

.. automodule:: AlgoTree.utils
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: AlgoTree
   :members:
   :undoc-members:
   :show-inheritance:
'''

### source/identity.rst


'''markdown
Understanding Equality in Trees and Nodes
=========================================

Identity and equality are foundational concepts that help us reason about
relationships between objects. While identity implies strict sameness, equality
often refers to contextual similarities between objects. In this document, we
will define identity in a strict sense and then explore different ways to define
and use equality.

Identity: The Strict Definition
-------------------------------

In philosophy, **Leibniz's Law** (or the *Indiscernibility of Identicals*)
states that two objects, `x` and `y`, are identical if and only if for all
predicates `p`, `p(x) = p(y)`. In other words, two objects are identical if
every possible property holds equally for both objects. This is a very strong
form of identity, implying that there is no possible distinction between `x` and
`y`.

In computer science, this strict definition of identity corresponds to the
concept of **object identity**. Two objects are identical if they are the same
instance in memory, which can be checked using the `id()` function in Python.
This is the only situation in which we can guarantee that every predicate will
yield the same result for both objects, as their memory addresses are the same.

**Example:** In Python, two variables are considered identical if they point to
the same object in memory:
  
.. code-block:: python

   x = [1, 2, 3]
   y = x
   assert id(x) == id(y)  # True, x and y are identical


However, strict identity is often not what we are interested in when reasoning
about data structures or values. In most cases, we want to compare objects based
on their properties or behaviors, rather than their memory addresses. This leads
us to the concept of **equality**, which can be defined in various ways
depending on the context.

Equality: Intrinsic and Extrinsic Properties
--------------------------------------------

When defining equality, we must consider whether we are comparing the
*intrinsic* properties of an object or its *extrinsic* properties:

1. **Intrinsic Properties:**: These are the properties that belong to the object
itself, independent of its relationships with other objects. For example, the
intrinsic properties of an object might include its name, value, or other
internal attributes.
   
2. **Extrinsic Properties:**: These are properties that depend on the object's 
relationships to other objects or its environment. For example, the extrinsic
properties of an object might include its position within a structure, its
relationships to other objects, or its role within a larger context.

Equality in Trees and Nodes
---------------------------

Now that we have discussed identity and equality at a high level, we can turn
our attention to how these concepts apply specifically to trees and nodes.
Trees, being hierarchical data structures, bring particular concerns about how
we compare nodes and entire tree structures. Equality can be defined based on
both intrinsic and extrinsic properties in this context.

1. **Value Equality (Intrinsic):**

   Two nodes are considered equal if they have the same intrinsic value
   (payload and name), even if they are different instances in memory. Note that
   we do not look at the parent-child relationships or the position in the tree.

2. **Path Equality (Mixed):**
   
   Two nodes or trees are equal if they occupy the same positions in trees that
   compare equal. This may often be relaxed and consider only the path from the
   root to the node, rather than the entire structure. Another related kind
   of equality is positional equality, which does not consider even the names
   of nodes, only their positions in isomorphic trees.

3. **Name Equality (Intrinsic):**
   
   Two nodes are equal if they share the same name. This focuses only on a
   specific intrinsic attribute, abstracting away other properties. It is
   often the most important property for certain types of trees (e.g., there
   may not even be payloads and names may be unique).

4. **Payload Equality (Intrinsic):**

   Two nodes are equal if they contain the same payload, even if their
   structure or position in the tree differs.

5. **Tree Equality (Mixed):**

   Two trees are equal if they have the same structure and the same data at each
   corresponding node, considering both intrinsic and extrinsic properties.

6. **Tree Isomorphism (Mixed):**

   Two trees are isomorphic if they have the same structure, but the labels and
   data at each node may differ. This is a weaker form of equality that focuses
   strictly on its structure.

Hashing and Equality
--------------------

Hashing is a technique used to map data of arbitrary size to fixed-size values.
It has a wide range of applications, but here we are interested in how it can be
used to implement different forms of equality. It is not necessarily the most
efficient way to implement equality, but it can also be used to store objects in
hash-based data structures like dictionaries or sets.

Here are examples of how different hash functions can be used to implement
various forms of equality for trees and nodes:

1. **Name Equality:**

   Two nodes are considered equal if they have the same name.

   .. code-block:: python
   
      node1 = Node('A', payload=10)
      node2 = Node('A', payload=20)
      assert NodeHasher.name(node1) == NodeHasher.name(node2) 

2. **Payload Equality:**

   Two nodes are considered equal if they have the same payload.

   .. code-block:: python

      node1 = Node('A', payload=10)
      node2 = Node('B', payload=10)
      assert NodeHasher.payload(node1) == NodeHasher.payload(node2)

3. **Node Equality (Name + Payload):**

   Two nodes are considered equal if they share the same name and payload.

   .. code-block:: python

      node1 = Node('A', payload=10)
      node2 = Node('A', payload=10)
      assert NodeHasher.node(node1) == NodeHasher.node(node2)

4. **Path Equality:**

   Two nodes are considered equal if they occupy the same position in their
   respective trees.

   .. code-block:: python

      root1 = Node('Root')
      child1 = Node('A')
      root1.add_child(child1)

      root2 = Node('Root')
      child2 = Node('B')
      root2.add_child(child2)

      assert NodeHasher.path(child1) == NodeHasher.path(child2)

5. **Tree Equality:**

   Two trees are considered equal if they have the same structure and data.

   .. code-block:: python

      root1 = Node('Root')
      child1_1 = Node('A', payload=10)
      child1_2 = Node('B', payload=20)
      root1.add_child(child1_1)
      root1.add_child(child1_2)

      root2 = Node('Root')
      child2_1 = Node('A', payload=10)
      child2_2 = Node('B', payload=20)
      root2.add_child(child2_1)
      root2.add_child(child2_2)

      assert TreeHasher.tree(root1) == TreeHasher.tree(root2)

6. **Tree Isomorphism:**

   Two trees are considered equal if they have the same structure, but not
   necessarily the same data or labels.

   .. code-block:: python

      root1 = Node('Root')
      child1_1 = Node('A', payload=10)
      child1_2 = Node('B', payload=20)
      root1.add_child(child1_1)
      root1.add_child(child1_2)

      root2 = Node('Root')
      child2_1 = Node('1', payload=30)
      child2_2 = Node('2', payload=40)
      root2.add_child(child2_1)
      root2.add_child(child2_2)

      assert TreeHasher.isomorphic(root1) == TreeHasher.isomorphic(root2)

Explanation of Hash Collisions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's important to note that hashing functions, while efficient for comparisons,
have a small probability of producing hash collisions—situations where two
different objects produce the same hash value. This is because the space of
possible hash values is finite, while the space of possible inputs (nodes,
trees, etc.) is effectively infinite.

For example, two different trees might produce the same hash value due to a
collision, but this would be rare assuming a good hash function.

Philosophical Perspective: The Ship of Theseus
----------------------------------------------

The **Ship of Theseus** is a famous philosophical thought experiment that raises
questions about identity and persistence over time. The thought experiment asks:
if all the parts of a ship are gradually replaced, piece by piece, is it still
the same ship? This highlights the tension between identity as a matter of
intrinsic properties (the materials of the ship) versus extrinsic properties
(the ship as a whole and its continuity over time).

In the context of trees and nodes, this thought experiment reminds us that
identity is often a convention and can depend on what we consider intrinsic or
extrinsic. For instance, a node might be considered the "same" if it has the
same name and payload, even if its position in the tree changes. Alternatively,
a node’s identity might be tied to its position within the tree, and changing
that position might alter its identity.

Conclusion
----------

Identity and equality are distinct but related concepts. **Identity** in its
strictest sense, as defined by Leibniz's Law, implies complete
indistinguishability and is typically realized in computer science through
object identity (i.e., the `id()` function). However, in practice, we often work
with different forms of **equality**, which allow us to compare objects based on
specific properties or criteria.

By distinguishing between **intrinsic** and **extrinsic** properties, we can
better define equality in context. Whether we care about value, structure, or
position, choosing the right form of equality for our problem is crucial to
building correct and efficient systems, particularly when working with tree
structures.
'''

### source/expr_trees_nb.rst


'''markdown
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
'''

### Source Files

### Source File: `setup.py`

```python
from setuptools import find_packages, setup

setup(
    name="AlgoTree",
    version="0.8.0",
    author="Alex Towell",
    author_email="lex@metafunctor.com",
    description="A algorithmic tookit for working with trees in Python",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    packages=find_packages() + ['bin'],
    url='https://github.com/queelius/AlgoTree',
    project_urls={
        "Documentation": "https://queelius.github.io/AlgoTree/",
        "Source Code": "https://github.com/queelius/AlgoTree",
        "Issue Tracker": "https://github.com/queelius/AlgoTree/issues",
    },
    python_requires=">=3.6",
    extras_require={
         'dev': [
            'sphinx',
            'sphinx-rtd-theme',
            'sphinxcontrib-napoleon',
            'coverage',
        ],
    },
    test_suite="tests",
    entry_points={
        'console_scripts': [
            'jt=bin.jt:main',
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
)

```

#### Source File: `source/conf.py`

```python
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath("../.."))


project = "AlgoTree"
copyright = "2024, Alex Towell"
author = "Alex Towell"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

release = '0.8.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx'
]

templates_path = ['_templates']
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = 'alabaster'
#html_theme = 'sphinx_rtd_theme'
#html_theme = 'classic'


html_static_path = ['_static', 'images']


```

#### Source File: `source/make.bat`

```batch
@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd

```

#### Source File: `AlgoTree/__init__.py`

```python
from .flat_forest import FlatForest
from .flat_forest_node import FlatForestNode
from .tree_converter import TreeConverter
from .treenode_api import TreeNodeApi
from .pretty_tree import PrettyTree, pretty_tree
from .node_hasher import NodeHasher
from .tree_hasher import TreeHasher
from .treenode import TreeNode
from .utils import (
    map, visit, descendants, ancestors, siblings, leaves, height, depth,
    is_root, is_leaf, is_internal,
    breadth_first, find_nodes, find_node, find_path, node_stats, size, prune,
    lca, breadth_first_undirected, node_to_leaf_paths, distance,
    subtree_centered_at, subtree_rooted_at, paths_to_tree, is_isomorphic)

```

#### Source File: `AlgoTree/flat_forest.py`

```python
from typing import TYPE_CHECKING, Any, List, Optional, Dict
from copy import deepcopy

if TYPE_CHECKING:
    from flat_forest_node import FlatForestNode

class FlatForest(dict):
    """
    A forest class that is also a standard dictionary.

    This class represents a forest using a flat dictionary structure where each
    node has a unique name (key) and an optional 'parent' name (keY) to
    reference its parent node.

    Nodes without a 'parent' key (or with a 'parent' key set to None) are
    root nodes of trees in the forest. Nodes with a 'parent' key set to a valid
    name (key) in the forest are children of the node with that name. Each
    node represents a tree rooted at that node, which we expose through the
    `FlatForestNode` class, which provides a proxy interface to the structure
    centered around nodes abstracted away from the dictionary structure.

    The `FlatForest` class is a dictionary whose data represents a forest-like
    structure. It provides methods to manipulate the forest structure and
    validation methods to check its integrity, but is essentially a view of the
    `dict` object passed into it (or created with it).

    We provide a `FlatForestNode` class which provides an interface centered
    around nodes in a tree. See `flat_forest_node.py` for more details.
    """

    PARENT_KEY = "parent"
    """
    The key used to store the parent key of a node. Modify this if you want to
    use a different key to store the parent key.
    """

    DETACHED_KEY = "__DETACHED__"
    """
    The name used to represent a detached node. This is a special name that is
    assumed to not exist in the tree. When a node is detached, its parent name
    is set to this value. Any descendants of the detached node are also
    detached.
    """

    @staticmethod
    def spec() -> dict:
        """
        Get the JSON specification of the FlatForest data structure.
        
        This method returns a dictionary representing the structure of the
        FlatForest. This is useful for documentation purposes and for
        understanding the structure of the data. The structure is as follows::

        :return: A dict pattern representing the structure of the FlatForest.
        """

        return {
            "<node_key>": {
                "parent | None": "<parent_key> | None",
                "<any_key>": "<any_value>",
                "...": "...",
                "<any_key>": "<any_value>"
            },
            "...": "...",
            "<node_key>": {
                "parent | None": "<parent_key> | None",
                "<any_key>": "<any_value>",
                "...": "...",
                "<any_key>": "<any_value>"
            }
        }
    
    @staticmethod
    def is_valid(data) -> bool:
        """
        Check if the given data is a valid FlatForest.

        :param data: The data to check.
        :return: True if the data is a valid FlatForest, False otherwise.
        """
        try:
            FlatForest.check_valid(data)
            return True
        except ValueError:
            return False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a FlatForest.

        An empty FlatForest can be created by calling `FlatForest()`.

        Since dictionaries can be created in multiple ways, we have multiple
        ways to create a FlatForest:

        Examples:
            FlatForest('a': {'parent': None}, 'b': {'parent': None}, 'c': {'parent': 'a'})
            FlatForest({'a': {}, 'b': {}, 'c': {'parent': 'a'}})
            FlatForest(a={}, b={}, c={'parent': 'a'})
            FlatForest([('a', {}), ('b', {}), ('c', {'parent': 'a'})])

        These examples are equivalent. They create a forest with 3 nodes,
        'a', 'b', and 'c', where 'a' and 'b' are root nodes and 'c' is a child
        of 'a'. The second example is the most common way to create a FlatForest,
        where we pass a dictionary to the constructor. Since the `FlatForest` is
        a subclass of the dictionary class, we can use all the methods of the
        dictionary class on the FlatForest. The FlatForest class provides
        additional methods to manipulate the tree structure. The FlatForest
        class also provides a `FlatForestNode` class that provides an interface
        to the tree structure centered around nodes, abstracting away the
        dictionary structure.

        :param args: Positional arguments to be passed to the dictionary constructor.
        :param kwargs: Keyword arguments to be passed to the dictionary constructor.
        """
        super().__init__(*args, **kwargs)
        self._preferred_root = None

    def logical_root_names(self) -> List[str]:
        """
        Get the logical nodes of the forest. These occur when a node has a parent
        that is not in the forest. A special case for this is the `DETACHED_KEY`
        which is used for detached nodes, i.e., when we detach a node, we set
        its parent to `DETACHED_KEY`.

        :return: List of logical root names.
        """
        parents = [v[FlatForest.PARENT_KEY] for v in self.values() if
                   FlatForest.PARENT_KEY in v and v[FlatForest.PARENT_KEY] is not None]
        #print(parents)
        keys = [k for k in parents if k not in self.keys()]
        if self.DETACHED_KEY not in keys:
            keys.append(self.DETACHED_KEY)
        return keys

    def interior_node_names(self) -> List[str]:
        """
        Get interior node names, i.e., nodes that are not root nodes or logical
        nodes.

        :return: List of interior node names.
        """
        return [k for k in self.keys() if self[k][FlatForest.PARENT_KEY] is not None]
    
    def node_names(self) -> List[str]:
        """
        Get the unique names in the tree, even if they are not nodes in the tree
        but only parent names without corresponding nodes.

        :return: List of unique names in the tree.
        """
        return list(self.keys()) + self.logical_root_names()

    def child_names(self, name: str) -> List[str]:
        """
        Get the children names of a node with the given name.

        :param name: The name of the node to get the children of.
        :return: List of names of the children of the node.
        """

        if name not in self.node_names():
            raise KeyError(f"Node name not found: {name!r}")

        return [k for k, v in self.items() if v.get(FlatForest.PARENT_KEY) == name]
    
    def detach(self, name: str) -> "FlatForestNode":
        """
        Detach subtree rooted at node with the given name by setting its parent
        to `FlatForest.DETACHED_KEY`, which denotes a special name (key) that we
        assume doesn't exist in the forest.

        :param name: The name of the node to detach.
        :return: The detached subtree rooted at the node.
        :raises KeyError: If the node is not found in the tree.
        """
        if name not in self:
            raise KeyError(f"Node not found: {name!r}")
        
        # let's make sure it's not already detached by being an ancestor of a
        # detached node
        if name in self.detached:
            raise KeyError(f"Node {name!r} is already detached")
        
        self[name][FlatForest.PARENT_KEY] = FlatForest.DETACHED_KEY
        return self.subtree(name)

    @staticmethod
    def check_valid(data) -> None:
        """
        Validate the forest structure to ensure the structural integrity of the
        trees.

        This function performs the following validation checks:

         1) No cycles exist in any trees.
         2) All names (unique node identifiers) map to dictionary values.
         3) All nodes have a parent key that is either None or a valid key
            in the tree.

        :param data: The forest data to validate.
        :return: None
        :raises ValueError: If the forest structure is invalid.
        """

        if not isinstance(data, dict):
            raise ValueError(f"Data is not a dictionary: {data=}")
        
        def _check_cycle(key, visited):
            if key in visited:
                raise ValueError(f"Cycle detected: {visited}")
            visited.add(key)
            par_key = data[key].get(FlatForest.PARENT_KEY, None)
            if par_key is not None:
                _check_cycle(par_key, visited)

        for key, value in data.items():
            if not isinstance(value, dict):
                raise ValueError(
                    f"Node {key!r} does not have a payload dictionary: {value!r}")

            par_key = value.get(FlatForest.PARENT_KEY)
            if par_key == FlatForest.DETACHED_KEY:
                continue

            if par_key is not None and par_key != FlatForest.DETACHED_KEY and par_key not in data:
                raise KeyError(
                    f"Parent {par_key!r} not in forest for node {key!r}")

            _check_cycle(key, set())

    def as_tree(self, root_name = "__ROOT__") -> "FlatForestNode":
        """
        Retrieve the forest as a single tree rooted at a logical root node.
        """

        from .flat_forest_node import FlatForestNode
        
        new_dict = {}
        new_dict[root_name] = {FlatForest.PARENT_KEY: None}
        for key in self.keys():
            #new_dict[key] = copy.deepcopy(self[key])
            new_dict[key] = self[key].copy()
            if self[key].get(FlatForest.PARENT_KEY) is None:
                new_dict[key][FlatForest.PARENT_KEY] = root_name
        return FlatForestNode(forest=FlatForest(new_dict), name=root_name)

    def root_key(self, name: str) -> str:
        """
        Get the root key of the node with given name.

        :param key: The key of the node.
        :return: The key of the root node.
        :raises KeyError: If the key is not found in the tree.
        """
        if name not in self.node_names():
            raise KeyError(f"Node name not found: {name!r}")
        
        if name in self.logical_root_names():
            return name

        while self[name].get(FlatForest.PARENT_KEY) is not None:
            name = self[name][FlatForest.PARENT_KEY]
        return name

    @property
    def trees(self) -> List["FlatForestNode"]:
        """
        Retrieve the trees in the forest.

        :return: The trees in the forest.
        """
        return [self.subtree(root_name) for root_name in self.root_names]
    
    @property
    def root_names(self) -> List[str]:
        """
        Retrieve the names of the root nodes. These are the nodes that have no
        parent.

        :return: The names of the root nodes.
        """
        keys = [k for k, v in self.items() if v.get(FlatForest.PARENT_KEY) is None]
        return keys + self.logical_root_names()
        
    def purge(self) -> None:
        """
        Purge detached nodes (tree rooted at `FlatForest.DETACHED_KEY`).
        """
        def _purge(node):
            for child in node.children:
                _purge(child)
            del self[node.name]
        
        for child in self.detached.children:
            _purge(child)

    @property
    def detached(self) -> "FlatForestNode":
        """
        Retrieve the detached tree. This is a special tree for which detached
        nodes are rooted at a logical node with the name `FlatForest.DETACHED_KEY`.

        :return: The detached logical root node.
        """
        return self.subtree(FlatForest.DETACHED_KEY)

    def __repr__(self) -> str:
        return f"FlatForest({dict(self)})"

    def __str__(self) -> str:
        return f"FlatForest(root_names={self.root_names})"

    #### implementation of node-centric methods, we treat the forest as a tree
    #### and either raise an exception if it is a forest, or return the first
    #### root node if that is desired.

    @property
    def children(self):
        """
        Get the children of the preferred root node.

        :return: The children of the preferred root node.
        """
        return self.subtree().children
    
    def add_child(self, name: Optional[str] = None, *args, **kwargs) -> "FlatForestNode":
        """
        Add a child node to the preferred root node.

        :param name: The name of the child node.
        :param payload: The payload of the child node.
        :return: The child node.
        """
        return self.subtree().add_child(name=name, *args, **kwargs)
    
    @property
    def parent(self) -> Optional["FlatForestNode"]:
        """
        Get the parent of the preferred root node. This is always None
        since the preferred root node is a root node.
        """
        return None
    
    @property
    def roots(self) -> List["FlatForestNode"]:
        """
        Get the root nodes of the forest.

        :return: The root nodes of the forest.
        """
        return [self.subtree(name) for name in self.root_names]

    @property
    def preferred_root(self) -> str:
        """
        Get the preferred root node of the forest.

        :return: The preferred root node.
        :raises KeyError: If the preferred root node is not found.
        """

        if self._preferred_root is not None:
            return self._preferred_root
        elif len(self.root_names) == 0:
            raise KeyError("No root nodes and no explicit preferred root set")
        else:
            return self.root_names[0]
        
    @preferred_root.setter
    def preferred_root(self, name: Optional[str]) -> None:
        """
        Set the preferred root node of the forest.

        :param name: The name of the preferred root node.
        :return: None
        :raises KeyError: If the preferred root node is not found.
        """
        self._preferred_root = name

    def __eq__(self, other: Any) -> bool:
        """
        Check if the forest is equal to another forest.

        :param other: The other forest to compare to.
        :return: True if the forests are equal, False otherwise.
        """
        #return isinstance(other, FlatForest) and dict(self) == dict(other)
        return hash(self.subtree()) == hash(other.subtree())
    
    def nodes(self) -> List["FlatForestNode"]:
        """
        Get all the nodes in the forest.

        :return: A list of all the nodes in the forest.
        """
        from .flat_forest_node import FlatForestNode
        return [FlatForestNode.proxy(forest=self, node_key=key, root_key=key) for key in self.node_names()]

    @property
    def root(self) -> "FlatForestNode":
        """
        Get the tree rooted at the preferred root node.

        :return: The root node.
        """
        return self.subtree().root
    
    @property    
    def payload(self) -> dict:
        """
        Get the payload of the preferred root node.

        :return: The payload of the preferred root node.
        """
        return self.subtree().payload
    

    @payload.setter
    def payload(self, data: Dict) -> None:
        """
        Set the payload of the preferred root node.

        :param payload: The payload to set.
        :return: None
        """
        self.subtree().payload = data

    @property
    def name(self) -> str:
        """
        Get the name of the preferred root node. This is just
        self.preferred_root.

        :return: The name of the preferred root node.
        """
        return self.preferred_root
    
    @name.setter
    def name(self, name: str) -> None:
        """
        Set the name of the preferred root node.

        :param name: The name to set.
        :return: None
        """
        self.subtree().name = name
        self._preferred_root = name
    
    def node(self, name: str) -> "FlatForestNode":
        """
        Get an ancestor node with the given name under the preferred root node.

        :param name: The name of the node.
        :return: The node.
        """
        from .flat_forest_node import FlatForestNode

        return FlatForestNode.proxy(forest=self, node_key=name,
                                    root_key=self.root_key(name))

    def subtree(self, name: Optional[str] = None) -> "FlatForestNode":
        """
        Get sub-tree rooted at the node with the name `name` with the current
        node also set to that node. If `name` is None, the preferred root node
        is used.

        NOTE: This behavior is different from the expected behavior of a tree,
        since this is a forest. If the forest has multiple trees, this method
        will return any subtree under any root node. We could instead return
        the subtree under the preferred root node, which would then replicate
        the expected behavior and be consistent with the other node-centric
        methods like `node` and `children`. However, we choose to return the
        subtree under any root node to provide more flexibility. Once you
        return a subtree, the `FlatForestNode` class provides a node-centric
        interface to the tree structure consistent with the expected behavior.

        :param name: The unique name of the node.
        :return: FlatForestNode proxy representing the node.
        """
        from .flat_forest_node import FlatForestNode

        if name is None:
            name = self.preferred_root

        if name not in self.node_names():
            raise KeyError(f"Node name not found: {name!r}")
        
        return FlatForestNode.proxy(forest=self, node_key=name, root_key=name)

    def contains(self, name: str) -> bool:
        """
        Check if the tree rooted at the preferred root node contains a node
        with the given name.

        :param name: The name of the node.
        :return: True if the node is in the forest, False otherwise.
        """
        return self.subtree().contains(name)
    
    def to_dict(self) -> dict:
        """
        Convert the forest to a dictionary. Note this since this is already
        a dictionary, we just return a copy of the dictionary.

        :return: A dictionary representation of the forest.
        """
        return deepcopy(self)
    
    def __hash__(self) -> int:
        return hash(self.subtree())

```

#### Source File: `AlgoTree/flat_forest_node.py`

```python
import collections.abc
import uuid
from typing import Any, Dict, Iterator, List, Optional, Union
from copy import deepcopy
from AlgoTree.flat_forest import FlatForest

class FlatForestNode(collections.abc.MutableMapping):
    __slots__ = ("_forest", "_key", "_root_key")

    def __deepcopy__(self, memo):
        """
        Deepcopy the entire forest that the node is a part of and return a new
        node with the copied forest. This is a deep copy of the forest, not just
        the node. If you want to copy just the node, see the `clone` method.

        :param memo: The memo dictionary.
        :return: A new node with a deep copy of the forest.
        """
        new_node = FlatForestNode.__new__(FlatForestNode)
        memo[id(self)] = new_node
        new_node._forest = deepcopy(self._forest, memo)
        new_node._key = self._key
        new_node._root_key = self._root_key
        return new_node
      
    def clone(self, parent=None, clone_children=False) -> "FlatForestNode":
        """
        Clone the node and, optionally, its children. If you want to
        clone the entire forest, see `deepcopy`. We allow
        the parent to be set to a new parent node to facilitate flexible
        cloning of nodes into new forest structures.

        :return: A new node (or subtree rooted at the node if `clone_children`
                 is True)
        """
        new_node = FlatForestNode.__new__(FlatForestNode)
        if parent is None:
            new_node._forest = FlatForest({ self._key: deepcopy(self._forest[self._key]) })
            new_node._root_key = self._key
        else:
            if self._key in parent._forest:
                raise ValueError(f"Node {self} already exists in the forest")
            new_node._forest = parent._forest
            new_node._forest[self._key] = deepcopy(self._forest[self._key])
            new_node._root_key = parent._root_key

        if clone_children:
            for child in self.children:
                child.clone(parent=new_node, clone_children=True)
        new_node._key = self._key
        return new_node

    @staticmethod
    def proxy(
        forest: FlatForest, node_key: str, root_key: Optional[str] = None
    ) -> "FlatForestNode":
        """
        Create a proxy node for a node in a forest. The proxy node is a
        lightweight object that provides a node-centric abstraction of the
        tree that a node is a part of.

        We do not check do any checks on the validity of the keys or the
        structure of the tree. This is a low-level method that should be used
        with caution. For instance, if `node_key` is not a descendent of
        `root_key`, the proxy node will not behave as expected.

        :param forest: The forest in which the proxy node exists (or logically exists).
        :param node_key: The key of the node.
        :param root_key: The key of the (real or logical) root node.
        """
        node = FlatForestNode.__new__(FlatForestNode)
        node._forest = forest
        node._key = node_key
        if root_key is None:
            root_key = node_key
        node._root_key = root_key
        return node

    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional[Union["FlatForestNode",str]] = None,
        forest: Optional[FlatForest] = None,
        payload: Optional[Dict] = None,
        *args,
        **kwargs,
    ):
        """
        Create a new node. If the key is None, a UUID is generated.

        If a parent is provided, the node is created as a child of the parent.

        Otherwise, if parent is None, the node is created as a root node in a
        new tree. If the forest is provided, the node is created in the given
        forest, otherwise a new forest is created.

        :param parent: The parent node. If None, new tree created.
        :param name: The unique name (key) for the node. If None, UUID generated.
        :param forest: The forest in which the node is created.
        :param payload: The payload data for the node.
        :param args: Positional arguments for the node.
        :param kwargs: Additional attributes for the node.
        """

        if name is None:
            self._key = str(uuid.uuid4())
        else:
            self._key = str(name)

        if parent is not None:
            # check if parent is a node or a key
            if isinstance(parent, str):
                if forest is None:
                    raise ValueError("Parent key provided without a forest")
                parent = FlatForestNode.proxy(forest=forest, node_key=parent)
            self._forest = parent._forest
            if self._key in self._forest.keys():
                raise KeyError(f"key already exists in the tree: {self._key}")
            kwargs[FlatForest.PARENT_KEY] = parent._key
            self._root_key = parent._root_key
        else:
            self._forest = FlatForest() if forest is None else forest
            self._root_key = self._key
            kwargs[FlatForest.PARENT_KEY] = None

        # add payload to kwargs too
        kwargs.update(payload or {})
        self._forest[self._key] = dict(*args, **kwargs)

    @property
    def name(self):
        """
        Get the unique name of the node.

        :return: The unique name of the node.
        """
        return self._key
    
    @name.setter
    def name(self, name: str) -> None:
        """
        Set the unique name of the node.

        :param name: The new unique name of the node.
        """

        if name == self._key:
            return

        if name in self._forest.keys():
            raise ValueError(f"Node with name {name} already exists")

        for child_key in self._forest.keys():
            if self._forest[child_key].get(FlatForest.PARENT_KEY, None) == self._key:
                self._forest[child_key][FlatForest.PARENT_KEY] = name
        self._forest[name] = self._forest.pop(self._key)
        self._key = name
    
    @property
    def root(self) -> "FlatForestNode":
        """
        Get the root node of the subtree.

        :return: The root node.
        """
        return FlatForestNode.proxy(
            forest=self._forest, node_key=self._root_key, root_key=self._root_key
        )
        
    @property
    def parent(self) -> Optional["FlatForestNode"]:
        """
        Get the parent node of the node.

        :return: The parent node.
        """
        if self._key == self._root_key or self._key not in self._forest.keys():
            return None

        # we do it this way in case for instance it's a logical root like
        # the root of the detached nodes.
        par_key = self._forest[self._key].get(
            FlatForest.PARENT_KEY, self._root_key)
        
        return FlatForestNode.proxy(
            forest=self._forest, node_key=par_key, root_key=self._root_key
        )

    @parent.setter
    def parent(self, node: "FlatForestNode") -> None:
        """
        Set the parent node of the node.

        :param node: The new parent node.
        """
        if self._key not in self._forest:
            raise ValueError(f"{self._key} is an immutable logical root")

        if node._forest != self._forest:
            if self._key in node._forest:
                raise ValueError(f"Node {self} already exists in the forest")
            node._forest[self._key] = self._forest[self._key].copy()

        node._forest[self._key][FlatForest.PARENT_KEY] = node._key

    @property
    def forest(self) -> FlatForest:
        """
        Get the underlying FlatForest object.

        :return: The FlatForest object.
        """
        return self._forest

    def __repr__(self):
        par = None if self._key == self._root_key else self.parent.name
        child_keys = self._forest.child_names(self._key)
        return f"{__class__.__name__}(name={self.name}, parent={par}, payload={self.payload}, root={self.root.name}, children={child_keys})"

    def __getitem__(self, key) -> Any:
        if self._key not in self._forest:
            raise KeyError(
                f"{self._key} is an immutable logical root without a payload"
            )

        return self._forest[self._key][key]

    def __setitem__(self, key, value) -> None:
        if self._key not in self._forest:
            raise TypeError(f"{self._key} is an immutable logical root")

        self._forest[self._key][key] = value

    def __delitem__(self, key) -> None:
        if self._key not in self._forest:
            raise TypeError(f"{self._key} is an immutable logical root")

        del self._forest[self._key][key]

    def __getattr__(self, key) -> Any:
        if key in ["name", "parent", "root", "forest", "payload", "children"]:
            return object.__getattribute__(self, key)
        if key in self:
            return self[key]
        return None

    def detach(self) -> "FlatForestNode":
        """
        Detach the node.

        :return: The detached node.
        """
        return self._forest.detach(self._key)

    @property
    def payload(self) -> Dict:
        """
        Get the payload data of the node.

        :return: Dictionary representing the data of the node.
        """
        if self._key not in self._forest.keys():
            return dict()  # logical node

        data = self._forest[self._key].copy()
        data.pop(FlatForest.PARENT_KEY, None)
        return data

    @payload.setter
    def payload(self, data: Dict) -> None:
        """
        Set the payload data of the node.

        :param data: Dictionary representing the new data of the node.
        """
        if not isinstance(data, dict):
            raise ValueError("Payload must be a dictionary")

        if self._key not in self._forest:
            raise KeyError(
                f"{self._key} is an immutable logical root without a payload"
            )
        if FlatForest.PARENT_KEY in data:
            raise ValueError("Cannot set parent using payload setter")

        data[FlatForest.PARENT_KEY] = self._forest[self._key].get(FlatForest.PARENT_KEY)
        self._forest[self._key] = data

    def __iter__(self) -> Iterator[Any]:
        return iter([] if self._key not in self._forest else self._forest[self._key])

    def __len__(self) -> int:
        return len(self.payload)

    def add_child(self, name: Optional[str] = None, *args, **kwargs) -> "FlatForestNode":
        """
        Add a child node. See `__init__` for details on the arguments.

        :return: The child node, from the perspective of the subtree that
                 contains the parent.
        """
        return FlatForestNode(name=name, parent=self, *args, **kwargs)
    
    @property
    def children(self) -> List["FlatForestNode"]:
        """
        Get the children of the node.

        :return: List of child nodes.
        """
        return [
            FlatForestNode.proxy(
                forest=self._forest, node_key=child_key, root_key=self._root_key
            )
            for child_key in self._forest.child_names(self._key)
        ]

    @children.setter
    def children(self, nodes: List["FlatForestNode"], append: bool = False) -> None:
        """
        Set the children of the node.

        :param nodes: The new children nodes.
        """
        if not append:
            for node in self.children:
                node.detach()

        if nodes is None:
            return

        if not isinstance(nodes, list):
            nodes = [nodes]

        for node in nodes:
            node.parent = self

    def __eq__(self, other):
        """
        There are many ways to define equality for nodes in a tree. We define
        node equality, by default, as path equality. Two nodes are equal if
        they have the same path in a tree. Note that we allow equality of nodes
        in different trees.

        :param other: The other node to compare with.
        :return: True if the nodes are equal, False otherwise.
        """
        return hash(self) == hash(other)
    
    def node(self, name: str) -> "FlatForestNode":
        """
        Get an ancestor node with the given name.

        :param name: The name of the node.
        :return: The node.
        """
        return FlatForestNode.proxy(forest=self._forest, node_key=name, root_key=self._root_key)

    def subtree(self, name: Optional[str] = None) -> "FlatForestNode":
        """
        Get a subtree rooted at the node with the name `name`. If `name` is
        None, the subtree is rooted at the current node.

        :param name: The name of the root node.
        :return: A subtree rooted at the given node.
        """

        if name is None:
            name = self.name

        return FlatForestNode.proxy(forest=self._forest, node_key=name, root_key=name)
    
    def contains(self, name) -> bool:
        """
        Check if the the subtree rooted at the node contains any children
        with the given name

        :param key: The key to check.
        :return: True if the child node is present, False otherwise.
        """

        from .utils import is_ancestor
        return is_ancestor(self, self.node(name))
        
    def __contains__(self, key) -> bool:
        """
        Check if the node's payload contains the given key.

        :param key: The key to check for.
        :return: True if the key is present in the payload, False otherwise.
        """
        return key in self.payload
    
    def to_dict(self):
        """
        Convert the subtree rooted at `node` to a dictionary.

        :return: A dictionary representation of the subtree.
        """
        from .tree_converter import TreeConverter
        return TreeConverter.convert(self, FlatForestNode).forest
    
    def __hash__(self) -> int:
        """
        Get the hash of the node.

        :return: The hash of the node.
        """
        
        from .node_hasher import NodeHasher
        return NodeHasher.path(self)
```

#### Source File: `AlgoTree/node_hasher.py`

```python
from typing import Any
import AlgoTree.utils as utils
from AlgoTree.tree_converter import TreeConverter

class NodeHasher:
    """
    A class providing various hash functions for tree nodes.
    """
    def __init__(self, hash_fn=None):
        """
        Initialize the NodeHasher with a specified hash function.

        :param hash_function: A hash function to use for nodes. If None, defaults to `self.node`.
        """
        self.hash_fn = hash_fn or self.node

    def __call__(self, node: Any) -> int:
        """
        Apply the hash function to a node.

        :param node: The node to hash.
        :return: The hash value for the node.
        """
        return self.hash_fn(node)

    @staticmethod
    def name(node: Any) -> int:
        """
        Compute a hash based on the name of the node.

        Use Case:
        - Useful when you want to compare nodes solely based on their names, ignoring their position and other attributes.

        Example:
        - Checking if two nodes represent the same entity based on their name.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's name.
        """
        if node is None or not hasattr(node, 'name'):
            raise ValueError("Node must have a 'name' attribute")
        return hash(str(node.name))

    @staticmethod
    def payload(node: Any) -> int:
        """
        Compute a hash based on the payload of the node.

        Use Case:
        - Useful when comparing nodes based on their payload, ignoring their name and position in the tree.

        Example:
        - Identifying nodes that carry the same data.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's payload.
        """
        if node is None or not hasattr(node, 'payload'):
            raise ValueError("Node must have a 'payload' attribute")
        return hash(str(node.payload))
    
    @staticmethod
    def node(node: Any) -> int:
        """
        Compute a hash based on the name and payload of the node.

        Use Case:
        - This is the most common notion of node equality, focusing on the node's intrinsic properties and ignoring its position in the tree.
        - Useful when you want to compare nodes by both name and payload, but not their position in the tree.

        Example:
        - Checking if two nodes are equivalent in terms of both their name and the data they carry, without considering their location in the tree structure.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's name and payload.
        """
        if node is None or not hasattr(node, 'name') or not hasattr(node, 'payload'):
            raise ValueError("Node must have 'name' and 'payload' attributes")
        
        return hash(str((node.name, node.payload)))

    @staticmethod
    def path(node: Any) -> int:
        """
        Compute a hash based on the path of the node in the tree.

        Use Case:
        - Useful when the position of the node in the tree is more important than its name or payload.

        Example:
        - Determining if two nodes occupy the same position in the same or different trees.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's path in the tree.
        """
        if node is None:
            raise ValueError("Node cannot be None")
        return hash(str([n.name for n in utils.path(node)]))

```

#### Source File: `AlgoTree/pretty_tree.py`

```python
from typing import Callable, Optional, Dict, Any, List

#from AlgoTree.treenode_api import TreeNodeApi

class PrettyTree:
    """
    A class to print a tree in a more readable way.
    """

    default_style = {
        "vertical": "│",
        "horizontal": "─",
        "last_child_connector": "└",
        "markers": ["🔵", "🔴", "🟢", "🟣", "🟠", "🟡", "🟤", "⚫", "⚪", "⭕", "🔘"],
        "spacer": " ",
        "child_connector": "├",
        "payload_connector": "◄"
    }

    def __init__(self,
                 style: Optional[Dict[str, str]] = None,
                 node_name: Callable[[Any], str] = lambda node: node.name,
                 indent: int = 7,
                 mark: Optional[List[str]] = None,
                 node_details: Optional[Callable[[Any], Any]] = None):
        """
        Initialize the PrettyTree object. If a node name is not provided, the default
        node name is the `name` property of the node. If a node detail is not provided,
        no additional node details are displayed. If a style is not provided, the default
        style is used. Any missing style keys are filled in with the default style.

        :param style: A style to use for printing. See `default_style` for the default style.
        :param node_name: A function that returns the name of a node. Defaults to returning the node's `name` property.
        :param mark: A list of node names. The marker will be a function of the hash of the node's name,
        which indexes into the markers.
        :param node_details: A function to map a node to a string to be displayed next to the node name. Default is None.
        :param indent: The number of spaces to indent each level of the tree.
        """
        self.style = self.default_style.copy()
        if style:
            self.style.update(style)

        self.node_name = node_name
        self.node_details = node_details
        self.marked_nodes = mark if mark is not None else []
        self.indent = indent

    @staticmethod
    def mark(name: str, markers: List[str]) -> str:
        """
        Get the marker for a node based on the hash of the node name.

        :param name: The name of the node.
        :return: The marker for the node.
        """
        return markers[hash(name) % len(markers)]

    def __call__(self, node, **kwargs) -> str:
        """
        Print the tree.

        :param node: The root node of the tree.
        :param kwargs: Additional style parameters to override the default style.
        :return: A pretty string representation of the tree.
        """
        # TreeNodeApi.check(node)
        style = self.style.copy()
        style.update(kwargs.get("style", {}))

        marked_nodes = self.marked_nodes + kwargs.get("mark", [])
        node_name = kwargs.get("node_name", self.node_name)
        node_details = kwargs.get("node_details", self.node_details)
        indent = kwargs.get("indent", self.indent)
        markers = kwargs.get("markers", style['markers'])

        def _build(cur, ind, bar_levels, is_last):
            s = ""
            if ind > 0:
                for i in range(ind - 1):
                    if i in bar_levels:
                        s += style["vertical"]
                    else:
                        s += style["spacer"]
                    s += style["spacer"] * (indent - 1)
                if is_last:
                    s += style["last_child_connector"]
                else:
                    s += style["child_connector"]
                s += style["horizontal"] * (indent - 2)
                s += style["spacer"] 

            s += str(node_name(cur))
            if node_details is not None:
                s += style["spacer"]
                s += style["payload_connector"]
                s += style["spacer"]
                s += str(node_details(cur))
            if node_name(cur) in marked_nodes:
                s += style["spacer"]
                s += PrettyTree.mark(str(node_name(cur)), markers)
            s += "\n"

            for i, child in enumerate(cur.children):
                new_bar_levels = bar_levels.copy()
                if i < len(cur.children) - 1:
                    new_bar_levels.add(ind)
                s += _build(child, ind + 1, new_bar_levels, i == len(cur.children) - 1)

            return s

        return _build(node, 0, set(), True)


def pretty_tree(node, **kwargs) -> str:
    """
    Converts a tree to a pretty string representation.

    :param kwargs: Key-word arguments. See `PrettyTree` for more details.
    :return: A pretty string representation of the tree.
    """
    return PrettyTree()(node, **kwargs)

```

#### Source File: `AlgoTree/tree_converter.py`

```python
import uuid
from copy import deepcopy
from typing import Any, Callable, Type, Dict

class TreeConverter:
    """
    Utility class for converting between tree representations.
    """

    @staticmethod
    def default_extract(node):
        """
        Default extractor of relevant payload from a node.

        :param node: The node to extract payload data from.
        :return: The extracted data.
        """
        return node.payload if hasattr(node, "payload") else None

    @staticmethod
    def default_node_name(node):
        """
        Default function to map nodes to unique keys. If the node has a
        `name` attribute, then it is used as the unique key. Otherwise,
        a random UUID is generated.

        :param node: The node to map to a unique key.
        :return: The unique key for the node.
        """
        return node.name if hasattr(node, "name") else str(uuid.uuid4())


    @staticmethod
    def copy_under(
        node,
        under,
        node_name: Callable = default_node_name,
        extract: Callable = default_extract,
        max_tries: int = 1000) -> Any:
        """
        Copy the subtree rooted at `node` as a child of `under`, where
        the copy takes on the node type of `under`. It returns the subtree
        that contains `under` with current node at `under`.

        :param node: The subtree rooted at `node` to copy.
        :param under: The node to copy the subtree under.
        :param node_name: The function to map nodes to names.
        :param extract: A callable to extract relevant payload from a node.
        :param max_tries: The maximum number of tries to generate a unique name
                          if a name conflict occurs.
        :return: A subtree extending `under` with the copied nodes.
        """

        if not hasattr(node, "children"):
            raise ValueError("Node must have a children attribute or property")

        node_type = type(under)
        tries: int = 0
        def build(cur, und):
            nonlocal tries
            data = deepcopy(extract(cur))
            name = node_name(cur)
            base_name = name
            while tries <= max_tries:
                try:
                    node = node_type(name=name, parent=und, payload=data)
                    break
                except Exception as e:
                    name = f"{base_name}_{tries}"

                tries += 1
                if tries >= max_tries:
                    raise ValueError("Max tries exceeded")

            for child in cur.children:
                build(child, node)
            return node

        return build(node, under)

    @staticmethod
    def convert(
        source,
        target_type: Type,
        node_name: Callable = default_node_name,
        extract: Callable = default_extract) -> Any:
        """
        Convert a tree rooted at `node` to a target tree type representation.

        :param src_node: The root node of the tree to convert.
        :param target_type: The target tree type to convert to.
        :param node_name: The function to map nodes to unique keys.
        :param extract: A callable to extract relevant data from a node.
        :return: The converted tree.
        """

        if source is None:
            return None
        
        root = target_type(
            name=node_name(source),
            parent=None,
            payload=deepcopy(extract(source)))
        
        for child in source.children:
            TreeConverter.copy_under(node=child,
                                     under=root,
                                     node_name=node_name,    
                                     extract=extract)
        return root
        
    @staticmethod
    def to_dict(node,
                node_name: Callable = default_node_name,
                extract: Callable  = default_extract,
                **kwargs) -> Dict:
        """
        Convert the subtree rooted at `node` to a dictionary.

        :param node: The root node of the subtree to convert.
        :param node_name: The function to map nodes to unique keys.
        :param extract: A callable to extract relevant data from a node.
        :return: A dictionary representation of the subtree.
        """

        def _build(node):
            return {
                "name": node_name(node),
                "payload": extract(node, **kwargs),
                "children": [_build(child, **kwargs) for child in node.children]
            }
        
        return _build(node)


```

#### Source File: `AlgoTree/tree_hasher.py`

```python

from typing import Any
from AlgoTree.tree_converter import TreeConverter

class TreeHasher:
    """
    A class that provides various hash functions for trees, with a default hashing strategy.
    """

    def __init__(self, hash_fn=None):
        """
        Initialize the TreeHasher with a specified hash function.
        
        :param hash_function: A hash function to use for trees. If None, defaults to `self.tree`.
        """
        self.hash_fn = hash_fn or self.tree

    def __call__(self, tree: Any) -> int:
        """
        Make TreeHasher callable, using the default hash function.
        
        :param tree: The tree to hash.
        :return: The hash value for the tree.
        """
        return self.hash_fn(tree)

    @staticmethod
    def tree(tree: Any) -> int:
        """
        Hash based on the entire tree structure.

        :param tree: The tree to hash.
        :return: The hash value for the tree.
        """
        if tree is None:
            raise ValueError("Tree cannot be None")
        
        return hash(str(TreeConverter.to_dict(tree)))

    @staticmethod
    def isomorphic(tree: Any) -> int:
        """Hash based on tree structure only, ignoring node names and payloads."""
        if tree is None:
            raise ValueError("Tree cannot be None")

        def build(node):            
            child_nums = [TreeHasher.isomorphic(child) for child in tree.children]
            return [len(node.children), child_nums]

        return build(tree)

```

#### Source File: `AlgoTree/treenode.py`

```python
from typing import Dict, List, Optional, Any
import copy
import uuid

class TreeNode(dict):
    """
    A tree node class. This class stores a nested
    representation of the tree. Each node is a TreeNode object, and if a node
    is a child of another node, it is stored in the parent node's `children`
    attribute.
    """

    @staticmethod
    def from_dict(data: Dict) -> "TreeNode":
        """
        Create a TreeNode from a dictionary.

        :param data: The dictionary to convert to a TreeNode.
        :return: A TreeNode object.
        """

        def _from_dict(data, parent):
            node = TreeNode(parent=parent, payload=None,
                            name=data.pop("name", None))
            node.payload = data.pop("payload", {})
            for k, v in data.items():
                if k == "children":
                    for child in v:
                        _from_dict(child, node)
                else:
                    node.payload[k] = v
            return node
        
        return _from_dict(copy.deepcopy(data), None)

    def clone(self) -> "TreeNode":
        """
        Clone the tree node (sub-tree) rooted at the current node.

        :return: A new TreeNode object with the same data as the current node.
        """
        def _clone(node, parent):
            new_node = TreeNode(parent=parent,
                                name=node.name,
                                payload=copy.deepcopy(node.payload))
            for child in node.children:
                _clone(child, new_node)
            return new_node
        
        return _clone(self, None)

    def __init__(
        self,
        parent: Optional["TreeNode"] = None,
        name: Optional[str] = None,
        payload: Optional[Any] = None,
        *args, **kwargs):
        """
        Initialize a TreeNode. The parent of the node is set to the given parent
        node. If the parent is None, the node is the root of the tree. The name
        of the node is set to the given name. If the name is None, a random name
        is generated. The payload of the node is any additional arguments passed
        to the constructor.

        :param parent: The parent node of the current node. Default is None.
        :param name: The name of the node. Default is None, in which case a
                     random name is generated.
        :param payload: The payload of the node. Default is None.
        :param args: Additional arguments to pass to the payload.
        :param kwargs: Additional keyword arguments to pass to the payload.
        """
        if name is None:
            name = str(uuid.uuid4())
        self.name = name

        if parent is not None and not isinstance(parent, TreeNode):
            raise ValueError("Parent must be a TreeNode object")
        self.children = []
        self._parent = None
        self.parent = parent

        if payload is not None:
            self.payload = payload
        elif args or kwargs:
            self.payload = dict(*args, **kwargs)
        else:
            self.payload = None


    @property
    def parent(self) -> Optional["TreeNode"]:
        """
        Get the parent of the node.

        :return: The parent of the node.
        """
        return self._parent

    @parent.setter
    def parent(self, parent: Optional["TreeNode"]) -> None:
        """
        Set the parent of the node.

        :param parent: The new parent of the node.
        """
        if parent is not None and not isinstance(parent, TreeNode):
            raise ValueError("Parent must be a TreeNode object")
        
        # remove the node from the parent's children
        if self._parent is not None:
            self._parent.children.remove(self)
            #self._parent.children = [child for child in self._parent.children if child != self]

        self._parent = parent

        # update parent's children
        if parent is not None:
            parent.children.append(self)

    @property
    def root(self) -> "TreeNode":
        """
        Get the root of the tree.

        :return: The root node of the tree.
        """
        node = self
        while node.parent is not None:
            node = node.parent
        return node
    
    def nodes(self) -> List["TreeNode"]:
        """
        Get all the nodes in the current sub-tree.

        :return: A list of all the nodes in the current sub-tree.
        """
        nodes = []
        for child in self.children:
            nodes.extend(child.nodes())
        nodes.append(self)
        return nodes
    
    def subtree(self, name: str) -> "TreeNode":
        """
        Get the subtree rooted at the node with the given name. This is not
        a view, but a new tree rooted at the node with the given name. This
        is different from the `node` method, which just changes the current
        node position. It's also different from the `subtree` method in the
        `FlatForestNode` class, which returns a view of the tree.

        :param name: The name of the node.
        :return: The subtree rooted at the node with the given name.
        """
        from copy import deepcopy
        node = deepcopy(self.node(name))
        node.parent = None
        return node
    
    def node(self, name: str) -> "TreeNode":
        """
        Get the node with the given name in the current sub-tree. The sub-tree
        remains the same, we just change the current node position. If the name
        is not found, raise a KeyError.

        :param name: The name of the node.
        :return: The node with the given name.
        """

        def _descend(node, name):
            if node.name == name:
                return node
            for child in node.children:
                result = _descend(child, name)
                if result is not None:
                    return result
            return None
        
        def _ascend(node, name):
            if node.name == name:
                return node
            if node.parent is not None:
                return _ascend(node.parent, name)
            return None
        
        asc_node = _ascend(self, name)
        if asc_node is not None:
            return asc_node
        dsc_node =_descend(self, name)
        if dsc_node is not None:
            return dsc_node
        
        raise KeyError(f"Node with name {name} not found")

    def add_child(self, name: Optional[str] = None,
                  payload: Optional[Any] = None,
                  *args, **kwargs) -> "TreeNode":
        """
        Add a child node to the tree. Just invokes `__init__`. See `__init__` for
        details.
        """
        return TreeNode(parent=self, name=name, payload=payload, *args, **kwargs)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        result = f"TreeNode(name={self.name}"
        if self._parent is not None:
            result += f", parent={self.parent.name}"
        result += f", root={self.root.name}"
        result += f", payload={self.payload}"
        result += f", len(children)={len(self.children)})"
        return result
    
    @staticmethod
    def is_valid(data) -> bool:
        """
        Check if the given data is a valid TreeNode data.

        :param data: The data to check.
        :return: True if the data is a valid TreeNode, False otherwise.
        """
        if not isinstance(data, dict):
            return False
        if "children" in data:
            if not isinstance(data["children"], list):
                return False
            for child in data["children"]:
                if not TreeNode.is_valid(child):
                    return False
        
        return True
    
    def to_dict(self):
        """
        Convert the subtree rooted at `node` to a dictionary.

        :return: A dictionary representation of the subtree.
        """
        def _convert(node):
            node_dict = {}
            node_dict["name"] = node.name
            node_dict["payload"] = node.payload
            node_dict["children"] = [_convert(child) for child in node.children]
            return node_dict

        return _convert(self)
    
    def __eq__(self, other) -> bool:
        """
        Check if the current node is equal to the given node.

        :param other: The other node to compare with.
        :return: True if the nodes are equal, False otherwise.
        """
        if not isinstance(other, TreeNode):
            return False
        
        return hash(self) == hash(other)
    
    def __hash__(self) -> int:
        """
        Compute the hash of the current node.

        :return: The hash of the node.
        """
        return id(self)
    
    def __contains__(self, key) -> bool:
        """
        Check if the node's payload contains the given key.

        :param key: The key to check for.
        :return: True if the key is present in the payload, False otherwise.
        """
        return key in self.payload

```

#### Source File: `AlgoTree/treenode_api.py`

```python
from typing import Any

class TreeNodeApi:
    """
    A class to check if a tree object models the concept of a tree node.
    The tree node concept is defined as follows:

    - **children** property

        Represents a list of child nodes for the current node that can be
        accessed and modified.

    - **parent** property
    
        Represents the parent node of the current node that can be accessed
        and modified. 
        
        Suppose we have the subtree `G` at node `G`::

                B (root)
                ├── D
                └── E (parent)
                    └── G (current node)

        Then, `G.parent` should refer node `E`. `G.root.parent` should be None
        since `root` is the root node of subtree `G` and the root node has no parent.
        This is true even if subtree `G` is a subtree view of a larger tree.

        If we set `G.parent = D`, then the tree structure changes to::

                B (root)
                ├── D
                │   └── G (current node)
                └── E
        
        This also changes the view of the sub-tree, since we changed the
        underlying tree structure. However, the same nodes are still accessible
        from the sub-tree.

        If we had set `G.parent = X` where `X` is not in the subtree `G`, then
        we would have an invalid subtree view even if is is a well-defined
        operation on the underlying tree structure. It is undefined
        behavior to set a parent that is not in the subtree, but leave it
        up to each implementation to decide how to handle such cases.

    - **node(name: str) -> NodeType** method.

        Returns a node in the current subtree that the
        current node belongs to. The returned node should be the node with the
        given name, if it exists. If the node does not exist, it should raise
        a `KeyError`.

        The node-centric view of the returned node should be consistent with the
        view of the current node, i.e., if the current node belongs to a specific sub-tree
        rooted at some other node, the returned node should also belong to the
        same sub-tree (i.e., with the same root), just pointing to the new node,
        but it should be possible to use `parent` and `children` to go up and down
        the sub-tree to reach the same nodes. Any node that is an ancestor of the
        root of the sub-tree remains inaccessible.

        Example: Suppose we have the sub-tree `t` rooted at `A` and the current node
        is `B`::

                A (root)
                ├── B (current node)
                │   ├── D
                │   └── E
                |       └── G
                └── C
                    └── F
        
        If we get node `F`, `t.node(F)`, then the sub-tree `t` remains the same,
        but the current node is now `F`::
        
                A (root)
                ├── B
                │   ├── D
                │   └── E
                |       └── G
                └── C
                    └── F (current node)

    - **subtree(node: Optional[NodeType] = None) -> NodeType** method.

        Returns a view of another sub-tree rooted at `node` where `node` is
        contained in the original sub-tree view. If `node` is `None`, the method
        will return the sub-tree rooted at the current node.
        
        `subtree` is a *partial function* over the the nodes in the sub-tree,
        which means it is only well-defined when `node` is a descendant of
        the root of the sub-tree. We do not specify how to deal with the case
        when this condition is not met, but one approach would be to raise an
        exception.

        Example: Suppose we have the sub-tree `t` rooted at `A` and the current node
        is `C`::

                A (root)
                ├── B
                │   ├── D
                │   └── E
                |       └── G
                └── C (current node)
                    └── F

        The subtree `t.subtree(B)` returns a new subtree::

                B (root, current node)
                ├── D
                └── E
                    └── G
        
    - **root** property

        An immutable property that represents the root node of the sub-tree.
        
        Suppose we have the subtree `G` at node `G`::

                B (root)
                ├── D
                └── E
                    └── G (current node)

        Then, `G.root` should refer node `B`.

    - **payload** property

        Returns the payload of the current node. The payload
        is the data associated with the node but not with the structure of the
        tree, e.g., it does not include the `parent` or `children` of the node.

    - **name** property

        Returns the name of the current node. The name is
        an identifier for the node within the tree. It is not necessarily unique,
        and nor is it necessarily even a meaningful identifier, e.g., a random
        UUID.

    - **contains(name) -> bool** method.

        Returns `True` if the sub-tree contains a node with the given name,
        otherwise `False`.
    """

    properties = ["name", "root", "children", "parent", "node", "subtree", "payload", "contains"]

    @staticmethod
    def missing(node, require_props = properties):

        if node is None:
            raise ValueError("node must not be None")
        
        missing_props = []
        for prop in require_props:
            if not hasattr(node, prop):
                missing_props.append(prop)
        return missing_props
        
    @staticmethod
    def check(node, require_props = properties) -> Any:

        missing_prop = TreeNodeApi.missing(node, require_props)
        if len(missing_prop) > 0:
            raise ValueError(f"missing properties: {missing_prop}")
        return node

    @staticmethod
    def is_valid(value, require_props = properties) -> bool:
        try:
            TreeNodeApi.check(value, require_props)
        except ValueError:
            return False
        return True

```

#### Source File: `AlgoTree/utils.py`

```python
from collections import deque
from typing import Any, Callable, Deque, List, Tuple, Type
from AlgoTree.treenode_api import TreeNodeApi

def visit(node: Any,
          func: Callable[[Any], bool],
          order: str = "post",
          max_hops: int = float("inf"),
          **kwargs) -> bool:
    """
    Visit the nodes in the tree rooted at `node` in a pre-order or post-order
    traversal. The procedure `proc` should have a side-effect you want to
    achieve, such as printing the node or mutating the node in some way.

    If `func` returns True, the traversal will stop and the traversal will
    return True immediately. Otherwise, it will return False after traversing
    all nodes.

    Requirement:

    - This function requires that the node has a `children` property that is
      iterable.

    :param node: The root node to start the traversal.
    :param func: The function to call on each node. The function should take a
                 single argument, the node. It should have some side-effect
                 you want to achieve. See `map` if you want to return a new
                 node to rewrite the sub-tree rooted at `node`.
    :param max_hops: The maximum number of hops to traverse.
    :param order: The order of traversal (`pre`, `post`, or `level`).
    :param kwargs: Additional keyword arguments to pass to `func`.
    :raises ValueError: If the order is not valid.
    :raises TypeError: If func is not callable.
    :raises AttributeError: If the node does not have a 'children'.
    """

    if not callable(func):
        raise TypeError("func must be callable")
    
    if node is None:
        raise ValueError("Node must not be None")

    if order not in ("pre", "post", "level"):
        raise ValueError(f"Invalid order: {order}")

    if not hasattr(node, "children"):
        raise AttributeError("node must have a 'children' property")

    if order == "level":
        return breadth_first(node, func, **kwargs)

    s = deque([(node, 0)])
    while s:
        node, depth = s.pop()
        if max_hops < depth:
            continue

        if order == "pre":
            if func(node, **kwargs):
                return True

        s.extend([(c, depth + 1) for c in reversed(node.children)])
        if order == "post":
            if func(node, **kwargs):
                return True

    return False

def map(node: Any,
        func: Callable[[Any], Any],
        order: str = "post",
        **kwargs) -> Any:
    """
    Map a function over the nodes in the tree rooted at `node`. It is a map
    operation over trees. In particular, the function `func`, of type::

        func : Node -> Node,

    is called on each node in pre or post order traversal. The function should
    return a new node. The tree rooted at `node` will be replaced (in-place)
    with the tree rooted at the new node. The order of traversal can be
    specified as 'pre' or 'post'.

    Requirement:

    - This function requires that the node has a `children` property that is
      iterable and assignable, e.g., `node.children = [child1, child2, ...]`.

    :param node: The root node to start the traversal.
    :param func: The function to call on each node. The function should take a
                 single argument, the node, and return a new node (or
                 have some other side effect you want to achieve).
    :param order: The order of traversal (pre or post).
    :param kwargs: Additional keyword arguments to pass to `func`.
    :raises ValueError: If the order is not 'pre' or 'post'.
    :raises TypeError: If func is not callable.
    :return: The modified node. If `func` returns a new node, the tree rooted
             at `node` will be replaced with the tree rooted at the new node.
    """

    if not callable(func):
        raise TypeError("`func` must be callable")
    
    if node is None:
        return None

    if order not in ("pre", "post"):
        raise ValueError(f"Invalid order: {order}")

    if not hasattr(node, "children"):
        raise AttributeError("node must have a 'children' property")

    if order == "pre":
        node = func(node, **kwargs)

    if node is None:
        return None

    if hasattr(node, "children"):
        node.children = [c for c in [map(c, func, order, **kwargs) for c in
                         node.children] if c is not None]

    if order == "post":
        node = func(node, **kwargs)

    return node


def descendants(node) -> List:
    """
    Get the descendants of a node.

    :param node: The root node.
    :return: List of descendant nodes.
    """
    if node is None:
        raise ValueError("Node must not be None")

    results = []
    visit(node, lambda n: results.append(n) or False, order="pre")
    return results[1:]


def siblings(node) -> List:
    """
    Get the siblings of a node.

    :param node: The node.
    :return: List of sibling nodes.
    """
    if node is None:
        raise ValueError("Node must not be None")

    if node.parent is None:
        return []   
    sibs = [c for c in node.parent.children]
    sibs.remove(node)
    return sibs

def leaves(node) -> List:
    """
    Get the leaves of a node.

    :param node: The root node.
    :return: List of leaf nodes.
    """

    if node is None:
        raise ValueError("Node must not be None")

    results = []
    visit(
        node,
        lambda n: results.append(n) or False if not n.children else False,
        order="post",
    )
    return results


def height(node) -> int:
    """
    Get the height of a subtree (containing the node `node`, but any
    other node in the subtree would return the same height)

    :param node: The subtree containing `node`.
    :return: The height of the subtree.
    """
    if node is None:
        raise ValueError("Node must not be None")

    def _height(n):
        return 0 if is_leaf(n) else 1 + max(_height(c) for c in n.children)
    
    return _height(node)


def depth(node) -> int:
    """
    Get the depth of a node in its subtree view.

    :param node: The node.
    :return: The depth of the node.
    """
    if node is None:
        raise ValueError("Node must not be None")

    return 0 if is_root(node) else 1 + depth(node.parent)


def is_root(node) -> bool:
    """
    Check if a node is a root node.

    :param node: The node to check.
    :return: True if the node is a root node, False otherwise.
    """
    return node.parent is None


def is_leaf(node) -> bool:
    """
    Check if a node is a leaf node.

    :param node: The node to check.
    :return: True if the node is a leaf node, False otherwise.
    """
    return not is_internal(node)


def is_internal(node) -> bool:
    """
    Check if a node is an internal node.

    :param node: The node to check.
    :return: True if the node is an internal node, False otherwise.
    """

    if node is None:
        raise ValueError("Node must not be None")

    return len(node.children) > 0


def breadth_first(node: Any,
                  func: Callable[[Any], bool],
                  max_lvl = None,
                  **kwargs) -> bool:
    """
    Traverse the tree in breadth-first order. The function `func` is called on
    each node and level. The function should have a side-effect you want to
    achieve, and if it returns True, the traversal will stop. The keyword
    arguments are passed to `func`.

    If `func` returns True, the traversal will stop and the traversal will
    return True immediately. Otherwise, it will return False after traversing
    all nodes. This is useful if you want to find a node that satisfies a
    condition, and you want to stop the traversal as soon as you find it.

    Requirement:

    - This function requires that the node has a `children` property that is
      iterable.

    - The function `func` should have the signature::

        func(node: Any, **kwargs) -> bool

    :param node: The root node.
    :param func: The function to call on each node and any additional keyword
                 arguments. We augment kwargs with a level key, too, which
                 specifies the level of the node in the tree.
    :param max_lvl: The maximum number of levels to descend. If None, the
                    traversal will continue until all nodes are visited
                    or until `func` returns True.
    :param kwargs: Additional keyword arguments to pass to `func`.
    :raises TypeError: If func is not callable.
    :raises AttributeError: If the node does not have a 'children'.
    :return: None
    """
    if not callable(func):
        raise TypeError("func must be callable")
    
    if node is None:
        raise ValueError("Node must not be None")

    if not hasattr(node, "children"):
        raise AttributeError("node must have a 'children' property")

    q: Deque[Tuple[Any, int]] = deque([(node, 0)])
    while q:
        cur, lvl = q.popleft()
        if max_lvl is not None and lvl > max_lvl:
            continue

        kwargs["level"] = lvl
        if func(cur, **kwargs):
            return True

        for child in cur.children:
            q.append((child, lvl + 1))
    return False

def breadth_first_undirected(node, max_hops = float("inf")):
    """
    Traverse the tree in breadth-first order. It treats the tree as an
    undirected graph, where each node is connected to its parent and children.
    """

    if node is None:
        raise ValueError("Node must not be None")

    within_hops = []
    q : Deque[Tuple[Any, int]] = deque([(node, 0)])
    visited = []
    while q:
        cur, depth = q.popleft()
        if depth > max_hops:
            continue
        if cur not in visited:            
            visited.append(cur)
            within_hops.append(cur)
            for child in cur.children:
                q.append((child, depth + 1))
            if cur.parent is not None:
                q.append((cur.parent, depth + 1))
    return within_hops



def find_nodes(node: Any, pred: Callable[[Any], bool], **kwargs) -> List[Any]:
    """
    Find nodes that satisfy a predicate.

    :param pred: The predicate function.
    :param kwargs: Additional keyword arguments to pass to `pred`.
    :return: List of nodes that satisfy the predicate.
    """
    nodes: List[Any] = []
    visit(
        node,
        lambda n, **kwargs: (nodes.append(n) or False
                             if pred(n, **kwargs) else False),
        order="pre",
    )
    return nodes


def find_node(node: Any, pred: Callable[[Any], bool], **kwargs) -> Any:
    """
    Find closest descendent node of `node` that satisfies a predicate (where
    distance is defined with respect to path length). Technically, an order
    defined by path length is a partial order, sine many desendents that
    satisfy the condition may be at the same distance from `node`. We leave
    it up to each implementation to define which among these nodes to return.
    Use `find_nodes` if you want to return all nodes that satisfy the condition
    (return all the nodes in the partial order).
    
    The predicate function `pred` should return True if the node satisfies the
    condition. It can also accept
    any additional keyword arguments, which are passed to the predicate. Note
    that we also augment the keyword arguments with a level key, which specifies
    the level of the node in the tree, so you can use this information in your
    predicate function.

    :param pred: The predicate function which returns True if the node satisfies
                 the condition.
    :param kwargs: Additional keyword arguments to pass to `pred`.
    :return: The node that satisfies the predicate.
    """
    result = None
    def _func(n, **kwargs):
        nonlocal result
        if pred(n, **kwargs):
            result = n
            return True
        else:
            return False

    breadth_first(node, _func, **kwargs)
    return result


def prune(node: Any, pred: Callable[[Any], bool], **kwargs) -> Any:
    """
    Prune the tree rooted at `node` by removing nodes that satisfy a predicate.
    The predicate function should return True if the node should be pruned. It
    can also accept any additional keyword arguments, which are passed to the
    predicate.

    :param node: The root node.
    :param pred: The predicate function which returns True if the node should be
                 pruned.
    :param kwargs: Additional keyword arguments to pass to `pred`.
    :return: The pruned tree.
    """
    return map(node=node,
               func=lambda n, **kwargs: None if pred(n, **kwargs) else n,
               order="pre",
               **kwargs)


def node_to_leaf_paths(node: Any) -> List:
    """
    List all node-to-leaf paths in a tree. Each path is a list of nodes from the
    current node `node` to a leaf node.

    Example: Suppose we have the following sub-tree structure for node `A`::

        A
        ├── B
        │   ├── D
        │   └── E
        └── C
            └── F
    
    Invoking `node_to_leaf_paths(A)` enumerates the following list of paths::

        [[A, B, D], [A, B, E], [A, C, F]]
    
    :param node: The current node.
    :return: List of paths in the tree under the current node.
    """

    paths = []
    def _find_paths(n, path):
        if is_leaf(n):
            paths.append(path + [n])
        else:
            for c in n.children:
                _find_paths(c, path + [n])

    _find_paths(node, [])
    return paths

def find_path(source: Any, dest: Any, bidirectional: bool = False) -> List:
    """
    Find the path from a source node to a destination node.

    :param source: The source node.
    :param dest: The destination node.
    :return: The path from the source node to the destination node.
    """
    if source is None or dest is None:
        raise ValueError("Source and destination nodes must not be None")

    def _find(n, p, dst):
        p.append(n)
        if n == dst:
            # return the reversed path
            return p[::-1]
        elif is_root(n):
            return None
        else:
            return _find(n.parent, p, dst)

    found_path = _find(dest, [], source)
    if found_path is None and bidirectional:
        found_path = _find(source, [], dest)
    return found_path
    

def ancestors(node) -> List:
    """
    Get the ancestors of a node.

    We could have used the `path` function, but we want to show potentially
    more efficient use of the `parent` property. As a tree, each node has at
    most one parent, so we can traverse the tree by following the parent
    relationship without having to search for the path from the root to the
    node. If parent pointers are not available but children pointers are, we
    can use the `path` function. In our implementations of trees, we implement
    both parent and children pointers.

    :param node: The root node.
    :return: List of ancestor nodes.
    """
    anc = []
    def _ancestors(n):
        nonlocal anc
        if not is_root(n):
            anc.append(n.parent)
            _ancestors(n.parent)

    _ancestors(node)
    return anc

def path(node: Any) -> List:
    """
    Get the path from the root node to the given node.

    :param node: The node.
    :return: The path from the root node to the given node.
    """
    anc = ancestors(node)
    return [node] + anc[::-1]

def size(node: Any) -> int:
    """
    Get the size of the subtree under the current node.

    :param node: The node.
    :return: The number of descendents of the node.
    """
    return len(descendants(node)) + 1

def lca(node1, node2, hash_fn=None) -> Any:
    """
    Find the lowest common ancestor of two nodes.

    :param node1: The first node.
    :param node2: The second node.
    :return: The lowest common ancestor of the two nodes.
    """

    if node1 is None or node2 is None:
        raise ValueError("Nodes must not be None")

    if hash_fn is None:
        hash_fn = hash

    ancestors = set()
    while node1 is not None:
        ancestors.add(hash_fn(node1))
        node1 = node1.parent
    
    while node2 is not None:
        if hash_fn(node2) in ancestors:
            return node2
        node2 = node2.parent
    
    return None

def distance(node1: Any, node2: Any) -> int:
    """
    Find the distance between two nodes.

    :param node1: The first node.
    :param node2: The second node.
    :return: The distance between the two nodes.
    """
    if node1 is None or node2 is None:
        raise ValueError("Nodes must not be None")
    
    lca_node = lca(node1, node2)
    if lca_node is None:
        raise ValueError("Nodes must be in the same tree")
    return depth(node1) + depth(node2) - 2 * depth(lca_node)

def subtree_rooted_at(node: Any, max_lvl: int) -> Any:
    """
    Get the subtree rooted at a node whose descendents are within a certain
    number of hops it. We return a subtree rooted the node itself, that contains
    all nodes within `max_hops` hops from the node.

    :param node: The node.
    :return: The subtree centered at the node.
    """
    
    within_hops = []
    def _helper(node, **kwargs):
        within_hops.append(node)
        return False
    breadth_first(node, _helper, max_lvl)

    def _build(n, par):
        #new_node = type(n)(name=n.name, payload=n.payload, parent=par)
        new_node = n.clone(par)
        for c in n.children:
            if c in within_hops:
                _build(c, new_node)
        return new_node
    
    return _build(node, None)


def subtree_centered_at(node: Any, max_hops: int) -> Any:
    """
    Get the subtree centered at a node within a certain number of hops
    from the node. We return a subtree rooted at some ancestor of the node,
    or the node itself, that contains all nodes within `max_hops` hops
    from the node.

    :param node: The node.
    :return: The subtree centered at the node.
    """
    
    within_hops = breadth_first_undirected(node, max_hops)
    root = node
    while root.parent is not None:
        if root.parent in within_hops:
            root = root.parent

    def _build(n, par):
        new_node = n.clone(par)
        #new_node = type(n)(name=n.name, payload=n.payload, parent=par)
        for c in n.children:
            if c in within_hops:
                _build(c, new_node)
        return new_node
    
    return _build(root, None)

def average_distance(node: Any) -> float:
    """
    Compute the average distance between all pairs of nodes in the subtree
    rooted at the current node.

    :param node: The node.
    :return: The average distance between all pairs of nodes.
    """
    from itertools import combinations
    from statistics import mean
    distances = []
    nodes = descendants(node) + [node]
    for n1, n2 in combinations(nodes, 2):
        distances.append(distance(n1, n2))
    return mean(distances)

def node_stats(node,
               node_name: Callable = lambda node: node.name,
               payload: Callable = lambda node: node.payload) -> dict:
    """
    Gather statistics about the current node and its subtree.

    :param node: The current node in the subtree.
    :param node_name: A function that returns the name of a node. Defaults to
                      returning the node's `name` property.
    :param payload: A function that returns the payload of a node. Defaults to
                    returning the node's `payload` property.
    :return: A dictionary containing the statistics.
    """

    from AlgoTree.treenode_api import TreeNodeApi
    if not TreeNodeApi.is_valid(node):
        raise ValueError("Node must be a valid TreeNode")

    return {
        "type": str(type(node)),
        "name": node_name(node),
        "payload": payload(node),
        "children": [node_name(n) for n in node.children],
        "parent": node_name(node.parent) if node.parent is not None else None,
        "depth": depth(node),
        "height": height(node),
        "is_root": is_root(node),
        "is_leaf": is_leaf(node),
        "is_internal": is_internal(node),
        "ancestors": [node_name(n) for n in ancestors(node)],
        "siblings": [node_name(n) for n in siblings(node)],
        "descendants": [node_name(n) for n in descendants(node)],
        "path": [node_name(n) for n in path(node)],
        "root_distance": distance(node.root, node),
        "leaves_under": [node_name(n) for n in leaves(node)],
        "subtree_size": size(node),
        "average_distance": average_distance(node)
    }


def paths_to_tree(paths: List,
                  type: Type,
                  max_tries: int = 1000) -> type:
    """
    Convert a list of paths to a tree structure. Each path is a list of nodes
    from the root to a leaf node. (A tree can be uniquely identified by
    this list of paths.)

    Example: Suppose we have the following list of paths::

        paths = [ ["A", "B", "D"], ["A", "B", "E"], ["A", "C", "F"] ]

    We can convert this list of paths to a tree structure using the following
    code::

        tree = paths_to_tree(paths, TreeNode)

    This will create the following tree structure::

        A
        ├── B
        │   ├── D
        │   └── E
        └── C
            └── F

    For some tree-like data structures, it may be the case that the names of
    nodes must be unique. We can use the `max_tries` parameter to try to create
    a node with a unique name like the one provided by suffixing the name with
    an integer.

    :param paths: The list of paths.
    :param type: The type of the tree node.
    :param max_tries: The maximum number of tries to create a node with a
                      unique name.
    """
    nodes = { }
    for p in paths:
        parent = None
        path = []
        for n in p:
            path.append(n)
            path_tuple = tuple(path)
            name = n
            if path_tuple not in nodes:
                for tries in range(max_tries):
                    try:
                        new_node = type(name=name, parent=parent)
                        break
                    except KeyError as e:
                        pass
                    name = f"{n}_{tries}"

                if tries == max_tries:
                    raise ValueError(f"Failed to create node with prefix {n}.")
                nodes[path_tuple] = new_node
            parent = nodes[path_tuple]
    return parent.root

def is_isomorphic(node1, node2):
    """
    Check if two (sub)trees are isomorphic. To check if two trees are isomorphic,
    just pass in the root nodes of the trees.

    This is another kind of equivalence: two nodes are equivalent if they have
    the same substructure (extensic relations), but the names and payloads of
    the nodes (intrinsic relations) can be different.
    
    We ignore the parents of the nodes in this comparison. If we also included
    the parents, this would be the  same as calling `is_isomorphic` on the
    root nodes of the trees.

    :param node1: The root node of the first tree.
    :param node2: The root node of the second tree.
    :return: True if the trees are isomorphic, False otherwise.
    """

    if not hasattr(node1, "children") or not hasattr(node2, "children"):
        raise ValueError("Nodes must have 'children' property")

    if len(node1.children) != len(node2.children):
        return False
    for child1 in node1.children:
        if not any(is_isomorphic(child1, child2) for child2 in node2.children):
            return False
    return True
```

#### Source File: `test/__init__.py`

```python

```

#### Source File: `test/test_algos.py`

```python
import unittest
from AlgoTree.utils import node_to_leaf_paths, prune
from AlgoTree.treenode import TreeNode
from AlgoTree.flat_forest_node import FlatForestNode

class TestUtils(unittest.TestCase):

    def setUp(self):
        """
        Create a sample tree for testing
        
        Here is what the tree looks like:
        
            A
            ├── B
            │   ├── E
            │   └── F
            |       └── H
            ├── C
            │   └── G
            └── D            
        """

        # Create a sample tree for testing
        self.node_a = FlatForestNode(name="A")
        self.node_b = FlatForestNode(name="B", parent=self.node_a)
        self.node_c = FlatForestNode(name="C", parent=self.node_a)
        self.node_d = FlatForestNode(name="D", parent=self.node_a)
        self.node_e = FlatForestNode(name="E", parent=self.node_b)
        self.node_f = FlatForestNode(name="F", parent=self.node_b)
        self.node_g = FlatForestNode(name="G", parent=self.node_c)
        self.node_h = FlatForestNode(name="H", parent=self.node_f)

    def test_node_to_leaf_paths(self):
        """
        Test the root_to_leaf_paths function

        See the setUp method for the tree structure.

        Expected paths:
        [
            [A, B, E],
            [A, B, F, H]
            [A, C, G],
            [A, D]
        ]
        """
        expected_paths = [
            [self.node_a, self.node_b, self.node_e],
            [self.node_a, self.node_b, self.node_f, self.node_h],
            [self.node_a, self.node_c, self.node_g],
            [self.node_a, self.node_d]
        ]
        result = node_to_leaf_paths(self.node_a)
        self.assertEqual(result, expected_paths)

    def test_prune(self):
        def pred(node):
            # let's just prune sub-trees rooted at B and D
            return node.name in ["B", "D"]

        pruned_tree = prune(self.node_a, pred)
        self.assertEqual(pruned_tree.name, "A")
        self.assertEqual(len(pruned_tree.children), 1)
        self.assertEqual(pruned_tree.children[0].name, "C")
        self.assertEqual(len(pruned_tree.children[0].children), 1)
        self.assertEqual(pruned_tree.children[0].children[0].name, "G")


if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_algos_treenode.py`

```python
import unittest
from AlgoTree.utils import node_to_leaf_paths, prune
from AlgoTree.treenode import TreeNode
from AlgoTree.flat_forest_node import FlatForestNode

class TestUtils(unittest.TestCase):

    def setUp(self):
        """
        Create a sample tree for testing
        
        Here is what the tree looks like:
        
            A
            ├── B
            │   ├── E
            │   └── F
            |       └── H
            ├── C
            │   └── G
            └── D            
        """

        # Create a sample tree for testing
        self.node_a = TreeNode(name="A")
        self.node_b = TreeNode(name="B", parent=self.node_a)
        self.node_c = TreeNode(name="C", parent=self.node_a)
        self.node_d = TreeNode(name="D", parent=self.node_a)
        self.node_e = TreeNode(name="E", parent=self.node_b)
        self.node_f = TreeNode(name="F", parent=self.node_b)
        self.node_g = TreeNode(name="G", parent=self.node_c)
        self.node_h = TreeNode(name="H", parent=self.node_f)

    def test_node_to_leaf_paths(self):
        """
        Test the root_to_leaf_paths function

        See the setUp method for the tree structure.

        Expected paths:
        [
            [A, B, E],
            [A, B, F, H]
            [A, C, G],
            [A, D]
        ]
        """
        expected_paths = [
            [self.node_a, self.node_b, self.node_e],
            [self.node_a, self.node_b, self.node_f, self.node_h],
            [self.node_a, self.node_c, self.node_g],
            [self.node_a, self.node_d]
        ]
        result = node_to_leaf_paths(self.node_a)
        self.assertEqual(result, expected_paths)


    def test_prune(self):
        def pred(node):
            # let's just prune sub-trees rooted at B and D
            return node.name in ["B", "D"]

        pruned_tree = prune(self.node_a, pred)
        self.assertEqual(pruned_tree.name, "A")
        self.assertEqual(len(pruned_tree.children), 1)
        self.assertEqual(pruned_tree.children[0].name, "C")
        self.assertEqual(len(pruned_tree.children[0].children), 1)
        self.assertEqual(pruned_tree.children[0].children[0].name, "G")

if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_flat_forest.py`

```python
import unittest

from AlgoTree.flat_forest import FlatForest

class TestFlatTree(unittest.TestCase):
    def setUp(self):
        self.tree_data = {
            "a": {"parent": None},
            "b": {"parent": "a"},
            "c": {"parent": "a"},
            "d": {"parent": "b"},
            "e": {"parent": "b"},
            "f": {"parent": "c"},
        }
        self.flat_tree = FlatForest(self.tree_data)

    def test_initialization(self):
        self.assertEqual(self.flat_tree["a"]["parent"], None)
        self.assertEqual(self.flat_tree["b"]["parent"], "a")
        self.assertEqual(self.flat_tree["c"]["parent"], "a")

    def test_node_names(self):
        keys = self.flat_tree.node_names()
        expected_keys = [
            "__DETACHED__",
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
        ]
        self.assertCountEqual(keys, expected_keys)

    def test_child_names(self):
        self.assertEqual(self.flat_tree.child_names("a"), ["b", "c"])
        self.assertEqual(self.flat_tree.child_names("b"), ["d", "e"])
        self.assertEqual(self.flat_tree.child_names("c"), ["f"])

    def test_detach(self):
        detached_node = self.flat_tree.detach("b")
        self.assertEqual(self.flat_tree["b"]["parent"], FlatForest.DETACHED_KEY)
        self.assertEqual(detached_node._key, "b")

    def test_purge(self):
        self.flat_tree.detach("b")
        self.flat_tree.purge()
        # order doesn't matter, so use this instead:
        self.assertNotIn("b", self.flat_tree)
        self.assertNotIn("d", self.flat_tree)
        self.assertNotIn("e", self.flat_tree)

    def test_check_valid(self):
        # Valid tree
        FlatForest.check_valid(self.flat_tree)

        # Invalid tree (cycle)
        self.flat_tree["a"]["parent"] = "f"
        with self.assertRaises(ValueError):
            FlatForest.check_valid(self.flat_tree)

        # Invalid tree (non-dict node value)
        self.flat_tree["a"] = "invalid"
        with self.assertRaises(ValueError):
            FlatForest.check_valid(self.flat_tree)

        # Invalid tree (non-existing parent)
        self.flat_tree["a"] = {"parent": "non_existing"}
        with self.assertRaises(KeyError):
            FlatForest.check_valid(self.flat_tree)

    def test_node(self):
        node_b = self.flat_tree.node("b")
        self.assertEqual(node_b._key, "b")

        with self.assertRaises(KeyError):
            self.flat_tree.node("non_existing")

    def test_root(self):
        root_node = self.flat_tree.root
        self.assertEqual(root_node._key, "a")

    def test_detached(self):
        detached_node = self.flat_tree.detached
        self.assertEqual(detached_node._key, FlatForest.DETACHED_KEY)


if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_flat_forest_additional.py`

```python
import json
import unittest
import uuid

from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode


class TestFlatTreeNodeAdditional(unittest.TestCase):
    def setUp(self):
        self.root = FlatForestNode(name="root", data=0)
        self.tree = self.root.forest

    def test_node_creation_with_uuid(self):
        # Create node without specifying a name
        unnamed_node = FlatForestNode(parent=self.root, data="data without name")
        # Verify that a UUID is assigned
        self.assertTrue(uuid.UUID(unnamed_node.name))

    def test_cycle_detection(self):
        node1 = self.root.add_child(name="node1", data=1)
        node2 = self.root.add_child(name="node2", data=2)
        node3 = node1.add_child(name="node3", data=3)

        # Attempt to create a cycle: making node1 a child of node3
        with self.assertRaises(ValueError):
            node1.parent = node3
            FlatForest.check_valid(node1.tree)

    def test_serialization_and_deserialization(self):
        node1 = self.root.add_child(name="node1", data="data1")
        self.root.add_child(name="node2", data="data2")
        node1.add_child(name="node3", data="data3")

        # Serialize to JSON
        tree_json = json.dumps(self.tree, indent=2)
        # Deserialize back to FlatTree
        deserialized_tree_data = json.loads(tree_json)
        deserialized_tree = FlatForest(deserialized_tree_data)

        # Verify structure is the same
        self.assertEqual(self.tree, deserialized_tree)

    def test_handling_non_serializable_data(self):
        # Create a tree with non-serializable data (function)
        non_serializable_data = {"node1": {"data": lambda x: x}}
        non_serializable_tree = FlatForest(non_serializable_data)

        # Verify serialization fails
        with self.assertRaises(TypeError):
            json.dumps(non_serializable_tree)

    def test_tree_visualization(self):
        node1 = self.root.add_child(name="node1", data=1)
        node2 = self.root.add_child(name="node2", data=2)
        node3 = node1.add_child(name="node3", data=3)

        def pretty_print(node, depth=0):
            result = ""
            if depth != 0:
                result += "    " * depth + "|\n"
                result += "    " * depth + "+ " + "-" * depth + " "
            result += node.name + "\n"
            for child in node.children:
                result += pretty_print(child, depth + 1)
            return result

        expected_output = """root
    |
    + - node1
        |
        + -- node3
    |
    + - node2
"""
        actual_output = pretty_print(self.root)
        self.assertEqual(expected_output, actual_output)


if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_flat_forest_nb.py`

```python
import unittest

from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode


class TestFlatTree(unittest.TestCase):
    def setUp(self):
        """
        Create a sample tree for testing

        Here is what the tree looks like::

          node1
          └── node3
          |   ├── node4
          |   └── node5
          └── node2

        """
        self.tree_data = {
            "node1": {
                "data": "Some data for node1",
                "more": "Some more data for node1",
            },
            "node2": {"data": "Some data for node2", "parent": "node1"},
            "node3": {
                "parent": "node1",
                "data": "Some data for node3",
                "test": "Some test data for node3",
            },
            "node4": {"parent": "node3", "data": "Some data for node4"},
            "node5": {"parent": "node3", "data": "Some data for node5"},
        }
        self.flat_tree = FlatForest(self.tree_data)

    def test_parent(self):
        #self.assertEqual(self.flat_tree.root.parent, None)
        self.assertEqual(
            self.flat_tree.node("node3").parent,
            self.flat_tree.node("node1"),
        )
        #self.assertEqual(self.flat_tree.subtree("node3").parent, None)

    def test_initialization(self):
        self.assertEqual(
            self.flat_tree["node1"]["data"], "Some data for node1"
        )
        self.assertEqual(
            self.flat_tree["node2"]["data"], "Some data for node2"
        )
        self.assertEqual(self.flat_tree["node3"]["parent"], "node1")

    def test_node_names(self):
        unique_keys = self.flat_tree.node_names()
        expected_keys = [
            "__DETACHED__",
            "node1",
            "node2",
            "node3",
            "node4",
            "node5",
        ]
        self.assertCountEqual(unique_keys, expected_keys)

    def test_child_names(self):
        self.assertCountEqual(self.flat_tree.child_names("node1"), ["node2","node3"])
        self.assertEqual(
            self.flat_tree.child_names("node3"), ["node4", "node5"]
        )
        self.assertEqual(self.flat_tree.child_names("node2"), [])

    def test_detach(self):
        detached_node = self.flat_tree.detach("node3")
        self.assertEqual(
            self.flat_tree["node3"]["parent"], FlatForest.DETACHED_KEY
        )
        self.assertEqual(detached_node._key, "node3")

    def test_purge(self):
        self.flat_tree.detach("node3")
        self.flat_tree.purge()
        self.assertNotIn("node3", self.flat_tree)
        self.assertNotIn("node4", self.flat_tree)
        self.assertNotIn("node5", self.flat_tree)

    def test_check_valid(self):
        FlatForest.check_valid(self.flat_tree)
        self.flat_tree["node1"]["parent"] = "node5"
        with self.assertRaises(ValueError):
            FlatForest.check_valid(self.flat_tree)

    def test_node(self):
        node3 = self.flat_tree.node("node3")
        self.assertEqual(node3._key, "node3")

        with self.assertRaises(KeyError):
            self.flat_tree.node("non_existing")

    def test_root(self):
        root_node = self.flat_tree.root
        self.assertEqual(root_node._key, "node1")

    def test_detached(self):
        detached_node = self.flat_tree.detached
        self.assertEqual(detached_node._key, FlatForest.DETACHED_KEY)


class TestFlatTreeNode(unittest.TestCase):
    def setUp(self):
        """
        Create a sample tree for testing

        Here is what the tree looks like::

          node1
          ├── node3
          │   ├── node4
          │   └── node5
          └── node2

        """
        self.tree_data = {
            "node1": {
                "data": "Some data for node1",
                "more": "Some more data for node1",
            },
            "node2": {"data": "Some data for node2", "parent": "node1"},
            "node3": {
                "parent": "node1",
                "data": "Some data for node3",
                "test": "Some test data for node3",
            },
            "node4": {"parent": "node3", "data": "Some data for node4"},
            "node5": {"parent": "node3", "data": "Some data for node5"},
        }
        self.flat_tree = FlatForest(self.tree_data)
        self.node1 = FlatForestNode.proxy(self.flat_tree, "node1")
        self.node3 = FlatForestNode.proxy(self.flat_tree, "node3")

    def test_initialization(self):
        self.assertEqual(self.node1.name, "node1")
        self.assertEqual(self.node3.name, "node3")

    def test_children(self):
        children_node1 = [child.name for child in self.node1.children]
        self.assertCountEqual(children_node1, ["node2", "node3"])

        children_node3 = [child.name for child in self.node3.children]
        self.assertCountEqual(children_node3, ["node4", "node5"])

    def test_add_child(self):
        new_node = self.node1.add_child(name="node6", data="data for node6")
        self.assertIn("node6", self.flat_tree)
        self.assertEqual(self.flat_tree["node6"]["parent"], "node1")
        self.assertEqual(new_node.parent.name, "node1")

    def test_detach(self):
        detached_node = self.node3.detach()
        self.assertEqual(detached_node._key, "node3")
        self.assertEqual(
            self.flat_tree["node3"]["parent"], FlatForest.DETACHED_KEY
        )

    def test_getitem_setitem_delitem(self):
        self.node1["key1"] = "value1"
        self.assertEqual(self.node1["key1"], "value1")
        del self.node1["key1"]
        with self.assertRaises(KeyError):
            _ = self.node1["key1"]

    def test_clear(self):
        self.node1.payload = {"key1": "value1", "key2": "value2"}
        self.node1.clear()
        self.assertEqual(len(self.node1), 0)
        self.assertEqual(self.node1.payload, {})

    def test_child_operations(self):
        self.node1.add_child(name="child1", data="child1 data")
        child1 = self.node1.node("child1")
        self.assertEqual(child1.parent.name, "node1")
        self.assertEqual(child1.payload["data"], "child1 data")

    def test_create_cycle(self):
        self.node3.add_child(name="node6", data="node6 data")
        node6 = self.flat_tree.node("node6")
        with self.assertRaises(ValueError):
            self.node3.parent = node6
            FlatForest.check_valid(self.flat_tree)

if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_flat_forest_node.py`

```python
import unittest

from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode


class TestFlatTreeNode(unittest.TestCase):
    def setUp(self):
        self.tree_data = {
            "a": {"parent": None},
            "b": {"parent": "a"},
            "c": {"parent": "a"},
            "d": {"parent": "b"},
            "e": {"parent": "b"},
            "f": {"parent": "c"},
        }
        self.flat_tree = FlatForest(self.tree_data)
        self.node_a = FlatForestNode.proxy(self.flat_tree, "a")
        self.node_b = FlatForestNode.proxy(self.flat_tree, "b")
        self.node_c = FlatForestNode.proxy(self.flat_tree, "c")
        self.root = FlatForestNode.proxy(self.flat_tree, "a")

    def test_initialization(self):
        self.assertEqual(self.node_a.name, "a")
        self.assertEqual(self.node_b.name, "b")

    def test_parent(self):
        children = self.node_a.children
        for child in children:
            self.assertEqual(child.parent, self.node_a)

    def test_children(self):
        children_a = [child.name for child in self.node_a.children]
        self.assertCountEqual(children_a, ["b", "c"])

        children_b = [child.name for child in self.node_b.children]
        self.assertCountEqual(children_b, ["d", "e"])

    def test_payload(self):
        self.assertEqual(self.node_a.payload, {})
        self.node_a.payload = {"key1": "value1"}
        self.assertEqual(self.node_a.payload, {"key1": "value1"})

    def test_add_child(self):
        new_node = self.node_a.add_child(name="g")
        self.assertIn("g", self.flat_tree)
        self.assertEqual(self.flat_tree["g"]["parent"], "a")
        self.assertEqual(new_node.parent.name, "a")

    def test_detach(self):
        detached_node = self.node_b.detach()
        self.assertEqual(detached_node._key, "b")
        self.assertEqual(self.flat_tree["b"]["parent"], FlatForest.DETACHED_KEY)

    def test_set_parent(self):
        self.flat_tree.node("b").parent = self.node_c
        self.assertEqual(self.flat_tree["b"]["parent"], "c")

    def test_len_and_iter(self):
        self.assertEqual(len(self.node_a), 0)
        self.node_a.payload = {"data": "value"}
        self.assertEqual(self.node_a.payload, {"data": "value"})

    def test_getitem_setitem_delitem(self):
        self.node_a["key1"] = "value1"
        self.assertEqual(self.node_a["key1"], "value1")
        del self.node_a["key1"]
        with self.assertRaises(KeyError):
            _ = self.node_a["key1"]


if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_flat_forest_node_api.py`

```python
import unittest

from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode


class TestFlatTreeNodeAPI(unittest.TestCase):
    def setUp(self):
        self.root = FlatForestNode(name="root", data=0)
        self.tree = self.root.forest

    def test_create_and_add_nodes(self):
        # Create nodes
        node1 = FlatForestNode(name="node1", parent=self.root, data=1)
        node2 = FlatForestNode(name="node2", parent=self.root, data=2)
        node3 = self.root.add_child(name="node3", data=3)

        # Verify creation
        self.assertIn("node1", self.tree)
        self.assertIn("node2", self.tree)
        self.assertIn("node3", self.tree)
        self.assertEqual(self.tree["node1"]["data"], 1)
        self.assertEqual(self.tree["node2"]["data"], 2)
        self.assertEqual(self.tree["node3"]["data"], 3)
        self.assertEqual(self.tree["node3"]["parent"], "root")

    def test_retrieve_and_manipulate_children(self):
        # Create nodes
        node1 = self.root.add_child(name="node1", data=1)
        node3 = self.root.add_child(name="node3", data=3)
        node4 = node3.add_child(name="node4", data=4)
        node5 = node3.add_child(name="node5", data=5)
        node6 = node3.add_child(name="node6", data=6)

        # Retrieve node3 and verify children
        retrieved_node3 = self.tree.node("node3")
        children_names = [child.name for child in retrieved_node3.children]
        self.assertCountEqual(children_names, ["node4", "node5", "node6"])

        # Update children
        node7 = FlatForestNode(name="node7", data=7, parent=node3)
        node3.children = [node4, node5, node7]
        updated_children_names = [child.name for child in node3.children]
        self.assertCountEqual(
            updated_children_names, ["node4", "node5", "node7"]
        )

    def test_detach_and_purge(self):
        # Create nodes
        node1 = self.root.add_child(name="node1", data=1)
        node3 = self.root.add_child(name="node3", data=3)
        node4 = node3.add_child(name="node4", data=4)
        node5 = node3.add_child(name="node5", data=5)

        # Detach node3
        detached_node3 = node3.detach()
        self.assertEqual(self.tree["node3"]["parent"], FlatForest.DETACHED_KEY)
        detached_children_names = [
            child.name for child in detached_node3.children
        ]
        self.assertCountEqual(detached_children_names, ["node4", "node5"])

        # Prune detached node3
        self.tree.purge()
        self.assertNotIn("node3", self.tree)
        self.assertNotIn("node4", self.tree)
        self.assertNotIn("node5", self.tree)

    def test_payload_manipulation(self):
        # Create node
        node1 = self.root.add_child(name="node1", data=1)

        # Manipulate payload
        node1.payload = {"new_key": "new_value"}
        self.assertEqual(node1.payload, {"new_key": "new_value"})

        node1["another_key"] = "another_value"
        self.assertEqual(node1["another_key"], "another_value")

        del node1["new_key"]
        self.assertNotIn("new_key", node1.payload)

    def test_clear_children(self):
        # Create nodes
        node3 = self.root.add_child(name="node3", data=3)
        node4 = node3.add_child(name="node4", data=4)
        node5 = node3.add_child(name="node5", data=5)

        # Clear children of node3
        node3.children = []
        self.assertEqual(node3.children, [])


if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_flat_forest_node_eq.py`

```python
import unittest
from AlgoTree.pretty_tree import PrettyTree, pretty_tree
from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode

class TestFlatTreeNodeEq(unittest.TestCase):
    
    def setUp(self):
        """
        Create a sample tree for testing, denoted by `t`.

        Here is what the tree `t` looks like:

            a (root)
            ├── b
            │   ├── d
            │   |   ├── i
            │   |   └── j
            │   └── e
            ├── c
            |   └── f
            └── g
                └── h

        When we get a node in `t` like `t.node("d")`, it looks like:

            a (root)
            ├── b
            │   ├── d (current node)
            │   |   ├── i
            │   |   └── j
            │   └── e
            ├── c
            |   └── f
            └── g
                └── h

        So we just repositioned the current node in the tree `t`.

        When we get a subtree `t.subtree("b")`, it looks like:

            b (root, current node)
            ├── d
            │   ├── i
            │   └── j
            └── e


        When we get a node in the subtree `t.subtree("b").node("d")`, it looks like:

            b (root)
            ├── d (current node)
            │   ├── i
            │   └── j
            └── e

        So we just repositioned the current node in the subtree `t.subtree("b")`.

        When we test for equality of a node, there are many ways to define it.
        By default, we define it by path equality, i.e., the path from the root
        to the current node.
        """
        self.tree_data = {
            "a": {"parent": None},
            "b": {"parent": "a"},
            "c": {"parent": "a"},
            "d": {"parent": "b"},
            "e": {"parent": "b"},
            "f": {"parent": "c"},
            "g": {"parent": "a"},
            "h": {"parent": "g"},
            "i": {"parent": "d"},
            "j": {"parent": "d"},
        }
        self.flat_tree = FlatForest(self.tree_data)
        self.root_b_node_d = self.flat_tree.subtree("b").node("d")


    def test_eq(self):
        root_logical_node_d = self.flat_tree.node("d")
        self.assertNotEqual(root_logical_node_d, self.root_b_node_d)
        self.assertNotEqual(self.flat_tree.node("b"), self.root_b_node_d)
        self.assertNotEqual(self.flat_tree.node("e"), self.root_b_node_d)
        self.assertNotEqual(self.flat_tree.node("b"), self.flat_tree.node("d"))
        self.assertNotEqual(self.flat_tree.node("b"), self.flat_tree.node("e"))
        self.assertNotEqual(self.flat_tree.node("d"), self.flat_tree.node("e"))
        self.assertEqual(self.flat_tree.subtree("b").node("d"), self.root_b_node_d)
        self.assertEqual(self.flat_tree.subtree("b").node("i"), self.flat_tree.subtree("b").node("i"))

```

#### Source File: `test/test_flat_forest_node_hash.py`

```python
import unittest
from AlgoTree.treenode import TreeNode
from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode
from AlgoTree.node_hasher import NodeHasher

class TestFlatNodeHash(unittest.TestCase):
    def setUp(self):
        self.node_a = FlatForestNode(name="a", data1=1, data2=2)
        self.node_b = FlatForestNode(name="b", parent=self.node_a, data="test")
        self.node_c = FlatForestNode(name="c", parent=self.node_a, different_data="test2")

    def test_name_hash(self):
        # Test that the name hash of two nodes with different names is not the same
        self.assertNotEqual(NodeHasher.name(self.node_a), NodeHasher.name(self.node_b))

        # Test that the name hash of two nodes with the same name is the same
        root = FlatForestNode(name="root")
        another_a = FlatForestNode(name="a", parent=root)
        self.assertEqual(NodeHasher.name(self.node_a), NodeHasher.name(another_a))

        # Test that the name hash of two nodes with different names is not the same
        self.assertNotEqual(NodeHasher.name(self.node_a), NodeHasher.name(self.node_b))

        # Test that the name hash of two nodes with the same name is the same
        root = FlatForestNode(name="root")
        another_a = FlatForestNode(name="a", parent=root)
        self.assertEqual(NodeHasher.name(self.node_a), NodeHasher.name(another_a))

        # try different tree types with same name
        self.assertEqual(NodeHasher.name(self.node_a), NodeHasher.name(self.node_a))

        self.assertEqual(NodeHasher.name(self.node_a), NodeHasher.name(FlatForestNode(name="a")))
        self.assertNotEqual(NodeHasher.name(self.node_a), NodeHasher.name(FlatForestNode(name="b", data1=1, data2=2)))

    def test_payload_hash(self):
        # Test that the payload hash of two nodes with different payloads is not the same
        self.assertNotEqual(NodeHasher.payload(self.node_a), NodeHasher.payload(self.node_b))

        # Test that the payload hash of two nodes with the same payload is the same
        self.assertNotEqual(NodeHasher.payload(self.node_a), NodeHasher.payload(TreeNode(name="a")))

        self.assertEqual(NodeHasher.payload(self.node_a), NodeHasher.payload(TreeNode(name="a", data1=1, data2=2)))
        self.assertNotEqual(NodeHasher.payload(self.node_a), NodeHasher.payload(TreeNode(name="a", data1=1, data2=2, more=None)))
        
        # try different tree types with same payloads
        self.assertEqual(NodeHasher.payload(self.node_a), NodeHasher.payload(self.node_a))

    def test_node_hash(self):
        # Test that the node hash of two nodes with different payloads is not the same
        self.assertNotEqual(NodeHasher.node(self.node_a), NodeHasher.node(self.node_b))

        # Test that the node hash of two nodes with the same payload and same names are the same
        self.assertEqual(NodeHasher.node(self.node_a), NodeHasher.node(FlatForestNode(name="a", data1=1, data2=2)))

        self.assertEqual(NodeHasher.node(self.node_a), NodeHasher.node(self.node_a))

        self.assertNotEqual(NodeHasher.node(self.node_a), NodeHasher.node(FlatForestNode(name="a", data1=1, data2=2, more=None)))

    def test_path_hash(self):
        # Test that the path hash of two nodes with different paths is not the same
        self.assertNotEqual(NodeHasher.path(self.node_a), NodeHasher.path(self.node_b))

        # Test that the path hash of two nodes with the same path is the same
        #self.assertEqual(NodeHash.path_hash(self.node_b), NodeHash.path_hash(FlatTreeNode(name="b", parent=FlatTreeNode(name="a",data=0), data1=10, data2=2)))

        #self.assertEqual(NodeHash.path_hash(self.node_a), NodeHash.path_hash(self.node_a))

if __name__ == "__main__":
    unittest.main()
```

#### Source File: `test/test_flat_forest_node_utils.py`

```python
import unittest

from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode
from AlgoTree.utils import (
    ancestors,
    breadth_first,
    depth,
    descendants,
    find_node,
    find_nodes,
    height,
    is_internal,
    is_leaf,
    is_root,
    leaves,
    map,
    siblings,
    visit,
    size
)


class TestTreeUtils(unittest.TestCase):
    def setUp(self):
        self.node0 = FlatForestNode(name="node0", data=0)
        self.node1 = FlatForestNode(name="node1", parent=self.node0, data=1)
        self.node2 = FlatForestNode(name="node2", parent=self.node0, data=2)
        self.node3 = FlatForestNode(name="node3", parent=self.node0, data=3)
        self.node4 = FlatForestNode(name="node4", parent=self.node3, data=4)
        self.node5 = FlatForestNode(name="node5", parent=self.node3, data=5)
        self.node6 = FlatForestNode(name="node6", parent=self.node3, data=6)
        self.node7 = FlatForestNode(name="node7", parent=self.node3, data=7)
        self.node8 = FlatForestNode(name="node8", parent=self.node3, data=8)
        self.node9 = FlatForestNode(name="node9", parent=self.node6, data=9)
        self.nodes = [
            self.node0, self.node1, self.node2, self.node3, self.node4,
            self.node5, self.node6, self.node7, self.node8, self.node9
        ]
        self.tree = self.node0.forest
        """
        Create a sample tree for testing

        Here is what the tree looks like::

            node0
            ├── node1
            ├── node2
            └── node3
                ├── node4
                ├── node5
                ├── node6
                │   └── node9
                ├── node7
                └── node8
        """

    def test_visit_pre_order(self):
        result = []
        visit(self.node0, lambda n: result.append(n.name) or False, order="pre")
        self.assertEqual(
            result,
            [
                "node0",
                "node1",
                "node2",
                "node3",
                "node4",
                "node5",
                "node6",
                "node9",
                "node7",
                "node8",
            ],
        )

    def test_visit_level_order(self):
        result = []
        visit(
            self.node0,
            lambda n, **kwargs: result.append((n.name, kwargs["level"]))
            or False,
            order="level",
        )
        self.assertEqual(
            result,
            [
                ("node0", 0),
                ("node1", 1),
                ("node2", 1),
                ("node3", 1),
                ("node4", 2),
                ("node5", 2),
                ("node6", 2),
                ("node7", 2),
                ("node8", 2),
                ("node9", 3),
            ],
        )

    def test_visit_stop_on_match(self):
        result = []
        visit(
            self.node0,
            lambda n: result.append(n.name) or n.name == "node6",
            order="pre",
        )
        self.assertEqual(
            result,
            ["node0", "node1", "node2", "node3", "node4", "node5", "node6"],
        )

    def test_map(self):
        def increment_data(node):
            node["data"] += 1
            return node

        map(self.node0, increment_data)
        self.assertEqual(self.node0["data"], 1)
        self.assertEqual(self.node1["data"], 2)
        self.assertEqual(self.node9["data"], 10)

    def test_descendants_node0(self):
        self.assertCountEqual(
            descendants(self.node0),
            [self.node1, self.node2, self.node3, self.node4, self.node5, self.node6, self.node7, self.node8, self.node9]
        )

    def test_descendants_root(self):
        true_descendants = [self.tree.node(n.name) for n in self.nodes[1:]]
        self.assertCountEqual(descendants(self.tree.root), true_descendants)

    def test_descendants_node3(self):
        self.assertCountEqual(
            descendants(self.node3),
            [self.node4, self.node5, self.node6, self.node9, self.node7, self.node8]
        )

    def test_ancestors(self):
        node9 = self.tree.node("node9")
        from AlgoTree.pretty_tree import pretty_tree
        print(pretty_tree(node9.parent))
        anc = [n.name for n in ancestors(node9)]
        self.assertCountEqual(anc, ["node6", "node3", "node0"])

    def test_subtree(self):
        subtree = self.tree.subtree("node3")
        self.assertEqual(subtree.name, "node3")
        self.assertEqual(subtree.root.name, "node3")
        self.assertEqual(subtree.parent, None)
        true_childs = [self.tree.subtree("node3").node("node4"),
                       self.tree.subtree("node3").node("node5"),
                       self.tree.subtree("node3").node("node6"),
                       self.tree.subtree("node3").node("node7"),
                       self.tree.subtree("node3").node("node8")]
        for n in true_childs:
            print(n)
        self.assertCountEqual(subtree.children, true_childs)

    def test_siblings(self):
        self.assertEqual(siblings(self.node6), [self.node4, self.node5, self.node7, self.node8])

    def test_leaves(self):
        self.assertEqual(
            leaves(self.node0),
            [self.node1, self.node2, self.node4, self.node5, self.node9, self.node7, self.node8]
        )

    def test_height(self):
        self.assertEqual(height(self.node0), 3)
        self.assertEqual(height(self.node3), 2)
        self.assertEqual(height(self.node9), 0)
        
    def test_height_subtree(self):
        self.assertEqual(height(self.node9.subtree()), 0)
        self.assertEqual(height(self.node9.subtree().node("node9")), 0)
        self.assertEqual(height(self.node3.subtree()), 2)
        self.assertEqual(height(self.node3.subtree().subtree("node3")), 2)
        self.assertEqual(height(self.node3.subtree().subtree().node("node3")), 2)
        self.assertEqual(height(self.node3.subtree().subtree().node("node9")), 0)
        self.assertEqual(height(self.node0.subtree()), 3)
        self.assertEqual(height(self.node0.subtree().node("node0")), 3)
        self.assertEqual(height(self.node0.subtree().node("node3")), 2)
        self.assertEqual(height(self.node0.subtree().subtree("node3").node("node9")), 0)

    def test_depth(self):
        self.assertEqual(depth(self.node0), 0)
        self.assertEqual(depth(self.node3), 1)
        self.assertEqual(depth(self.node9), 3)

    def test_is_root(self):
        self.assertTrue(is_root(self.node0))
        self.assertFalse(is_root(self.node1))

    def test_is_leaf(self):
        self.assertTrue(is_leaf(self.node9))
        self.assertFalse(is_leaf(self.node3))

    def test_is_internal(self):
        self.assertTrue(is_internal(self.node3))
        self.assertFalse(is_internal(self.node1))

    def test_breadth_first(self):
        result = []
        breadth_first(
            self.node0,
            lambda n, **kwargs: result.append((n.name, kwargs["level"]))
            or False,
        )
        self.assertCountEqual(
            result,
            [
                ("node0", 0),
                ("node1", 1),
                ("node2", 1),
                ("node3", 1),
                ("node4", 2),
                ("node5", 2),
                ("node6", 2),
                ("node7", 2),
                ("node8", 2),
                ("node9", 3),
            ],
        )

    def test_find_nodes(self):
        nodes = find_nodes(self.node0, lambda n: n["data"] > 3)
        self.assertCountEqual(
            nodes, [self.node4, self.node5, self.node6, self.node7, self.node8, self.node9]
        )


    def test_size(self):
        self.assertEqual(size(self.node0), 10)
        self.assertEqual(size(self.tree.node("node0")), 10)
        self.assertEqual(size(self.tree.node("node0")), 10)
        self.assertEqual(size(self.node3), 7)
        self.assertEqual(size(self.node9.root), 10)
        self.assertEqual(size(self.node9), 1)
        self.assertEqual(size(self.node9.subtree().root), 1)
        self.assertEqual(size(self.node9.subtree()), 1)
        self.assertEqual(size(self.node9.forest.root), len(self.nodes))

    def test_find_node(self):
        node = find_node(self.node0, lambda n, **_: n["data"] == 7)
        self.assertEqual(node.name, "node7")


if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_misc.py`

```python
import logging
import time
import unittest

from AlgoTree.treenode import TreeNode
from AlgoTree.utils import visit

logging.basicConfig(level=logging.DEBUG)


class TestTreeNodeAdvanced(unittest.TestCase):
    def setUp(self):
        """
        Create a tree with the following structure:

        root
        ├── child1
        │   └── child1_1
        └── child2
            └── child2_1
        """
        self.root = TreeNode(name="root", value="root_value")
        self.child1 = TreeNode(
            name="child1", parent=self.root, value="child1_value"
        )
        self.child2 = TreeNode(
            name="child2", parent=self.root, value="child2_value"
        )
        self.child1_1 = TreeNode(
            name="child1_1", parent=self.child1, value="child1_1_value"
        )
        self.child2_1 = TreeNode(
            name="child2_1", parent=self.child2, value="child2_1_value"
        )

    def test_move_subtree(self):
        new_parent = self.child2
        subtree_root = self.child1
        subtree_root.parent = new_parent
        # Verify new structure
        self.assertEqual(subtree_root.parent, new_parent)
        self.assertIn(subtree_root, self.child2.children)

    def test_large_tree_performance(self):
        # Create a large tree
        large_root = TreeNode(name="large_root")
        current_level = [large_root]
        for _ in range(5):  # Adjust depth as needed
            next_level = []
            for node in current_level:
                for i in range(10):  # Adjust branching factor as needed
                    next_level.append(TreeNode(name=f"node_{i}", parent=node))
            current_level = next_level

        # Measure traversal time
        start_time = time.time()
        visit(large_root, lambda n: False, order="pre")
        traversal_time = time.time() - start_time

        # Assert traversal time is within acceptable limits (e.g., 1 second)
        self.assertLess(traversal_time, 1)

    def test_edge_cases(self):
        empty_tree = TreeNode()
        single_node_tree = TreeNode(name="single")

        # Empty tree checks
        self.assertEqual(len(empty_tree.children), 0)
        self.assertIsNone(empty_tree.parent)

        # Single node tree checks
        self.assertEqual(len(single_node_tree.children), 0)
        self.assertIsNone(single_node_tree.parent)
        self.assertEqual(single_node_tree.name, "single")


if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_node_hash.py`

```python
import unittest
from AlgoTree.treenode import TreeNode
from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode
from AlgoTree.node_hasher import NodeHasher

class TestNodeHash(unittest.TestCase):
    def setUp(self):
        """
        Create a sample tree for testing

        Here is what the tree looks like::
            
                a
                |
                +-- b
                |   |
                |   +-- d
                |   |   |
                |   |   +-- f
                |   |
                |   +-- e
                |
                +-- c
        """
        self.node_a = FlatForestNode(name="a", data1=1, data2=2)
        self.node_b = FlatForestNode(name="b", parent=self.node_a, data="test")
        self.node_c = FlatForestNode(name="c", parent=self.node_a, different_data="test2")
        self.node_d = FlatForestNode(name="d", parent=self.node_b, data="test")
        self.node_e = FlatForestNode(name="e", parent=self.node_b, different_data="test2")
        self.node_f = FlatForestNode(name="f", parent=self.node_d, data="test")

        self.tree_node_a = TreeNode(name="a", data1=1, data2=2)
        self.tree_node_b = TreeNode(name="b", parent=self.tree_node_a, data="test")
        self.tree_node_c = TreeNode(name="c", parent=self.tree_node_a, different_data="test2")
        self.tree_node_d = TreeNode(name="d", parent=self.tree_node_b, data="test")
        self.tree_node_e = TreeNode(name="e", parent=self.tree_node_b, different_data="test2")
        self.tree_node_f = TreeNode(name="f", parent=self.tree_node_d, data="test")

    def test_name_hash(self):
        # Test that the name hash of two nodes with different names is not the same
        self.assertNotEqual(NodeHasher.name(self.tree_node_a), NodeHasher.name(self.tree_node_b))

        # Test that the name hash of two nodes with the same name is the same
        root = TreeNode(name="root")
        another_a = TreeNode(name="a", parent=root)
        self.assertEqual(NodeHasher.name(self.tree_node_a), NodeHasher.name(another_a))

        # Test that the name hash of two nodes with different names is not the same
        self.assertNotEqual(NodeHasher.name(self.node_a), NodeHasher.name(self.node_b))

        # Test that the name hash of two nodes with the same name is the same
        root = FlatForestNode(name="root")
        another_a = FlatForestNode(name="a", parent=root)
        self.assertEqual(NodeHasher.name(self.node_a), NodeHasher.name(another_a))

        # try different tree types with same name
        self.assertEqual(NodeHasher.name(self.tree_node_a), NodeHasher.name(self.node_a))

        self.assertEqual(NodeHasher.name(self.node_a), NodeHasher.name(TreeNode(name="a")))
        self.assertNotEqual(NodeHasher.name(self.node_a), NodeHasher.name(TreeNode(name="b", data1=1, data2=2)))

    def test_payload_hash(self):
        # Test that the payload hash of two nodes with different payloads is not the same
        self.assertNotEqual(NodeHasher.payload(self.tree_node_a), NodeHasher.payload(self.tree_node_b))

        # Test that the payload hash of two nodes with the same payload is the same
        self.assertNotEqual(NodeHasher.payload(self.tree_node_a), NodeHasher.payload(TreeNode(name="a")))

        self.assertEqual(NodeHasher.payload(self.tree_node_a), NodeHasher.payload(TreeNode(name="a", data1=1, data2=2)))
        self.assertNotEqual(NodeHasher.payload(self.tree_node_a), NodeHasher.payload(TreeNode(name="a", data1=1, data2=2, more=None)))
        
        # try different tree types with same payloads
        self.assertEqual(NodeHasher.payload(self.tree_node_a), NodeHasher.payload(self.node_a))

    def test_node_hash(self):
        # Test that the node hash of two nodes with different payloads is not the same
        self.assertNotEqual(NodeHasher.node(self.tree_node_a), NodeHasher.node(self.tree_node_b))

        # Test that the node hash of two nodes with the same payload and same names are the same
        self.assertEqual(NodeHasher.node(self.tree_node_a), NodeHasher.node(TreeNode(name="a", data1=1, data2=2)))

        self.assertEqual(NodeHasher.node(self.tree_node_a), NodeHasher.node(self.node_a))

        self.assertNotEqual(NodeHasher.node(self.tree_node_a), NodeHasher.node(TreeNode(name="a", data1=1, data2=2, more=None)))

    def test_path_hash(self):
        # Test that the path hash of two nodes with different paths is not the same
        self.assertNotEqual(NodeHasher.path(self.tree_node_a), NodeHasher.path(self.tree_node_b))
        self.assertEqual(NodeHasher.path(self.tree_node_b), NodeHasher.path(TreeNode(name="b", parent=TreeNode(name="a",data=0), data1=10, data2=2)))
        self.assertEqual(NodeHasher.path(self.tree_node_a), NodeHasher.path(self.node_a))

if __name__ == "__main__":
    unittest.main()
```

#### Source File: `test/test_tree_converter.py`

```python
import unittest

from anytree import Node

from AlgoTree.flat_forest_node import FlatForestNode
from AlgoTree.tree_converter import TreeConverter
from AlgoTree.treenode import TreeNode


class TestTreeConverter(unittest.TestCase):
    def setUp(self):
        """
        Create a sample tree for testing

        Here is what the tree looks like::

            root
            ├── child1
            │   └── child1_1
            │       └── child2_1 (child1_1_1 value)
            │   
            └── child2
                ├── child2_1
                └── child2_2

        Notice that child2_1 is not unique in the tree. It appears under both
        child1_1 and child2. This is fine for `TreeNode`, but for `FlatForestNode`
        it will be an issue -- it will have to either rename one of the nodes
        (child_2_1_0, for example) or raise an error, depending on whether
        renaming is set to true or false.
        """
        self.root = TreeNode(name="root", value="root_value")
        self.child1 = TreeNode(
            name="child1", parent=self.root, value="child1_value"
        )
        self.child1_1 = TreeNode(
            name="child1_1", parent=self.child1, value="child1_1_value"
        )
        self.child1_1_1 = TreeNode(
            name="child2_1", parent=self.child1_1, value="child1_1_1_value"
        )

        self.child2 = TreeNode(
            name="child2", parent=self.root, value="child2_value"
        )
        self.child2_1 = TreeNode(
            name="child2_1", parent=self.child2, value="child2_1_value"
        )
        self.child2_2 = TreeNode(
            name="child2_2", parent=self.child2, value="child2_2_value"
        )

    def verify_tree_structure(self, root):
        self.assertEqual(root["name"], "root")
        self.assertEqual(root["payload"], { "value" : "root_value"})
        self.assertEqual(len(root["children"]), 2)
        child1 = root["children"][0]
        child2 = root["children"][1]
        self.assertEqual(child1["name"], "child1")
        self.assertEqual(child1["payload"], { "value" : "child1_value"})
        self.assertEqual(child2["name"], "child2")
        self.assertEqual(child2["payload"], { "value" : "child2_value"})

        self.assertEqual(len(child1["children"]), 1)
        child1_1 = child1["children"][0]
        self.assertEqual(child1_1["name"], "child1_1")
        self.assertEqual(child1_1["payload"], { "value" : "child1_1_value"})

        self.assertEqual(len(child1_1["children"]), 1)
        child1_1_1 = child1_1["children"][0]
        self.assertEqual(child1_1_1["name"], "child2_1")
        self.assertEqual(child1_1_1["payload"], { "value" : "child1_1_1_value"})
        self.assertEqual(len(child1_1_1["children"]), 0)

        self.assertEqual(len(child2["children"]), 2)
        child2_1 = child2["children"][0]
        child2_2 = child2["children"][1]
        self.assertEqual(child2_1["name"], "child2_1")
        self.assertEqual(child2_1["payload"], { "value" : "child2_1_value"})
        self.assertEqual(len(child2_1["children"]), 0)

        self.assertEqual(child2_2["name"], "child2_2")
        self.assertEqual(child2_2["payload"], { "value" : "child2_2_value"})
        self.assertEqual(len(child2_2["children"]), 0)

    def verify_tree_structure_flattree_renamed(self, root):
        self.assertEqual(root["name"], "root")
        self.assertEqual(root["payload"], { "value" : "root_value"})
        self.assertEqual(len(root["children"]), 2)
        child1 = root["children"][0]
        child2 = root["children"][1]
        self.assertEqual(child1["name"], "child1")
        self.assertEqual(child1["payload"], { "value" : "child1_value"})
        self.assertEqual(child2["name"], "child2")
        self.assertEqual(child2["payload"], { "value" : "child2_value"})

        self.assertEqual(len(child1["children"]), 1)
        child1_1 = child1["children"][0]
        self.assertEqual(child1_1["name"], "child1_1")
        self.assertEqual(child1_1["payload"], { "value" : "child1_1_value"})

        self.assertEqual(len(child1_1["children"]), 1)
        child1_1_1 = child1_1["children"][0]
        self.assertTrue(child1_1_1["name"] == "child2_1" or child1_1_1["name"] == "child2_1_0")
        self.assertEqual(child1_1_1["payload"], { "value" : "child1_1_1_value"})
        self.assertEqual(len(child1_1_1["children"]), 0)

        self.assertEqual(len(child2["children"]), 2)
        child2_1 = child2["children"][0]
        child2_2 = child2["children"][1]
        self.assertTrue(child2_1["name"] == "child2_1_0" or child2_1["name"] == "child2_1")
        self.assertEqual(child2_1["payload"], { "value" : "child2_1_value"})
        self.assertEqual(len(child2_1["children"]), 0)

        self.assertEqual(child2_2["name"], "child2_2")
        self.assertEqual(child2_2["payload"], { "value" : "child2_2_value"})
        self.assertEqual(len(child2_2["children"]), 0)


    def test_to_dict(self):
        """
            root
            ├── child1
            │   └── child1_1
            │       └── child2_1 (child1_1_1 value)
            └── child2
                ├── child2_1
                └── child2_2
        """
        
        # Test converting TreeNode to dict
        tree_dict = TreeConverter.to_dict(self.root)
        # logging.debug(json.dumps(tree_dict, indent=2))
        self.verify_tree_structure(tree_dict)

    def test_copy_under(self):
        # Test copying a subtree under another node
        new_root = TreeNode(name="new_root", value="new_root_value")
        TreeConverter.copy_under(self.root, new_root)
        self.assertEqual(len(new_root.children), 1)
        root = new_root.children[0]
        tree_dict = TreeConverter.to_dict(root)
        self.verify_tree_structure(tree_dict)

    def test_convert_to_treenode(self):
        # Test converting TreeNode to TreeNode (identity transformation)
        new_tree = TreeConverter.convert(self.root, TreeNode)

        # logging.debug(json.dumps(new_tree, indent=2))
        self.assertIsInstance(new_tree, TreeNode)
        tree_dict = TreeConverter.to_dict(new_tree)
        self.verify_tree_structure(tree_dict)

    def test_convert_to_flat_forest_node(self):
        # Test converting TreeNode to FlatForestNode
        new_tree = TreeConverter.convert(self.root, FlatForestNode)
        #self.assertIsInstance(new_tree, FlatForestNode)
        #tree_dict = TreeConverter.to_dict(new_tree)
        #self.assertIsInstance(tree_dict, dict)
        #self.verify_tree_structure_flattree_renamed(tree_dict)

    def test_clone_treenode(self):
        root = TreeNode(name="root", value="root value")
        A = TreeNode(name="A", value=1, parent=root)
        B = TreeNode(name="B", value=2, parent=root)
        C = TreeNode(name="C", value=3, parent=root)
        D = TreeNode(name="D", value=4, parent=B)
        E = TreeNode(name="E", value=5, parent=D)
        self.assertEqual(len(root.children), 3)
        new_root = root.clone()
        new_root.add_child(name="F", value=6)
        self.assertEqual(len(new_root.children), 4)
        
        self.assertEqual(new_root.name, "root")
        self.assertEqual(new_root.payload['value'], "root value")
        self.assertEqual(new_root.children[0].name, "A")
        self.assertEqual(new_root.children[0].payload["value"], 1)
        self.assertEqual(new_root.children[1].name, "B")
        self.assertEqual(new_root.children[1].payload["value"], 2)
        self.assertEqual(new_root.children[2].name, "C")
        self.assertEqual(new_root.children[2].payload["value"], 3)
        self.assertEqual(new_root.children[3].name, "F")
        self.assertEqual(new_root.children[3].payload["value"], 6)
        self.assertEqual(new_root.children[1].children[0].name, "D")
        self.assertEqual(new_root.children[1].children[0].payload["value"], 4)
        self.assertEqual(new_root.children[1].children[0].children[0].name, "E")
        self.assertEqual(new_root.children[1].children[0].children[0].payload["value"], 5)
        
    def test_clone_flat_forest(self):
        root = FlatForestNode(name="root", value="root value")
        A = FlatForestNode(name="A", value=1, parent=root)
        B = FlatForestNode(name="B", value=2, parent=root)
        C = FlatForestNode(name="C", value=3, parent=root)
        D = FlatForestNode(name="D", value=4, parent=B)
        E = FlatForestNode(name="E", value=5, parent=D)
        new_root = root.clone(clone_children=True)
        new_root.add_child(name="F", value=6)
        self.assertEqual(len(new_root.children), 4)
        self.assertEqual(len(root.children), 3)
        self.assertEqual(new_root.name, "root")
        self.assertEqual(new_root.payload['value'], "root value")
        self.assertEqual(new_root.children[0].name, "A")
        self.assertEqual(new_root.children[0].payload["value"], 1)
        self.assertEqual(new_root.children[1].name, "B")
        self.assertEqual(new_root.children[1].payload["value"], 2)
        self.assertEqual(new_root.children[2].name, "C")
        self.assertEqual(new_root.children[2].payload["value"], 3)
        self.assertEqual(new_root.children[3].name, "F")
        self.assertEqual(new_root.children[3].payload["value"], 6)
        self.assertEqual(new_root.children[1].children[0].name, "D")
        self.assertEqual(new_root.children[1].children[0].payload["value"], 4)
        self.assertEqual(new_root.children[1].children[0].children[0].name, "E")
        self.assertEqual(new_root.children[1].children[0].children[0].payload["value"], 5)

if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_tree_hasher.py`

```python
import unittest
from AlgoTree.tree_hasher import TreeHasher
from AlgoTree.tree_converter import TreeConverter  # Assuming this converts trees to dictionaries
from AlgoTree.treenode import TreeNode

class Node:
    """Simple node class for testing purposes."""
    def __init__(self, name, payload=None):
        self.name = name
        self.payload = payload
        self.children = []

    def add_child(self, child):
        self.children.append(child)

class TestTreeHasher(unittest.TestCase):

    def setUp(self):
        # Create some example trees for testing
        self.tree1 = Node('Root')
        child1_1 = Node('A', payload=10)
        child1_2 = Node('B', payload=20)
        self.tree1.add_child(child1_1)
        self.tree1.add_child(child1_2)

        self.tree2 = Node('Root')
        child2_1 = Node('A', payload=10)
        child2_2 = Node('B', payload=20)
        self.tree2.add_child(child2_1)
        self.tree2.add_child(child2_2)

        self.tree3 = Node('Root')
        child3_1 = Node('A', payload=10)
        child3_2 = Node('C', payload=30)  # Different payload and name
        self.tree3.add_child(child3_1)
        self.tree3.add_child(child3_2)

        self.tree4 = TreeNode(name='Root', payload=None)
        TreeNode(name='A', payload=10, parent=self.tree4)
        TreeNode(name='B', payload=20, parent=self.tree4)


        self.non_iso_tree = TreeNode(name='Root', payload=None)
        nodeAnoniso = TreeNode(name='A', payload=10, parent=self.non_iso_tree)
        TreeNode(name='B', payload=20, parent=nodeAnoniso)


        self.tree_hasher = TreeHasher()

    def test_tree_hash_equal_trees(self):
        """Test that two identical trees have the same hash."""
        from AlgoTree.pretty_tree import pretty_tree

        self.assertEqual(self.tree_hasher(self.tree1), self.tree_hasher(self.tree2))
        self.assertEqual(self.tree_hasher(self.tree1), self.tree_hasher(self.tree4))

    def test_tree_hash_different_trees(self):
        """Test that two different trees have different hashes."""
        self.assertNotEqual(self.tree_hasher(self.tree1), self.tree_hasher(self.tree3))

    def test_tree_hash_isomorphic_trees(self):
        """Test that isomorphic trees are handled correctly (depending on the implementation)."""
        # For now, assuming the default `tree` method considers both structure and data
        self.assertNotEqual(self.tree_hasher(self.tree1), self.tree_hasher(self.tree3))

    def test_isomorphic_tree_hash(self):
        """Test that isomorphic trees hash the same if we ignore node names and payloads."""
        isomorphic_hasher = TreeHasher(TreeHasher.isomorphic)
        
        # Create isomorphic trees (structure is the same, names and payloads differ)
        tree4 = Node('X')
        child4_1 = Node('Y')
        child4_2 = Node('Z')
        tree4.add_child(child4_1)
        tree4.add_child(child4_2)

        self.assertEqual(isomorphic_hasher(self.tree1), isomorphic_hasher(tree4))

    def test_non_isomorphic_tree_hash(self):
        """Test that non-isomorphic trees hash differently if we ignore node names and payloads."""
        isomorphic_hasher = TreeHasher(TreeHasher.isomorphic)

        self.assertNotEqual(isomorphic_hasher(self.tree1), isomorphic_hasher(self.non_iso_tree))

    def test_tree_hash_with_empty_tree(self):
        """Test hashing of an empty tree (if applicable)."""
        empty_tree = Node(None)
        self.assertIsInstance(self.tree_hasher(empty_tree), int)

    def test_tree_hash_with_single_node(self):
        """Test hashing of a tree with a single node."""
        single_node_tree = Node('Single', payload=42)
        self.assertIsInstance(self.tree_hasher(single_node_tree), int)

if __name__ == '__main__':
    unittest.main()

```

#### Source File: `test/test_tree_print.py`

```python
import unittest
from AlgoTree.pretty_tree import PrettyTree, pretty_tree

class TestTreePrettyPrinter(unittest.TestCase):
    
    class Node:
        def __init__(self, name, children=None, payload=None):
            self.name = name
            self.payload = payload
            self.children = children or []
            for child in self.children:
                child.parent = self
            self.parent = None

        @property
        def root(self):
            node = self
            while node.parent:
                node = node.parent
            return node
    
    def setUp(self):
        # Creating a sample tree structure for testing
        self.root = self.Node('root', [
            self.Node('child1', [
                self.Node('child1.1'),
                self.Node('child1.2')
            ]),
            self.Node('child2', [
                self.Node('child2.1')
            ])
        ])
    
    def test_default_pretty_print(self):
        printer = PrettyTree()
        out = printer(self.root)
        expected_output = (
            "root\n"
            "├───── child1\n"
            "│      ├───── child1.1\n"
            "│      └───── child1.2\n"
            "└───── child2\n"
            "       └───── child2.1\n"
        )
        self.assertEqual(out, expected_output, msg="Tree not displayed correctly")
    
    def test_mark_nodes(self):
        printer = PrettyTree()
        out = printer(self.root, mark=['child1', 'child2.1'], markers=['(?)'])
        expected_output = (
            "root\n"
            "├───── child1 (?)\n"
            "│      ├───── child1.1\n"
            "│      └───── child1.2\n"
            "└───── child2\n"
            "       └───── child2.1 (?)\n"
        )
        self.assertEqual(out, expected_output, msg="Marked nodes are not displayed correctly")

if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_tree_with_flat_forest_node.py`

```python
import unittest
from AlgoTree.pretty_tree import PrettyTree, pretty_tree
from AlgoTree.flat_forest import FlatForest
from AlgoTree.flat_forest_node import FlatForestNode

class TestTreePrettyPrinter(unittest.TestCase):
    
    def setUp(self):
        # Create a flat tree
        #
        # Here is what the tree looks like:
        #
        #     a
        #     ├── b
        #     │   ├── d
        #     │   |   ├── i
        #     │   |   └── j
        #     │   └── e
        #     ├── c
        #     |   └── f
        #     └── g
        #         └── h
        self.tree_data = {
            "a": {"parent": None},
            "b": {"parent": "a"},
            "c": {"parent": "a"},
            "d": {"parent": "b"},
            "e": {"parent": "b"},
            "f": {"parent": "c"},
            "g": {"parent": "a"},
            "h": {"parent": "g"},
            "i": {"parent": "d"},
            "j": {"parent": "d"},
        }
        self.flat_tree = FlatForest(self.tree_data)

    def test_default_pretty_print(self):
        printer = PrettyTree()
        out = printer(self.flat_tree.subtree("a"))
        expected_output = (
            "a\n"
            "├───── b\n"
            "│      ├───── d\n"
            "│      │      ├───── i\n"
            "│      │      └───── j\n"
            "│      └───── e\n"
            "├───── c\n"
            "│      └───── f\n"
            "└───── g\n"
            "       └───── h\n"
        )
        self.assertEqual(out, expected_output, msg="Tree not displayed correctly")
    
    def test_pretty_print_marks(self):
        printer = PrettyTree()
        out = printer(self.flat_tree.subtree("a"), mark=["d", "f"], markers=["(?)"])
        expected_output = (
            "a\n"
            "├───── b\n"
            "│      ├───── d (?)\n"
            "│      │      ├───── i\n"
            "│      │      └───── j\n"
            "│      └───── e\n"
            "├───── c\n"
            "│      └───── f (?)\n"
            "└───── g\n"
            "       └───── h\n"
        )
        self.assertEqual(out, expected_output, msg="Tree not displayed correctly")

    def test_pretty_print_subtree_marks(self):
        printer = PrettyTree()
        B = self.flat_tree.subtree("b")
        out = printer(B, mark=[B.root.name], markers=["(root)"])
        expected_output = (
            "b (root)\n"
            "├───── d\n"
            "│      ├───── i\n"
            "│      └───── j\n"
            "└───── e\n"
        )
        self.assertEqual(out, expected_output, msg="Tree not displayed correctly")

if __name__ == "__main__":
    unittest.main()
```

#### Source File: `test/test_treenode.py`

```python
import unittest

from AlgoTree.treenode import TreeNode

class TestTreeNode(unittest.TestCase):
    def test_constructor_with_name_and_value(self):
        node = TreeNode(name="root", value=10)
        self.assertEqual(node.name, "root")
        self.assertEqual(node.payload["value"], 10)
        self.assertEqual(node.children, [])

    def test_add_child(self):
        root = TreeNode(name="root", value=10)
        child = root.add_child(name="child1", value=1)
        self.assertEqual(len(root.children), 1)
        self.assertEqual(root.children[0].name, "child1")
        self.assertEqual(root.children[0].payload["value"], 1)
        self.assertEqual(child.name, "child1")
        self.assertEqual(child.payload["value"], 1)

    def test_set_get_children(self):
        root = TreeNode(name="root", value=10)
        child1 = TreeNode(name="child1", value=1)
        child2 = TreeNode(name="child2", value=2)
        root.children = [child1, child2]
        self.assertEqual(len(root.children), 2)
        self.assertEqual(root.children[0].name, "child1")
        self.assertEqual(root.children[1].name, "child2")

    def test_set_get_payload(self):
        root = TreeNode(name="root", value=10, extra="extra_data")
        self.assertEqual(root.payload, {"value": 10, "extra": "extra_data"})
        root.payload = {"value": 20, "new_data": "new_value"}
        self.assertEqual(root.payload["value"], 20)
        self.assertEqual(root.payload["new_data"], "new_value")
        self.assertNotIn("extra", root)

    def test_node_method(self):
        root = TreeNode(name="root", value=10)
        with self.assertRaises(KeyError):
            root.node("non_existent")

if __name__ == "__main__":
    unittest.main()

```

#### Source File: `test/test_treenode_utils.py`

```python
import unittest

from AlgoTree.treenode import TreeNode
from AlgoTree.utils import (
    ancestors,
    breadth_first,
    depth,
    descendants,
    find_node,
    find_nodes,
    height,
    is_internal,
    is_leaf,
    is_root,
    leaves,
    map,
    siblings,
    visit,
)

class TestTreeNodeUtils(unittest.TestCase):
    def setUp(self):
        """
        Create a sample tree for testing

        Here is what the tree looks like::

            node0
            ├── node1
            ├── node2
            └── node3
                ├── node4
                ├── node5
                ├── node6
                │   └── node9
                ├── node7
                └── node8
        """
        self.node0 = TreeNode(name="node0", value=0)
        self.node1 = TreeNode(name="node1", parent=self.node0, value=1)
        self.node2 = TreeNode(name="node2", parent=self.node0, value=2)
        self.node3 = TreeNode(name="node3", parent=self.node0, value=3)
        self.node4 = TreeNode(name="node4", parent=self.node3, value=4)
        self.node5 = TreeNode(name="node5", parent=self.node3, value=5)
        self.node6 = TreeNode(name="node6", parent=self.node3, value=6)
        self.node7 = TreeNode(name="node7", parent=self.node3, value=7)
        self.node8 = TreeNode(name="node8", parent=self.node3, value=8)
        self.node9 = TreeNode(name="node9", parent=self.node6, value=9)

    def test_visit_pre_order(self):
        from AlgoTree.pretty_tree import pretty_tree
        from AlgoTree.treenode import TreeNode
        import json
        print("\npre-order\n")
        print(pretty_tree(self.node0))
        print("\n\n")
        print(json.dumps(self.node0.to_dict(), indent=4))
        result = []
        visit(self.node0, lambda n: result.append(n.name) or False, order="pre")
        self.assertEqual(
            result,
            [
                "node0",
                "node1",
                "node2",
                "node3",
                "node4",
                "node5",
                "node6",
                "node9",
                "node7",
                "node8",
            ],
        )

    def test_visit_level_order(self):
        result = []
        visit(
            self.node0,
            lambda n, **kwargs: result.append((n.name, kwargs["level"]))
            or False,
            order="level",
        )
        self.assertEqual(
            result,
            [
                ("node0", 0),
                ("node1", 1),
                ("node2", 1),
                ("node3", 1),
                ("node4", 2),
                ("node5", 2),
                ("node6", 2),
                ("node7", 2),
                ("node8", 2),
                ("node9", 3),
            ],
        )

    def test_visit_stop_on_match(self):
        result = []
        visit(
            self.node0,
            lambda n: result.append(n) or n.name == "node6",
            order="pre",
        )
        self.assertEqual(
            result, [self.node0, self.node1, self.node2, self.node3, self.node4, self.node5, self.node6]
        )

    def test_map(self):
        def increment_value(node):
            node.payload["value"] += 1
            return node

        map(self.node0, increment_value)
        self.assertEqual(self.node0.payload["value"], 1)
        self.assertEqual(self.node1.payload["value"], 2)
        self.assertEqual(self.node9.payload["value"], 10)

    def test_descendants_node3(self):
        self.assertCountEqual(
            descendants(self.node3),
            [self.node4, self.node5, self.node6, self.node9, self.node7, self.node8]
        )

    def test_ancestors_node9(self):
        self.assertCountEqual(ancestors(self.node9), [self.node6, self.node3, self.node0])

    def test_siblings_node6(self):
        from AlgoTree.pretty_tree import pretty_tree
        print(pretty_tree(self.node0.node("node6")))
        print(pretty_tree(self.node0.node("node6").root))
        print(siblings(self.node0.node("node6")))

        self.assertCountEqual(siblings(self.node0.node("node6")),
                              [self.node4, self.node5, self.node7, self.node8])

    def test_leaves(self):
        self.assertCountEqual(
            leaves(self.node0),
            [self.node1, self.node2, self.node4, self.node5, self.node7, self.node8, self.node9]
        )

    def test_height(self):
        """
        node0
            ├── node1
            ├── node2
            └── node3
                ├── node4
                ├── node5
                ├── node6
                │   └── node9
                ├── node7
                └── node8
        """
        self.assertEqual(height(self.node0), 3)
        self.assertEqual(height(self.node3), 2)
        self.assertEqual(height(self.node9), 0)
        self.assertEqual(height(self.node3.root), 3)


    def test_root(self):
        self.assertEqual(self.node0.root, self.node0)
        self.assertEqual(self.node3.root, self.node0)
        self.assertEqual(self.node9.root, self.node0)

    def test_depth(self):
        self.assertEqual(depth(self.node0), 0)
        self.assertEqual(depth(self.node3), 1)
        self.assertEqual(depth(self.node9), 3)

    def test_is_root(self):
        self.assertTrue(is_root(self.node0))
        self.assertFalse(is_root(self.node1))

    def test_is_leaf(self):
        self.assertTrue(is_leaf(self.node9))
        self.assertFalse(is_leaf(self.node3))

    def test_is_internal(self):
        self.assertTrue(is_internal(self.node3))
        self.assertFalse(is_internal(self.node1))

    def test_breadth_first(self):
        result = []
        breadth_first(
            self.node0,
            lambda n, **kwargs: result.append((n.name, kwargs["level"]))
            or False,
        )
        self.assertEqual(
            result,
            [
                ("node0", 0),
                ("node1", 1),
                ("node2", 1),
                ("node3", 1),
                ("node4", 2),
                ("node5", 2),
                ("node6", 2),
                ("node7", 2),
                ("node8", 2),
                ("node9", 3),
            ],
        )

    def test_find_nodes(self):
        nodes = find_nodes(self.node0, lambda n, **_: n.payload["value"] > 3)
        self.assertCountEqual(
            [n.name for n in nodes],
            ["node4", "node5", "node6", "node7", "node8", "node9"],
        )

    def test_find_node(self):
        node = find_node(self.node0, lambda n, **_: n.payload["value"] == 7)
        self.assertEqual(node.name, "node7")

    def test_get_node(self):
        node = self.node0.node("node7")
        self.assertEqual(node.name, "node7")


if __name__ == "__main__":
    unittest.main()

```

#### Source File: `bin/__init__.py`

```python

```

#### Source File: `bin/jt.py`

```python
#!/usr/bin/env python3

import argparse
import json
import sys
import textwrap
import AlgoTree
from pprint import pprint

def main():
    parser = argparse.ArgumentParser(
        description="Query a tree represented in JSON format (FlatForest, TreeNode)",
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Path to JSON file (reads from stdin if not provided)",
    )
    parser.add_argument(
        "--node-name",
        type=str,
        nargs=1,
        metavar="LAMBA_EXPRESSION",
        help="Lambda expression to generate node names from a node, defaults to `lambda node: node.name`",
    )
    parser.add_argument(
        "--lca",
        metavar=("NODE_KEY1", "NODE_KEY2"),
        help="Get the lowest common ancestor of two nodes",
        type=str,
        nargs=2,
    )
    parser.add_argument(
        "--depth",
        metavar="NODE_KEY",
        help="Get the depth of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--mark-nodes",
        metavar="NODE_KEY",
        help="Mark nodes in the tree",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "--distance",
        metavar=("NODE_KEY1", "NODE_KEY2"),
        help="Get the distance between two nodes",
        type=str,
        nargs=2,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0"
    )
    parser.add_argument(
        "--size",
        action="store_true",
        help="Print the size of the tree"
    )
    parser.add_argument(
        "--siblings",
        metavar="NODE_KEY",
        help="Show siblings of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--children",
        metavar="NODE_KEY",
        help="Show children of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--parent",
        metavar="NODE_KEY",
        help="Show parent of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--ancestors",
        metavar="NODE_KEY",
        help="Show ancestors of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--descendants",
        metavar="NODE_KEY",
        help="Show descendants of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--has-node",
        metavar="NODE_KEY",
        help="Check if a node exists",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--subtree",
        metavar="NODE_KEY",
        help="Get the subtree rooted at a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--node",
        metavar="NODE_KEY",
        help="Get node by key",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--root",
        action="store_true",
        help="Get the root node"
    )
    parser.add_argument(
        "--root-to-leaves",
        action="store_true",
        help="Get a list of paths from the root to the leaves")
    parser.add_argument(
        "--leaves",
        action="store_true",
        help="Get the leaf nodes"
    )
    parser.add_argument(
        "--height",
        action="store_true",
        help="Get the height of the tree"
    )
    parser.add_argument(
        "--nodes",
        action="store_true",
        help="Get all nodes in the tree"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the tree in a pretty format",
    )
    parser.add_argument(
        "--prune",
        metavar="LAMBDA_EXPRESSION",
        help="Prune the tree by predicate function",
        type=str,
        nargs=1)
    parser.add_argument(
        "--subtree-rooted-at",
        metavar="NODE_KEY",
        help="Get the subtree rooted at a given node",
        type=str,
        nargs=1)
    parser.add_argument(
        "--find-nodes",
        nargs=1,
        type=str,
        metavar="LAMBDA_EXPRESSION",
        help="Find nodes by predicate function")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the tree in JSON format")
    parser.add_argument(
        "--convert",
        help="Convert the tree to a different format",
        nargs=1,
        type=str,
        metavar="TARGET_FORMAT"
    )
    parser.add_argument(
        "--type",
        action="store_true",
        help="Print the type of the tree"
    )
    parser.add_argument(
        "--merge-forest",
        nargs=1,
        type=str,
        metavar="NODE_KEY",
        help="Merge a forest into a single tree under a new node named NODE_KEY")
    parser.add_argument(
        "--set-root",
        nargs=1,
        type=str,
        metavar="NODE_KEY",
        help="Set the root node of the tree to the node with the given key"
    )
    parser.add_argument(
        "--epilog",
        help="Show example usage",
        action="store_true"
    )
    #parser.add_argument(
    #    "--partial",
    #    action="store_true",
    #    help="Depends on the context, but for instance if setting `--partial` with `--set-root stuff` it will match `stuff` as a partial match"
    #)

    parser.epilog = textwrap.dedent(
        """
            Example usage:
                # Check if a node exists
                {prog} ./example.json --has-node nodeName
                # Get specific node details
                {prog} ./example.json --get-node nodeKey
                # Show siblings of a node
                {prog} ./example.json --siblings nodeName
        """
    ).format(prog=parser.prog)

    args = parser.parse_args()

    try:
        if args.file == sys.stdin and sys.stdin.isatty():
            print("No JSON data provided, please provide a file or pipe data")
            parser.print_usage()
            sys.exit(1)

        if args.epilog:
            print(parser.epilog)
            sys.exit(0)

        node_name = lambda node: node.name
        if args.node_name:
            node_name = eval(args.node_name[0])

        data = json.load(args.file)
        tree = None
        if AlgoTree.FlatForest.is_valid(data):
            tree = AlgoTree.FlatForest(data)
        elif AlgoTree.TreeNode.is_valid(data):
            tree = AlgoTree.TreeNode.from_dict(data)
        else:
            print("Unrecognized tree format")
            sys.exit(1)

        if args.merge_forest:
            if type(tree) is AlgoTree.FlatForest:
                tree = tree.as_tree(args.merge_forest[0])

        if args.set_root:
            tree = tree.subtree(args.set_root[0])

        if args.prune:
            AlgoTree.prune(tree, eval(args.prune[0]))

        if args.nodes:
            pprint([node_name(n) for n in tree.nodes()])

        if args.convert:
            target_type = args.convert[0].strip().lower()
            if target_type == "flatforest":
                tree = AlgoTree.TreeConverter.convert(tree, AlgoTree.FlatForestNode)
            elif target_type == "treenode":
                tree = AlgoTree.TreeConverter.convert(tree, AlgoTree.TreeNode)
            else:
                raise ValueError("Invalid target type")
            
        if args.json:
            print(json.dumps(tree.to_dict(), indent=4))

        if args.find_nodes:
            lam = args.find_nodes[0]
            nodes = AlgoTree.find_nodes(tree, eval(args.find_nodes[0]))
            print([node_name(n) for n in nodes])

        if args.root:
            print(node_name(tree.root))

        if args.size:
            print(AlgoTree.size(tree))

        if args.siblings:
            sibs = AlgoTree.siblings(tree.node(args.siblings[0]))
            print([node_name(s) for s in sibs])

        if args.children:
            children = tree.node(args.children[0]).children
            print([node_name(c) for c in children])

        if args.parent:
            node = tree.node(args.parent[0])
            print(node_name(node.parent) if node.parent else None)

        if args.ancestors:
            anc = AlgoTree.ancestors(tree.node(args.ancestors[0]))
            print([node_name(a) for a in anc])

        if args.descendants:
            desc = AlgoTree.descendants(tree.node(args.descendants[0]))
            print([node_name(d) for d in desc])

        if args.has_node:
            print(tree.node(args.has_node[0]) is not None)

        if args.height:
            print(AlgoTree.height(tree))

        if args.leaves:
            print([node_name(l) for l in AlgoTree.leaves(tree)])

        if args.node:
            node = tree.node(args.node[0])
            print(node)
            
        if args.subtree:
            sub = AlgoTree.TreeConverter.convert(tree.subtree(args.subtree[0]), AlgoTree.FlatForestNode)
            print(json.dumps(sub.tree, indent=4))

        if args.depth:
            print(AlgoTree.depth(tree.node(args.depth[0])))

        if args.distance:
            n1, n2 = args.distance
            print(AlgoTree.distance(tree.node(n1), tree.node(n2)))

        if args.lca:
            n1, n2 = args.lca
            print(node_name(AlgoTree.lca(tree.node(n1), tree.node(n2))))

        if args.root_to_leaves:
            paths = [p for p in AlgoTree.node_to_leaf_paths(tree)]
            for p in paths:
                print([node_name(n) for n in p])

        if args.subtree_rooted_at:
            # this does not work, look more closely at this
            node = tree.node(args.subtree_rooted_at[0])
            sub = AlgoTree.subtree_rooted_at(node, 1)
            print(sub.to_dict())

        if args.pretty:
            print(AlgoTree.pretty_tree(tree.root, node_name=node_name, mark=args.mark_nodes or []))

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

#### Source File: `bin/treenode.json`

```json
{
  "name": "node1",
  "payload": { "data": "Some data for node1 (root)" },
  "children": [
    {
      "name": "node2",
      "payload": { "data": "Some data for node2" },
      "children": [
        {
          "name": "node4",
          "payload": { "data": "Some data for node4" }
        },
        {
          "name": "node5",
          "payload": { "data": "Some data for node5" }
        }
      ]
    },
    {
      "name": "node3",
      "payload" : { "data": "Some data for node3" }
    }
  ]
}

```

