from collections import deque
from copy import deepcopy
from typing import List, Optional, Dict
import json

class TreeNode(dict):
    """
    A tree node class that is also a dictionary. This class stores a nested
    representation of the tree. Each node is a TreeNode object, and if a node
    is a child of another node, it is stored in the parent node as a key-value
    pair where the key is `children` and the value is a list of child nodes
    (TreeNode objects).

    This class is a wrapper around a dictionary, so it can be used as a dictionary
    as well as a tree. The tree structure is maintained by the `children` attribute
    of each node, and we provide methods to manipulate the tree structure.
    """

    NAME_KEY = '__name__'
    CHILDREN_KEY = 'children'

    def __init__(self, *args, **kwargs):
        """
        Initialize a TreeNode.

        :param args: Arguments to be passed to the dictionary constructor.
        :param kwargs: Keyword arguments to be passed to the dictionary constructor.
        """
        # Extract children from kwargs if present
        children = kwargs.pop(TreeNode.CHILDREN_KEY, None)

        # Initialize the dict part
        super().__init__(*args, **kwargs)
        
        # Only add the 'children' key if it was present in the kwargs
        if children is not None:
            self[TreeNode.CHILDREN_KEY] = [TreeNode(child) if not isinstance(child, TreeNode) else child for child in children]

    def children(self) -> List['TreeNode']:
        """
        Get the children of a node.

        :return: List of child nodes (TreeNode objects).
        """
        return self.get(TreeNode.CHILDREN_KEY, [])

    def add_child(self, *args, **kwargs) -> 'TreeNode':
        """
        Add a child node to the tree.

        :param args: Arguments to be passed to the TreeNode constructor for the child.
        :param kwargs: Keyword arguments to be passed to the TreeNode constructor for the child.
        :return: The newly added child node (TreeNode object).
        """
        child = TreeNode(*args, **kwargs)
        if TreeNode.CHILDREN_KEY not in self:
            self[TreeNode.CHILDREN_KEY] = []
        self[TreeNode.CHILDREN_KEY].append(child)
        return child

    def __repr__(self) -> str:
        return f"TreeNode({dict(self)})"

    def get_root(self) -> 'TreeNode':
        """
        Get the root of the tree.

        :return: The root node of the tree.
        """
        return self

    def depth_first(self, fn, ctx=None, order='post', max_depth=None):
        """
        Applies a function `fn` to the nodes in the tree using depth-first traversal.

        :param fn: Function to apply to each node. Should accept two arguments: the node and the context.
        :param ctx: Optional context data to pass to the function.
        :param order: The order in which the function is applied ('pre' or 'post'). Default is 'post'.
        :param max_depth: Maximum depth to traverse. If None, traverses the entire tree.
        :return: The tree with the function `fn` applied to its nodes.
        """
        def _walk(node, ctx, depth):
            if max_depth is not None and depth > max_depth:
                return node
            ctx = deepcopy(ctx)
            if order == 'pre':
                node = fn(node, ctx)
            node[TreeNode.CHILDREN_KEY] = [_walk(c, ctx, depth + 1) for c in node.children()]
            if order == 'post':
                node = fn(node, ctx)
            return node

        return _walk(self, ctx, depth=0)
