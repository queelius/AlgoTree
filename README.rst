AlgoTree
========

.. image:: https://img.shields.io/pypi/v/AlgoTree.svg
   :target: https://pypi.org/project/AlgoTree/

.. image:: https://img.shields.io/pypi/l/AlgoTree.svg
   :target: https://pypi.org/project/AlgoTree/

``AlgoTree`` is a Python package for working with tree structures. It provides
a modern fluent API for tree construction and manipulation.

⚠️ **BREAKING CHANGES in v1.0.0** ⚠️
--------------------------------------

**Version 1.0.0 introduces a completely new API that is NOT backward compatible.**

- The old ``TreeNode`` and ``FlatForest`` dict-based classes have been replaced
- New modern ``Node`` class with clean OOP design
- New fluent API with ``TreeBuilder`` and ``FluentNode``
- Tree DSL for parsing trees from text

**If you need the old API:**

.. code-block:: shell

   pip install "AlgoTree<1.0.0"

For migration guide and old documentation, see the `v0.8 branch <https://github.com/queelius/AlgoTree/tree/v0.8>`_.


Introduction
------------

Welcome to the documentation for the ``AlgoTree`` package. This package provides a
suite of utilities for working with tree-like data structures in Python. It
supports various tree representations and APIs:

**New Fluent API (Recommended)**:

- ``Node`` - Modern tree node class with clean OOP design
- ``TreeBuilder`` - Fluent API for building trees with method chaining
- ``FluentNode`` - Chainable operations for filtering, mapping, and transforming trees
- ``parse_tree`` - DSL parser supporting visual, indent, and S-expression formats

**Traditional API**:

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
provided by the package. 

Quick Start with the Fluent API (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import TreeBuilder, parse_tree, FluentNode
   
   # Method 1: Build with fluent API
   tree = (TreeBuilder()
       .root("company")
       .child("engineering")
           .child("frontend")
           .sibling("backend")
           .up()
       .sibling("sales")
       .build())
   
   # Method 2: Parse from text DSL
   tree = parse_tree("""
   company
   ├── engineering
   │   ├── frontend
   │   └── backend
   └── sales
   """)
   
   # Process with chainable operations
   (FluentNode(tree)
       .descendants()
       .where(lambda n: "end" in n.name)
       .each(lambda n: print(n.name)))  # Prints: frontend, backend

For detailed examples, see the `Fluent API Guide <https://queelius.github.io/AlgoTree/fluent_api.html>`_ in the documentation.

Traditional API Example
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree.flat_forest_node import FlatForestNode
   from AlgoTree.pretty_tree import pretty_tree
   root = FlatForestNode(name="root", data=0)
   node1 = FlatForestNode(name="node1", parent=root, data=1)
   node2 = FlatForestNode(name="node2", parent=root, data=2)
   node3 = FlatForestNode(name="node3", parent=node2, data=3)

   pretty_tree(root)

This produces the output::

   root
   ├── node1
   └── node2
       └── node3

The ``AlgoTree`` package provides a wide range of tree structures and utilities
to help you work with tree-like data structures in Python. You can explore the
documentation to learn more about the available features and how to use them.

Features
--------

**New in v0.9+ (Fluent API)**:

- **Modern Node class** - Clean OOP design without dict inheritance
- **TreeBuilder** - Intuitive tree construction with method chaining
- **FluentNode** - Powerful chainable operations (filter, map, prune, sort)
- **Tree DSL** - Parse trees from visual, indent, or S-expression formats
- **Rich traversal** - Built-in preorder, postorder, and level-order traversal

**Core Features**:

- Clean, intuitive API with the modern ``Node`` class
- Powerful operations for traversal, searching, and manipulation
- Multiple tree construction methods (programmatic, fluent, DSL)
- Pretty printing and visualization
- Command-line tool ``jt`` for tree manipulation from the terminal


Modern API Design
-----------------

AlgoTree v1.0 provides a clean, modern API built around the ``Node`` class,
which represents tree nodes as proper Python objects rather than dictionaries.

Key properties and methods:

- ``parent`` - Parent node reference
- ``children`` - List of child nodes  
- ``is_root``, ``is_leaf`` - Node type checks
- ``level`` - Depth in tree
- ``add_child()`` - Add a child node
- ``traverse_*()`` - Various traversal methods
- ``find()``, ``find_all()`` - Search with predicates
- ``to_dict()``, ``from_dict()`` - JSON compatibility

See the `API documentation <https://queelius.github.io/AlgoTree/fluent_api.html>`_ for complete details.
