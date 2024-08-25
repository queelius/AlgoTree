AlgoTree
========

.. image:: https://img.shields.io/pypi/v/AlgoTree.svg
   :target: https://pypi.org/project/AlgoTree/

.. image:: https://img.shields.io/pypi/l/AlgoTree.svg
   :target: https://pypi.org/project/AlgoTree/

```AlgoTree``` is a Python package for working with tree structures, including
FlatForest and TreeNode representations.


Introduction
------------

Welcome to the documentation for the ```AlgoTree``` package. This package provides a
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
