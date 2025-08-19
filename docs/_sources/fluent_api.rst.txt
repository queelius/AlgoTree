AlgoTree Fluent API Guide
=========================

The new fluent API provides a modern, intuitive way to work with trees in Python. This guide covers the new features added to AlgoTree.

.. contents:: Table of Contents
   :local:
   :depth: 2

Modern Node Class
-----------------

The new ``Node`` class provides a clean, object-oriented approach to tree structures:

.. code-block:: python

   from AlgoTree import Node

   # Create nodes
   root = Node(name="root", value=100, type="folder")
   child1 = Node(name="child1", parent=root, value=50)
   child2 = root.add_child(name="child2", value=75)

   # Access properties
   print(root.is_root)        # True
   print(child1.level)        # 1
   print(child2.parent.name)  # "root"
   print(root.is_leaf)        # False

   # Traverse the tree
   for node in root.traverse_preorder():
       print(f"{node.name}: {node.payload}")

   # Find nodes
   high_value = root.find(lambda n: n.payload.get("value", 0) > 60)
   all_children = root.find_all(lambda n: n.level == 1)

Key Features
^^^^^^^^^^^^

- **Clean API**: ``node.parent`` instead of ``node['parent']``
- **Built-in traversal**: preorder, postorder, level-order
- **Rich properties**: ``is_root``, ``is_leaf``, ``level``, ``siblings``
- **Find operations**: ``find()`` and ``find_all()`` with predicates

TreeBuilder - Fluent Tree Construction
---------------------------------------

Build complex trees with intuitive method chaining:

.. code-block:: python

   from AlgoTree import TreeBuilder

   # Build a company org chart
   tree = (TreeBuilder()
       .root("TechCorp", employees=1000, founded=2010)
       .child("Engineering", head="Alice", size=450)
           .child("Frontend", lead="Bob", size=150)
               .child("React Team", size=50)
               .child("Vue Team", size=50)
               .child("Mobile Team", size=50)
               .up()
           .sibling("Backend", lead="Charlie", size=200)
               .child("API Team", size=100)
               .child("Database Team", size=100)
               .up()
           .sibling("DevOps", lead="Dana", size=100)
           .up(2)  # Go up 2 levels to Engineering's parent
       .sibling("Sales", head="Eve", size=300)
           .child("North America", size=150)
           .sibling("Europe", size=100)
           .sibling("Asia", size=50)
           .up()
       .sibling("HR", head="Frank", size=250)
       .build())

   # The tree is a regular Node object
   print(f"Company: {tree.name}")
   print(f"Total departments: {len(list(tree.traverse_preorder())) - 1}")

Navigation Methods
^^^^^^^^^^^^^^^^^^

- ``.child(name, **data)`` - Add child and move to it
- ``.sibling(name, **data)`` - Add sibling node
- ``.up(levels=1)`` - Move up by N levels
- ``.to_root()`` - Jump back to root
- ``.build()`` - Get the constructed tree

FluentNode - Chainable Operations
----------------------------------

Perform complex tree operations with method chaining:

.. code-block:: python

   from AlgoTree import FluentNode, Node

   # Create a sample file system tree
   root = Node(name="project", type="folder", size=0)
   src = root.add_child(name="src", type="folder", size=0)
   src.add_child(name="main.py", type="file", size=1024)
   src.add_child(name="utils.py", type="file", size=512)
   src.add_child(name="test.py", type="file", size=2048)
   docs = root.add_child(name="docs", type="folder", size=0)
   docs.add_child(name="README.md", type="file", size=4096)

   # Chain operations
   result = (FluentNode(root)
       .descendants()                           # Get all descendants
       .where(lambda n: n.payload.get("type") == "file")  # Filter files only
       .map(lambda n: {"size_kb": n.payload.get("size", 0) / 1024})  # Convert to KB
       .where(lambda n: n.payload.get("size_kb", 0) > 1)  # Files > 1KB
       .to_list())

   for node in result:
       print(f"{node.name}: {node.payload['size_kb']:.1f} KB")

   # More operations
   (FluentNode(root)
       .children()                              # Direct children only
       .sort(key=lambda n: n.name)             # Sort alphabetically
       .each(lambda n: print(f"- {n.name}")))  # Process each

   # Prune empty folders
   (FluentNode(root)
       .prune(lambda n: n.payload.get("type") == "folder" and n.is_leaf))

