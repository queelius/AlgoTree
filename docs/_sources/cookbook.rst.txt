AlgoTree Cookbook
=================

This cookbook provides practical recipes for common tree manipulation tasks using AlgoTree v1.0.

Tree Construction Patterns
--------------------------

Building a File System Tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import TreeBuilder
   
   # Build a file system structure
   fs = (TreeBuilder()
       .root("/", type="directory")
       .child("home", type="directory")
           .child("user", type="directory")
               .child("documents", type="directory")
                   .child("report.pdf", type="file", size=1024)
                   .sibling("notes.txt", type="file", size=256)
                   .up()
               .sibling("downloads", type="directory")
                   .child("data.csv", type="file", size=2048)
                   .up(2)
           .sibling("alice", type="directory")
               .child("projects", type="directory")
                   .up(3)
       .sibling("etc", type="directory")
           .child("config.ini", type="file", size=128)
       .build())

Building an Organization Chart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import Node
   
   # Build org chart with Node API
   ceo = Node("CEO", title="Chief Executive Officer", reports=0)
   
   cto = ceo.add_child("CTO", title="Chief Technology Officer", reports=50)
   cfo = ceo.add_child("CFO", title="Chief Financial Officer", reports=20)
   
   eng_mgr = cto.add_child("Engineering Manager", reports=25)
   qa_mgr = cto.add_child("QA Manager", reports=15)
   
   eng_mgr.add_child("Senior Engineer 1", level="senior")
   eng_mgr.add_child("Senior Engineer 2", level="senior")
   eng_mgr.add_child("Junior Engineer", level="junior")

Creating from DSL
^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import parse_tree
   
   # Visual DSL
   tree = parse_tree("""
   root
   ├── branch1
   │   ├── leaf1
   │   └── leaf2
   └── branch2
       └── leaf3
   """)
   
   # Indent DSL
   tree = parse_tree("""
   root
     branch1
       leaf1
       leaf2
     branch2
       leaf3
   """)
   
   # S-expression DSL
   tree = parse_tree("""
   (root
     (branch1
       (leaf1)
       (leaf2))
     (branch2
       (leaf3)))
   """)

Tree Navigation Patterns
------------------------

Finding Nodes
^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import Node, dotmatch, pattern_match
   
   # Create a sample tree
   root = Node("app")
   models = root.add_child("models")
   user = models.add_child("user", type="model")
   post = models.add_child("post", type="model")
   
   # Find by exact path
   users = dotmatch(root, "app.models.user")
   
   # Find with wildcards
   all_models = dotmatch(root, "app.models.*")
   
   # Find anywhere in tree
   all_models = dotmatch(root, "app.**.model")
   
   # Find by attributes
   models = pattern_match(root, {"attributes": {"type": "model"}})

Path Operations
^^^^^^^^^^^^^^^

.. code-block:: python

   # Get path from root to node
   user_node = root.find(lambda n: n.name == "user")
   path = user_node.get_path()  # [root, models, user]
   
   # Get dot path string
   paths = dotmatch(root, "**.user", return_paths=True)
   # Returns: ["app.models.user"]
   
   # Check if path exists
   from AlgoTree import dotexists
   if dotexists(root, "app.models.user"):
       print("User model exists")

Tree Transformation Patterns
----------------------------

Filtering Trees
^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import FluentNode, dotfilter
   
   # Filter with FluentNode
   large_nodes = (FluentNode(root)
       .descendants()
       .where(lambda n: n.payload.get("size", 0) > 1000)
       .to_list())
   
   # Filter with dot expressions
   test_files = dotfilter(root, "contains(@.name, 'test')")
   
   # Complex filtering
   important = dotfilter(root, 
       "@.priority == 'high' and @.children.length > 2")

Transforming Nodes
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Map transformation
   from AlgoTree import FluentNode
   
   # Double all sizes
   (FluentNode(root)
       .descendants()
       .map(lambda n: {"size": n.payload.get("size", 0) * 2}))
   
   # Rename nodes matching pattern
   import re
   (FluentNode(root)
       .descendants()
       .where(lambda n: re.match(r"test_.*", n.name))
       .each(lambda n: setattr(n, "name", n.name.replace("test_", "spec_"))))

Pruning Trees
^^^^^^^^^^^^^

.. code-block:: python

   # Remove leaf nodes
   (FluentNode(root)
       .prune(lambda n: n.is_leaf and n.payload.get("deprecated", False)))
   
   # Remove empty directories
   def is_empty_dir(node):
       return (node.payload.get("type") == "directory" and 
               len(node.children) == 0)
   
   (FluentNode(root).prune(is_empty_dir))

Tree Analysis Patterns
----------------------

