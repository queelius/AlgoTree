from typing import Any

class TreeNodeApi:
    """
    A class to check if a tree object models the concept of a tree node.
    The tree node concept is defined as follows:

    - **children** property

        Represents a list of child nodes for the current node that can be
        accessed and modified.

    - **parent** property
    
        Represents the parent node of the current node that can be accessed
        and modified. 
        
        Suppose we have the subtree `G` at node `G`::

                B (root)
                ├── D
                └── E (parent)
                    └── G (current node)

        Then, `G.parent` should refer node `E`. `G.root.parent` should be None
        since `root` is the root node of subtree `G` and the root node has no parent.
        This is true even if subtree `G` is a subtree view of a larger tree.

        If we set `G.parent = D`, then the tree structure changes to::

                B (root)
                ├── D
                │   └── G (current node)
                └── E
        
        This also changes the view of the sub-tree, since we changed the
        underlying tree structure. However, the same nodes are still accessible
        from the sub-tree.

        If we had set `G.parent = X` where `X` is not in the subtree `G`, then
        we would have an invalid subtree view even if is is a well-defined
        operation on the underlying tree structure. It is undefined
        behavior to set a parent that is not in the subtree, but leave it
        up to each implementation to decide how to handle such cases.

    - **node(name: str) -> NodeType** method.

        Returns a node in the current subtree that the
        current node belongs to. The returned node should be the node with the
        given name, if it exists. If the node does not exist, it should raise
        a `KeyError`.

        The node-centric view of the returned node should be consistent with the
        view of the current node, i.e., if the current node belongs to a specific sub-tree
        rooted at some other node, the returned node should also belong to the
        same sub-tree (i.e., with the same root), just pointing to the new node,
        but it should be possible to use `parent` and `children` to go up and down
        the sub-tree to reach the same nodes. Any node that is an ancestor of the
        root of the sub-tree remains inaccessible.

        Example: Suppose we have the sub-tree `t` rooted at `A` and the current node
        is `B`::

                A (root)
                ├── B (current node)
                │   ├── D
                │   └── E
                |       └── G
                └── C
                    └── F
        
        If we get node `F`, `t.node(F)`, then the sub-tree `t` remains the same,
        but the current node is now `F`::
        
                A (root)
                ├── B
                │   ├── D
                │   └── E
                |       └── G
                └── C
                    └── F (current node)

    - **subtree(node: Optional[NodeType] = None) -> NodeType** method.

        Returns a view of another sub-tree rooted at `node` where `node` is
        contained in the original sub-tree view. If `node` is `None`, the method
        will return the sub-tree rooted at the current node.
        
        `subtree` is a *partial function* over the the nodes in the sub-tree,
        which means it is only well-defined when `node` is a descendant of
        the root of the sub-tree. We do not specify how to deal with the case
        when this condition is not met, but one approach would be to raise an
        exception.

        Example: Suppose we have the sub-tree `t` rooted at `A` and the current node
        is `C`::

                A (root)
                ├── B
                │   ├── D
                │   └── E
                |       └── G
                └── C (current node)
                    └── F

        The subtree `t.subtree(B)` returns a new subtree::

                B (root, current node)
                ├── D
                └── E
                    └── G
        
    - **root** property

        An immutable property that represents the root node of the sub-tree.
        
        Suppose we have the subtree `G` at node `G`::

                B (root)
                ├── D
                └── E
                    └── G (current node)

        Then, `G.root` should refer node `B`.

    - **payload** property

        Returns the payload of the current node. The payload
        is the data associated with the node but not with the structure of the
        tree, e.g., it does not include the `parent` or `children` of the node.

    - **name** property

        Returns the name of the current node. The name is
        an identifier for the node within the tree. It is not necessarily unique,
        and nor is it necessarily even a meaningful identifier, e.g., a random
        UUID.

    - **contains(name) -> bool** method.

        Returns `True` if the sub-tree contains a node with the given name,
        otherwise `False`.
    """

    properties = ["name", "root", "children", "parent", "node", "subtree", "payload", "contains"]

    @staticmethod
    def missing(node, require_props = properties):

        if node is None:
            raise ValueError("node must not be None")
        
        missing_props = []
        for prop in require_props:
            if not hasattr(node, prop):
                missing_props.append(prop)
        return missing_props
        
    @staticmethod
    def check(node, require_props = properties) -> Any:

        missing_prop = TreeNodeApi.missing(node, require_props)
        if len(missing_prop) > 0:
            raise ValueError(f"missing properties: {missing_prop}")
        return node

    @staticmethod
    def is_valid(value, require_props = properties) -> bool:
        try:
            TreeNodeApi.check(value, require_props)
        except ValueError:
            return False
        return True
