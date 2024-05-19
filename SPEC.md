# DictTree Specification

The dict (or JSON) data should have the following structure:

```json
{
    // Any key-value pairs *not* in the mapping is metadata.
    // Under the hood, we store metadata in the root node, which is a "dummy" node
    // that always exists with the unique key that by default has the value
    // "__root__".
    "<key>": "<value>", // ... more key-value pairs

    "<mapping_key>": {
        "<node_key>": {
            // Parent node key (optional). If blank, we assume it connects to the root node.
            // The root node is a "dummy" node that always exists with a key
            // that is not present in the JSON data, e.g., "root".
            "parent": "<parent_node_key>",
                
            // Node payload (optional key-value pairs)
            "<key>": "<value>" // ... more key-value pairs
        }
        // ... more node key-value pairs
    }
}
```

where:

- <mapping_key> is the key in the JSON that maps to the structure of the tree.
  - Default mapping key is "mapping".
- <node_key> is the key (unique name or label) of a node.
  - Must be unique within the tree.
- <parent_node_key> is the key of the parent node.
  - If a node has no parent key specified, its parent is the root node.
  - The root node is a "dummy" node and the payload of the root node
    is the "metadata" of the tree.
- The payload of a node is a dictionary of key-value pairs.
  - The payload can be any JSON-serializable data.
  - When we refer to the "data" of a node, we mean the payload of the node.
  - node['payload'] is where we store the payload.

