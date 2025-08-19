Pattern Matching
================

AlgoTree v1.0 introduces powerful pattern matching capabilities for finding and manipulating
specific structural patterns within trees. The dot notation support is inspired by the
`dotsuite project <https://github.com/queelius/dotsuite>`_, which provides a comprehensive
algebra for querying and transforming nested data structures.

Basic Usage
-----------

The simplest way to use pattern matching is through the ``pattern_match`` function:

.. code-block:: python

   from AlgoTree import Node, pattern_match
   
   # Create a tree
   root = Node("root")
   branch1 = root.add_child("branch1", type="container")
   leaf1 = branch1.add_child("leaf1", type="data")
   branch2 = root.add_child("branch2", type="container")
   
   # Find all nodes named "branch1"
   matches = pattern_match(root, "branch1")
   
   # Find all nodes with type="container"
   matches = pattern_match(root, {"attributes": {"type": "container"}})

Pattern Syntax
--------------

String Patterns
^^^^^^^^^^^^^^^

String patterns provide a concise way to express common matching scenarios:

.. code-block:: python

   # Match by name
   pattern = "nodename"
   
   # Match any single node (wildcard)
   pattern = "*"
   
   # Match any subtree (deep wildcard)
   pattern = "**"
   
   # Match with attributes
   pattern = "node[type=container,size=10]"
   
   # Match with specific children
   pattern = "parent(child1, child2, *)"

Dictionary Patterns
^^^^^^^^^^^^^^^^^^^

Dictionary patterns provide more control:

.. code-block:: python

   pattern = {
       "name": "parent",
       "attributes": {"type": "container"},
       "children": [
           {"name": "child1"},
           {"name": "*"}  # Wildcard child
       ],
       "min_children": 2,
       "max_children": 5
   }

Pattern Objects
^^^^^^^^^^^^^^^

For maximum flexibility, use Pattern objects directly:

.. code-block:: python

   from AlgoTree import Pattern
   
   # Pattern with custom predicate
   pattern = Pattern(
       predicate=lambda n: n.name.startswith("test_") and len(n.children) > 2
   )
   
   # Pattern with mixed constraints
   pattern = Pattern(
       name="container",
       attributes={"type": "branch"},
       min_children=1
   )

Advanced Matching
-----------------

Wildcards
^^^^^^^^^

Wildcards allow flexible matching:

.. code-block:: python

   # Single wildcard - matches exactly one node
   pattern = Pattern.from_string("parent(*, child2, *)")
   
   # Deep wildcard - matches zero or more nodes
   pattern = Pattern.from_string("root(**, target)")
   
   # This matches:
   # root -> target (direct child)
   # root -> a -> target
   # root -> a -> b -> c -> target

Match Types
^^^^^^^^^^^

Control how patterns match tree structures:

.. code-block:: python

   from AlgoTree import PatternMatcher, MatchType
   
   # Exact matching - children must match exactly
   matcher = PatternMatcher(MatchType.EXACT)
   pattern = Pattern.from_string("parent(child1, child2)")
   # Only matches if parent has exactly child1 and child2 in that order
   
   # Partial matching (default) - pattern children must exist
   matcher = PatternMatcher(MatchType.PARTIAL)
   # Matches if parent contains child1 and child2 among its children

Custom Predicates
^^^^^^^^^^^^^^^^^

Use custom functions for complex matching logic:

.. code-block:: python

   def is_large_branch(node):
       return (node.payload.get("type") == "branch" and 
               len(node.children) > 5 and
               sum(1 for c in node.children if c.is_leaf) > 3)
   
   pattern = Pattern(predicate=is_large_branch)
   matches = pattern_match(tree, pattern)

Fluent API Integration
----------------------

Pattern matching integrates seamlessly with the fluent API:

.. code-block:: python

   from AlgoTree import TreeBuilder, FluentNode
   
   # Build a tree
   tree = (TreeBuilder()
       .root("app")
       .child("models")
           .child("user.py", type="file")
           .sibling("post.py", type="file")
           .up()
       .sibling("views")
           .child("index.py", type="file")
           .sibling("admin.py", type="file")
       .build())
   
   # Find all Python files
   (FluentNode(tree)
       .match("*[type=file]")
       .each(lambda n: print(f"Found: {n.name}")))
   
   # Replace all admin files with secured versions
   (FluentNode(tree)
       .replace_matches(
           "admin.py",
           lambda n: Node("admin_secured.py", **n.payload)
       ))

Pattern Replacement
-------------------

Replace nodes matching patterns:

.. code-block:: python

   from AlgoTree import PatternMatcher, Pattern
   
   matcher = PatternMatcher()
   pattern = Pattern(name="old_node")
   
   # Replace with a fixed node
   new_node = Node("new_node", value=42)
   count = matcher.replace(tree, pattern, new_node)
   
   # Replace with a transformation function
   def transform(old_node):
       return Node(
           name=f"{old_node.name}_v2",
           value=old_node.payload.get("value", 0) * 2
       )
   
   count = matcher.replace(tree, pattern, transform)
   print(f"Replaced {count} nodes")

