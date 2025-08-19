API Reference
=============

This is the complete API reference for AlgoTree v1.0+.

Core Classes
-----------

Node
^^^^

.. autoclass:: AlgoTree.Node
   :members:
   :undoc-members:
   :show-inheritance:

.. code-block:: python

   from AlgoTree import Node
   
   # Create nodes
   root = Node("root", type="container")
   child = root.add_child("child", value=42)
   
   # Access properties
   print(root.name)        # "root"
   print(root.payload)     # {"type": "container"}
   print(root.children)    # [child]
   print(root.is_root)     # True
   print(child.parent)     # root
   print(child.level)      # 1

TreeBuilder
^^^^^^^^^^^

.. autoclass:: AlgoTree.TreeBuilder
   :members:
   :undoc-members:
   :show-inheritance:

.. code-block:: python

   from AlgoTree import TreeBuilder
   
   tree = (TreeBuilder()
       .root("app")
       .child("config", debug=True)
       .sibling("database", host="localhost")
       .up()
       .child("modules")
           .child("auth")
           .sibling("api")
       .build())

FluentNode
^^^^^^^^^^

.. autoclass:: AlgoTree.FluentNode
   :members:
   :undoc-members:
   :show-inheritance:

.. code-block:: python

   from AlgoTree import FluentNode
   
   fluent = FluentNode(tree)
   
   # Chain operations
   (fluent
       .filter(lambda n: n.payload.get("enabled"))
       .map(lambda n: {"processed": True})
       .each(lambda n: print(n.name)))

Pattern Matching
---------------

Pattern
^^^^^^^

.. autoclass:: AlgoTree.Pattern
   :members:
   :undoc-members:
   :show-inheritance:

PatternMatcher
^^^^^^^^^^^^^^

.. autoclass:: AlgoTree.PatternMatcher
   :members:
   :undoc-members:
   :show-inheritance:

Pattern Functions
^^^^^^^^^^^^^^^^

.. autofunction:: AlgoTree.pattern_match
.. autofunction:: AlgoTree.dotmatch
.. autofunction:: AlgoTree.dotpluck
.. autofunction:: AlgoTree.dotexists
.. autofunction:: AlgoTree.dotcount
.. autofunction:: AlgoTree.dotfilter

Closed Transformations (Tree → Tree)
------------------------------------

.. autofunction:: AlgoTree.dotmod
.. autofunction:: AlgoTree.dotmap
.. autofunction:: AlgoTree.dotprune
.. autofunction:: AlgoTree.dotmerge
.. autofunction:: AlgoTree.dotgraft
.. autofunction:: AlgoTree.dotsplit
.. autofunction:: AlgoTree.dotflatten
.. autofunction:: AlgoTree.dotreduce
.. autofunction:: AlgoTree.dotannotate
.. autofunction:: AlgoTree.dotvalidate
.. autofunction:: AlgoTree.dotnormalize

Open Transformations (Tree → Any)
---------------------------------

.. autofunction:: AlgoTree.dotpipe
.. autofunction:: AlgoTree.to_dict
.. autofunction:: AlgoTree.to_list
.. autofunction:: AlgoTree.to_paths
.. autofunction:: AlgoTree.to_adjacency_list
.. autofunction:: AlgoTree.to_edge_list
.. autofunction:: AlgoTree.to_nested_lists
.. autofunction:: AlgoTree.to_table
.. autofunction:: AlgoTree.dotextract
.. autofunction:: AlgoTree.dotcollect
.. autofunction:: AlgoTree.dotgroup
.. autofunction:: AlgoTree.dotpartition
.. autofunction:: AlgoTree.dotproject
.. autofunction:: AlgoTree.to_graphviz_data
.. autofunction:: AlgoTree.to_json_schema

Tree DSL Parsing
---------------

.. autofunction:: AlgoTree.parse_tree

.. autoclass:: AlgoTree.TreeDSL
   :members:
   :undoc-members:
   :show-inheritance:

Export Functions
---------------

.. autoclass:: AlgoTree.TreeExporter
   :members:
   :undoc-members:
   :show-inheritance:

.. autofunction:: AlgoTree.export_tree
.. autofunction:: AlgoTree.save_tree

Visualization
------------

.. autofunction:: AlgoTree.pretty_tree

.. autoclass:: AlgoTree.PrettyTree
   :members:
   :undoc-members:
   :show-inheritance: