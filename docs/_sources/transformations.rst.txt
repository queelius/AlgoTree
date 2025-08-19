Tree Transformations
====================

AlgoTree provides two families of transformation functions inspired by dotsuite's Shape pillar:

- **Closed Transformations (dotmod family)**: Tree → Tree transformations that preserve structure
- **Open Transformations (dotpipe family)**: Tree → Any transformations that reshape to any structure

Dot Notation and Escaping
------------------------

All transformation functions use dot notation for path navigation:

- Dots (``.``) separate path components
- Use ``\.`` to escape literal dots in node names
- Wildcards: ``*`` matches any single node, ``**`` matches any subtree
- Attributes: ``[key=value]`` or ``[key]`` to check existence

.. code-block:: python

   # Match nodes with dots in names
   dotmatch(tree, "files.doc1\.txt")  # Matches node named "doc1.txt"
   
   # Match all .txt files
   dotmatch(tree, "files.*\.txt")     # Wildcard with escaped dot
   
   # Match nodes with attributes
   dotmatch(tree, "**[type=file]")    # All nodes with type="file"
   dotmatch(tree, "**[size]")         # All nodes that have a size attribute

Closed Transformations (dotmod family)
--------------------------------------

These functions transform trees while preserving their tree structure.

dotmod
^^^^^^

Apply transformations to specific nodes using dot paths.

.. code-block:: python

   from AlgoTree import dotmod
   
   # Update node payloads
   tree = dotmod(tree, {
       "app.config": {"debug": False, "port": 9000},
       "app.database": {"host": "prod.db.com"}
   })
   
   # Rename nodes
   tree = dotmod(tree, {"app.cache": "redis_cache"})
   
   # Apply functions
   tree = dotmod(tree, {
       "app.config": lambda n: {"port": n.payload.get("port", 0) * 2}
   })
   
   # Clear payload
   tree = dotmod(tree, {"app.temp": None})

dotmap
^^^^^^

Map transformations over nodes matching a pattern.

.. code-block:: python

   from AlgoTree import dotmap
   
   # Transform all nodes
   tree = dotmap(tree, lambda n: {"processed": True})
   
   # Transform specific fields
   tree = dotmap(tree, {
       "size": lambda v: v * 1024,  # Convert to bytes
       "name": lambda v: v.upper()
   })
   
   # Apply to specific pattern
   tree = dotmap(tree, 
                lambda n: {"validated": True},
                dot_path="app.modules.*")

dotprune
^^^^^^^^

Remove nodes from tree based on condition.

.. code-block:: python

   from AlgoTree import dotprune
   
   # Remove by pattern
   tree = dotprune(tree, "**.test_*")
   
   # Remove by predicate
   tree = dotprune(tree, lambda n: n.payload.get("deprecated", False))
   
   # Keep structure but clear nodes
   tree = dotprune(tree, "**.temp", keep_structure=True)

dotmerge
^^^^^^^^

Merge two trees with various strategies.

.. code-block:: python

   from AlgoTree import dotmerge
   
   # Overlay (tree2 overrides tree1)
   merged = dotmerge(tree1, tree2, "overlay")
   
   # Underlay (tree1 takes precedence)
   merged = dotmerge(tree1, tree2, "underlay")
   
   # Combine (merge arrays and dicts)
   merged = dotmerge(tree1, tree2, "combine")
   
   # Custom resolution
   def resolver(node1, node2):
       # Custom merge logic
       return Node(node2.name, **{**node1.payload, **node2.payload})
   
   merged = dotmerge(tree1, tree2, "custom", conflict_resolver=resolver)

dotannotate
^^^^^^^^^^^

Add metadata annotations to nodes.

.. code-block:: python

   from AlgoTree import dotannotate
   
   # Add computed annotations
   tree = dotannotate(tree,
                     lambda n: {
                         "depth": n.level,
                         "path": ".".join(p.name for p in n.get_path()),
                         "has_children": len(n.children) > 0
                     },
                     annotation_key="_meta")
   
   # Add static annotations to specific nodes
   tree = dotannotate(tree,
                     {"reviewed": True, "version": "1.0"},
                     dot_path="**.critical_*")

dotvalidate
^^^^^^^^^^^

Validate nodes against constraints.

.. code-block:: python

   from AlgoTree import dotvalidate
   
   # Validate with predicate (raises on failure)
   dotvalidate(tree,
              lambda n: n.payload.get("size", 0) < 1000000,
              dot_path="**[type=file]")
   
   # Get invalid nodes instead of raising
   invalid = dotvalidate(tree,
                        lambda n: len(n.name) <= 255,
                        raise_on_invalid=False)
   
   # Validate required attributes
   dotvalidate(tree,
              {"type": "module", "enabled": True},
              dot_path="app.modules.*")

Additional Closed Transformations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import (
       dotgraft,      # Graft subtree at specific points
       dotsplit,      # Split tree extracting subtrees
       dotflatten,    # Flatten to list of nodes
       dotreduce,     # Reduce tree to single value
       dotnormalize   # Normalize node names
   )
   
   # Graft a subtree
   tree = dotgraft(tree, "app.modules", new_module_tree)
   
   # Split tree
   tree, extracted = dotsplit(tree, "app.deprecated")
   
   # Flatten tree
   all_nodes = dotflatten(tree, "**[type=file]")
   
   # Reduce to aggregate value
   total_size = dotreduce(tree,
                         lambda acc, n: acc + n.payload.get("size", 0),
                         initial=0)
   
   # Normalize names
   tree = dotnormalize(tree)  # my-node -> my_node

