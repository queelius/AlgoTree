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

    def __init__(self, *args, **kwargs):
        """
        Initialize a TreeNode.

        :param args: Arguments to be passed to the dictionary constructor.
        :param kwargs: Keyword arguments to be passed to the dictionary constructor.
        """
        # Extract children from kwargs if present
        children = kwargs.pop('children', None)

        # Initialize the dict part
        super().__init__(*args, **kwargs)
        
        # Only add the 'children' key if it was present in the kwargs
        if children is not None:
            self['children'] = [TreeNode(child) if not isinstance(child, TreeNode) else child for child in children]

    def children(self) -> List['TreeNode']:
        """
        Get the children of a node.

        :return: List of child nodes (TreeNode objects).
        """
        return self.get('children', [])

    def add_child(self, *args, **kwargs) -> 'TreeNode':
        """
        Add a child node to the tree.

        :param args: Arguments to be passed to the TreeNode constructor for the child.
        :param kwargs: Keyword arguments to be passed to the TreeNode constructor for the child.
        :return: The newly added child node (TreeNode object).
        """
        child = TreeNode(*args, **kwargs)
        if 'children' not in self:
            self['children'] = []
        self['children'].append(child)
        return child

    def height(self) -> int:
        """
        Get the height of the tree.

        :return: Integer representing the height of the tree.
        """
        return 1 + max([c.height() for c in self.children()], default=0)

    def width(self) -> int:
        """
        Get the width of the tree.

        :return: Integer representing the width of the tree.
        """
        return max([1 + c.width() for c in self.children()], default=0)

    def is_leaf(self) -> bool:
        """
        Determine if a node is a leaf.

        :return: True if the node is a leaf, False otherwise.
        """
        return not self.children()

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
            node['children'] = [_walk(c, ctx, depth + 1) for c in node.children()]
            if order == 'post':
                node = fn(node, ctx)
            return node

        return _walk(self, ctx, depth=0)

    def search(self, key, value=None) -> Optional['TreeNode']:
        """
        Search for a node by a specific key and value. Returns the first node
        that matches the key and value, or None if not found.

        If value is None, the search will return the first node that has the key
        regardless of the value.

        :param key: The key to search for.
        :param value: The value to search for.
        :return: The first node that matches the key and value, or None if not found.
        """
        if value is None:
            if key in self:
                return self
        elif self.get(key) == value:
            return self

        for child in self.children():
            result = child.search(key, value)
            if result:
                return result

        return None

    def get_parent(self) -> Optional['TreeNode']:
        """
        Get the parent of a node.

        :return: The parent node (TreeNode) if it exists, None otherwise.
        """
        # we must iterate through the entire tree to find the parent
        # using a depth-first search

        def _find_parent(node, parent):
            if node is self:
                return parent
            for child in node.children():
                result = _find_parent(child, node)
                if result:
                    return result
            return None

        return _find_parent(self, None)
    
    def name(self):
        """
        Get the name of the node.

        :return: The name of the node.
        """
        return self.get('__name__', hash(json.dumps((self))))

    def remove(self, key, value=None) -> Optional['TreeNode']:
        """
        Remove a node from the tree by a specific key and value. Removes the
        first node that matches the key and value, or None if not found.

        If value is None, the search will remove the first node that has the key
        regardless of the value.

        :param key: The key to identify the node to be removed.
        :param value: The value to identify the node to be removed.
        :return: The removed node (TreeNode) if found and removed, None otherwise.
        """
        for i, child in enumerate(self.children()):
            if value is None:
                if key in child:
                    return self['children'].pop(i)
            else:
                if child.get(key) == value:
                    return self['children'].pop(i)
            result = child.remove(key, value)
            if result:
                return result

        return None