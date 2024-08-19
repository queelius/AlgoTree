# TODO

- Found a bug with subtree and node for `FlatTreeNode`. It seems to point
  to the current current node, but not the current root. It points to the
  main root still. This is a problem because I want to be able to use
  `FlatTreeNode` as a way to traverse the tree and get the subtree of the
  current node.

- Most of the functions in `AlgoTree.utils` module should not use `node.root`,
  but `node`. `node.root` can always be passed as an argument if needed, and
  any functions that need both `node` and `node.root` should work just fine
  after a bit of refactoring.

  This is an issue I may have to revisit, but I think it makes sense to
  continue to situate a node within the context of its subtree, but by default
  have the operations use the node itself, even for the subtree operations.

- `PrettyTree`: Replaces `TreeViz`. It's a simple class that
  provides a pretty-printed version of the tree. Highly customizable and more
  user-friendly than `TreeViz`. Removes dependency on `graphviz` and `anytree`.

- `TreeDot`: I may want to create a tree structure called `TreeDot` that
  wraps any tree-like structure that models the node-centric API, and
  is specialized for visualization. But, no compelling reason to do this
  yet, so I'll leave it as a TODO.

- `json-tree.py` command line tool. I call it `json-tree` because it works over
  JSON representations of trees, either `FlatTree` or `TreeNode` (autodetect).
  It is based mostly on piping and redirection. For any operation that modifies
  the tree, it will output the modified tree as a JSON string. This also allows
  it to be used with other tools, like `jq` for filtering and selecting.

  on the command line via piping and redirection. Since it also has a nice
  looking unicode tree output, it can be used to visualize trees in the
  terminal as well. I have something like this in mind:

      - `json-tree-view` - view a JSON tree (use with `jq` for filtering
                           and selecting and pretty-json). I will also use
                          JSMEPath for querying and computing new views.

      - `json-tree-edit` - edit a JSON tree

      - `json-tree-convert` - convert to different kinds of mapping formats
                              I have `FlatTree` and `TreeNode` in mind.

      - `json-tree-stats` - get statistics on a JSON tree. This will output
                            non-tree JSON data, so it can be seen as a final
                            output of the tree, or a summary of the tree,
                            same as `json-tree-pretty`.

      - `json-tree-pretty` - pretty print a JSON tree using `PrettyTree`.
                             Note that this is different from `json-tree-view`.
                             `json-tree-view` will also allow for marking
                             nodes, that may be used by this pretty printer,
                             in a chain of commands.

      - `json-tree-merge` - merge two JSON trees using `TreeConverter`.

      - `json-tree-filter` - filter a JSON tree 

      - `json-tree-search` - search a JSON tree -- maybe this one can use
                              JMESPath for querying and also be able to output
                              node paths (search orders) and subtrees.
