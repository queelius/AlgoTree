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
    "author": "John Doe",
    "version": "1.0"
    "mapping": {
        "node1": {
            // no parent specified, will connect to the root node
            "data": "Some data for node1"
        },
        "node2": {
            "parent": "node1",
            "data": "Some data for node2",
            "more_data": "More data"
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
# __root__
# └── node1
#     ├── node2
#     └── node3
```

Here is another example:

```bash
./jsontree-view.py \
    --node-name "lambda n: f'{n.name}: {n.payload}'" tree.json 

# __root__: { "author": "John Doe", "version": "1.0" }
# └── node1: { "data": "Some data for node1" }
# ├── node2: { "data": "Some data for node2", "more_data": "More data" }
# └── node3: { "data": "Some data for node3" }
```

For more options, you can use the help command:

```bash
./jsontree-view.py --help
```

## `DictTree` Class

`DictTree` is a Python class that can be used to create tree structures from
dictionary (or JSON) data. It provides a robust API for creating, editing,
searching/querying, and viewing/visualizing tree structures.

This is what the command line tools use for most of the heavy lifting.

```python
from treekit import DictTree
# Load a tree from a JSON file and save it as a PNG file
DictTree(json.load("tree.json")).save("tree.png")
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
