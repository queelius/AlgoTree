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

