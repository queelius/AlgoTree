from typing import Dict, List, Optional, Union, Any, Callable
import copy
from AlgoTree.utils import find_node
from AlgoTree.node_hash import NodeHash

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

    NAME_KEY = "__name__"
    """
    The key used to store the name of a node. It does not need to exist in the
    dictionary, but if it is present, it will be used as the name of the node.
    """

    CHILDREN_KEY = "children"
    """
    The key used to store the children of a node.
    """

    @classmethod
    def check_valid(cls, node: "TreeNode") -> None:
        """
        Check if the node is a valid tree.

        Raises an appropriate exception if the tree is invalid in any way.

        :param node: The node to check.
        :raises ValueError: If the tree is invalid.
        """

        def _check_cycle(key, visited):
            key = hash(str(node))
            if key in visited:
                raise ValueError(f"Cycle detected: {visited}")
            visited.add(key)
            _check_cycle(node.parent, visited)

        _check_cycle(node, set())

    def clone(self, parent=None) -> "TreeNode":
        """
        Clone the current node and all its children.

        :param parent: The parent of the new node.
        :return: A new TreeNode object with the same data as the current node.
        """
        dict_node = copy.deepcopy(dict(self))
        new_node = TreeNode(dict_node)
        new_node.parent = parent
        return new_node

    def __init__(
        self,
        *args,
        parent: Optional["TreeNode"] = None,
        name: Optional[str] = None,
        hash_fn: Callable[["TreeNode"], int] = None,
        **kwargs
    ):
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

        if hash_fn is None:
            hash_fn = NodeHash.node_hash
        
        if not callable(hash_fn):
            raise ValueError("hash_fn must be callable")
        
        self._hash_fn = hash_fn

        children = self.pop(TreeNode.CHILDREN_KEY, None)
        # Initialize children if present
        if children is not None:
            self[TreeNode.CHILDREN_KEY] = [
                TreeNode(child) if not isinstance(child, TreeNode) else child
                for child in children
            ]
        self._parent = None
        self.parent = parent

    @property
    def parent(self) -> Optional["TreeNode"]:
        """
        Get the parent of the node.

        :return: The parent of the node.
        """
        return self._parent

    @parent.setter
    def parent(self, parent: Optional["TreeNode"]) -> None:
        """
        Set the parent of the node.

        :param parent: The new parent of the node.
        """
        #if self._root == self:
        #    raise ValueError("Cannot set parent of root node of subtree")

        if self._parent is not None:
            self._parent.children = [
                child for child in self._parent.children if child != self
            ]
        self._parent = parent
        if parent is not None:
            if TreeNode.CHILDREN_KEY not in parent:
                parent[TreeNode.CHILDREN_KEY] = []
            parent[TreeNode.CHILDREN_KEY].append(self)

    @property
    def root(self) -> "TreeNode":
        """
        Get the root of the tree.

        :return: The root node of the tree.
        """
        node = self
        while node.parent:
            node = node.parent
        return node

    @property
    def payload(self) -> Dict:
        """
        Get the data (minus the children) stored in the tree.

        :return: The data stored in the tree.
        """
        return {
            k: v
            for k, v in self.items()
            if k != TreeNode.CHILDREN_KEY and k != TreeNode.NAME_KEY
        }

    @payload.setter
    def payload(self, data: Dict) -> None:
        """
        Set the data (minus the children) stored in the tree.

        :param data: The data to store in the tree.
        """
        if TreeNode.CHILDREN_KEY in data:
            raise ValueError("Cannot set children using payload setter")
        
        if TreeNode.NAME_KEY in data:
            raise ValueError("Cannot set name using payload setter")

        children = self.pop(TreeNode.CHILDREN_KEY, None)
        self.clear()
        if children is not None:
            self[TreeNode.CHILDREN_KEY] = children
        self.update(data)

    def __setitem__(self, key, value):
        if key == TreeNode.CHILDREN_KEY:
            if not isinstance(value, list):
                value = [value]
            value = [
                TreeNode(child) if not isinstance(child, TreeNode) else child
                for child in value
            ]
        super().__setitem__(key, value)

    def __getitem__(self, key):
        if key == TreeNode.CHILDREN_KEY:
            return self.get(key, [])
        return super().__getitem__(key)

    def __getattr__(self, key):
        if key in ["parent", "root", "payload", "name", "children"]:
            return object.__getattribute__(self, key)
        if key in self:
            return self[key]
        return None
    
    
    def node(self, name: str) -> "TreeNode":
        """
        Get the node with the given name in the current sub-tree. The sub-tree
        remains the same, we just change the current node position. If the name
        is not found, raise a KeyError.

        :param name: The name of the node.
        :return: The node with the given name.
        """
        new_node = find_node(self, lambda n, **_: n.name == name)
        if new_node is None:
            raise KeyError(f"Node not found: {name}")
        return new_node

    @property
    def name(self) -> Optional[str]:
        """
        Get the name of the node.

        :return: The name of the node.
        """
        if TreeNode.NAME_KEY in self:
            return self[TreeNode.NAME_KEY]
        
        return self.__hash__()  

    def __hash__(self) -> int:
        """
        Get the hash of the node. The hash is based on the hash of the name
        of the node.

        :return: The hash of the node.
        """
        return self._hash_fn(self)

    def __deepcopy__(self, memo):
        """
        Deep copy the (sub)tree rooted at current node. This method is called
        by the `copy` module when a deep copy is requested.

        :param memo: A dictionary to keep track of the copied nodes.
        :return: A new TreeNode object with the same data as the current node.
        """
        # Create a new instance of TreeNode with a copy of the current node's data
        new_node = TreeNode(copy.deepcopy(dict(self), memo))
        # Deep copy the children
        new_node[TreeNode.CHILDREN_KEY] = [copy.deepcopy(child, memo) for child in self.children]
        # Set the parent of the new node
        new_node._parent = self._parent
        return new_node
    
    @name.setter
    def name(self, name: str) -> None:
        """
        Set the name of the node.

        :param name: The name of the node.
        """
        self[TreeNode.NAME_KEY] = name

    @property
    def children(self) -> List["TreeNode"]:
        """
        Get the children of a node.

        :return: List of child nodes (TreeNode objects).
        """
        return self.get(TreeNode.CHILDREN_KEY, [])

    @children.setter
    def children(self, nodes: List["TreeNode"]) -> None:
        """
        Set the children of a node.

        :param children: List of child nodes (TreeNode objects).
        """
        if nodes is None:
            self.pop(TreeNode.CHILDREN_KEY, None)
        else:
            if not isinstance(nodes, list):
                nodes = [nodes]
            self[TreeNode.CHILDREN_KEY] = [
                TreeNode(child) if not isinstance(child, TreeNode) else child
                for child in nodes
            ]

    def add_child(self, name: Optional[str] = None, *args, **kwargs) -> "TreeNode":
        """
        Add a child node to the tree. Just invokes `__init__`. See `__init__` for
        details.
        """
        return TreeNode(*args, parent=self, name=name, **kwargs)

    def __repr__(self) -> str:
        return f"TreeNode({self.to_dict()})"

    def __str__(self) -> str:
        result = f"TreeNode(name={self.name}"
        if self._parent is not None:
            result += f", parent={self.parent.name}"
        result += f", root={self.root.name}"
        result += f", payload={self.payload}"
        result += f", len(children)={len(self.children)})"
        return result
    
    def to_dict(self):
        """
        It is already a dict, so we just want to recast it as a dict,
        recursively. It's a no-op in a sense, since it does not change
        the data, only the type associated with it.

        :return: A dictionary representation of the subtree.
        """
        def _recast(node):
            node_dict = dict(node)
            if TreeNode.CHILDREN_KEY in node_dict:
                node_dict[TreeNode.CHILDREN_KEY] = [_recast(child) for child in node_dict[TreeNode.CHILDREN_KEY]]
            return node_dict

        return _recast(self)