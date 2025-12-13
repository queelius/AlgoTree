AlgoTree
========

.. image:: https://img.shields.io/pypi/v/AlgoTree.svg
   :target: https://pypi.org/project/AlgoTree/

.. image:: https://img.shields.io/pypi/l/AlgoTree.svg
   :target: https://pypi.org/project/AlgoTree/

.. image:: https://img.shields.io/badge/coverage-86%25-brightgreen.svg
   :target: https://github.com/queelius/AlgoTree

A powerful, immutable-by-default tree manipulation library for Python with functional programming patterns, composable transformations, and advanced pattern matching.

⚠️ **BREAKING CHANGES in v2.0.0** ⚠️
--------------------------------------

**Version 2.0.0 is a complete redesign with NO backward compatibility.**

- **Immutable-by-default API** - All operations return new trees
- **Functional programming style** - map, filter, reduce, fold operations
- **Composable transformations** - Selectors and transformers compose with operators
- **Type-safe with full type hints** - Complete IDE support
- **86% test coverage** - 197 passing tests across comprehensive test suite

**Upgrading from v1.x:**

The v1.x API has been completely removed. See the `Migration Guide <#migration-from-v1x>`_ below.

**If you need the old API:**

.. code-block:: shell

   pip install "AlgoTree<2.0.0"

Introduction
------------

AlgoTree v2.0 provides a modern, functional approach to working with tree structures in Python. Built on immutable-by-default principles, it offers:

- **Immutable trees** - Safe, predictable transformations without side effects
- **Functional operations** - map, filter, reduce, fold, and more
- **Pattern matching** - Powerful selectors with wildcards and composition
- **Composable transformers** - Build complex pipelines with simple operators
- **Multiple construction styles** - Fluent builders, DSL parsing, factory methods
- **Rich export formats** - JSON, GraphViz, Mermaid, paths, and more
- **Interactive shell** - Terminal-based exploration and quick operations

**For Scripting & Automation:** Use the fluent Python API (recommended)

**For Interactive Exploration:** Use the shell/CLI tools

Installation
------------

.. code-block:: shell

   pip install AlgoTree

Quick Start
-----------

Building Trees
^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import Node, node, Tree, TreeBuilder

   # Simple construction with Node
   tree = Node("root",
       Node("child1", attrs={"value": 1}),
       Node("child2", attrs={"value": 2})
   )

   # Convenience function (auto-converts strings)
   tree = node("root",
       node("child1", value=1),
       "child2",  # Strings auto-convert to nodes
       node("child3",
           "grandchild1",
           "grandchild2"
       )
   )

   # Fluent builder API
   tree = (TreeBuilder("root", type="container")
       .child("src")
           .child("main.py", type="file", size=1024)
           .child("utils.py", type="file", size=512)
           .up()
       .child("docs")
           .child("README.md", type="file")
       .build())

Immutable Transformations
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # All operations return new trees
   tree2 = tree.with_name("new_root")
   tree3 = tree.with_attrs(status="active")
   tree4 = tree.with_child(Node("new_child"))

   # Functional tree-wide operations
   doubled = tree.map(lambda n: n.with_attrs(
       value=n.get("value", 0) * 2
   ))

   filtered = tree.filter(lambda n: n.get("value", 0) > 5)
   nodes = tree.find_all(lambda n: n.is_leaf)

Composable Selectors
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import name, attrs, leaf, type_

   # Pattern matching with wildcards
   selector = name("*.txt")

   # Attribute matching with predicates
   selector = attrs(size=lambda s: s > 1000)

   # Logical composition with operators
   selector = type_("file") & ~leaf()

   # Structural selectors
   selector = type_("file").child_of(name("src"))
   selector = leaf().at_depth(2)

   # Use selectors with trees
   matching_nodes = list(selector.select(tree))

Composable Transformers
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import map_, filter_, prune, normalize, extract

   # Build transformation pipelines with >> operator
   pipeline = (
       map_(lambda n: {"processed": True}) >>
       filter_(lambda n: n.get("active")) >>
       normalize(sort_children=True) >>
       extract(lambda n: n.name)
   )

   # Apply to tree
   result = pipeline(tree)

   # Or use Tree's fluent API
   result = (Tree(tree)
       .map(lambda n: {"processed": True})
       .filter(lambda n: n.get("active"))
       .prune(lambda n: n.name == "temp"))

