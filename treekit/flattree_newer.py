import uuid
import collections.abc
from typing import Dict, Any, List, Union, Optional, Iterator
from copy import deepcopy

class FlatTreeNew(dict):
    """
    A tree class that is also a standard dictionary.
    """

    LOGICAL_ROOT = '__ROOT__'
    PARENT_KEY = 'parent'
    DETACHED_KEY = '__DETACHED__'

    class ProxyNode(collections.abc.MutableMapping):
        __slots__ = ('_tree', '_key')

        def __init__(self, key: Optional[str] = None, tree: Optional['FlatTreeNew'] = None, parent: Optional['FlatTreeNew.ProxyNode'] = None, **kwargs):
            """
            Initialize a ProxyNode.

            :param key: The unique key of the node. If None, a UUID is generated.
            :param tree: The tree to which the node belongs.
            :param parent: The parent node (only used if creating a new tree).
            :param kwargs: Additional attributes for the node (only used if creating a new node).
            """
            if tree is None:
                # Create a new FlatTreeNew and initialize the node
                node = FlatTreeNew.ProxyNode.create(key, parent, **kwargs)
                self._tree: FlatTreeNew = node.flattree
                self._key = node._key
            else:
                # Initialize with an existing FlatTreeNew
                if key is None:
                    raise ValueError("Key must be provided when using an existing tree")
                if key not in tree:
                    raise KeyError(f"Node {key} does not exist in the provided FlatTreeNew")
                self._tree: FlatTreeNew = tree
                self._key = key

        @staticmethod
        def create(key: Optional[str] = None, parent: Optional['FlatTreeNew.ProxyNode'] = None, **kwargs) -> 'FlatTreeNew.ProxyNode':
            key = key if key is not None else str(uuid.uuid4())
            if parent is None:
                tree: FlatTreeNew = FlatTreeNew()
                tree[key] = deepcopy(kwargs)
                return tree.get_node(key)
            else:
                tree: FlatTreeNew = parent.flattree
                parent.add_child(key, **kwargs)
                return tree.get_node(key)

        @staticmethod
        def clone(node: 'FlatTreeNew.ProxyNode', key: Optional[str] = None, clone_children: bool = False, **kwargs) -> 'FlatTreeNew.ProxyNode':
            key = key if key is not None else str(uuid.uuid4())
            new_node = node.add_child(key, **kwargs)
            if clone_children:
                for child in node.children:
                    FlatTreeNew.ProxyNode.clone(child, None, clone_children, **child.payload)
            return new_node

        @property
        def name(self):
            return self._key

        @property
        def parent(self) -> Optional['FlatTreeNew.ProxyNode']:
            if self._key == FlatTreeNew.LOGICAL_ROOT:
                return None
            key = self.parent_key
            return self._tree.get_node(key) if key is not None else self._tree.root

        @property
        def parent_key(self) -> Optional[str]:
            return None if self._key == FlatTreeNew.LOGICAL_ROOT else self._tree[self._key].get(FlatTreeNew.PARENT_KEY)

        def __repr__(self):
            return f"{__class__.__name__}({dict(self)})"

        def __getitem__(self, key) -> Dict[str, Any]:
            return {} if self._key == FlatTreeNew.LOGICAL_ROOT else self._tree[self._key][key]

        def __setitem__(self, key, value):
            if self._key == FlatTreeNew.LOGICAL_ROOT:
                raise TypeError(f"{self} is immutable")
            self._tree[self._key][key] = value
            self._tree.check_valid()

        def __delitem__(self, key):
            if self._key == FlatTreeNew.LOGICAL_ROOT:
                raise TypeError(f"{self} is immutable")
            del self._tree[self._key][key]
            self._tree.check_valid()

        def detach(self) -> None:
            """
            Detach the node by setting its parent to `FlatTreeNew.DETACHED_KEY`.
            """
            self._tree.detach(self._key)

        @property
        def payload(self) -> Dict[str, Any]:
            """
            Get the payload data of the node.

            :return: Dictionary representing the data of the node.
            """
            return self._tree.payload if self._key == FlatTreeNew.LOGICAL_ROOT else self._tree[self._key]

        def __iter__(self) -> Iterator[Any]:
            if self._key == FlatTreeNew.LOGICAL_ROOT:
                return iter([])
            return iter(self._tree[self._key])

        def __len__(self) -> int:
            if self._key == FlatTreeNew.LOGICAL_ROOT:
                return 0
            return len(self._tree[self._key])

        def add_child(self, new_node: Optional[Union[str, 'FlatTreeNew.ProxyNode']] = None, *args, **kwargs) -> 'FlatTreeNew.ProxyNode':
            """
            Add a child node. If a string key is given, create a new ProxyNode with that key.

            :param new_node: The unique key for the node or a ProxyNode. If None, a new node is created with a UUID key.
            :param args: Positional arguments for the node.
            :param kwargs: Additional attributes for the node.
            :return: The newly added node.
            """
            if new_node is None:
                key = str(uuid.uuid4())
                new_child = FlatTreeNew.ProxyNode(key, self._tree, **kwargs)
                self._tree[key][FlatTreeNew.PARENT_KEY] = self._key
                return new_child
            elif isinstance(new_node, str):
                key = new_node
                if key in self._tree:
                    raise KeyError("Node key already exists in the tree")
                new_child = FlatTreeNew.ProxyNode(key, self._tree, **kwargs)
                self._tree[key][FlatTreeNew.PARENT_KEY] = self._key
                return new_child
            elif isinstance(new_node, FlatTreeNew.ProxyNode):
                if new_node._tree is not self._tree:
                    raise ValueError("Cannot add a child from a different FlatTreeNew")
                if new_node._key in self._tree:
                    raise KeyError("Node key already exists in the tree")
                self._tree[new_node._key][FlatTreeNew.PARENT_KEY] = self._key
                return new_node
            else:
                raise TypeError("new_node must be a string, a ProxyNode, or None")

        @property
        def children(self) -> List['FlatTreeNew.ProxyNode']:
            """
            Get the children of the node.
            """
            if self._key == FlatTreeNew.LOGICAL_ROOT:
                return [self._tree.get_node(k) for k in self._tree if self._tree[k].get(FlatTreeNew.PARENT_KEY) is None]
            else:
                return [self._tree.get_node(k) for k in self._tree if self._tree[k].get(FlatTreeNew.PARENT_KEY) == self._key]

        def remove_children(self, children: Optional[List['FlatTreeNew.ProxyNode']] = None) -> List['FlatTreeNew.ProxyNode']:
            """
            Remove child nodes.

            :param children: The child nodes to remove.
            :return: List of removed child nodes.
            """
            if children is None:
                children = self.children

            # Ensure all provided nodes are actually children
            for child in children:
                if child.parent != self:
                    raise ValueError(f"Node {child} is not a child of {self}")

            removed_children = []
            for child in children:
                child.detach()
                removed_children.append(child)

            return removed_children
        
        @property
        def flattree(self) -> 'FlatTreeNew':
            """
            Get the underlying FlatTreeNew dictionary.
            """
            return self._tree

    def __init__(self, *args, **kwargs):
        """
        Initialize a FlatTreeNew.
        """
        super().__init__(*args, **kwargs)

    def detach(self, node: Union[str, 'FlatTreeNew.ProxyNode']) -> None:
        """
        Detach a node by setting its parent to `FlatTreeNew.DETACHED_KEY`.

        :param node: The node or key of the node to detach.
        :raises KeyError: If the node is not found in the tree.
        """
        if isinstance(node, FlatTreeNew.ProxyNode):
            node = node._key

        if node not in self:
            raise KeyError(f"Node not found: {node!r}")
        self[node][FlatTreeNew.PARENT_KEY] = FlatTreeNew.DETACHED_KEY

    def prune_detached(self) -> None:
        """
        Prune all detached nodes.

        :raises KeyError: If the node is not found in the tree.
        """
        detached = [key for key, value in self.items() if value.get(FlatTreeNew.PARENT_KEY) == FlatTreeNew.DETACHED_KEY]
        for key in detached:
            self.prune(key)

    def prune(self, node: Union[str, 'FlatTreeNew.ProxyNode']) -> None:
        """
        Prune a subtree rooted at the given key.

        :param node: The node or key of the node to prune.
        :raises KeyError: If the node is not found in the tree.
        """
        def _post_del(node):
            for child in node.children:
                _post_del(child)
            del self[node._key]

        if isinstance(node, str):
            node = self.get_node(node)

        if node._tree is not self:
            raise ValueError("Cannot prune a node from a different FlatTreeNew")

        _post_del(node)

    @property
    def root(self) -> ProxyNode:
        """
        Lazily compute the logical root. It is the parent of all nodes
        without a parent key or with a None parent key.

        :return: The logical root node.
        """
        return FlatTreeNew.ProxyNode(FlatTreeNew.LOGICAL_ROOT, self)

    @property
    def payload(self) -> dict:
        """
        Get the data of the root node.

        :return: Dictionary representing the data of the root node.
        """
        return {}

    def add_child(self, node: Optional[Union[ProxyNode, str]] = None, *args, **kwargs) -> ProxyNode:
        """
        Add a child node to the logical root. If `node` is None, a new node is
        created with a UUID key. If `node` is a string, it is used as the key for
        the new node. If `node` is a ProxyNode, it is cloned and added as a child.

        :param node: The unique key for the node or an existing ProxyNode.
        :param args: Positional arguments for the node. See ProxyNode.add_child.
        :param kwargs: Additional attributes for the node. See ProxyNode.add_child.
        For instance, you may want to clone the children of `node` too and thus
        `add_child` is called with the additional keyward argument `clone_children=True`.
        :return: The newly added node.
        """
        return self.root.add_child(node, *args, **kwargs)

    @property
    def children(self) -> List[ProxyNode]:
        """
        Get the children of the logical root node.

        :return: List of children nodes.
        """
        return self.root.children

    def check_valid(self) -> None:
        """
        Validate the tree structure to ensure the structural integrity of the tree.

        Ensures that all keys are unique and that parent references are valid.
        Raises a ValueError if the tree structure is invalid.
        """
        def _check_cycle(key, visited):
            if key in visited:
                raise ValueError(f"Cycle detected: {visited}")
            visited.add(key)
            par_key = self[key].get(FlatTreeNew.PARENT_KEY, None)
            if par_key is not None:
                _check_cycle(par_key, visited)

        for key, value in self.items():
            if not isinstance(value, dict):
                raise ValueError(f"Node {key}'s value must be a dictionary: {value=}")

            par_key = value.get(FlatTreeNew.PARENT_KEY, None)
            if par_key is not None and par_key not in self:
                raise KeyError(f"Parent node non-existent: {par_key!r}")

            _check_cycle(key, set())

    def get_node(self, key) -> ProxyNode:
        """
        Get a node from the tree.

        :param key: The unique key of the node.
        :return: ProxyNode representing the node.
        """
        if key not in self:
            raise KeyError(f"Node not found: {key!r}")
        return FlatTreeNew.ProxyNode(key, self)
