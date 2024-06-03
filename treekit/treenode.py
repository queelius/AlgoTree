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
    """
    The key used to store the name of a node. It does not need to exist in the
    dictionary, but if it is present, it will be used as the name of the node.
    """

    CHILDREN_KEY = 'children'
    """
    The key used to store the children of a node.
    """

    def __init__(self,
                 *args,
                 parent: Optional['TreeNode'] = None,
                 name: Optional[str] = None,
                 **kwargs):
        """
        Initialize a TreeNode.

        :param args: Positional arguments to initialize the TreeNode.
        :param parent: The parent node of the current node. Default is None.
        :param name: The name of the node. Default is None.
        :param kwargs: Additional keyword arguments to initialize the TreeNode.
        """
        # Initialize the dict part with data and kwargs
        super().__init__(*args, **kwargs)

        if name is not None:
            self[TreeNode.NAME_KEY] = name

        children = self.pop(TreeNode.CHILDREN_KEY, None)
        # Initialize children if present
        if children is not None:
            self[TreeNode.CHILDREN_KEY] = [ TreeNode(child) if
                not isinstance(child, TreeNode) else child for child in children]

        if parent is not None:
            if TreeNode.CHILDREN_KEY not in parent:
                parent[TreeNode.CHILDREN_KEY] = []
            parent[TreeNode.CHILDREN_KEY].append(self)

    def __setitem__(self, key, value):
        if key == TreeNode.CHILDREN_KEY:
            if not isinstance(value, list):
                value = [value]
            value = [TreeNode(child) if not
                     isinstance(child, TreeNode) else child for child in value]
        super().__setitem__(key, value)
        

    @property
    def name(self) -> Optional[str]:
        """
        Get the name of the node.

        :return: The name of the node.
        """
        return self.get(TreeNode.NAME_KEY, hash(str(self.payload)))

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
        return self.get(TreeNode.CHILDREN_KEY, [])

    def add_child(self, name: Optional[str] = None, *args, **kwargs) -> 'TreeNode':
        """
        Add a child node to the tree.

        :param args: Arguments to be passed to the TreeNode constructor for the child.
        :param kwargs: Keyword arguments to be passed to the TreeNode constructor for the child.
        :return: The newly added child node (TreeNode object).
        """
        return TreeNode(*args, parent=self, name=name, **kwargs)
    
    def remove_children(self, child: Optional[List['TreeNode']] = None) -> List['TreeNode']:
        """
        Remove a child node from the tree.

        :param child: The child node to remove.
        :return: The removed child nodes (List of TreeNode objects).
        """
        if child is None:
            if TreeNode.CHILDREN_KEY in self:
                childs = deepcopy(self.children)
                del self[TreeNode.CHILDREN_KEY]
                return childs
            else:
                return []

        results : List['TreeNode'] = []
        for i, c in enumerate(self.children):
            if c == child:
                results.append(self[TreeNode.CHILDREN_KEY].pop(i))
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
        return {k: v for k, v in self.items() if k != TreeNode.CHILDREN_KEY}