Real-World Examples
-------------------

Finding Test Files
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Find all test files in a project structure
   pattern = Pattern.from_string("*[name.endswith('_test.py')]")
   test_files = pattern_match(project_tree, pattern)

Refactoring Components
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Find React components with specific structure
   pattern = {
       "attributes": {"type": "component"},
       "children": [
           {"name": "render"},
           {"name": "state"}
       ]
   }
   
   # Convert to functional components
   def modernize_component(old_component):
       new_comp = Node(
           name=old_component.name,
           type="functional_component",
           hooks=["useState", "useEffect"]
       )
       # Copy non-lifecycle methods
       for child in old_component.children:
           if child.name not in ["render", "componentDidMount"]:
               new_comp.add_child(child.name, **child.payload)
       return new_comp
   
   matcher = PatternMatcher()
   matcher.replace(component_tree, Pattern.from_dict(pattern), modernize_component)

Analyzing Tree Structure
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Find all deeply nested nodes
   deep_pattern = Pattern(
       predicate=lambda n: len(list(n.get_path())) > 5
   )
   
   deep_nodes = pattern_match(tree, deep_pattern)
   
   # Find unbalanced branches
   def is_unbalanced(node):
       if len(node.children) < 2:
           return False
       heights = [n.height for n in node.children]
       return max(heights) - min(heights) > 2
   
   unbalanced = pattern_match(tree, Pattern(predicate=is_unbalanced))

Dot Notation (dotsuite-inspired)
---------------------------------

AlgoTree implements dot notation for tree navigation inspired by the
`dotsuite <https://github.com/queelius/dotsuite>`_ project's approach to 
querying nested data structures.

Basic Dot Paths
^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import dotmatch, dotexists, dotpluck
   
   # Navigate paths like object properties
   users = dotmatch(tree, "app.models.user")
   
   # Check if path exists
   if dotexists(tree, "app.config.database"):
       db_config = dotmatch(tree, "app.config.database")[0]
   
   # Extract values from paths
   values = dotpluck(tree, "app.version", "app.config.port")

Advanced Path Features
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Wildcards - match any single node
   dotmatch(tree, "app.*.config")  # Any child's config
   
   # Deep wildcards - match at any depth
   dotmatch(tree, "app.**.test_*")  # All test files anywhere
   
   # Attribute filters
   dotmatch(tree, "app.*[type=model]")  # Children with type=model
   
   # Predicate filters (JSONPath-like)
   dotmatch(tree, "app.**[?(@.size > 100)]")  # Nodes with size > 100
   
   # Array indexing and slicing
   dotmatch(tree, "app.children[0]")  # First child
   dotmatch(tree, "app.children[-1]")  # Last child
   dotmatch(tree, "app.children[1:3]")  # Slice of children
   
   # Regex matching
   dotmatch(tree, "app.~test_.*")  # Regex pattern on names
   
   # Fuzzy matching
   dotmatch(tree, "app.%usr:0.8")  # Fuzzy match "usr" with 80% threshold

Filter Expressions
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import dotfilter
   
   # Complex filter expressions
   nodes = dotfilter(tree, "@.size > 100 and @.type == 'model'")
   
   # Using functions
   nodes = dotfilter(tree, "contains(@.name, 'test') and @.children.length > 0")
   
   # Checking properties
   leaves = dotfilter(tree, "@.is_leaf")
   branches = dotfilter(tree, "not @.is_leaf and @.children.length > 2")

dotsuite Philosophy
^^^^^^^^^^^^^^^^^^^

Following dotsuite's design principles:

1. **Depth** - Address data with paths (dotmatch, dotexists)
2. **Truth** - Query and validate (dotfilter, dotexists)  
3. **Shape** - Transform structures (future: dotmod, dotpipe)

Each operation answers exactly one question and composes cleanly with others,
providing a minimal yet complete algebra for tree manipulation.

Command-Line Usage
------------------

The ``jt`` tool supports pattern matching:

.. code-block:: bash

   # Find nodes matching a pattern
   jt tree.json --match "container(*)"
   
   # Filter by pattern and transform
   jt tree.json --match "*[type=test]" --map "{'status': 'pending'}"
   
   # Replace matching nodes
   jt tree.json --replace-pattern "old_*" --with "new_node"

Performance Considerations
--------------------------

- Pattern matching is optimized for common cases (name and attribute matching)
- Deep wildcards can be expensive on large trees - use specific patterns when possible
- Custom predicates are called for every node - keep them efficient
- Consider using indices for frequently searched attributes in large trees

See Also
--------

- :doc:`fluent_api` - Fluent API documentation
- :doc:`tutorial` - Step-by-step tutorials
- `GitHub Examples <https://github.com/queelius/AlgoTree/tree/main/examples>`_