TreeNode
========

The `TreeNode` class represents a node in a tree structure. It is a dictionary-based recursive data structure where each node can have an arbitrary number of children. The tree structure is maintained using the `children` attribute of each node.

TreeNode Structure
------------------

Each node is a `TreeNode` object, and child nodes are stored in the parent node as a list under the `children` key.

Example Structure:

.. code-block:: json

    {
      "__name__": "root",
      "value": "root_value",
      "children": [
        {
          "__name__": "child1",
          "value": "child1_value",
          "children": [
            {
              "__name__": "child1_1",
              "value": "child1_1_value"
            }
          ]
        },
        {
          "__name__": "child2",
          "value": "child2_value",
          "children": [
            {
              "__name__": "child2_1",
              "value": "child2_1_value"
            }
          ]
        }
      ]
    }

Where:

- `__name__` (optional) is a key that maps to the name of the node. If not
  provided, the name defaults to a hash of the node's value.
- `children` is a list of child nodes, each of which is a `TreeNode(dict)` object.
- Other key-value pairs can be stored in the node as needed, which in total
  form the `payload` of the node, which can be accessed using the `payload` property.

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

    other = TreeNode(name="other", value="other_value", parent=child1_1)
    TreeNode(name="other2", value="other2_value", parent=other)

    print(root.node('child1').value)  # Output: 'child1_value'
    print(child1_1.root.name)         # Output: 'root'
