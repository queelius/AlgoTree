# FlatTree Specification

The dict (or JSON) data should have the following structure:

```json
{
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

- <node_key> is the key (unique name or label) of a node.
  - Must be unique within the tree.
- <parent_node_key> is the key of the parent node.
  - If a node has no parent key specified, its parent is the logical root node.
  - TODO: Considering allowing an alternative way of loading the tree from JSON.
    - Have a dictionary with a `mapping` key that defines the tree structure.
    - However, outside the mapping key, all of that data is the payload of the
      logical root node. We will make the logical root node mutable so that
      the metadata can be modified.
    - This will coexist with the current format.
  - The root node is a "dummy" node and the payload of the root node
    is the "metadata" of the tree.
- The payload of a node is a dictionary of key-value pairs.
  - The payload can be any dictionary.
  - When we refer to the "data" of a node, we mean the payload of the node.
  - node["<key>"'] refers to the value of the key in the node's payload.
  
We expose a tree API that allows you to work within the domain of the tree,
but the underlying dictionary (which the tree has an is-a relationship with)
can be directly modified too. The tree API is a convenience layer on top of
the dictionary.

Here is what the newer format looks like:

```json
{
  "<key>": "<value>",
  // as many more key-value pairs (meta-data or payload of logical root)
  "mapping": {
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


