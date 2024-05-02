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
            "data": "Some data for node1"
        },
        "node2": {
            "parent": "node1",
            "data": "Some data for node2"
        },
        "node3": {
            "parent": "node1",
            "data": "Some data for node3"
        }
    }
}
```

To convert this JSON to a visual tree structure:

```bash
./bin/jsontree-view.py tree.json
# node1
# ├── node2
# └── node3
```

Here is another example:

```bash
./jsontree-view.py \
    --mapping-key "mapping" \
    --node-name "lambda n: f'{n.name}: {n.data}'" tree.json 
# node1: Some data for node1
# ├── node2: Some data for node2
# └── node3: Some data for node3
```

For more options, you can use the help command:

```bash
./jsontree-view.py --help
```

## `DictTree` Class

`DictTree` is a Python class that can be used to create tree structures from dictionary (or JSON) data. It provides a robust API for creating, managing, and visualizing tree structures.

This is the main workhorse for the set of `jsontree-*.py` command line tools.

```python
from treekit import DictTree
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
