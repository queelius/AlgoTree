AlgoTree
========

.. image:: https://img.shields.io/pypi/v/AlgoTree.svg
   :target: https://pypi.org/project/AlgoTree/

.. image:: https://img.shields.io/pypi/l/AlgoTree.svg
   :target: https://pypi.org/project/AlgoTree/

``AlgoTree`` is a powerful Python library for working with tree structures, featuring a modern 
fluent API, advanced pattern matching, and comprehensive tree transformations inspired by dotsuite.

⚠️ **BREAKING CHANGES in v1.0.0** ⚠️
--------------------------------------

**Version 1.0.0 introduces a completely new API that is NOT backward compatible.**

For the old API, install: ``pip install "AlgoTree<1.0.0"``

Key Features
-----------

- **Modern Fluent API**: Build and manipulate trees with intuitive method chaining
- **Pattern Matching**: Advanced dot notation paths with wildcards and filters
- **Tree Transformations**: Both closed (tree→tree) and open (tree→any) transformations
- **Multiple DSL Formats**: Parse trees from visual, indent, or S-expression notation
- **Export Formats**: GraphViz, Mermaid, JSON, XML, YAML, HTML, and more
- **Command-Line Tool**: ``jt`` for tree manipulation from the shell

Installation
-----------

.. code-block:: shell

   pip install AlgoTree

Quick Start
----------

Building Trees
^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import TreeBuilder, Node, parse_tree
   
   # Method 1: Fluent API
   tree = (TreeBuilder()
       .root("app", version="1.0")
       .child("config", debug=True)
       .sibling("database", host="localhost")
       .sibling("modules")
           .child("auth", enabled=True)
           .sibling("api", enabled=False)
       .build())
   
   # Method 2: Node API
   root = Node("app", version="1.0")
   config = root.add_child("config", debug=True)
   db = root.add_child("database", host="localhost")
   
   # Method 3: Parse from DSL
   tree = parse_tree("""
   app
   ├── config
   ├── database
   └── modules
       ├── auth
       └── api
   """)

Pattern Matching
^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import dotmatch, dotfilter, dotexists
   
   # Find nodes by path (with escaped dots for literal dots)
   dotmatch(tree, "app.config")           # Exact path
   dotmatch(tree, "files.report\.pdf")    # Node named "report.pdf"
   dotmatch(tree, "app.*.settings")       # Wildcard
   dotmatch(tree, "app.**")               # All descendants
   
   # Filter by attributes
   dotmatch(tree, "**[type=file]")        # Has type="file"
   dotmatch(tree, "**[size]")             # Has size attribute
   dotmatch(tree, "**[?(@.size > 1000)]") # Size > 1000
   
   # Advanced filtering
   enabled_modules = dotfilter(tree, "@.enabled == True")
   large_files = dotfilter(tree, "@.type == 'file' and @.size > 1000000")

Tree Transformations
^^^^^^^^^^^^^^^^^^^

**Closed Transformations (Tree → Tree)**

.. code-block:: python

   from AlgoTree import dotmod, dotmap, dotprune, dotannotate
   
   # Modify specific nodes
   tree = dotmod(tree, {
       "app.config": {"debug": False, "env": "production"},
       "app.cache": "redis_cache"  # Rename node
   })
   
   # Map function over nodes
   tree = dotmap(tree, lambda n: {"processed": True})
   
   # Add annotations
   tree = dotannotate(tree,
                     lambda n: {"level": n.level, "path": n.get_path()})
   
   # Prune nodes
   tree = dotprune(tree, lambda n: n.payload.get("deprecated"))

**Open Transformations (Tree → Any Structure)**

