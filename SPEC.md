# DictTree Specification

The dict (or JSON) data should have the following structure:

```json
{
    // Meta-data (optional key-value pairs)
    "<key>": "<value>", ...

    "<mapping_key>": {
        "<node_key>": {
            // Parent node key (optional)
            "parent": "<parent_node_key>",

            // Children node keys (optional)
            "children": [
                "<child_node_key>", ...
            ],
                
            // Node data (optional key-value pairs)
            "<key>": "<value>", ...
        },

        // More node key-value pairs
        ...
    }
}
```

where:

- <mapping_key> is the key in the JSON that maps to the structure of the tree. Default is "mapping".
- <node_key> is the key of the node.
- <parent_node_key> is the key of the parent node.
- <child_node_key> is the key of a child node.
- Additional key-value pairs can be added to each node to store arbitrary data.
- The JSON data can have additional key-value pairs for meta-data, such as the name of the tree.
- You can also create the tree structure using the `DictTree` class directly, e.g.,
  `tree.add_node("node1", parent="root", data="Some data for node1")`.
  `tree.get_node("node2").parent = tree.get_node("node1")`.