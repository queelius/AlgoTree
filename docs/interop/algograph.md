# AlgoGraph Interoperability

AlgoTree provides seamless interoperability with [AlgoGraph](https://github.com/queelius/AlgoGraph), enabling conversion between tree and graph representations.

## Installation

AlgoGraph is an optional dependency:

```bash
pip install AlgoGraph
```

## Converting Trees to Graphs

Use `tree_to_graph()` to convert a tree to a graph:

```python
from AlgoTree import Node, tree_to_graph

# Create a tree
tree = Node('root',
    Node('child1', attrs={'value': 10}),
    Node('child2', attrs={'value': 20})
)

# Convert to graph
graph = tree_to_graph(tree)

# The graph contains all nodes as vertices
print(graph.vertex_count)  # 3

# And parent-child edges
print(graph.edge_count)    # 2
```

### Options

```python
# Directed edges (default)
graph = tree_to_graph(tree, directed=True)

# Undirected edges
graph = tree_to_graph(tree, directed=False)
```

## Converting Graphs to Trees

Use `graph_to_tree()` to extract a spanning tree from a graph:

```python
from AlgoGraph import Graph, Vertex, Edge
from AlgoTree import graph_to_tree

# Create a graph
v1, v2, v3 = Vertex('A'), Vertex('B'), Vertex('C')
e1, e2 = Edge('A', 'B'), Edge('A', 'C')
graph = Graph({v1, v2, v3}, {e1, e2})

# Convert to tree (specify root)
tree = graph_to_tree(graph, 'A')

print(tree.name)          # 'A'
print(len(tree.children)) # 2
```

### Notes on Graph-to-Tree Conversion

- Requires specifying a root vertex
- Uses BFS traversal to build spanning tree
- Cycles in the graph are broken
- All vertices reachable from root are included

## Flat Dictionary Format

Both libraries support a flat dictionary format for interoperability:

### Tree to Flat Dict

```python
from AlgoTree import Node, node_to_flat_dict

tree = Node('A',
    Node('B'),
    Node('C', attrs={'value': 10})
)

flat = node_to_flat_dict(tree)
# {
#   'A': {'.name': 'A', '.children': ['B', 'C']},
#   'A/B': {'.name': 'B', '.children': []},
#   'A/C': {'.name': 'C', '.children': [], 'value': 10}
# }
```

### Flat Dict to Tree

```python
from AlgoTree import flat_dict_to_node

flat = {
    'A': {'.name': 'A', '.children': ['B', 'C'], 'value': 10},
    'B': {'.name': 'B', '.children': []},
    'C': {'.name': 'C', '.children': []}
}

tree = flat_dict_to_node(flat, root_key='A')
print(tree.name)  # 'A'
print(tree.get('value'))  # 10
```

### Auto-detecting Root

```python
# Root is auto-detected if not specified
tree = flat_dict_to_node(flat)
```

## Tree Wrapper Functions

For `Tree` objects:

```python
from AlgoTree import Tree, tree_to_flat_dict, flat_dict_to_tree

tree = Tree(Node('root', Node('a'), Node('b')))

# To flat dict
flat = tree_to_flat_dict(tree)

# From flat dict
tree = flat_dict_to_tree(flat)
```

## Format Details

The flat dictionary format uses:

- **Keys**: Node identifiers (with path prefix for duplicates)
- **`.name`**: Original node name
- **`.children`**: List of child node names
- **Other keys**: Node attributes

Example:
```json
{
  "root": {
    ".name": "root",
    ".children": ["child1", "child2"],
    "type": "directory"
  },
  "root/child1": {
    ".name": "child1",
    ".children": [],
    "type": "file"
  },
  "root/child2": {
    ".name": "child2",
    ".children": [],
    "type": "file"
  }
}
```

## Round-Trip Conversion

Trees can be converted to graphs and back:

```python
from AlgoTree import Node, tree_to_graph, graph_to_tree

# Original tree
original = Node('root',
    Node('a', attrs={'value': 1}),
    Node('b', attrs={'value': 2})
)

# Convert to graph and back
graph = tree_to_graph(original)
recovered = graph_to_tree(graph, 'root')

# Structure and attributes preserved
assert recovered.name == original.name
assert len(recovered.children) == len(original.children)
```

## Use Cases

### Graph Algorithms on Trees

```python
from AlgoTree import tree_to_graph

# Convert tree to graph for graph algorithms
graph = tree_to_graph(tree)

# Use AlgoGraph's algorithms
shortest_path = graph.shortest_path('root', 'leaf')
connected = graph.is_connected()
```

### Tree View of Graphs

```python
from AlgoTree import graph_to_tree, pretty_tree

# Extract spanning tree from graph
tree = graph_to_tree(graph, 'start_node')

# Visualize as tree
print(pretty_tree(tree))
```

### Data Exchange

```python
from AlgoTree import node_to_flat_dict, flat_dict_to_node
import json

# Serialize tree
flat = node_to_flat_dict(tree)
json_str = json.dumps(flat)

# Deserialize
flat = json.loads(json_str)
tree = flat_dict_to_node(flat)
```

## API Reference

| Function | Description |
|----------|-------------|
| `tree_to_graph(node, directed)` | Convert tree to AlgoGraph |
| `graph_to_tree(graph, root_id)` | Extract tree from graph |
| `node_to_flat_dict(node)` | Convert node to flat dict |
| `flat_dict_to_node(flat, root)` | Convert flat dict to node |
| `tree_to_flat_dict(tree)` | Convert Tree to flat dict |
| `flat_dict_to_tree(flat, root)` | Convert flat dict to Tree |
