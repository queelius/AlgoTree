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

    NAME_KEY = '__name__'
    CHILDREN_KEY = 'children'

    def __init__(self, *args, **kwargs):
        """
        Initialize a TreeNode.

        :param key: The key to use for the node.
        :param data: The data to store in the node.
        :param kwargs: Additional keyword arguments to initialize the TreeNode.
        """
        # Initialize the dict part with data and kwargs
        super().__init__(*args, **kwargs)

        # Extract children from data if present
        children = self.pop(self.CHILDREN_KEY, None)
        
        # Initialize children if present
        if children is not None:
            self[self.CHILDREN_KEY] = [TreeNode(child) if \
                                       not isinstance(child, TreeNode) else \
                                        child for child in children]

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

    @property
    def name(self) -> str:
        """
        Get the name of the node.
    
        :return: The name of the node.
        """
        return self.get(TreeNode.NAME_KEY, str(self.get_data()))

    def __repr__(self) -> str:
        return f"TreeNode({dict(self)})"

    def get_root(self) -> 'TreeNode':
        """
        Get the root of the tree.

        :return: The root node of the tree.
        """
        return self

    def get_data(self) -> Dict:
        """
        Get the data (minus the children) stored in the tree.

        :return: The data stored in the tree.
        """
        return {k: v for k, v in self.items() if k != TreeNode.CHILDREN_KEY}