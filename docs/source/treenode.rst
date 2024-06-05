TreeNode
========

The `TreeNode` class represents a node in a tree structure. It is a dictionary-based recursive data structure where each node can have an arbitrary number of children. The tree structure is maintained using the `children` attribute of each node.

TreeNode Structure
------------------

Each node is a `TreeNode` object, and child nodes are stored in the parent node as a list under the `children` key.

Example Structure:

.. code-block:: json

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
    }

Where:

- `name` (optional) is the name of the node.
- `value` (optional) is the payload of the node.
- `children` is a list of child nodes, each of which is a `TreeNode` object.

Attributes and Methods
----------------------

Initialization
~~~~~~~~~~~~~~

Each `TreeNode` can be initialized with an optional parent, name, and additional key-value pairs.

.. code-block:: python

    def __init__(self, *args, parent: Optional['TreeNode'] = None, name: Optional[str] = None, **kwargs):
        # Initialization code here

Properties
~~~~~~~~~~

- `name`: Returns the name of the node.
- `children`: Returns the list of children of the node.
- `payload`: Returns the data stored in the node (excluding children).

Methods
~~~~~~~

- `node(name: str) -> 'TreeNode'`: Retrieves the node with the given name.
- `add_child(name: Optional[str] = None, *args, **kwargs) -> 'TreeNode'`: Adds a child node to the tree.
- `root`: Returns the root of the tree.

Tree API
--------

The `TreeNode` class also provides a tree API that allows manipulation of the tree structure. The underlying dictionary can be directly modified, and the tree API serves as a convenience layer on top of it.

Example Usage
-------------

.. code-block:: python

    root = TreeNode(name='root', value='root_value')
    child1 = root.add_child(name='child1', value='child1_value')
    child1_1 = child1.add_child(name='child1_1', value='child1_1_value')
    child2 = root.add_child(name='child2', value='child2_value')
    child2_1 = child2.add_child(name='child2_1', value='child2_1_value')

    print(root.node('child1').value)  # Output: 'child1_value'
    print(child1_1.root.name)         # Output: 'root'
