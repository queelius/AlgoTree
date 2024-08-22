from typing import Dict, List, Optional, Union, Any, Callable
import copy
from AlgoTree.utils import find_node
from AlgoTree.node_hash import NodeHash
import uuid

class TreeImporter:
    def __init__(self,
                 name_field: str = "name",
                 children_field: str = "children",
                 payload_only: bool = False,
                 payload_field: Optional[str] = None):
        """
        Initialize the TreeImporter.

        :param name_field: The key in the dictionary that contains the node
                           name. Default is "name".
        :param children_field: The key in the dictionary that contains the list
                               of child nodes. Default is "children".
        :param payload_only: If True, the payload is only in the payload_field
                             and the payload_field is the key in the dictionary
                             that contains the payload. Default is False.
                             If False, all keys in the dictionary (except name
                             and children) are stored in the payload. If
                             payload_field is not None, we unpack the values
                             from the payload_field and store them in the
                             payload of the node.
        """
        
        self.name_field = name_field
        self.children_field = children_field
        self.payload_only = payload_only
        self.payload_field = payload_field

    def __call__(self, data: Dict, forest: "Forest") -> "Forest.Node":
        """
        Create a Forest.Node from a nested dictionary

        :param data: The dictionary to convert to a Forest.Node.
        :param forest The Forest object to add the subtree rooted at the node
                      to.

        :return: A Tree object.
        """

        def build(data, parent, forest):
            node = Forest.Node(forest=forest,
                               parent=parent,
                               payload=None,
                               name=data.pop(self.name_field, None))
        
            node.payload = data.pop(self.payload_field, {})
            for k, v in data.items():
                if k == self.children_field:
                    for child in v:
                        build(child, node, tree)
                elif not self.payload_only:
                    node.payload[k] = v
            return node
        
        return build(data, None, forest)
        
    def is_valid(self, data) -> bool:
        """
        Check if the data is a valid tree.

        :param data: The data to check for validity.
        :return: True if the data is a valid, False otherwise.
        """
        try:
            self.check_valid(data)
            return True
        except ValueError:
            return False

    def check_valid(self, data) -> None:
        """
        Check if the data is a valid tree.

        Raises an appropriate exception if the tree is invalid in any way.

        :param data: The data to check for validity.
        :raises ValueError: If the data is not a valid.
        """

        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        if self.children_field in data:
            if not isinstance(data[self.children_field], list):
                raise ValueError("Children must be a list")
            for child in data[self.children_field]:
                Forest.check_valid(child)

