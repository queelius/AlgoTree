import collections.abc
import uuid
from typing import Any, Dict, Iterator, List, Optional

from treekit.flattree import FlatTree
from treekit.utils import visit


class FlatTreeNode(collections.abc.MutableMapping):
    __slots__ = ("_tree", "_key", "_root_key")

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
            self._tree = parent._tree
            if self._key in self._tree:
                raise KeyError(f"key already exists in the tree: {self._key}")

            # if parent._key not in self._tree:
            #    raise ValueError(f"Parent {parent} is not in the tree")

            if parent._key == FlatTree.LOGICAL_ROOT:
                kwargs.pop(FlatTree.PARENT_KEY, None)
            else:
                kwargs[FlatTree.PARENT_KEY] = parent._key
            self._root_key = parent._root_key
        else:
            self._tree = FlatTree()
            self._root_key = self._key
            if FlatTree.PARENT_KEY in kwargs:
                del kwargs[FlatTree.PARENT_KEY]
        self._tree[self._key] = dict(*args, **kwargs)

    @property
    def name(self):
        return self._key

    @property
    def parent(self) -> Optional["FlatTreeNode"]:
        """
        Get the parent node of the node.

        :return: The parent node.
        """
        if self._key == self._root_key:
            return None

        par_key = self._tree[self._key].get(FlatTree.PARENT_KEY, self._root_key)
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
        if self._key not in self._tree:
            return f"{__class__.__name__}(name={self.name}, payload={self.payload})"
        if FlatTree.PARENT_KEY in self._tree[self._key]:
            par = self._tree[self._key][FlatTree.PARENT_KEY]
        else:
            par = None
        return f"{__class__.__name__}(name={self.name}, parent={par}, payload={self.payload})"

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
        if key in self:
            return self[key]
        return None

    def detach(self) -> "FlatTreeNode":
        """
        Detach the node from the tree.

        :return: The sub-tree rooted at node.
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
        if self._key not in self._tree:
            raise KeyError(
                f"{self._key} is an immutable logical root without a payload"
            )
        if FlatTree.PARENT_KEY in data:
            raise ValueError(f"Cannot set parent using payload setter")

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
