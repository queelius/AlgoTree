# DictTree Specification

The dict (or JSON) data should have the following structure:

```json
{
    // Meta-data (optional key-value pairs)
    "<key>": "<value>", // ... more key-value pairs

    "<mapping_key>": {
        "<node_key>": {
            // Parent node key (optional)
            "parent": "<parent_node_key>",

            // Children node keys (optional)
            "children": [
                "<child_node_key>" // ... more child node keys
            ],
                
            // Node payload (optional key-value pairs)
            "<key>": "<value>" // ... more key-value pairs
        }

        // ... more node key-value pairs
    }
}
```

where:

- <mapping_key> is the key in the JSON that maps to the structure of the tree. Default is "mapping".
- <node_key> is the key of the node.
- <parent_node_key> is the key of the parent node.
- <child_node_key> is the key of a child node.
- If a node has no parent key specified, it is assumed to be the root node.
- If a node has no children key specified, it is assumed to be a leaf node.
- There is, however, only one root node, which either may be specified
- Additional key-value pairs can be added to each node to store arbitrary data.
- The JSON data can have additional key-value pairs for meta-data, such as the name of the tree.
- You can also create the tree structure using the `DictTree` class directly, e.g.,
  `tree.add_node("node1", parent="root", data="Some data for node1")`.
  `tree.get_node("node2").parent = tree.get_node("node1")`.