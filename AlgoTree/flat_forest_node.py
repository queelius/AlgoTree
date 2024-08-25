import collections.abc
import uuid
from typing import Any, Dict, Iterator, List, Optional, Union
from copy import deepcopy
from AlgoTree.flat_forest import FlatForest

class FlatForestNode(collections.abc.MutableMapping):
    __slots__ = ("_forest", "_key", "_root_key")

    def __deepcopy__(self, memo):
        """
        Deepcopy the entire forest that the node is a part of and return a new
        node with the copied forest. This is a deep copy of the forest, not just
        the node. If you want to copy just the node, see the `clone` method.

        :param memo: The memo dictionary.
        :return: A new node with a deep copy of the forest.
        """
        new_node = FlatForestNode.__new__(FlatForestNode)
        memo[id(self)] = new_node
        new_node._forest = deepcopy(self._forest, memo)
        new_node._key = self._key
        new_node._root_key = self._root_key
        return new_node
      
    def clone(self, parent=None, clone_children=False) -> "FlatForestNode":
        """
        Clone the node and, optionally, its children. If you want to
        clone the entire forest, see `deepcopy`. We allow
        the parent to be set to a new parent node to facilitate flexible
        cloning of nodes into new forest structures.

        :return: A new node (or subtree rooted at the node if `clone_children`
                 is True)
        """
        new_node = FlatForestNode.__new__(FlatForestNode)
        if parent is None:
            new_node._forest = FlatForest({ self._key: deepcopy(self._forest[self._key]) })
            new_node._root_key = self._key
        else:
            if self._key in parent._forest:
                raise ValueError(f"Node {self} already exists in the forest")
            new_node._forest = parent._forest
            new_node._forest[self._key] = deepcopy(self._forest[self._key])
            new_node._root_key = parent._root_key

        if clone_children:
            for child in self.children:
                child.clone(parent=new_node, clone_children=True)
        new_node._key = self._key
        return new_node

    @staticmethod
    def proxy(
        forest: FlatForest, node_key: str, root_key: Optional[str] = None
    ) -> "FlatForestNode":
        """
        Create a proxy node for a node in a forest. The proxy node is a
        lightweight object that provides a node-centric abstraction of the
        tree that a node is a part of.

        We do not check do any checks on the validity of the keys or the
        structure of the tree. This is a low-level method that should be used
        with caution. For instance, if `node_key` is not a descendent of
        `root_key`, the proxy node will not behave as expected.

        :param forest: The forest in which the proxy node exists (or logically exists).
        :param node_key: The key of the node.
        :param root_key: The key of the (real or logical) root node.
        """
        node = FlatForestNode.__new__(FlatForestNode)
        node._forest = forest
        node._key = node_key
        if root_key is None:
            root_key = node_key
        node._root_key = root_key
        return node

    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional[Union["FlatForestNode",str]] = None,
        forest: Optional[FlatForest] = None,
        payload: Optional[Dict] = None,
        *args,
        **kwargs,
    ):
        """
        Create a new node. If the key is None, a UUID is generated.

        If a parent is provided, the node is created as a child of the parent.

        Otherwise, if parent is None, the node is created as a root node in a
        new tree. If the forest is provided, the node is created in the given
        forest, otherwise a new forest is created.

        :param parent: The parent node. If None, new tree created.
        :param name: The unique name (key) for the node. If None, UUID generated.
        :param forest: The forest in which the node is created.
        :param payload: The payload data for the node.
        :param args: Positional arguments for the node.
        :param kwargs: Additional attributes for the node.
        """

        if name is None:
            self._key = str(uuid.uuid4())
        else:
            self._key = str(name)

        if parent is not None:
            # check if parent is a node or a key
            if isinstance(parent, str):
                if forest is None:
                    raise ValueError("Parent key provided without a forest")
                parent = FlatForestNode.proxy(forest=forest, node_key=parent)
            self._forest = parent._forest
            if self._key in self._forest.keys():
                raise KeyError(f"key already exists in the tree: {self._key}")
            kwargs[FlatForest.PARENT_KEY] = parent._key
            self._root_key = parent._root_key
        else:
            self._forest = FlatForest() if forest is None else forest
            self._root_key = self._key
            kwargs[FlatForest.PARENT_KEY] = None

        # add payload to kwargs too
        kwargs.update(payload or {})
        self._forest[self._key] = dict(*args, **kwargs)

    @property
    def name(self):
        """
        Get the unique name of the node.

        :return: The unique name of the node.
        """
        return self._key
    
    @name.setter
    def name(self, name: str) -> None:
        """
        Set the unique name of the node.

        :param name: The new unique name of the node.
        """

        if name == self._key:
            return

        if name in self._forest.keys():
            raise ValueError(f"Node with name {name} already exists")

        for child_key in self._forest.keys():
            if self._forest[child_key].get(FlatForest.PARENT_KEY, None) == self._key:
                self._forest[child_key][FlatForest.PARENT_KEY] = name
        self._forest[name] = self._forest.pop(self._key)
        self._key = name
    
    @property
    def root(self) -> "FlatForestNode":
        """
        Get the root node of the subtree.

        :return: The root node.
        """
        return FlatForestNode.proxy(
            forest=self._forest, node_key=self._root_key, root_key=self._root_key
        )
        
    @property
    def parent(self) -> Optional["FlatForestNode"]:
        """
        Get the parent node of the node.

        :return: The parent node.
        """
        if self._key == self._root_key or self._key not in self._forest.keys():
            return None

        # we do it this way in case for instance it's a logical root like
        # the root of the detached nodes.
        par_key = self._forest[self._key].get(
            FlatForest.PARENT_KEY, self._root_key)
        
        return FlatForestNode.proxy(
            forest=self._forest, node_key=par_key, root_key=self._root_key
        )

    @parent.setter
    def parent(self, node: "FlatForestNode") -> None:
        """
        Set the parent node of the node.

        :param node: The new parent node.
        """
        if self._key not in self._forest:
            raise ValueError(f"{self._key} is an immutable logical root")

        if node._forest != self._forest:
            if self._key in node._forest:
                raise ValueError(f"Node {self} already exists in the forest")
            node._forest[self._key] = self._forest[self._key].copy()

        node._forest[self._key][FlatForest.PARENT_KEY] = node._key

    @property
    def forest(self) -> FlatForest:
        """
        Get the underlying FlatForest object.

        :return: The FlatForest object.
        """
        return self._forest

    def __repr__(self):
        par = None if self._key == self._root_key else self.parent.name
        child_keys = self._forest.child_names(self._key)
        return f"{__class__.__name__}(name={self.name}, parent={par}, payload={self.payload}, root={self.root.name}, children={child_keys})"

    def __getitem__(self, key) -> Any:
        if self._key not in self._forest:
            raise KeyError(
                f"{self._key} is an immutable logical root without a payload"
            )

        return self._forest[self._key][key]

    def __setitem__(self, key, value) -> None:
        if self._key not in self._forest:
            raise TypeError(f"{self._key} is an immutable logical root")

        self._forest[self._key][key] = value

    def __delitem__(self, key) -> None:
        if self._key not in self._forest:
            raise TypeError(f"{self._key} is an immutable logical root")

        del self._forest[self._key][key]

    def __getattr__(self, key) -> Any:
        if key in ["name", "parent", "root", "forest", "payload", "children"]:
            return object.__getattribute__(self, key)
        if key in self:
            return self[key]
        return None

    def detach(self) -> "FlatForestNode":
        """
        Detach the node.

        :return: The detached node.
        """
        return self._forest.detach(self._key)

    @property
    def payload(self) -> Dict:
        """
        Get the payload data of the node.

        :return: Dictionary representing the data of the node.
        """
        if self._key not in self._forest.keys():
            return dict()  # logical node

        data = self._forest[self._key].copy()
        data.pop(FlatForest.PARENT_KEY, None)
        return data

    @payload.setter
    def payload(self, data: Dict) -> None:
        """
        Set the payload data of the node.

        :param data: Dictionary representing the new data of the node.
        """
        if not isinstance(data, dict):
            raise ValueError("Payload must be a dictionary")

        if self._key not in self._forest:
            raise KeyError(
                f"{self._key} is an immutable logical root without a payload"
            )
        if FlatForest.PARENT_KEY in data:
            raise ValueError("Cannot set parent using payload setter")

        data[FlatForest.PARENT_KEY] = self._forest[self._key].get(FlatForest.PARENT_KEY)
        self._forest[self._key] = data

    def __iter__(self) -> Iterator[Any]:
        return iter([] if self._key not in self._forest else self._forest[self._key])

    def __len__(self) -> int:
        return len(self.payload)

    def add_child(self, name: Optional[str] = None, *args, **kwargs) -> "FlatForestNode":
        """
        Add a child node. See `__init__` for details on the arguments.

        :return: The child node, from the perspective of the subtree that
                 contains the parent.
        """
        return FlatForestNode(name=name, parent=self, *args, **kwargs)
    
    @property
    def children(self) -> List["FlatForestNode"]:
        """
        Get the children of the node.

        :return: List of child nodes.
        """
        return [
            FlatForestNode.proxy(
                forest=self._forest, node_key=child_key, root_key=self._root_key
            )
            for child_key in self._forest.child_names(self._key)
        ]

    @children.setter
    def children(self, nodes: List["FlatForestNode"], append: bool = False) -> None:
        """
        Set the children of the node.

        :param nodes: The new children nodes.
        """
        if not append:
            for node in self.children:
                node.detach()

        if nodes is None:
            return

        if not isinstance(nodes, list):
            nodes = [nodes]

        for node in nodes:
            node.parent = self

    def __eq__(self, other):
        """
        There are many ways to define equality for nodes in a tree. We define
        node equality, by default, as path equality. Two nodes are equal if
        they have the same path in a tree. Note that we allow equality of nodes
        in different trees.

        :param other: The other node to compare with.
        :return: True if the nodes are equal, False otherwise.
        """
        return hash(self) == hash(other)
    
    def node(self, name: str) -> "FlatForestNode":
        """
        Get an ancestor node with the given name.

        :param name: The name of the node.
        :return: The node.
        """
        return FlatForestNode.proxy(forest=self._forest, node_key=name, root_key=self._root_key)

    def subtree(self, name: Optional[str] = None) -> "FlatForestNode":
        """
        Get a subtree rooted at the node with the name `name`. If `name` is
        None, the subtree is rooted at the current node.

        :param name: The name of the root node.
        :return: A subtree rooted at the given node.
        """

        if name is None:
            name = self.name

        return FlatForestNode.proxy(forest=self._forest, node_key=name, root_key=name)
    
    def contains(self, name) -> bool:
        """
        Check if the the subtree rooted at the node contains any children
        with the given name

        :param key: The key to check.
        :return: True if the child node is present, False otherwise.
        """

        from .utils import is_ancestor
        return is_ancestor(self, self.node(name))
        
    def __contains__(self, key) -> bool:
        """
        Check if the node's payload contains the given key.

        :param key: The key to check for.
        :return: True if the key is present in the payload, False otherwise.
        """
        return key in self.payload
    
    def to_dict(self):
        """
        Convert the subtree rooted at `node` to a dictionary.

        :return: A dictionary representation of the subtree.
        """
        from .tree_converter import TreeConverter
        return TreeConverter.convert(self, FlatForestNode).forest
    
    def __hash__(self) -> int:
        """
        Get the hash of the node.

        :return: The hash of the node.
        """
        
        from .node_hasher import NodeHasher
        return NodeHasher.path(self)