DSL Parsing
^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import parse_tree

   # Visual ASCII format
   tree = parse_tree("""
   root
   ├── child1
   │   ├── grandchild1
   │   └── grandchild2
   └── child2
   """)

   # Indented format
   tree = parse_tree("""
   root
     child1
       grandchild1
       grandchild2
     child2
   """)

   # S-expression format
   tree = parse_tree("(root (child1 (grandchild1) (grandchild2)) (child2))")

Export & Serialization
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import export_tree, save, load

   # Export to various formats
   json_str = export_tree(tree, "json")
   dot_str = export_tree(tree, "graphviz")
   mermaid_str = export_tree(tree, "mermaid")

   # File operations
   save(tree, "tree.json")
   loaded = load("tree.json")

   # Export to dictionary
   data = Tree(tree).to_dict()

   # Export to paths
   paths = Tree(tree).to_paths()  # ['root/child1', 'root/child2', ...]

Core API
--------

Node (Immutable)
^^^^^^^^^^^^^^^^

The ``Node`` class is the foundation of AlgoTree v2.0. It's immutable by default, making trees safe to share and transform.

**Properties:**

- ``name`` - Node name (immutable)
- ``attrs`` - Node attributes dictionary (returns copy)
- ``children`` - Tuple of child nodes (immutable)
- ``parent`` - Parent node (weak reference)
- ``is_root`` - True if node has no parent
- ``is_leaf`` - True if node has no children
- ``depth`` - Distance from root (root has depth 0)
- ``height`` - Height of subtree rooted at this node
- ``size`` - Total number of nodes in subtree
- ``path`` - Path from root as string (e.g., "root/child/grandchild")

**Immutable transformations:**

.. code-block:: python

   new_node = node.with_name("new_name")
   new_node = node.with_attrs(key="value")
   new_node = node.without_attrs("key1", "key2")
   new_node = node.with_child(Node("child"))
   new_node = node.with_children(Node("a"), Node("b"))
   new_node = node.without_child("child_name")
   new_node = node.map_children(lambda c: c.with_attrs(tagged=True))
   new_node = node.filter_children(lambda c: c.get("active"))

**Tree-wide transformations:**

.. code-block:: python

   new_tree = node.map(lambda n: n.with_attrs(processed=True))
   filtered = node.filter(lambda n: n.get("value") > 0)
   found = node.find(lambda n: n.name == "target")
   all_matches = node.find_all(lambda n: n.is_leaf)

**Iteration:**

.. code-block:: python

   for n in node.walk("preorder"):  # or "postorder", "levelorder"
       print(n.name)

   for descendant in node.descendants():
       print(descendant.name)

   for ancestor in node.ancestors():
       print(ancestor.name)

   for leaf in node.leaves():
       print(leaf.name)

Tree (Wrapper)
^^^^^^^^^^^^^^

The ``Tree`` class wraps a root node and provides a consistent fluent API.

**Factory methods:**

.. code-block:: python

   tree = Tree.from_dict({
       "name": "root",
       "value": 1,
       "children": [
           {"name": "child1", "value": 2},
           {"name": "child2", "value": 3}
       ]
   })

   tree = Tree.from_paths([
       "root/a/b",
       "root/a/c",
       "root/d"
   ])

**Functional operations:**

.. code-block:: python

   # Map over all nodes
   result = tree.map(lambda n: {"processed": True})

   # Filter nodes (preserves structure)
   result = tree.filter(lambda n: n.get("active"))

   # Reduce to single value
   total = tree.reduce(
       lambda acc, n: acc + n.get("value", 0),
       0
   )

   # Fold bottom-up
   result = tree.fold(
       lambda node, child_results: sum(child_results) + 1
   )

**Structure operations:**

.. code-block:: python

   pruned = tree.prune(lambda n: n.name == "temp")
   grafted = tree.graft(lambda n: n.is_leaf, Node("new_child"))
   flattened = tree.flatten(max_depth=2)

**Query operations:**

.. code-block:: python

   node = tree.find(lambda n: n.name == "target")
   nodes = tree.find_all(lambda n: n.is_leaf)
   exists = tree.exists(lambda n: n.get("error"))
   count = tree.count(lambda n: n.get("active"))

**Properties:**

- ``root`` - Root node
- ``size`` - Total number of nodes
- ``height`` - Height of tree
- ``leaves`` - List of all leaf nodes
- ``is_empty`` - True if tree is empty

Selectors
^^^^^^^^^

Selectors provide composable pattern matching for tree nodes.

**Basic selectors:**

.. code-block:: python

   from AlgoTree import name, attrs, type_, predicate, depth, leaf, root

   # Name matching with wildcards
   sel = name("*.txt")
   sel = name("file_*")

   # Attribute matching
   sel = attrs(type="file")
   sel = attrs(size=lambda s: s > 1000)  # With predicate
   sel = attrs(type="file", active=True)  # Multiple attrs

   # Type matching
   sel = type_("directory")

   # Custom predicate
   sel = predicate(lambda n: n.name.startswith("test_"))

   # Depth matching
   sel = depth(2)  # Nodes at depth 2

   # Leaf/root selectors
   sel = leaf()
   sel = root()

**Logical composition:**

.. code-block:: python

   # AND
   sel = name("*.py") & type_("file")

   # OR
   sel = name("*.py") | name("*.txt")

   # NOT
   sel = ~leaf()

   # XOR
   sel = type_("file") ^ leaf()

**Structural composition:**

.. code-block:: python

   # Child of
   sel = name("*.py").child_of(name("src"))

   # Parent of
   sel = type_("directory").parent_of(name("main.py"))

   # Descendant of
   sel = name("*.txt").descendant_of(name("docs"))

   # Ancestor of
   sel = type_("directory").ancestor_of(leaf())

   # Sibling of
   sel = name("config.json").sibling_of(name("main.py"))

   # At specific depth
   sel = type_("file").at_depth(3)

**Using selectors:**

.. code-block:: python

   # Select all matching nodes
   for node in selector.select(tree):
       print(node.name)

   # Get first match
   first = selector.first(tree)

   # Count matches
   count = selector.count(tree)

   # Check existence
   exists = selector.exists(tree)

Transformers
^^^^^^^^^^^^

Transformers provide composable tree transformations.

**Tree -> Tree transformers:**

.. code-block:: python

   from AlgoTree import map_, filter_, prune, graft, flatten, normalize, annotate

   # Map over nodes
   t = map_(lambda n: {"processed": True})
   t = map_(lambda n: n.with_attrs(value=n.get("value", 0) * 2))

   # Filter nodes
   t = filter_(lambda n: n.get("active"))
   t = filter_(name("*.txt"))  # Can use selectors

   # Prune (remove) nodes
   t = prune(lambda n: n.name == "temp")
   t = prune(name("test_*"))

   # Graft (add) subtrees
   t = graft(leaf(), Node("new_child"))

   # Flatten to depth
   t = flatten(max_depth=2)

   # Normalize (sort, deduplicate)
   t = normalize(sort_children=True, dedup=True)

   # Annotate (add metadata)
   t = annotate(lambda n: {"depth": n.depth, "size": n.size})

**Tree -> Any transformers (shapers):**

.. code-block:: python

   from AlgoTree import reduce_, fold, extract, to_dict, to_paths

   # Reduce to single value
   t = reduce_(lambda acc, n: acc + n.get("value", 0), initial=0)

   # Fold bottom-up
   t = fold(lambda node, child_results: sum(child_results) + 1)

   # Extract values
   t = extract(lambda n: n.name)

   # Convert to dictionary
   t = to_dict(children_key="children")

   # Convert to paths
   t = to_paths(to_leaves_only=True)

**Composition:**

.. code-block:: python

   # Sequential composition with >>
   pipeline = map_(fn1) >> filter_(pred) >> prune(sel)

   # Parallel composition with &
   both = map_(fn1) & annotate(fn2)

   # Conditional application
   conditional = map_(fn).when(lambda t: t.size > 10)

   # Repeated application
   repeated = normalize().repeat(3)

   # Debug intermediate results
   debug = pipeline.debug("after_filter")

Builders
^^^^^^^^

Builders provide fluent APIs for tree construction.

**TreeBuilder:**

.. code-block:: python

   from AlgoTree import TreeBuilder

   tree = (TreeBuilder("root", type="container")
       .attr(version="1.0")
       .child("src", type="directory")
           .child("main.py", type="file", size=1024)
           .child("utils.py", type="file", size=512)
           .up()
       .child("tests", type="directory")
           .child("test_main.py", type="file")
       .build())

**DSL-style functions:**

.. code-block:: python

   from AlgoTree import tree, branch, leaf

   my_tree = tree("root",
       tree("child1",
           leaf("grandchild1", value=1),
           leaf("grandchild2", value=2)
       ),
       tree("child2",
           leaf("grandchild3", value=3)
       )
   ).build()

**QuickBuilder (path-based):**

.. code-block:: python

   from AlgoTree import QuickBuilder

   tree = (QuickBuilder()
       .root("project")
       .add("src/main.py", type="file", size=1024)
       .add("src/utils.py", type="file", size=512)
       .add("tests/test_main.py", type="file")
       .add("docs/README.md", type="file")
       .build())

Examples
--------

File System Tree
^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import TreeBuilder, name, type_, export_tree

   # Build file system tree
   fs = (TreeBuilder("home")
       .child("user")
           .child("documents", type="dir")
               .child("report.pdf", type="file", size=1024)
               .child("notes.txt", type="file", size=256)
               .up()
           .child("code", type="dir")
               .child("main.py", type="file", size=512)
               .child("test.py", type="file", size=128)
               .up()
           .up()
       .build())

   # Find all Python files
   py_files = fs.find_all(name("*.py"))
   for f in py_files:
       print(f.path, f.get("size"))

   # Calculate total size of all files
   total_size = fs.reduce(
       lambda acc, n: acc + n.get("size", 0),
       0
   )
   print(f"Total size: {total_size} bytes")

   # Export to GraphViz
   dot = export_tree(fs, "graphviz")
   print(dot)

Organization Hierarchy
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import node, attrs, map_, normalize

   # Build organization tree
   company = node("TechCorp",
       node("Engineering",
           node("Frontend", team_size=10, budget=500000),
           node("Backend", team_size=15, budget=750000),
           node("DevOps", team_size=5, budget=300000)
       ),
       node("Sales",
           node("Enterprise", team_size=8, budget=400000),
           node("SMB", team_size=12, budget=350000)
       ),
       node("Marketing",
           node("Digital", team_size=6, budget=250000),
           node("Content", team_size=4, budget=150000)
       )
   )

   # Calculate department budgets
   result = company.map(lambda n: {
       "total_budget": sum(
           child.get("budget", 0) for child in n.children
       ) if n.children else n.get("budget", 0)
   })

   # Find high-budget teams
   high_budget = result.find_all(
       lambda n: n.get("budget", 0) > 400000
   )

   for team in high_budget:
       print(f"{team.path}: ${team.get('budget'):,}")

Data Processing Pipeline
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import Tree, map_, filter_, normalize, extract

   # Create data tree
   data = Tree.from_dict({
       "name": "dataset",
       "children": [
           {"name": "record_1", "value": 10, "valid": True},
           {"name": "record_2", "value": 5, "valid": False},
           {"name": "record_3", "value": 15, "valid": True},
           {"name": "record_4", "value": 8, "valid": True},
       ]
   })

   # Build processing pipeline
   pipeline = (
       filter_(lambda n: n.get("valid", False)) >>
       map_(lambda n: {"value": n.get("value", 0) * 2}) >>
       normalize(sort_children=True) >>
       extract(lambda n: n.get("value"))
   )

   # Process data
   result = pipeline(data)
   print("Processed values:", result)

When to Use Python API vs Shell
--------------------------------

AlgoTree provides two interfaces for different use cases:

**Use the Python API (Recommended for Scripting):**

.. code-block:: python

   from AlgoTree import Node, Tree, node
   from AlgoTree.transformers import map_, filter_, prune

   # Fluent, composable, type-safe
   tree = Tree(node('root',
       node('child1', value=1),
       node('child2', value=2)
   ))

   # Powerful transformations with full Python
   result = tree.map(lambda n: n.with_attrs(doubled=n.get('value', 0) * 2))
   filtered = tree.filter(lambda n: n.get('value', 0) > 1)

   # Integration with Python ecosystem
   import pandas as pd
   df = pd.DataFrame([{'name': n.name, 'value': n.get('value')}
                      for n in tree.root.descendants()])

**Use the Shell/CLI (For Interactive Exploration):**

.. code-block:: bash

   # Quick exploration
   algotree shell tree.json

   # In the shell:
   > cd root
   > ls
   > find "child.*"
   > select "n.get('value', 0) > 1"
   > tree

   # One-off terminal operations
   algotree tree tree.json
   algotree select 'n.depth > 2' tree.json

**Decision Matrix:**

=====================  ====================  ==================
Use Case               Python API            Shell/CLI
=====================  ====================  ==================
Automation             **Recommended**       Not ideal
Scripts/Programs       **Recommended**       Not ideal
Complex logic          **Recommended**       Not ideal
Type safety            **Recommended**       No type checking
IDE support            **Recommended**       N/A
Testing                **Recommended**       Limited
Integration            **Recommended**       Limited
Quick exploration      Possible              **Recommended**
Terminal workflows     Possible              **Recommended**
Learning structure     Possible              **Recommended**
Human interaction      Possible              **Recommended**
=====================  ====================  ==================