.. code-block:: python

   from AlgoTree import dotpipe, to_dict, to_paths, dotextract
   
   # Pipeline transformations
   result = dotpipe(tree,
       ("**[type=file]", lambda n: n.payload["size"]),
       sum  # Total size of all files
   )
   
   # Convert to different formats
   data = to_dict(tree)                    # Nested dictionary
   paths = to_paths(tree)                  # ["app", "app.config", ...]
   table = to_table(tree)                  # For DataFrames
   
   # Extract and group data
   by_type = dotgroup(tree, "type")        # Group nodes by type
   sizes = dotextract(tree, lambda n: n.payload.get("size"))

Export and Visualization
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import export_tree, save_tree, pretty_tree
   
   # Pretty print
   print(pretty_tree(tree))
   
   # Export to various formats
   json_str = export_tree(tree, "json")
   dot_graph = export_tree(tree, "graphviz")
   mermaid = export_tree(tree, "mermaid")
   
   # Save to file (format auto-detected)
   save_tree(tree, "output.json")
   save_tree(tree, "output.dot")
   save_tree(tree, "output.html")

Command-Line Tool
^^^^^^^^^^^^^^^^

The ``jt`` tool provides command-line access to AlgoTree functionality:

.. code-block:: shell

   # Parse and display tree
   echo '{"name": "root", "children": [...]}' | jt --output-format visual
   
   # Query with dot notation
   jt data.json --query "app.config"
   
   # Filter nodes
   jt data.json --filter "@.type == 'file' and @.size > 1000"
   
   # Transform tree
   jt data.json --map "@.size * 2" --output-format json
   
   # Export to GraphViz
   jt data.json --output-format dot | dot -Tpng > tree.png

Advanced Features
----------------

Dot Notation with Escaping
^^^^^^^^^^^^^^^^^^^^^^^^^^

AlgoTree uses dot notation for paths, with ``\.`` to escape literal dots:

.. code-block:: python

   # Files with dots in names
   dotmatch(tree, "files.report\.pdf")     # Matches "report.pdf" node
   dotmatch(tree, "files.*\.txt")          # All .txt files
   dotmatch(tree, "data\.backup.2024")     # Node named "data.backup"

Tree DSL Formats
^^^^^^^^^^^^^^^

.. code-block:: python

   # Visual format
   tree = parse_tree("""
   root
   ├── branch1
   │   └── leaf1
   └── branch2
   """)
   
   # Indent format
   tree = parse_tree("""
   root
     branch1
       leaf1
     branch2
   """, format="indent")
   
   # S-expression format
   tree = parse_tree("""
   (root
     (branch1 leaf1)
     branch2)
   """, format="sexpr")

Custom Pattern Predicates
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import Pattern, pattern_match
   
   # Custom predicate
   pattern = Pattern(
       predicate=lambda n: n.level == 2 and len(n.children) > 3
   )
   matches = pattern_match(tree, pattern)
   
   # Regex patterns
   dotmatch(tree, "app.~test_.*")  # Regex matching
   
   # Fuzzy matching
   dotmatch(tree, "app.%cofig:0.8")  # Fuzzy match with threshold

Documentation
------------

Full documentation available at: https://algotree.readthedocs.io

- `Getting Started <https://algotree.readthedocs.io/en/latest/introduction.html>`_
- `Fluent API Guide <https://algotree.readthedocs.io/en/latest/fluent_api.html>`_
- `Pattern Matching <https://algotree.readthedocs.io/en/latest/pattern_matching.html>`_
- `Transformations <https://algotree.readthedocs.io/en/latest/transformations.html>`_
- `Cookbook <https://algotree.readthedocs.io/en/latest/cookbook.html>`_
- `API Reference <https://algotree.readthedocs.io/en/latest/api_reference.html>`_

Contributing
-----------

Contributions welcome! Please read our `Contributing Guide <CONTRIBUTING.md>`_ first.

License
------

MIT License - see `LICENSE <LICENSE>`_ file for details.

Credits
------

Tree transformations inspired by `dotsuite <https://github.com/queelius/dotsuite>`_'s 
three pillars: Depth (addressing), Truth (validation), and Shape (transformation).