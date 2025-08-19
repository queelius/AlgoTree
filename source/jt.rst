jt Command-Line Tool
====================

The ``jt`` tool is a powerful command-line utility for manipulating tree structures.
It supports pattern matching, transformations, and multiple export formats.
Version 1.0 has been completely rewritten with the modern AlgoTree API.

Installation
------------

The ``jt`` tool is automatically installed with AlgoTree:

.. code-block:: bash

   pip install AlgoTree
   jt --version  # Should show 1.0.0

Basic Usage
-----------

.. code-block:: bash

   # Read from file
   jt tree.json
   
   # Read from stdin
   cat tree.json | jt
   
   # Pretty print
   jt tree.json --pretty
   
   # Get statistics
   jt tree.json --stats

Input Formats
-------------

``jt`` can parse multiple input formats:

JSON Format
^^^^^^^^^^^

.. code-block:: bash

   echo '{"name": "root", "children": [{"name": "child"}]}' | jt

DSL Format (Indent-based)
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   echo "root
     child1
     child2" | jt --input-format dsl

DSL Format (Visual)
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   cat << EOF | jt --input-format dsl
   root
   ├── child1
   └── child2
   EOF

DSL Format (S-expression)
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   echo "(root (child1) (child2))" | jt --input-format dsl

Output Formats
--------------

JSON Output (default)
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   jt tree.json  # Default is JSON
   jt tree.json --output json --indent 4  # Custom indent

Pretty Tree Output
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   jt tree.json --pretty
   # Or
   jt tree.json --output pretty

DSL Output
^^^^^^^^^^

.. code-block:: bash

   # Indent format (default)
   jt tree.json --output dsl
   
   # Visual format
   jt tree.json --output dsl --dsl-format visual
   
   # S-expression format
   jt tree.json --output dsl --dsl-format sexpr

Filtering and Queries
---------------------

Filter by Level
^^^^^^^^^^^^^^^

.. code-block:: bash

   # Nodes deeper than level 2
   jt tree.json --filter "level > 2"
   
   # Nodes at level 1 or 0
   jt tree.json --filter "level < 2"

Filter by Name
^^^^^^^^^^^^^^

.. code-block:: bash

   # Nodes containing "test" in name
   jt tree.json --filter "name contains test"
   
   # Nodes with specific attribute
   jt tree.json --filter "type = 'folder'"

Custom Filter Expressions
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Lambda expressions
   jt tree.json --filter "n.payload.get('size', 0) > 100"

Tree Navigation
---------------

Get Specific Node
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   jt tree.json --get node_name

Children and Parents
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Get children of a node
   jt tree.json --children node_name
   
   # Get parent of a node
   jt tree.json --parent node_name
   
   # Get siblings
   jt tree.json --siblings node_name

Ancestors and Descendants
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # All ancestors up to root
   jt tree.json --ancestors node_name
   
   # All descendants (subtree)
   jt tree.json --descendants node_name
   
   # Path from root to node
   jt tree.json --path node_name

Tree Transformations
--------------------

Map Operations
^^^^^^^^^^^^^^^

.. code-block:: bash

   # Double all size values
   jt tree.json --map "{'size': n.payload.get('size', 0) * 2}"
   
   # Add computed field
   jt tree.json --map "{'depth': n.level}"

Prune Operations
^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Remove leaf nodes
   jt tree.json --prune "n.is_leaf"
   
   # Remove nodes with size < 10
   jt tree.json --prune "n.payload.get('size', 0) < 10"

Tree Analysis
-------------

Basic Statistics
^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Tree size (node count)
   jt tree.json --size
   
   # Tree height
   jt tree.json --height
   
   # All statistics
   jt tree.json --stats

Leaf Nodes
^^^^^^^^^^

.. code-block:: bash

   # List all leaf nodes
   jt tree.json --leaves

Format Conversion
-----------------

JSON to DSL
^^^^^^^^^^^

.. code-block:: bash

   # To indent format
   jt tree.json --output dsl
   
   # To visual format
   jt tree.json --output dsl --dsl-format visual

DSL to JSON
^^^^^^^^^^^

.. code-block:: bash

   cat tree.dsl | jt --input-format dsl --output json

Pretty Print Any Format
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Pretty print JSON
   jt tree.json --pretty
   
   # Pretty print DSL
   cat tree.dsl | jt --input-format dsl --pretty

Advanced Examples
-----------------

Pipeline Processing
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Filter, transform, and output
   jt data.json \
     --filter "level > 1" \
     --map "{'value': n.payload.get('value', 0) * 2}" \
     --output pretty

Complex Queries
^^^^^^^^^^^^^^^

.. code-block:: bash

   # Find all nodes with specific properties
   jt org.json --filter "n.payload.get('dept') == 'Engineering' and n.level > 2"

Tree Building from Multiple Sources
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Combine multiple trees
   (echo '{"name": "root", "children": ['; \
    jt tree1.json --get subtree1; echo ','; \
    jt tree2.json --get subtree2; \
    echo ']}') | jt --pretty

Comparison with v0.8
--------------------

The v1.0 ``jt`` tool has been completely rewritten with:

- **New features**: DSL support, fluent operations, better filtering
- **Better performance**: Uses modern Node class internally
- **Cleaner output**: Improved formatting and error messages
- **More formats**: Visual tree, S-expressions, multiple DSL styles
- **Chainable operations**: Filter, map, and prune in one command

Migration from v0.8
^^^^^^^^^^^^^^^^^^^

Most v0.8 commands still work, but some have been renamed:

- ``--subtree`` → ``--descendants``
- ``--node-stats`` → ``--stats``
- ``--find-path`` → ``--path``

Tips and Tricks
---------------

1. **Use stdin for pipelines**:
   
   .. code-block:: bash
   
      curl -s api.example.com/tree | jt --pretty

2. **Combine with jq for JSON processing**:
   
   .. code-block:: bash
   
      jt tree.json | jq '.children[0]'

3. **Save common filters as aliases**:
   
   .. code-block:: bash
   
      alias jt-leaves='jt --leaves'
      alias jt-deep='jt --filter "level > 2"'

4. **Use for directory trees**:
   
   .. code-block:: bash
   
      find . -type d | python -c "..." | jt --pretty

See Also
--------

- :doc:`fluent_api` - Full API documentation
- :doc:`tutorial` - Step-by-step tutorials
- `GitHub Examples <https://github.com/queelius/AlgoTree/tree/main/examples>`_