# Interoperability Between AlgoTree and AlgoGraph

This tutorial covers bidirectional conversion between AlgoTree (tree data structures) and AlgoGraph (graph data structures). You will learn how to convert trees to graphs for graph algorithms, extract spanning trees from graphs, and use the flat dictionary interchange format.

**Target Audience:** Intermediate Python developers familiar with AlgoTree basics.

**Prerequisites:**
- Python 3.8+
- AlgoTree installed (`pip install algotree`)
- AlgoGraph installed (`pip install algograph`) or available in PYTHONPATH
- Basic understanding of tree and graph data structures

**What You Will Learn:**
1. Converting trees to graphs for graph algorithm analysis
2. Extracting spanning trees from graphs
3. Using the flat dictionary interchange format
4. Round-trip conversions preserving attributes
5. Shell commands for interactive exploration

---

## Table of Contents

1. [Understanding the Relationship](#understanding-the-relationship)
2. [Setup and Installation](#setup-and-installation)
3. [Converting Trees to Graphs](#converting-trees-to-graphs)
4. [Converting Graphs to Trees](#converting-graphs-to-trees)
5. [The Flat Dictionary Interchange Format](#the-flat-dictionary-interchange-format)
6. [Practical Examples](#practical-examples)
7. [Shell Commands for Interactive Exploration](#shell-commands-for-interactive-exploration)
8. [When to Use Trees vs Graphs](#when-to-use-trees-vs-graphs)
9. [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)

---

## Understanding the Relationship

Trees are a special case of graphs with specific properties:
- **Acyclic:** No cycles exist in the structure
- **Connected:** All nodes are reachable from the root
- **Directed:** Parent-to-child relationships define direction
- **Single parent:** Each node (except root) has exactly one parent

This means any tree can be represented as a graph, but not every graph can be represented as a tree. When converting a graph to a tree, AlgoTree extracts a **spanning tree** using BFS traversal from a specified root.

### Key Interop Functions

| Function | Direction | Description |
|----------|-----------|-------------|
| `tree_to_graph(node, directed)` | Tree -> Graph | Convert tree to AlgoGraph |
| `graph_to_tree(graph, root_id)` | Graph -> Tree | Extract spanning tree from graph |
| `node_to_flat_dict(node)` | Tree -> Dict | Convert to interchange format |
| `flat_dict_to_node(flat_dict, root_key)` | Dict -> Tree | Convert from interchange format |

---

## Setup and Installation

### Install Both Libraries

```bash
pip install algotree algograph
```

### Verify Installation

```python
from AlgoTree import Node, tree_to_graph, graph_to_tree
from AlgoTree.interop import ALGOGRAPH_AVAILABLE

print(f"AlgoGraph available: {ALGOGRAPH_AVAILABLE}")
# Output: AlgoGraph available: True
```

If `ALGOGRAPH_AVAILABLE` is `False`, ensure AlgoGraph is installed or in your PYTHONPATH.

---

## Converting Trees to Graphs

### Basic Conversion

Convert any AlgoTree Node (and its subtree) to an AlgoGraph Graph:

```python
from AlgoTree import Node, tree_to_graph

# Create a tree
tree = Node('root',
    Node('child1', attrs={'value': 10}),
    Node('child2',
        Node('grandchild1'),
        Node('grandchild2'),
        attrs={'value': 20}
    )
)

# Convert to graph (directed edges by default)
graph = tree_to_graph(tree)

print(f"Vertices: {graph.vertex_count}")  # Output: 5
print(f"Edges: {graph.edge_count}")       # Output: 4

# Check edges exist
print(graph.has_edge('root', 'child1'))   # Output: True
print(graph.has_edge('root', 'child2'))   # Output: True
print(graph.has_edge('child2', 'grandchild1'))  # Output: True
```

### Directed vs Undirected Edges

By default, `tree_to_graph()` creates directed edges (parent -> child). For undirected graphs:

```python
# Create undirected graph
undirected_graph = tree_to_graph(tree, directed=False)

# Edges are bidirectional
edges = list(undirected_graph.edges)
print(f"First edge directed: {edges[0].directed}")  # Output: False
```

**Tip:** Use undirected graphs when you need to traverse the structure in both directions or when the hierarchical relationship is not important.

### Attribute Preservation

Node attributes are automatically copied to vertex attributes:

```python
from AlgoTree import Node, tree_to_graph

tree = Node('server',
    Node('database', attrs={'port': 5432, 'type': 'postgres'}),
    Node('cache', attrs={'port': 6379, 'type': 'redis'}),
    attrs={'host': 'localhost', 'env': 'production'}
)

graph = tree_to_graph(tree)

# Access vertex attributes
server_vertex = graph.get_vertex('server')
print(server_vertex.get('host'))  # Output: localhost
print(server_vertex.get('env'))   # Output: production

db_vertex = graph.get_vertex('database')
print(db_vertex.get('port'))  # Output: 5432
print(db_vertex.get('type'))  # Output: postgres
```

---

## Converting Graphs to Trees

### Basic Conversion

Convert an AlgoGraph Graph to an AlgoTree Node by specifying a root vertex:

```python
from AlgoGraph import Graph, Vertex, Edge
from AlgoTree import graph_to_tree

# Create a graph
vertices = {
    Vertex('A', attrs={'level': 0}),
    Vertex('B', attrs={'level': 1}),
    Vertex('C', attrs={'level': 1}),
    Vertex('D', attrs={'level': 2}),
}
edges = {
    Edge('A', 'B'),
    Edge('A', 'C'),
    Edge('B', 'D'),
}
graph = Graph(vertices, edges)

# Convert to tree with 'A' as root
tree = graph_to_tree(graph, 'A')

print(tree.name)  # Output: A
print([c.name for c in tree.children])  # Output: ['B', 'C'] (order may vary)
print(tree.get('level'))  # Output: 0
```

### Spanning Tree Extraction

When a graph has cycles or multiple paths, `graph_to_tree()` extracts a spanning tree using BFS:

```python
from AlgoGraph import Graph, Vertex, Edge
from AlgoTree import graph_to_tree

# Graph with cycle (A-B-C-A)
vertices = {Vertex('A'), Vertex('B'), Vertex('C')}
edges = {
    Edge('A', 'B'),
    Edge('B', 'C'),
    Edge('C', 'A'),  # Creates cycle
}
graph = Graph(vertices, edges)

# Extract spanning tree - cycle is broken
tree = graph_to_tree(graph, 'A')

# Count nodes in tree
def count_nodes(n):
    return 1 + sum(count_nodes(c) for c in n.children)

print(count_nodes(tree))  # Output: 3 (all nodes included)
# But no cycles exist - each node appears once
```

### Handling Disconnected Components

Only vertices reachable from the root are included in the tree:

```python
from AlgoGraph import Graph, Vertex, Edge
from AlgoTree import graph_to_tree

# Graph with disconnected vertex
vertices = {
    Vertex('A'),
    Vertex('B'),
    Vertex('C'),  # Not connected to A or B
}
edges = {Edge('A', 'B')}
graph = Graph(vertices, edges)

# Convert with 'A' as root
tree = graph_to_tree(graph, 'A')

def get_all_names(n):
    names = {n.name}
    for c in n.children:
        names.update(get_all_names(c))
    return names

print(get_all_names(tree))  # Output: {'A', 'B'}
# 'C' is excluded because it's not reachable from 'A'
```

---

## The Flat Dictionary Interchange Format

The flat dictionary format provides a JSON-serializable representation that works with both AlgoTree and AlgoGraph. This is useful for:
- Saving/loading data to files
- Transferring data between applications
- Working with systems that do not have AlgoGraph installed

### Structure

```python
{
    'node_key': {
        '.name': 'node_name',        # Node/vertex name
        '.children': ['child1', 'child2'],  # Child references
        'attr1': 'value1',           # Custom attributes
        'attr2': 'value2',
    }
}
```

**Note:** Metadata keys start with `.` (dot prefix) to distinguish them from user attributes.

### Converting Tree to Flat Dict

```python
from AlgoTree import Node, node_to_flat_dict

tree = Node('company',
    Node('engineering', attrs={'budget': 500000}),
    Node('marketing', attrs={'budget': 300000}),
    attrs={'founded': 2020}
)

flat = node_to_flat_dict(tree)

print(flat)
# Output:
# {
#     'company': {
#         '.name': 'company',
#         '.children': ['engineering', 'marketing'],
#         'founded': 2020
#     },
#     'company/engineering': {
#         '.name': 'engineering',
#         '.children': [],
#         'budget': 500000
#     },
#     'company/marketing': {
#         '.name': 'marketing',
#         '.children': [],
#         'budget': 300000
#     }
# }
```

**Note:** Child nodes use path prefixes (`company/engineering`) to handle duplicate names in different branches.

### Converting Flat Dict to Tree

```python
from AlgoTree import flat_dict_to_node

flat = {
    'root': {'.name': 'root', '.children': ['child1', 'child2']},
    'child1': {'.name': 'child1', '.children': [], 'value': 10},
    'child2': {'.name': 'child2', '.children': [], 'value': 20},
}

tree = flat_dict_to_node(flat, 'root')

print(tree.name)  # Output: root
print([c.name for c in tree.children])  # Output: ['child1', 'child2']
print(tree.children[0].get('value'))  # Output: 10
```

### Auto-Detecting Root

If you omit the root key, the function auto-detects it (the node not referenced as a child):

```python
from AlgoTree import flat_dict_to_node

flat = {
    'parent': {'.name': 'parent', '.children': ['child']},
    'child': {'.name': 'child', '.children': []},
}

tree = flat_dict_to_node(flat)  # Root auto-detected as 'parent'
print(tree.name)  # Output: parent
```

### Working with Tree Objects

For convenience, use the Tree-level wrappers:

```python
from AlgoTree import Tree, Node, tree_to_flat_dict, flat_dict_to_tree

# Create Tree (not just Node)
t = Tree(Node('root', Node('child', attrs={'x': 1})))

# Convert to flat dict
flat = tree_to_flat_dict(t)

# Convert back to Tree
recovered = flat_dict_to_tree(flat, 'root')
print(type(recovered))  # Output: <class 'AlgoTree.tree.Tree'>
print(recovered.root.name)  # Output: root
```

---

## Practical Examples

### Example 1: Analyzing a File System Tree with Graph Algorithms

Convert a file system tree to a graph to calculate centrality, find shortest paths, or detect patterns:

```python
from AlgoTree import Node, tree_to_graph

# File system tree
filesystem = Node('/',
    Node('home',
        Node('alice',
            Node('documents', attrs={'size': 1024}),
            Node('photos', attrs={'size': 4096}),
        ),
        Node('bob',
            Node('documents', attrs={'size': 512}),
        ),
    ),
    Node('var',
        Node('log', attrs={'size': 2048}),
        Node('tmp', attrs={'size': 128}),
    ),
)

# Convert to graph for analysis
graph = tree_to_graph(filesystem)

print(f"Total directories: {graph.vertex_count}")
# Output: Total directories: 9

print(f"Connections: {graph.edge_count}")
# Output: Connections: 8

# Now you can use AlgoGraph algorithms:
# - Find shortest path between directories
# - Calculate centrality of directories
# - Find all paths from root to leaves
# - Detect structural patterns
```

### Example 2: Converting a Dependency Graph to a Tree

Extract a dependency tree from a package dependency graph:

```python
from AlgoGraph import Graph, Vertex, Edge
from AlgoTree import graph_to_tree, pretty_tree

# Package dependency graph (may have multiple paths to same package)
vertices = {
    Vertex('myapp'),
    Vertex('requests', attrs={'version': '2.28.0'}),
    Vertex('urllib3', attrs={'version': '1.26.0'}),
    Vertex('certifi', attrs={'version': '2022.12.7'}),
    Vertex('flask', attrs={'version': '2.2.0'}),
    Vertex('werkzeug', attrs={'version': '2.2.0'}),
}
edges = {
    Edge('myapp', 'requests'),
    Edge('myapp', 'flask'),
    Edge('requests', 'urllib3'),
    Edge('requests', 'certifi'),
    Edge('flask', 'werkzeug'),
    Edge('werkzeug', 'urllib3'),  # Shared dependency
}
graph = Graph(vertices, edges)

# Extract dependency tree from perspective of 'myapp'
dep_tree = graph_to_tree(graph, 'myapp')

# Visualize the tree
print(pretty_tree(dep_tree))
# Output:
# myapp
# +-- requests
# |   +-- urllib3
# |   +-- certifi
# +-- flask
#     +-- werkzeug
```

**Note:** The shared dependency `urllib3` appears only once in the tree (under `requests`), because `graph_to_tree` uses BFS and assigns each node to its first-discovered parent.

### Example 3: Round-Trip Conversion Preserving Attributes

Verify that attributes survive round-trip conversion:

```python
from AlgoTree import Node, tree_to_graph, graph_to_tree

# Original tree with rich attributes
original = Node('project',
    Node('src',
        Node('main.py', attrs={'lines': 500, 'language': 'python'}),
        Node('utils.py', attrs={'lines': 200, 'language': 'python'}),
        attrs={'type': 'source'}
    ),
    Node('tests',
        Node('test_main.py', attrs={'lines': 300, 'language': 'python'}),
        attrs={'type': 'tests'}
    ),
    attrs={'name': 'MyProject', 'version': '1.0.0'}
)

# Convert tree -> graph -> tree
graph = tree_to_graph(original)
recovered = graph_to_tree(graph, 'project')

# Verify root attributes
print(recovered.get('name'))     # Output: MyProject
print(recovered.get('version'))  # Output: 1.0.0

# Find and verify nested attributes
def find_node(node, name):
    if node.name == name:
        return node
    for child in node.children:
        result = find_node(child, name)
        if result:
            return result
    return None

main_py = find_node(recovered, 'main.py')
print(main_py.get('lines'))     # Output: 500
print(main_py.get('language'))  # Output: python
```

### Example 4: Using Flat Dict as Data Exchange Format

Save tree data as JSON and reload it:

```python
import json
from AlgoTree import Node, node_to_flat_dict, flat_dict_to_node

# Create tree
tree = Node('config',
    Node('database', attrs={'host': 'localhost', 'port': 5432}),
    Node('cache', attrs={'host': 'localhost', 'port': 6379}),
    attrs={'environment': 'development'}
)

# Convert to flat dict and save as JSON
flat = node_to_flat_dict(tree)
with open('config_tree.json', 'w') as f:
    json.dump(flat, f, indent=2)

# Later: reload from JSON
with open('config_tree.json', 'r') as f:
    loaded_flat = json.load(f)

recovered = flat_dict_to_node(loaded_flat, 'config')
print(recovered.get('environment'))  # Output: development

db_node = recovered.children[0]
print(db_node.get('host'))  # Output: localhost
```

---

## Shell Commands for Interactive Exploration

The AlgoTree shell provides commands for interop without writing Python code.

### Starting the Shell

```bash
# Start interactive shell
python -m AlgoTree.shell.shell

# Or with a tree file
algotree-shell tree.json
```

### The tograph Command

Convert the current tree (or a named tree) to an AlgoGraph Graph:

```bash
# Create and enter a tree
/ $ mktree project
/ $ cd project
/project $ mkdir src
/project $ mkdir tests
/project $ cd src
/project/src $ touch main.py lines=500
/project/src $ touch utils.py lines=200

# Navigate to root and convert
/project/src $ cd /project
/project $ tograph

# Output:
# Converted 'project' to AlgoGraph:
#   Vertices: 5
#   Edges: 4
#   Directed: True

# Create undirected graph
/project $ tograph --undirected

# Output:
# Converted 'project' to AlgoGraph:
#   Vertices: 5
#   Edges: 4
#   Directed: False
```

### The fromgraph Command

Load a graph from a JSON file and convert it to a tree:

```bash
# First, save a graph using AlgoGraph
# (In Python: save_graph(graph, 'network.json'))

# Load graph as tree in shell
/ $ fromgraph network.json server1 network_tree

# Output:
# Loaded graph from network.json as tree 'network_tree' (root: server1)

/ $ cd network_tree
/network_tree $ tree

# Shows the spanning tree structure
```

**Command Syntax:**
```
fromgraph <filename> <root_vertex> [tree_name]
```

- `filename`: Path to graph JSON file
- `root_vertex`: Vertex ID to use as tree root
- `tree_name`: Optional name for the tree in the forest (defaults to root_vertex)

### Shell Workflow Example

```bash
# Start shell
$ python -m AlgoTree.shell.shell

# Create a tree structure
/ $ mktree servers
/ $ cd servers
/servers $ mkdir web tier=frontend port=80
/servers $ mkdir api tier=backend port=8080
/servers $ mkdir db tier=data port=5432
/servers $ cd api
/servers/api $ mkdir worker1 threads=4
/servers/api $ mkdir worker2 threads=8
/servers/api $ cd ..

# View tree
/servers $ tree
servers
+-- web
+-- api
|   +-- worker1
|   +-- worker2
+-- db

# Convert to graph for analysis
/servers $ tograph
Converted 'servers' to AlgoGraph:
  Vertices: 6
  Edges: 5
  Directed: True

# Save tree for later
/servers $ save servers.json

# Exit shell
/servers $ exit
```

---

## When to Use Trees vs Graphs

### Use Trees When:

- Data has natural parent-child hierarchy (file systems, org charts, DOM)
- Each element has exactly one parent
- No cycles exist in the relationships
- Navigation is primarily top-down or bottom-up
- Visualization as a hierarchical structure is important

### Use Graphs When:

- Elements can have multiple parents or connections
- Cycles may exist (dependencies, social networks)
- You need shortest path, centrality, or connectivity algorithms
- Relationships are peer-to-peer rather than hierarchical
- Bidirectional traversal is common

### Conversion Guidelines:

| Scenario | Recommendation |
|----------|----------------|
| Analyze tree structure with graph algorithms | Convert tree to graph |
| Visualize graph as hierarchy | Extract spanning tree |
| Serialize for JSON/YAML storage | Use flat dict format |
| Share data between AlgoTree and AlgoGraph | Use flat dict format |
| Find multiple paths in tree | Convert to undirected graph |
| Extract hierarchical view from network | Convert graph to tree |

---

## Common Issues and Troubleshooting

### ImportError: AlgoGraph not available

**Problem:** You see `ImportError: AlgoGraph is required for interop functions`.

**Solution:**
```bash
pip install algograph
```

Or add AlgoGraph to your PYTHONPATH:
```bash
export PYTHONPATH="/path/to/algograph:$PYTHONPATH"
```

### ValueError: Root vertex not in graph

**Problem:** The specified root vertex does not exist in the graph.

**Solution:** Verify the vertex ID exists:
```python
print(graph.has_vertex('my_root'))  # Should be True
print([v.id for v in graph.vertices])  # List all vertex IDs
```

### Cycle detected in flat dict

**Problem:** `ValueError: Cycle detected at node 'X'`

**Solution:** The flat dict has circular references. Trees cannot have cycles. Check your `.children` references:
```python
# Bad: A -> B -> A (cycle)
flat = {
    'A': {'.name': 'A', '.children': ['B']},
    'B': {'.name': 'B', '.children': ['A']},  # Points back to A
}

# Good: No cycles
flat = {
    'A': {'.name': 'A', '.children': ['B']},
    'B': {'.name': 'B', '.children': []},
}
```

### Empty flat dictionary

**Problem:** `ValueError: Empty flat dictionary`

**Solution:** Ensure the flat dict has at least one entry:
```python
flat = {'root': {'.name': 'root', '.children': []}}
```

### Child order differs after round-trip

**Problem:** Children appear in different order after tree -> graph -> tree conversion.

**Explanation:** Graph structures do not preserve child ordering. BFS traversal may visit neighbors in any order.

**Solution:** If order matters, sort children after conversion:
```python
def sort_children(node):
    sorted_children = tuple(
        sort_children(c) for c in sorted(node.children, key=lambda n: n.name)
    )
    return Node(node.name, *sorted_children, attrs=node.attrs)

recovered = graph_to_tree(graph, 'root')
ordered = sort_children(recovered)
```

### Disconnected vertices not in tree

**Problem:** Some vertices from the graph do not appear in the resulting tree.

**Explanation:** `graph_to_tree()` only includes vertices reachable from the root via BFS. Disconnected vertices are excluded.

**Solution:** Either:
1. Choose a different root that connects to all vertices
2. Process disconnected components separately:
```python
# Find all connected components
# Convert each component to a separate tree
```

---

## Summary

AlgoTree and AlgoGraph interoperability enables you to:

- **Convert trees to graphs** for analysis with graph algorithms
- **Extract spanning trees from graphs** for hierarchical visualization
- **Use flat dictionaries** as a portable interchange format
- **Preserve attributes** through round-trip conversions
- **Work interactively** using shell commands

The key functions to remember:

```python
from AlgoTree import (
    tree_to_graph,      # Node -> Graph
    graph_to_tree,      # Graph -> Node
    node_to_flat_dict,  # Node -> dict
    flat_dict_to_node,  # dict -> Node
)
```

For shell usage:
```bash
tograph [--undirected] [tree_name]       # Convert tree to graph
fromgraph <file> <root> [tree_name]      # Load graph as tree
```

---

## Next Steps

- Explore AlgoGraph's graph algorithms (shortest path, centrality, etc.)
- Combine with AlgoTree's transformers for powerful data pipelines
- Use flat dict format for data exchange with external systems
- Build hybrid tree/graph data models for complex relationships
