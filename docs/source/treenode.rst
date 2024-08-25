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