Statistics and Metrics
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Basic statistics
   total_nodes = len(list(root.traverse_preorder()))
   tree_height = root.height
   leaf_count = len([n for n in root.traverse_preorder() if n.is_leaf])
   
   # Size analysis for file trees
   def total_size(node):
       size = node.payload.get("size", 0)
       for child in node.children:
           size += total_size(child)
       return size
   
   print(f"Total size: {total_size(root)} bytes")
   
   # Find largest subtree
   def subtree_size(node):
       return len(list(node.traverse_preorder()))
   
   largest = max(root.traverse_preorder(), key=subtree_size)

Finding Patterns
^^^^^^^^^^^^^^^^

.. code-block:: python

   # Find unbalanced branches
   def is_unbalanced(node):
       if len(node.children) < 2:
           return False
       heights = [child.height for child in node.children]
       return max(heights) - min(heights) > 2
   
   unbalanced = pattern_match(root, Pattern(predicate=is_unbalanced))
   
   # Find duplicate names
   from collections import Counter
   
   names = [n.name for n in root.traverse_preorder()]
   duplicates = [name for name, count in Counter(names).items() if count > 1]
   
   # Find circular dependencies (if payload contains refs)
   def has_circular_ref(node, visited=None):
       if visited is None:
           visited = set()
       if node in visited:
           return True
       visited.add(node)
       for ref_name in node.payload.get("dependencies", []):
           ref_node = root.find(lambda n: n.name == ref_name)
           if ref_node and has_circular_ref(ref_node, visited.copy()):
               return True
       return False

Tree Comparison Patterns
------------------------

Comparing Trees
^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import Node
   
   # Check if two trees have same structure
   def same_structure(tree1, tree2):
       if len(tree1.children) != len(tree2.children):
           return False
       for c1, c2 in zip(tree1.children, tree2.children):
           if not same_structure(c1, c2):
               return False
       return True
   
   # Find differences between trees
   def diff_trees(tree1, tree2, path=""):
       diffs = []
       
       current_path = f"{path}/{tree1.name}" if path else tree1.name
       
       # Check current node
       if tree1.name != tree2.name:
           diffs.append(("name", current_path, tree1.name, tree2.name))
       
       # Check payload differences
       for key in set(tree1.payload.keys()) | set(tree2.payload.keys()):
           val1 = tree1.payload.get(key)
           val2 = tree2.payload.get(key)
           if val1 != val2:
               diffs.append(("payload", current_path, key, val1, val2))
       
       # Check children
       for i, (c1, c2) in enumerate(zip(tree1.children, tree2.children)):
           diffs.extend(diff_trees(c1, c2, current_path))
       
       # Check for different number of children
       if len(tree1.children) != len(tree2.children):
           diffs.append(("children_count", current_path, 
                        len(tree1.children), len(tree2.children)))
       
       return diffs

Merging Trees
^^^^^^^^^^^^^

.. code-block:: python

   # Merge two trees with conflict resolution
   def merge_trees(tree1, tree2, conflict_resolver=None):
       """
       Merge tree2 into tree1.
       conflict_resolver(node1, node2) -> Node
       """
       # Create merged root
       if conflict_resolver and tree1.name == tree2.name:
           merged = conflict_resolver(tree1, tree2)
       else:
           merged = Node(tree1.name, **tree1.payload)
       
       # Add children from tree1
       child_map = {child.name: child for child in tree1.children}
       
       # Merge children from tree2
       for child2 in tree2.children:
           if child2.name in child_map:
               # Recursive merge for common children
               merged_child = merge_trees(child_map[child2.name], child2, 
                                        conflict_resolver)
               merged.add_child(merged_child.name, **merged_child.payload)
           else:
               # Add new child from tree2
               merged.add_child(child2.name, **child2.payload)
       
       # Add remaining children from tree1
       for name, child1 in child_map.items():
           if not any(c.name == name for c in tree2.children):
               merged.add_child(child1.name, **child1.payload)
       
       return merged

Export and Visualization Patterns
----------------------------------

Exporting to Different Formats
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import export_tree, save_tree
   
   # Export to various formats
   json_str = export_tree(root, "json", indent=2)
   dot_graph = export_tree(root, "graphviz", 
       node_attr=lambda n: {"shape": "box", "style": "filled"})
   mermaid = export_tree(root, "mermaid", direction="LR")
   
   # Save to files with auto-format detection
   save_tree(root, "tree.json")
   save_tree(root, "tree.dot")
   save_tree(root, "tree.mmd")
   save_tree(root, "tree.html")
   
   # Custom GraphViz with colors
   def node_color(node):
       if node.is_leaf:
           return {"fillcolor": "lightgreen", "style": "filled"}
       elif node.is_root:
           return {"fillcolor": "lightblue", "style": "filled"}
       else:
           return {"fillcolor": "lightyellow", "style": "filled"}
   
   dot = export_tree(root, "graphviz", node_attr=node_color)