Available Operations
^^^^^^^^^^^^^^^^^^^^

- **Filtering**: ``.filter()``, ``.where()``, ``.leaves()``
- **Traversal**: ``.children()``, ``.descendants()``
- **Transformation**: ``.map()``, ``.sort()``, ``.prune()``
- **Execution**: ``.each()``, ``.to_list()``, ``.to_dict()``, ``.first()``, ``.count()``

Tree DSL - Multiple Format Support
-----------------------------------

Parse trees from various text formats:

Visual Format
^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import parse_tree

   # Unicode tree representation
   tree = parse_tree("""
   filesystem[type:root]
   ├── home[type:folder,owner:alice]
   │   ├── documents[type:folder]
   │   │   ├── report.pdf[size:2048]
   │   │   └── notes.txt[size:512]
   │   └── pictures[type:folder]
   │       └── vacation.jpg[size:4096]
   └── etc[type:folder,owner:root]
       └── config.ini[size:128]
   """)

   print(tree.name)  # "filesystem"
   print(tree.children[0].payload["owner"])  # "alice"

Indent Format (YAML-like)
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   tree = parse_tree("""
   company: {revenue: 10M, employees: 100}
     engineering: {head: Alice, size: 45}
       frontend: {lead: Bob, size: 20}
       backend: {lead: Charlie, size: 25}
     sales: {head: David, size: 30}
       domestic: {size: 20}
       international: {size: 10}
     hr: {head: Eve, size: 25}
   """, format='indent')

S-Expression Format
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   tree = parse_tree("""
   (company :revenue 10M :employees 100
     (engineering :head Alice :size 45
       (frontend :lead Bob :size 20)
       (backend :lead Charlie :size 25))
     (sales :head David :size 30
       (domestic :size 20)
       (international :size 10))
     (hr :head Eve :size 25))
   """, format='sexpr')

Auto-detection
^^^^^^^^^^^^^^

The parser automatically detects the format:

.. code-block:: python

   # Detects visual format from tree characters
   tree1 = parse_tree("root\n├── child1\n└── child2")

   # Detects S-expression from parentheses
   tree2 = parse_tree("(root (child1) (child2))")

   # Defaults to indent format
   tree3 = parse_tree("root\n  child1\n  child2")

Complete Examples
-----------------

Example 1: Building and Analyzing an Org Chart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import TreeBuilder, FluentNode

   # Build the organization
   org = (TreeBuilder()
       .root("GlobalTech", employees=5000)
       .child("Engineering", employees=2000)
           .child("Platform", employees=800)
           .sibling("Product", employees=700)
           .sibling("Infrastructure", employees=500)
           .up()
       .sibling("Sales", employees=1500)
           .child("Americas", employees=700)
           .sibling("EMEA", employees=500)
           .sibling("APAC", employees=300)
           .up()
       .sibling("Operations", employees=1500)
       .build())

   # Analyze the organization
   large_depts = (FluentNode(org)
       .descendants()
       .where(lambda n: n.payload.get("employees", 0) > 600)
       .to_list())

   print(f"Departments with >600 employees: {[n.name for n in large_depts]}")

   # Calculate total by region
   regions = (FluentNode(org)
       .find_all(lambda n: n.parent and n.parent.name == "Sales"))

   total = sum(r.payload.get("employees", 0) for r in regions)
   print(f"Total sales employees: {total}")