**Example: Automation with Python API**

.. code-block:: python

   # Production-ready script
   from AlgoTree import Tree, map_, filter_, save

   # Load, transform, save
   tree = Tree.from_dict(load_data())
   processed = tree.filter(validate).map(enrich).prune(cleanup)
   save(processed.root, 'output.json')

   # Full error handling, logging, etc.

**Example: Quick Exploration with Shell**

.. code-block:: bash

   # Quick terminal session
   $ algotree shell data.json
   > tree
   > cd interesting_node
   > stat
   > find "pattern.*"
   > exit

Migration from v1.x
-------------------

AlgoTree v2.0 is a complete redesign. Here's how to migrate:

**Old v1.x API:**

.. code-block:: python

   from AlgoTree import TreeBuilder

   # v1.x - mutable operations
   tree = (TreeBuilder()
       .root("company")
       .child("engineering")
           .child("frontend")
           .sibling("backend")
           .up()
       .sibling("sales")
       .build())

   # Mutable modification
   tree.add_child(Node("marketing"))

**New v2.0 API:**

.. code-block:: python

   from AlgoTree import TreeBuilder, Node

   # v2.0 - fluent builder
   tree = (TreeBuilder("company")
       .child("engineering")
           .child("frontend")
           .child("backend")
           .up()
       .child("sales")
       .build())

   # Immutable operations
   tree2 = Tree(tree.root.with_child(Node("marketing")))

**Key changes:**

1. **TreeBuilder** now takes root name in constructor, no ``.root()`` method
2. **No ``.sibling()`` method** - use ``.up()`` then ``.child()``
3. **All operations are immutable** - return new trees instead of mutating
4. **Node is immutable** - use ``.with_*()`` methods instead of property setters
5. **No FlatForest, FlatForestNode, TreeNode** - removed entirely
6. **Tree wrapper** provides functional API (map, filter, reduce, fold)
7. **Selectors** replace string-based pattern matching
8. **Transformers** provide composable pipelines

Advanced Features
-----------------

Lazy Evaluation
^^^^^^^^^^^^^^^

Transformers support lazy evaluation for large trees:

.. code-block:: python

   # Create lazy pipeline
   pipeline = map_(expensive_fn) >> filter_(predicate)

   # Only evaluated when called
   result = pipeline(tree)

Structural Sharing
^^^^^^^^^^^^^^^^^^

Immutable operations use structural sharing for efficiency:

.. code-block:: python

   tree1 = Node("root", Node("a"), Node("b"))
   tree2 = tree1.with_child(Node("c"))

   # tree1 and tree2 share "a" and "b" nodes
   # Only "c" and new root are created

Custom Selectors
^^^^^^^^^^^^^^^^

Create custom selectors by subclassing:

.. code-block:: python

   from AlgoTree import Selector

   class ExtensionSelector(Selector):
       def __init__(self, ext):
           self.ext = ext

       def matches(self, node):
           return node.name.endswith(self.ext)

   # Use it
   py_files = ExtensionSelector(".py")
   for node in py_files.select(tree):
       print(node.name)

Custom Transformers
^^^^^^^^^^^^^^^^^^^

Create custom transformers:

.. code-block:: python

   from AlgoTree import TreeTransformer

   class CapitalizeNames(TreeTransformer):
       def __call__(self, tree):
           return tree.map(lambda n: n.with_name(n.name.upper()))

   # Use it
   uppercase_tree = CapitalizeNames()(tree)

   # Or compose it
   pipeline = CapitalizeNames() >> normalize()

Testing
-------

AlgoTree v2.0 has 86% test coverage with 197 passing tests:

.. code-block:: shell

   # Run tests
   python -m pytest

   # Run with coverage
   python -m pytest --cov=AlgoTree --cov-report=html

   # Run specific test
   python -m pytest test/test_node.py::TestNode::test_immutability

Contributing
------------

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

License
-------

MIT License - see LICENSE file for details.

Links
-----

- **Documentation:** https://queelius.github.io/AlgoTree/
- **Source Code:** https://github.com/queelius/AlgoTree
- **Issue Tracker:** https://github.com/queelius/AlgoTree/issues
- **PyPI:** https://pypi.org/project/AlgoTree/
- **Changelog:** https://github.com/queelius/AlgoTree/blob/master/CHANGELOG.md