class Forest:
    """
    A simple forest class.
    """
    def __init__(
        self,
        hash_fn: Callable[["Forest.Node"], Any] = NodeHash.node_hash,
        node_namer: Callable[["Forest.Node"], str] = lambda _: str(uuid.uuid4())):
        """
        Initialize a Forest.

        :param hash_fn: The hash function to use for nodes. Default is
                        NodeHash.node_hash.
        :param node_namer: The function to use to generate a names for nodes
                           when one is not provided. Defaults to UUID.
        """
        if not callable(hash_fn):
            raise ValueError("Hash function must be callable")
        if not callable(node_namer):
            raise ValueError("Node namer must be callable")

        self._hash_fn = hash_fn
        self._node_namer = node_namer
        self._nodes = []

    def trees(self) -> List["Forest.Node"]:
        """
        Get the trees in the forest.

        :return: A list of the trees in the forest.
        """
        return [node for node in self._nodes if node.parent is None]
    
    def node(self, name: str) -> "Forest.Node":
        """
        Get the node with the given name in the forest. If the name is not found,
        raise a KeyError.

        :param name: The name of the node.
        :return: The node with the given name.
        """
        for node in self._nodes:
            if node.name == name:
                return node
            
        raise KeyError(f"Node not found: {name}")
    
    def __contains__(self, key) -> bool:
        """
        Check if the forest contains a node with the given name.

        :param key: The name of the node.
        :return: True if the node is present in the forest, False otherwise.
        """
        return any(node.name == key for node in self._nodes)
    
    def add_node(
            self,
            name: Optional[str] = None,
            parent: Optional["Forest.Node"] = None,
            payload: Optional[Dict] = None) -> "Forest.Node":
        """
        Add a new node to the forest with the given name and payload. If the
        parent is not provided, the node is added as a root node.

        :param name: The name of the tree.
        :param payload: The payload of the tree.
        :param parent: The parent of the node.
        :return: The node that was added.
        """
        return Forest.Node(forest=self, parent=parent, payload=payload, name=name)
    
    def remove_subtree(self, node: "Forest.Node") -> None:
        """
        Remove a node rooted at `node` from the forest.

        :param node: The root of the subtree to remove.
        """

        def _remove(node):
            for child in node.children:
                _remove(child)
            self._nodes.remove(node)

        _remove(node)
        
    class Node:
        def __init__(self, forest, parent, payload, name):
            self._parent = parent
            self._payload = payload
            self._name = name
            self._forest = forest
            self._forest._nodes.append(self)

        def clone(self) -> "Forest.Node":
            """
            Clone the sub-tree rooted at the current node and place it in the
            forest.

            :return: The root of the cloned sub-tree.
            """
            def _clone(node, parent):
                new_node = Forest.Node(
                    forest=node._forest,
                    parent=parent,
                    payload=copy.deepcopy(node.payload),
                    name=node.name)
                
                for child in self.children:
                    _clone(child, new_node)
                return new_node
            
            return _clone(self, None)

        @property
        def parent(self) -> Optional["Forest.Node"]:
            """
            Get the parent of the node.

            :return: The parent of the node.
            """
            return self._parent

        @parent.setter
        def parent(self, parent: Optional["Forest.Node"]) -> None:
            """
            Set the parent of the node.

            :param parent: The new parent of the node.
            """
            if parent is not None and not isinstance(parent, Forest.Node):
                raise ValueError("Parent must be a Forest.Node object")
            self._parent = parent

        @property
        def root(self) -> "Forest.Node":
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

        def nodes(self) -> List["Forest.Node"]:
            """
            Get all the nodes in the current sub-tree.

            :return: A list of all the nodes in the current sub-tree.
            """
            nodes = []
            for child in self.children:
                nodes.extend(child.nodes())
            nodes.append(self)
            return nodes
    
        def node(self, name: str) -> "Forest.Node":
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
            Get the hash of the node.

            :return: The hash of the node.
            """
            return self._forest._hash_fn(self)

        @property
        def children(self) -> List["Forest.Node"]:
            """
            Get the children of the node.

            :return: List of child nodes.
            """
            return [node for node in self._forest._nodes if node.parent == self]

        def add_child(self, name: Optional[str] = None, payload: Optional[Dict] = None) -> "Forest.Node":
            """
            Add a child node to the tree.

            :param name: The name of the child node.
            :param payload: The payload of the child node.
            :return: The child node.
            """
            return Forest.Node(forest=self._forest, parent=self, name=name, payload=payload)

        def __repr__(self) -> str:
            return self.__str__()

        def __str__(self) -> str:
            result = f"Forest.Node(name={self.name}"
            if self._parent is not None:
                result += f", parent={self.parent.name}"
            result += f", root={self.root.name}"
            result += f", payload={self.payload}"
            result += f", len(children)={len(self.children)})"
            return result
    
        def to_dict(self, use_payload_field: bool = False) -> Dict:
            """
            Convert the subtree rooted at current node to a dictionary.

            :param use_payload_field: If True, the payload is stored in a field
                                    called "payload". Default is False. If False,
                                    the payload is stored as fields in the
                                    dictionary that represents the node.
            :return: A dictionary representation of the subtree.
            """
            def build(node):
                node_dict = {}
                node_dict["name"] = node.name
                if use_payload_field:
                    node_dict["payload"] = node.payload
                else:
                    for k, v in node.payload.items():
                        node_dict[k] = v            
                node_dict["children"] = [build(child) for child in node.children]
                return node_dict

            return build(self)
    
        def __contains__(self, key) -> bool:
            """
            Check if the node's payload contains the given key.

            :param key: The key to check for.
            :return: True if the key is present in the payload, False otherwise.
            """
            return key in self.payload