Pretty Printing
^^^^^^^^^^^^^^^

.. code-block:: python

   from AlgoTree import pretty_tree, PrettyTree
   
   # Simple pretty print
   print(pretty_tree(root))
   
   # Custom pretty printing with markers
   printer = PrettyTree(
       mark=["important_node", "critical_node"],
       node_details=lambda n: f"[{n.payload.get('type', 'unknown')}]"
   )
   print(printer(root))
   
   # Unicode vs ASCII
   print(pretty_tree(root, style="unicode"))  # ├── └── │
   print(pretty_tree(root, style="ascii"))    # +-- \-- |

Advanced Patterns
-----------------

Lazy Tree Loading
^^^^^^^^^^^^^^^^^

.. code-block:: python

   class LazyNode(Node):
       """Node that loads children on demand."""
       
       def __init__(self, name, loader=None, **kwargs):
           super().__init__(name, **kwargs)
           self._loader = loader
           self._loaded = False
       
       @property
       def children(self):
           if not self._loaded and self._loader:
               self._children = self._loader(self)
               self._loaded = True
           return self._children
   
   # Usage
   def load_directory(node):
       """Load directory contents lazily."""
       import os
       children = []
       path = node.payload["path"]
       for item in os.listdir(path):
           item_path = os.path.join(path, item)
           if os.path.isdir(item_path):
               children.append(LazyNode(item, loader=load_directory, 
                                      path=item_path, type="dir"))
           else:
               children.append(Node(item, path=item_path, type="file"))
       return children
   
   # Create lazy file system tree
   root = LazyNode("/", loader=load_directory, path="/", type="dir")

Tree Visitors
^^^^^^^^^^^^^

.. code-block:: python

   class TreeVisitor:
       """Base visitor for tree traversal."""
       
       def visit(self, node):
           method_name = f"visit_{node.payload.get('type', 'default')}"
           method = getattr(self, method_name, self.visit_default)
           return method(node)
       
       def visit_default(self, node):
           pass
   
   class FileSystemVisitor(TreeVisitor):
       def __init__(self):
           self.total_size = 0
           self.file_count = 0
           self.dir_count = 0
       
       def visit_file(self, node):
           self.file_count += 1
           self.total_size += node.payload.get("size", 0)
       
       def visit_directory(self, node):
           self.dir_count += 1
           for child in node.children:
               self.visit(child)
   
   # Usage
   visitor = FileSystemVisitor()
   visitor.visit(fs_tree)
   print(f"Files: {visitor.file_count}, Dirs: {visitor.dir_count}")

Tree Generators
^^^^^^^^^^^^^^^

.. code-block:: python

   import random
   
   def generate_random_tree(depth, branch_factor=2, name_prefix="node"):
       """Generate a random tree with specified parameters."""
       
       def build(level, index):
           name = f"{name_prefix}_{level}_{index}"
           node = Node(name, level=level, value=random.randint(1, 100))
           
           if level < depth:
               num_children = random.randint(1, branch_factor)
               for i in range(num_children):
                   child = build(level + 1, i)
                   node.children.append(child)
                   child.parent = node
           
           return node
       
       return build(0, 0)
   
   # Generate test tree
   test_tree = generate_random_tree(depth=4, branch_factor=3)

Performance Patterns
--------------------

Efficient Tree Operations
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Cache computed values
   class CachedNode(Node):
       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           self._height_cache = None
           self._size_cache = None
       
       @property
       def height(self):
           if self._height_cache is None:
               if not self.children:
                   self._height_cache = 0
               else:
                   self._height_cache = 1 + max(c.height for c in self.children)
           return self._height_cache
       
       @property
       def size(self):
           if self._size_cache is None:
               self._size_cache = 1 + sum(c.size for c in self.children)
           return self._size_cache
       
       def invalidate_cache(self):
           self._height_cache = None
           self._size_cache = None
           if self.parent:
               self.parent.invalidate_cache()
   
   # Batch operations
   def batch_update(root, updates):
       """Apply multiple updates efficiently."""
       # Collect all nodes first
       node_map = {n.name: n for n in root.traverse_preorder()}
       
       # Apply updates
       for name, changes in updates.items():
           if name in node_map:
               node = node_map[name]
               node.payload.update(changes)
       
       # Single traversal for all updates
       return root

See Also
--------

- :doc:`fluent_api` - Fluent API documentation
- :doc:`pattern_matching` - Pattern matching guide
- :doc:`tutorial` - Step-by-step tutorials
- `GitHub Examples <https://github.com/queelius/AlgoTree/tree/main/examples>`_