Open Transformations (dotpipe family)
-------------------------------------

These functions transform trees into arbitrary data structures.

dotpipe
^^^^^^^

The main pipeline function for chaining transformations.

.. code-block:: python

   from AlgoTree import dotpipe
   
   # Extract all names
   names = dotpipe(tree,
                  lambda t: [n.name for n in t.traverse_preorder()])
   
   # Multi-stage pipeline
   result = dotpipe(tree,
                   ("**[type=file]", lambda n: n.payload),  # Extract payloads
                   lambda payloads: [p["size"] for p in payloads],  # Get sizes
                   sum)  # Total size
   
   # Convert to different format
   json_data = dotpipe(tree, to_dict)

Conversion Functions
^^^^^^^^^^^^^^^^^^^

Convert trees to common data structures.

.. code-block:: python

   from AlgoTree import (
       to_dict,           # Nested dictionary
       to_list,           # Flat list
       to_paths,          # Path strings
       to_adjacency_list, # Graph adjacency list
       to_edge_list,      # Edge pairs
       to_nested_lists,   # S-expressions
       to_table          # Tabular/DataFrame format
   )
   
   # Convert to dictionary
   data = to_dict(tree)
   # {"name": "root", "children": [...], ...}
   
   # Get all paths
   paths = to_paths(tree)
   # ["root", "root.child1", "root.child2", ...]
   
   # With payloads
   path_data = to_paths(tree, include_payload=True)
   # {"root": {...}, "root.child1": {...}, ...}
   
   # For graph algorithms
   adj = to_adjacency_list(tree)
   # {"root": ["child1", "child2"], ...}
   
   edges = to_edge_list(tree)
   # [("root", "child1"), ("root", "child2"), ...]
   
   # For DataFrames
   rows = to_table(tree, columns=["type", "size"])
   # df = pd.DataFrame(rows)

Data Extraction
^^^^^^^^^^^^^^^

Extract and collect data from trees.

.. code-block:: python

   from AlgoTree import (
       dotextract,   # Extract with custom function
       dotcollect,   # Collect/aggregate data
       dotgroup,     # Group nodes by key
       dotpartition, # Split into two groups
       dotproject    # SQL-like projection
   )
   
   # Extract specific data
   sizes = dotextract(tree, 
                     lambda n: n.payload.get("size"),
                     dot_path="**[type=file]")
   
   # Collect statistics
   stats = dotcollect(tree,
                     lambda n, acc: {
                         "count": acc["count"] + 1,
                         "total": acc["total"] + n.payload.get("size", 0)
                     },
                     initial={"count": 0, "total": 0})
   
   # Group by attribute
   by_type = dotgroup(tree, "type")
   # {"file": [node1, node2], "dir": [node3], ...}
   
   # Partition nodes
   large, small = dotpartition(tree, 
                              lambda n: n.payload.get("size", 0) > 1000)
   
   # Project specific fields
   data = dotproject(tree, ["name", "size", "type"])
   # [{"name": "...", "size": ..., "type": "..."}, ...]

Specialized Conversions
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import to_graphviz_data, to_json_schema
   
   # For visualization
   viz_data = to_graphviz_data(tree)
   # {"nodes": [...], "edges": [...]}
   
   # Convert to JSON Schema
   schema = to_json_schema(tree)

In-Place vs Copy Operations
---------------------------

Most transformation functions support an ``in_place`` parameter:

.. code-block:: python

   # Create a copy (default)
   new_tree = dotmod(tree, {"app.config": {"debug": False}})
   # Original tree unchanged
   
   # Modify in place
   dotmod(tree, {"app.config": {"debug": False}}, in_place=True)
   # Original tree modified

Chaining Transformations
------------------------

Transformations can be chained for complex operations:

.. code-block:: python

   from AlgoTree import dotpipe, dotmod, dotprune, to_dict
   
   result = dotpipe(tree,
       # First normalize names
       lambda t: dotnormalize(t),
       # Remove deprecated nodes
       lambda t: dotprune(t, lambda n: n.payload.get("deprecated")),
       # Update configurations
       lambda t: dotmod(t, {"app.config": {"env": "production"}}),
       # Convert to dict
       to_dict
   )

Pattern Matching Reference
--------------------------

Patterns support various matching strategies:

- ``name`` - Exact name match
- ``*`` - Single wildcard
- ``**`` - Deep wildcard (any subtree)
- ``*.txt`` - Wildcard with suffix
- ``[attr=value]`` - Attribute match
- ``[attr]`` - Attribute existence
- ``~regex`` - Regex pattern
- ``%fuzzy`` - Fuzzy matching
- ``[?(@.size > 100)]`` - Predicate expressions
- ``[0]``, ``[1:3]`` - Array indexing/slicing

Examples:

.. code-block:: python

   # Various pattern examples
   dotmatch(tree, "app.config")           # Exact path
   dotmatch(tree, "app.*.settings")       # Wildcard
   dotmatch(tree, "app.**")               # All descendants
   dotmatch(tree, "**[type=file]")        # Attribute filter
   dotmatch(tree, "**[size]")             # Has attribute
   dotmatch(tree, "files.*\.txt")         # Escaped dot
   dotmatch(tree, "**[?(@.size > 1000)]") # Size predicate