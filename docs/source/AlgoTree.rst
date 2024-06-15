AlgoTree
========

- **FlatTree**: A class for working with flat tree structures where nodes are represented as key-value pairs in a dictionary.
- **FlatTreeNode**: A class for representing nodes in a flat tree structure.
- **TreeNode**: A class for representing recursive tree structures.
- **TreeConverter**: A class containing utilities for converting between different tree representations.
- **Utils**: Utility functions for common tree operations such as traversal, searching, and manipulation.
- **Tree Visualization**: A class containing functions for visualizing tree structures.

.. Submodules
.. ----------


AlgoTree.flattree module
------------------------

A module for working with flat tree structures where nodes are represented as key-value pairs in a dictionary.
Encapsulated in a class `FlatTree`. 

.. automodule:: AlgoTree.flattree
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.flattree\_node module
------------------------------

A module for representing nodes in a flat tree structure. Encapsulated in
a class `FlatTreeNode`. Provides a complete implementation of the node-centric API.
May be used as a reference implementation for custom tree structures.

.. automodule:: AlgoTree.flattree_node
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.tree\_converter module
-------------------------------

A module containing utilities for converting between different tree representations.
Encapsulated in a class `TreeConverter`. It only depends on the node-centric API and
does not require any specific tree structure.

.. automodule:: AlgoTree.tree_converter
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.tree\_viz module
-------------------------

A module containing functions for visualizing tree structures.
Encapsulated in a class `TreeViz`. It only depends on the node-centric API and
does not require any specific tree structure.

.. automodule:: AlgoTree.tree_viz
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.treenode module
------------------------

A module for representing recursive tree structures. Encapsulated in a class `TreeNode`.
Provides a complete implementation of the node-centric API. May be used as a reference
implementation for custom tree structures. It is an alternative to the flat tree structure.
`FlatTreeNode`, and relatively simpler, but it is a recursive structure and thus may not be
suitable for very deep trees.

.. automodule:: AlgoTree.treenode
   :members:
   :undoc-members:
   :show-inheritance:

AlgoTree.utils module
---------------------

A module containing free-standing utility functions for common tree operations
such as traversal, searching, and manipulation. They only depend on the
node-centric API and do not require any specific tree structure.

.. automodule:: AlgoTree.utils
   :members:
   :undoc-members:
   :show-inheritance:

.. Module contents
.. ---------------

.. .. automodule:: AlgoTree
..    :members:
..    :undoc-members:
..    :show-inheritance:
