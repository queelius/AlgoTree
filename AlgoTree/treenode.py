from typing import Dict, List, Optional, Any
import copy
import uuid

class TreeNode(dict):
    """
    A tree node class. This class stores a nested
    representation of the tree. Each node is a TreeNode object, and if a node
    is a child of another node, it is stored in the parent node's `children`
    attribute.
    """

    @staticmethod
    def from_dict(data: Dict) -> "TreeNode":
        """
        Create a TreeNode from a dictionary.

        :param data: The dictionary to convert to a TreeNode.
        :return: A TreeNode object.
        """

        def _from_dict(data, parent):
            node = TreeNode(parent=parent, payload=None,
                            name=data.pop("name", None))
            node.payload = data.pop("payload", {})
            for k, v in data.items():
                if k == "children":
                    for child in v:
                        _from_dict(child, node)
                else:
                    node.payload[k] = v
            return node
        
        return _from_dict(copy.deepcopy(data), None)

    def clone(self) -> "TreeNode":
        """
        Clone the tree node (sub-tree) rooted at the current node.

        :return: A new TreeNode object with the same data as the current node.
        """
        def _clone(node, parent):
            new_node = TreeNode(parent=parent,
                                name=node.name,
                                payload=copy.deepcopy(node.payload))
            for child in node.children:
                _clone(child, new_node)
            return new_node
        
        return _clone(self, None)

    def __init__(
        self,
        parent: Optional["TreeNode"] = None,
        name: Optional[str] = None,
        payload: Optional[Any] = None,
        *args, **kwargs):
        """
        Initialize a TreeNode. The parent of the node is set to the given parent
        node. If the parent is None, the node is the root of the tree. The name
        of the node is set to the given name. If the name is None, a random name
        is generated. The payload of the node is any additional arguments passed
        to the constructor.

        :param parent: The parent node of the current node. Default is None.
        :param name: The name of the node. Default is None, in which case a
                     random name is generated.
        :param payload: The payload of the node. Default is None.
        :param args: Additional arguments to pass to the payload.
        :param kwargs: Additional keyword arguments to pass to the payload.
        """
        if name is None:
            name = str(uuid.uuid4())
        self.name = name

        if parent is not None and not isinstance(parent, TreeNode):
            raise ValueError("Parent must be a TreeNode object")
        self.children = []
        self._parent = None
        self.parent = parent

        if payload is not None:
            self.payload = payload
        elif args or kwargs:
            self.payload = dict(*args, **kwargs)
        else:
            self.payload = None


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
        if parent is not None and not isinstance(parent, TreeNode):
            raise ValueError("Parent must be a TreeNode object")
        
        # remove the node from the parent's children
        if self._parent is not None:
            self._parent.children.remove(self)
            #self._parent.children = [child for child in self._parent.children if child != self]

        self._parent = parent

        # update parent's children
        if parent is not None:
            parent.children.append(self)

    @property
    def root(self) -> "TreeNode":
        """
        Get the root of the tree.

        :return: The root node of the tree.
        """
        node = self
        while node.parent is not None:
            node = node.parent
        return node
    
    def nodes(self) -> List["TreeNode"]:
        """
        Get all the nodes in the current sub-tree.

        :return: A list of all the nodes in the current sub-tree.
        """
        nodes = []
        for child in self.children:
            nodes.extend(child.nodes())
        nodes.append(self)
        return nodes
    
    def subtree(self, name: str) -> "TreeNode":
        """
        Get the subtree rooted at the node with the given name. This is not
        a view, but a new tree rooted at the node with the given name. This
        is different from the `node` method, which just changes the current
        node position. It's also different from the `subtree` method in the
        `FlatForestNode` class, which returns a view of the tree.

        :param name: The name of the node.
        :return: The subtree rooted at the node with the given name.
        """
        from copy import deepcopy
        node = deepcopy(self.node(name))
        node.parent = None
        return node
    
    def node(self, name: str) -> "TreeNode":
        """
        Get the node with the given name in the current sub-tree. The sub-tree
        remains the same, we just change the current node position. If the name
        is not found, raise a KeyError.

        :param name: The name of the node.
        :return: The node with the given name.
        """

        def _descend(node, name):
            if node.name == name:
                return node
            for child in node.children:
                result = _descend(child, name)
                if result is not None:
                    return result
            return None
        
        def _ascend(node, name):
            if node.name == name:
                return node
            if node.parent is not None:
                return _ascend(node.parent, name)
            return None
        
        asc_node = _ascend(self, name)
        if asc_node is not None:
            return asc_node
        dsc_node =_descend(self, name)
        if dsc_node is not None:
            return dsc_node
        
        raise KeyError(f"Node with name {name} not found")

    def add_child(self, name: Optional[str] = None,
                  payload: Optional[Any] = None,
                  *args, **kwargs) -> "TreeNode":
        """
        Add a child node to the tree. Just invokes `__init__`. See `__init__` for
        details.
        """
        return TreeNode(parent=self, name=name, payload=payload, *args, **kwargs)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        result = f"TreeNode(name={self.name}"
        if self._parent is not None:
            result += f", parent={self.parent.name}"
        result += f", root={self.root.name}"
        result += f", payload={self.payload}"
        result += f", len(children)={len(self.children)})"
        return result
    
    @staticmethod
    def is_valid(data) -> bool:
        """
        Check if the given data is a valid TreeNode data.

        :param data: The data to check.
        :return: True if the data is a valid TreeNode, False otherwise.
        """
        if not isinstance(data, dict):
            return False
        if "children" in data:
            if not isinstance(data["children"], list):
                return False
            for child in data["children"]:
                if not TreeNode.is_valid(child):
                    return False
        
        return True
    
    def to_dict(self):
        """
        Convert the subtree rooted at `node` to a dictionary.

        :return: A dictionary representation of the subtree.
        """
        def _convert(node):
            node_dict = {}
            node_dict["name"] = node.name
            node_dict["payload"] = node.payload
            node_dict["children"] = [_convert(child) for child in node.children]
            return node_dict

        return _convert(self)
    
    def __eq__(self, other) -> bool:
        """
        Check if the current node is equal to the given node.

        :param other: The other node to compare with.
        :return: True if the nodes are equal, False otherwise.
        """
        if not isinstance(other, TreeNode):
            return False
        
        return hash(self) == hash(other)
    
    def __hash__(self) -> int:
        """
        Compute the hash of the current node.

        :return: The hash of the node.
        """
        return id(self)
    
    def __contains__(self, key) -> bool:
        """
        Check if the node's payload contains the given key.

        :param key: The key to check for.
        :return: True if the key is present in the payload, False otherwise.
        """
        return key in self.payload
