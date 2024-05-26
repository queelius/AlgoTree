from copy import deepcopy
from typing import List, Optional, Dict, Any

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

    DEFAULT_NAME_KEY = '__name__'
    """
    The default key used to store the name of a node.
    If the node does not contain a key with this name, the name is extracted
    from the data using the `payload` method.
    """

    DEFAULT_CHILDREN_KEY = 'children'
    """
    The default key used to store the children of a node.
    """

    def __init__(self,
                 *args,
                 children_key = DEFAULT_CHILDREN_KEY,
                 name_key = DEFAULT_NAME_KEY,
                 **kwargs):
        """
        Initialize a TreeNode.

        :param args: Positional arguments to initialize the TreeNode.
        :children_key: The key to use to store the children of the node.
        :param kwargs: Additional keyword arguments to initialize the TreeNode.
        """
        # Initialize the dict part with data and kwargs
        super().__init__(*args, **kwargs)

        self.children_key = children_key if children_key is not None else self.DEFAULT_CHILDREN_KEY
        self.name_key = name_key

        # Extract children from data if present
        children = self.pop(self.children_key, None)

        # Initialize children if present
        if children is not None:
            for child in children:
                self.add_child(child, children_key=children_key, name_key=name_key)

            #self[children_key] = [TreeNode(child, children_key=children_key, \
            #                               name_key=name_key) if \
            #                           not isinstance(child, TreeNode) else \
            #                            child for child in children]

    def __setitem__(self, key, value):
        if key == self.children_key:
            if not isinstance(value, list):
                value = [value]
            value = [TreeNode(child, children_key=self.children_key, name_key=self.name_key) if not isinstance(child, TreeNode) else child for child in value]
        super().__setitem__(key, value)
        

    @property
    def name(self) -> Optional[str]:
        """
        Get the name of the node.

        :return: The name of the node.
        """
        return self.get(self.name_key, self.payload)

    # let's allow for attribute access to the dictionary, read-only though
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError(f"TreeNode has no attribute '{name}'")

    @property
    def children(self) -> List['TreeNode']:
        """
        Get the children of a node.

        :return: List of child nodes (TreeNode objects).
        """
        return self.get(self.children_key, [])

    def add_child(self, *args, **kwargs) -> 'TreeNode':
        """
        Add a child node to the tree.

        :param args: Arguments to be passed to the TreeNode constructor for the child.
        :param kwargs: Keyword arguments to be passed to the TreeNode constructor for the child.
        :return: The newly added child node (TreeNode object).
        """

        child = TreeNode(*args, **kwargs)
        if self.children_key not in self:
            self[self.children_key] = []
        self[self.children_key].append(child)
        return child
    
    def remove_children(self, child: Optional[List['TreeNode']] = None) -> List['TreeNode']:
        """
        Remove a child node from the tree.

        :param child: The child node to remove.
        :return: None
        """

        if child is None:
            childs = deepcopy(self.children)
            if self.children_key in self:
                del self[self.children_key]
            return childs

        results : List['TreeNode'] = []
        for i, c in enumerate(self.children):
            if c == child:
                results.append(self[self.children_key].pop(i))

        return results

    def __repr__(self) -> str:
        return f"TreeNode({dict(self)})"

    @property
    def root(self) -> 'TreeNode':
        """
        Get the root of the tree.

        :return: The root node of the tree.
        """
        return self

    @property
    def payload(self) -> Dict:
        """
        Get the data (minus the children) stored in the tree.

        :return: The data stored in the tree.
        """
        return {k: v for k, v in self.items() if k != self.children_key}