Example 2: File System Processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import parse_tree, FluentNode

   # Parse a file system structure
   fs = parse_tree("""
   project[type:dir]
   ├── src[type:dir]
   │   ├── main.py[type:file,lines:200]
   │   ├── utils.py[type:file,lines:150]
   │   └── tests[type:dir]
   │       ├── test_main.py[type:file,lines:100]
   │       └── test_utils.py[type:file,lines:80]
   ├── docs[type:dir]
   │   └── README.md[type:file,lines:50]
   └── setup.py[type:file,lines:30]
   """)

   # Find all Python files
   py_files = (FluentNode(fs)
       .descendants()
       .where(lambda n: n.name.endswith('.py'))
       .to_list())

   # Calculate total lines of code
   total_lines = sum(f.payload.get("lines", 0) for f in py_files)
   print(f"Total Python lines: {total_lines}")

   # Find test files
   test_files = [f for f in py_files if "test" in f.name]
   print(f"Test files: {[f.name for f in test_files]}")

Example 3: Data Pipeline
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import Node, FluentNode

   # Create a data processing pipeline tree
   pipeline = Node(name="pipeline", status="ready")
   extract = pipeline.add_child(name="extract", status="complete", duration=10)
   extract.add_child(name="read_db", status="complete", duration=5)
   extract.add_child(name="read_api", status="complete", duration=5)

   transform = pipeline.add_child(name="transform", status="running", duration=0)
   transform.add_child(name="clean", status="complete", duration=3)
   transform.add_child(name="normalize", status="running", duration=0)
   transform.add_child(name="aggregate", status="pending", duration=0)

   load = pipeline.add_child(name="load", status="pending", duration=0)
   load.add_child(name="validate", status="pending", duration=0)
   load.add_child(name="write_db", status="pending", duration=0)

   # Analyze pipeline status
   status_summary = {}
   for node in pipeline.traverse_preorder():
       status = node.payload.get("status", "unknown")
       status_summary[status] = status_summary.get(status, 0) + 1

   print("Pipeline Status:")
   for status, count in status_summary.items():
       print(f"  {status}: {count}")

   # Find bottlenecks (completed tasks with high duration)
   bottlenecks = (FluentNode(pipeline)
       .descendants()
       .where(lambda n: n.payload.get("status") == "complete")
       .where(lambda n: n.payload.get("duration", 0) >= 5)
       .to_list())

   print(f"\nBottlenecks (duration >= 5): {[n.name for n in bottlenecks]}")

Migration from Dict-based API
------------------------------

If you're currently using the dict-based FlatForest or TreeNode classes, here's how to migrate:

Old Way (Dict-based)
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import TreeNode

   node = TreeNode(name="root", data={"value": 100})
   child = TreeNode(name="child", parent=node, data={"value": 50})

New Way (Node class)
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import Node

   node = Node(name="root", value=100)
   child = node.add_child(name="child", value=50)

Compatibility
^^^^^^^^^^^^^

The new Node class provides ``to_dict()`` and ``from_dict()`` methods for JSON compatibility:

.. code-block:: python

   # Export to JSON-compatible dict
   data = tree.to_dict()

   # Import from dict
   tree = Node.from_dict(data)

Best Practices
--------------

1. **Use TreeBuilder for complex structures** - It's more readable than manual node creation
2. **Leverage FluentNode for data processing** - Chain operations instead of nested loops
3. **Choose the right DSL format** - Visual for documentation, indent for hand-writing, S-expr for generation
4. **Keep predicates simple** - Complex logic should be extracted to named functions
5. **Use meaningful node names** - They're your primary identifiers

Performance Considerations
--------------------------

- **Node class** is optimized for tree operations, not storage efficiency
- **FluentNode operations** create new wrappers but don't copy nodes
- **DSL parsing** is meant for small to medium trees (< 10,000 nodes)
- For very large trees, consider using FlatForest with careful memory management

Next Steps
----------

- See the :doc:`AlgoTree` for complete API documentation
- Check out the :doc:`tutorial` for more patterns and recipes
- Read about traditional APIs in :doc:`treenode` and :doc:`flat_forest`