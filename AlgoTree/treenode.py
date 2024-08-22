from typing import Dict, List, Optional, Union, Any, Callable
import copy
from AlgoTree.utils import find_node
from AlgoTree.node_hash import NodeHash
import uuid

class TreeNode(dict):
    """
    A tree node class. This class stores a nested
    representation of the tree. Each node is a TreeNode object, and if a node
    is a child of another node, it is stored in the parent node's `children`
    attribute.
    """

    @staticmethod
    def from_dict(data: Dict,
                  
                  hash_fn: Callable = NodeHash.node_hash) -> "TreeNode":
        """
        Create a TreeNode from a dictionary.

        :param data: The dictionary to convert to a TreeNode.
        :param hash_fn: The hash function to use for the node. Default is NodeHash.node_hash.
        :return: A TreeNode object.
        """

        def _from_dict(data, parent):
            node = TreeNode(parent=parent, payload=None,
                            name=data.pop("name", None), hash_fn=hash_fn)
            node.payload = data.pop("payload", {})
            for k, v in data.items():
                if k == "children":
                    for child in v:
                        _from_dict(child, node)
                else:
                    node.payload[k] = v
            return node
        
        return _from_dict(data, None)
        
    
    @staticmethod
    def is_valid(data) -> bool:
        """
        Check if the data is a valid tree.

        :param data: The data to check for validity.
        :return: True if the data is a valid TreeNode, False otherwise.
        """
        try:
            TreeNode.check_valid(data)
            return True
        except ValueError:
            return False

    @staticmethod
    def check_valid(data) -> None:
        """
        Check if the data is a valid tree.

        Raises an appropriate exception if the tree is invalid in any way.

        :param data: The data to check for validity.
        :raises ValueError: If the data is not a valid TreeNode.
        """

        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        if "children" in data:
            if not isinstance(data["children"], list):
                raise ValueError("Children must be a list")
            for child in data["children"]:
                TreeNode.check_valid(child)

    def clone(self) -> "TreeNode":
        """
        Clone the tree node (sub-tree) rooted at the current node.

        :return: A new TreeNode object with the same data as the current node.
        """
        def _clone(node, parent):
            new_node = TreeNode(parent=parent,
                                payload=copy.deepcopy(node.payload),
                                name=node.name, hash_fn=node._hash_fn)
            for child in self.children:
                _clone(child, new_node)
            return new_node
        
        return _clone(self, None)

    def __init__(
        self,
        parent: Optional["TreeNode"] = None,
        payload: Optional[Dict] = None,
        name: Optional[str] = None,
        hash_fn: Optional[Callable[["TreeNode"], int]] = None):
        """
        Initialize a TreeNode.

        :param parent: The parent node of the current node. Default is None.
        :param name: The name of the node. Default is None, in which case a random name is generated.
        :param hash_fn: The hash function to use for the node. Default is NodeHash.node_hash.
        :param payload: The payload of the node. Default is an empty dictionary.
        """
        if name is None:
            name = str(uuid.uuid4())
        self.name = name

        if hash_fn is None:
            hash_fn = NodeHash.node_hash
        self._hash_fn = hash_fn
        if not callable(self._hash_fn):
            raise ValueError("Hash function must be callable")
        
        if parent is not None and not isinstance(parent, TreeNode):
            raise ValueError("Parent must be a TreeNode object")
        self._parent = parent

        if payload is None:
            payload = {}
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dictionary")
        self._payload = payload

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
        self._parent = parent

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
        Get the payload stored in the tree.

        :return: The data stored in the tree.
        """
        return self._payload

    @payload.setter
    def payload(self, data: Dict) -> None:
        """
        Set the payload stored in the tree.

        :param data: The data to store in the tree.
        """
        if not isinstance(data, dict):
            raise ValueError("Payload must be a dictionary")
            
        self._payload = data

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
    
    def node(self, name: str) -> "TreeNode":
        """
        Get the node with the given name in the current sub-tree. The sub-tree
        remains the same, we just change the current node position. If the name
        is not found, raise a KeyError.

        :param name: The name of the node.
        :return: The node with the given name.
        """
        node = find_node(self, lambda n, **_: n.name == name)
        if node is None:
            raise KeyError(f"Node not found: {name}")
        return node

    def __hash__(self) -> int:
        """
        Get the hash of the node. The hash is based on the hash of the name
        of the node.

        :return: The hash of the node.
        """
        return self._hash_fn(self)

    @property
    def children(self) -> List["TreeNode"]:
        """
        Get the children of a node. Note that we only store parent references
        and not child references, so we need to traverse the tree to get the
        children.

        :return: List of child nodes (TreeNode objects).
        """

    
        

    def add_child(self, name: Optional[str] = None, payload: Optional[Dict] = None) -> "TreeNode":
        """
        Add a child node to the tree. Just invokes `__init__`. See `__init__` for
        details.
        """
        return TreeNode(parent=self, name=name, payload=payload, hash_fn=self._hash_fn)

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
    
    def __contains__(self, key) -> bool:
        """
        Check if the node's payload contains the given key.

        :param key: The key to check for.
        :return: True if the key is present in the payload, False otherwise.
        """
        return key in self.payload
