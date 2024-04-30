# Python package: `treekit`

`treekit` is a Python toolkit for creating, managing, and visualizing tree structures derived from JSON and dictionary data.

## Installation

Clone this repository and run:

```bash
pip install .
```

## Usage

We have a JSON file that represents a tree structure:

```json
{
    "metadata": {
        "author": "John Doe",
        "version": "1.0"
    },
    "mapping": {
        "node1": {
            "parent": "root",
            "children": ["node2", "node3"],
            "data": "Some data for node1"
        },
        "node2": {
            "parent": "node1",
            "children": [],
            "data": "Some data for node2"
        },
        "node3": {
            "parent": "node1",
            "children": [],
            "data": "Some data for node3"
        }
    }
}
```

To convert this JSON to a visual tree structure:

```bash
./jsontree.py tree.json
# node1
# ├── node2
# └── node3
```

Here is another example:

```bash
./jsontree.py \
    --mapping-key "mapping" \
    --node-name "lambda n: f'{n.name}: {n.payload[\"data\"]}'" tree.json 
# node1: Some data for node1
# ├── node2: Some data for node2
# └── node3: Some data for node3
```

For more options, you can use the help command:

```bash
./jsontree.py --help
# usage: jsontree.py [-h]
#           [--flatten]
#           [--log {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
#           [--output OUTPUT]
#           [--fallback-node-name FALLBACK_NODE_NAME]
#           [--node-name NODE_NAME]
#           [--json-spec]
#           [--version]
#           [--mapping-key MAPPING_KEY]
#           [file]
#
# Render a tree from JSON data
#
# positional arguments:
#  file                  Path to JSON file
#
# options:
#   -h, --help            show this help message and exit
#   --flatten             Flatten the tree (list of paths)
#   --log {DEBUG,INFO,WARNING,ERROR,CRITICAL}
#                         Log level
#   --output OUTPUT       Output file name
#   --fallback-node-name FALLBACK_NODE_NAME
#                         Fallback function to generate node names
#   --node-name NODE_NAME
#                         Function to generate node names
#   --json-spec           Specification of the JSON data
#   --version             show program's version number and exit
#   --mapping-key MAPPING_KEY
#                         The key that maps to the structure of the tree
```

## `dicttree` Class

The `DictTree` class is a Python class that can be used to create tree structures from dictionary data. It can be used to create a tree structure from a dictionary, add nodes to the tree, and visualize the tree.

This is the main workhorse of the `jsontree` command line tool.

```python
from treekit import dicttree
# Load a tree from a JSON file and save it as a PNG file
tree = DictTree(json.load("tree.json")).save("tree.png")
```

This generates the PNG file `tree.png`:

![Tree](tree.png)

## Development

To set up a development environment:

1. Clone the repository.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
