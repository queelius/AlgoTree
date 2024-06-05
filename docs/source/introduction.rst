Introduction
============

Welcome to the documentation for the `treekit` package. This package provides a suite of utilities for working with tree-like data structures in Python. It supports various tree representations, including:

- `FlatTree` and `FlatTreeNode` for working with flat tree structures
- `TreeNode` for recursive tree structures
- Conversion utilities to convert between different tree representations
- Utility functions for common tree operations

Getting Started
---------------

To install the `treekit` package, you can use pip:

.. code-block:: shell

   pip install treekit

Once installed, you can start using the various tree structures and utilities provided by the package. Here is a quick example to get you started:

.. code-block:: python

   from treekit.flattree_node import FlatTreeNode

   root = FlatTreeNode(name="root", data=0)
   child1 = FlatTreeNode(name="child1", parent=root, data=1)
   child2 = FlatTreeNode(name="child2", parent=root, data=2)

   print(root)
   print(child1)
   print(child2)

This creates a simple tree with a root node and two child nodes.

Features
--------

- Flexible tree structures with `FlatTree`, `FlatTreeNode`, and `TreeNode`
- Utility functions for common tree operations such as traversal, searching, and manipulation
- Conversion utilities to easily convert between different tree representations
- Integration with visualization tools to visualize tree structures

Documentation Structure
-----------------------

The documentation is organized into the following sections:

- **Modules:** Detailed documentation of each module and class in the `treekit` package
- **Examples:** Code examples demonstrating how to use the various features of the package

We hope you find this documentation helpful. If you have any questions or encounter any issues, please feel free to open an issue on our GitHub repository.

