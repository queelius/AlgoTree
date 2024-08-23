# TODO

- `TreeDot`: I may want to create a tree structure called `TreeDot` that wraps any tree-like structure that models the node-centric API, and is specialized for visualization. But, no compelling reason to do this yet, so I'll leave it as a TODO.

- `jsontree.py` command line tool should be expanded. It is based mostly on piping and redirection. For any operation that modifies
the tree, it will output the modified tree as a JSON string. This also allows it to be used with other tools, like `jq` for filtering and selecting.
Since it also has a nice looking unicode tree output, it can be used to visualize trees in the
terminal as well. I have something like this in mind:

      - `jsontree --edit` - edit a JSON tree

      - `jsontree --merge` - merge two JSON trees using `TreeConverter`.

      - `json-tree --filter` - filter a JSON tree 

      - `json-tree --query` - query a JSON tree.maybe this one can use JMESPath for querying and also be able to output node paths (search orders) and subtrees.
