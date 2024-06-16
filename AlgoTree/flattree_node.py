import collections.abc
import uuid
from typing import Any, Dict, Iterator, List, Optional
from copy import deepcopy
from AlgoTree.flattree import FlatTree
from AlgoTree.utils import is_descendant

class FlatTreeNode(collections.abc.MutableMapping):
    __slots__ = ("_tree", "_key", "_root_key")

    def __deepcopy__(self, memo):
        """
        Deepcopy the node and its subtree.

        :param memo: The memo dictionary.
        :return: A new node with a deep copy of the tree (and its subtree)
        """
        new_node = FlatTreeNode.__new__(FlatTreeNode)
        memo[id(self)] = new_node
        new_node._tree = deepcopy(self._tree, memo)
        new_node._key = self._key
        new_node._root_key = self._root_key
        return new_node
      
    def clone(self, parent=None) -> "FlatTreeNode":
        """
        Clone the node without its relationships to other nodes. If you want to
        clone the entire tree, use `deepcopy(tree)` instead. We do allow
        the parent to be set to a new parent node to facilitate flexible
        cloning of nodes into new tree structures.

        :return: A new node with the same data but no relationships.
        """
        new_node = FlatTreeNode.__new__(FlatTreeNode)
        if parent is None:
            new_node._tree = FlatTree({ self._key: deepcopy(self._tree[self._key]) })
            new_node._root_key = self._key
        else:
            new_node._tree = parent._tree
            new_node._tree[self._key] = deepcopy(self._tree[self._key])
            new_node._root_key = parent._root_key
        new_node._key = self._key
        return new_node

    @classmethod
    def proxy(
        cls, tree: FlatTree, node_key: str, root_key: Optional[str] = None
    ) -> "FlatTreeNode":
        """
        Create a proxy node for a subtree.

        We do not check do any checks on the validity of the keys or the
        structure of the tree. This is a low-level method that should be used
        with caution. For instance, if `node_key` is not a descendent of
        `root_key`, the proxy node will not behave as expected.

        :param tree: The tree in which the proxy node exists (or logically exists).
        :param node_key: The key of the node.
        :param root_key: The key of the (logical) root node.
        """
        node = cls()
        node._tree = tree
        node._key = node_key
        if root_key is None:
            root_key = node_key
        node._root_key = root_key
        return node

    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional["FlatTreeNode"] = None,
        children: Optional[List["FlatTreeNode"]] = None,
        *args,
        **kwargs,
    ):
        """
        Create a new node. If the key is None, a UUID is generated.

        If a parent is provided, the node is created as a child of the parent.
        Otherwise, we create a new tree and it will be the single child of a
        logical root node. This is not normally how FlatTree objects are
        created, but it allows us to strictly use the FlatTreeNode API to
        create and manipulate the underlying FlatTree. Note that the underlying
        FlatTree may be accessed via the `tree` property.

        :param parent: The parent node. If None, new tree created.
        :param name: The unique name (key) for the node. If None, UUID generated.
        :param args: Positional arguments for the node.
        :param kwargs: Additional attributes for the node.
        """
        self._key = str(uuid.uuid4()) if name is None else name
        if parent is not None:
            if children is not None:
                raise ValueError("Cannot specify both parent and children.")
            self._tree = parent._tree
            if self._key in self._tree:
                raise KeyError(f"key already exists in the tree: {self._key}")
            kwargs[FlatTree.PARENT_KEY] = parent._key
            self._root_key = parent._root_key
        elif children is not None and len(children) > 0:
            self._tree = children[0]._tree
            if self._key in self._tree:
                raise KeyError(f"key already exists in the tree: {self._key}")
            self._root_key = children[0]._root_key
            self.children = children
        else:
            self._tree = FlatTree()
            self._root_key = self._key
            if FlatTree.PARENT_KEY in kwargs:
                del kwargs[FlatTree.PARENT_KEY]
        self._tree[self._key] = dict(*args, **kwargs)

    @property
    def name(self):
        """
        Get the unique name of the node.

        :return: The unique name of the node.
        """
        return self._key
    
    @property
    def root(self) -> "FlatTreeNode":
        """
        Get the root node of the subtree.

        :return: The root node.
        """
        return FlatTreeNode.proxy(
            tree=self._tree, node_key=self._root_key, root_key=self._root_key
        )
        
    @property
    def parent(self) -> Optional["FlatTreeNode"]:
        """
        Get the parent node of the node.

        :return: The parent node.
        """
        if self._key == self._root_key or self._key not in self._tree:
            return None

        par_key = self._tree[self._key].get(
            FlatTree.PARENT_KEY, self._root_key)
        return FlatTreeNode.proxy(
            tree=self._tree, node_key=par_key, root_key=self._root_key
        )

    @parent.setter
    def parent(self, node: "FlatTreeNode") -> None:
        """
        Set the parent node of the node.

        :param node: The new parent node.
        """
        if self._key not in self._tree:
            raise ValueError(f"{self._key} is an immutable logical root")

        if node._tree != self._tree:
            if self._key in node._tree:
                raise ValueError(f"Node {self} already exists in the tree")
            node._tree[self._key] = self._tree[self._key].copy()

        node._tree[self._key][FlatTree.PARENT_KEY] = node._key

    @property
    def tree(self) -> FlatTree:
        """
        Get the underlying FlatTree object.

        :return: The FlatTree object.
        """
        return self._tree

    def __repr__(self):
        par = None if self._key == self._root_key else self.parent.name
        child_keys = self._tree.child_keys(self._key)
        return f"{__class__.__name__}(name={self.name}, parent={par}, payload={self.payload}, root={self.root.name}, children={child_keys})"

    def __getitem__(self, key) -> Any:
        if self._key not in self._tree:
            raise KeyError(
                f"{self._key} is an immutable logical root without a payload"
            )

        return self._tree[self._key][key]

    def __setitem__(self, key, value) -> None:
        if self._key not in self._tree:
            raise TypeError(f"{self._key} is an immutable logical root")

        self._tree[self._key][key] = value

    def __delitem__(self, key) -> None:
        if self._key not in self._tree:
            raise TypeError(f"{self._key} is an immutable logical root")

        del self._tree[self._key][key]

    def __getattr__(self, key) -> Any:
        if key in ["name", "parent", "root", "tree", "payload", "children"]:
            return object.__getattribute__(self, key)
        if key in self:
            return self[key]
        return None

    def detach(self) -> "FlatTreeNode":
        """
        Detach the node from the tree.

        :return: The detached node.
        """
        return self._tree.detach(self._key)

    @property
    def payload(self) -> Dict:
        """
        Get the payload data of the node.

        :return: Dictionary representing the data of the node.
        """
        if self._key not in self._tree:
            return dict()  # logical node

        data = self._tree[self._key].copy()
        data.pop(FlatTree.PARENT_KEY, None)
        return data

    @payload.setter
    def payload(self, data: Dict) -> None:
        """
        Set the payload data of the node.

        :param data: Dictionary representing the new data of the node.
        """
        if not isinstance(data, dict):
            raise ValueError("Payload must be a dictionary")

        if self._key not in self._tree:
            raise KeyError(
                f"{self._key} is an immutable logical root without a payload"
            )
        if FlatTree.PARENT_KEY in data:
            raise ValueError("Cannot set parent using payload setter")

        data[FlatTree.PARENT_KEY] = self._tree[self._key].get(FlatTree.PARENT_KEY)
        self._tree[self._key] = data

    def __iter__(self) -> Iterator[Any]:
        return iter([] if self._key not in self._tree else self._tree[self._key])

    def __len__(self) -> int:
        return len(self.payload)

    def add_child(self, name: Optional[str] = None, *args, **kwargs) -> "FlatTreeNode":
        """
        Add a child node. See `__init__` for details on the arguments.

        :return: The child node, from the perspective of the subtree that
                 contains the parent.
        """
        return FlatTreeNode(name=name, parent=self, *args, **kwargs)

    @property
    def children(self) -> List["FlatTreeNode"]:
        """
        Get the children of the node.

        :return: List of child nodes.
        """
        return [
            FlatTreeNode.proxy(
                tree=self._tree, node_key=child_key, root_key=self._root_key
            )
            for child_key in self._tree.child_keys(self._key)
        ]

    @children.setter
    def children(self, nodes: List["FlatTreeNode"]) -> None:
        """
        Set the children of the node.

        :param nodes: The new children nodes.
        """
        for node in self.children:
            node.detach()

        if nodes is None:
            return

        if not isinstance(nodes, list):
            nodes = [nodes]
        for node in nodes:
            node.parent = self

    def __eq__(self, other):
        if not isinstance(other, FlatTreeNode):
            return False
        return (self._key == other._key and
                self._root_key == other._root_key and
                self._tree == other._tree)

    def node(self, name: Optional[str] = None) -> "FlatTreeNode":
        """
        Get an ancestor node with the given name.

        :param name: The name of the node.
        :return: The node.
        """

        if name is None:
            name = self.name

        return FlatTreeNode.proxy(tree=self._tree, node_key=name, root_key=self._root_key)

    def subtree(self, name: Optional[str] = None) -> "FlatTreeNode":
        """
        Get a subtree rooted at the node with the name `name`. If `name` is
        None, the subtree is rooted at the current node.

        :param name: The name of the root node.
        :return: A subtree rooted at the given node.
        """

        if name is None:
            name = self.name
        return FlatTreeNode.proxy(tree=self._tree, node_key=name, root_key=name)
