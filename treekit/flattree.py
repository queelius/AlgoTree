from typing import List
import uuid
import collections.abc
from typing import Dict, Any, List, Union

class FlatTree(dict):
    """
    A tree class that is also a standard dictionary.

    This class represents a tree using a flat dictionary structure where each node
    has a unique key and an optional 'parent' key to reference its parent node.

    If there is a single node without a  'parent' key, it is
    the root node. If there are multiple nodes without a 'parent' key, the
    tree conceptually has a logical root node that is not represented in the
    dictionary but is the parent of all nodes without a 'parent' key.
    """

    LOGICAL_ROOT = '__ROOT__'
    PARENT_KEY = 'parent'
    DETACHED_KEY = '__DETACHED__'

    class ProxyNode(collections.abc.MutableMapping):
        __slots__ = ('_tree', '_key')

        def __init__(self, tree: 'FlatTree', key: str):
            """
            Initialize a ProxyNode.

            :param tree: The tree to which the node belongs.
            :param key: The unique key of the node.
            """
            self._tree = tree
            self._key = key

        @property
        def name(self):
            return self._key
        
        def get_parent(self) -> 'FlatTree.ProxyNode':
            if self._key == FlatTree.LOGICAL_ROOT:
                return None
            par_key = self.get_parent_key()
            return self._tree.get_node(par_key) if par_key is not None \
                else self._tree.get_root()
        
        def get_parent_key(self) -> str:
            return None if self._key == FlatTree.LOGICAL_ROOT else \
                self._tree[self._key].get(FlatTree.PARENT_KEY)

        def __repr__(self):
            return f"{__class__.__name__}({self._key}: {self.get_data()})"

        def __getitem__(self, key):
            return {} if self._key == FlatTree.LOGICAL_ROOT else \
                self._tree[self._key][key]

        def __setitem__(self, key, value):
            if self._key == FlatTree.LOGICAL_ROOT:
                raise TypeError(f"{self} is immutable")
            
            self._tree[self._key][key] = value
            self._tree.check_valid()

        def __delitem__(self, key):
            if self._key == FlatTree.LOGICAL_ROOT:
                raise TypeError(f"{self} is immutable")
            del self._tree[self._key][key]
            self._tree.check_valid()

        def detach(self) -> None:
            """
            Detach the node by setting its parent to `FlatTree.DETACHED_KEY`.
            """
            self._tree.detach(self._key)

        def get_data(self):
            """
            Get the data of the node.

            :return: Dictionary representing the data of the node.
            """
            return {} if self._key == FlatTree.LOGICAL_ROOT else self._tree[self._key]

        def __iter__(self):
            if self._key == FlatTree.LOGICAL_ROOT:
                return iter([])
            return iter(self._tree[self._key])

        def __len__(self):
            if self._key == FlatTree.LOGICAL_ROOT:
                return 0
            return len(self._tree[self._key])
        
        def add_child(self, key: str = None, *args, **kwargs) -> 'FlatTree.ProxyNode':
            """
            Add a child node. If the key is None, a UUID is generated.

            :param key: The unique key for the node.
            :param args: Positional arguments for the node.
            :param kwargs: Additional attributes for the node.
            :return: The newly added node.
            """
            if key is None:
                key = str(uuid.uuid4())
            if key in self._tree:
                raise KeyError("Node key already exists in the tree")
            
            child = dict(*args, **kwargs)
            if self._key == FlatTree.LOGICAL_ROOT:
                if child.get(FlatTree.PARENT_KEY) is not None:
                    raise ValueError("Child of logical root cannot have a parent key not None")
            else:
                if FlatTree.PARENT_KEY in child and child.get(FlatTree.PARENT_KEY) != self._key:
                    raise ValueError("Child of {self} cannot set a parent that is different from the node's key")
                child[FlatTree.PARENT_KEY] = self._key
            
            self._tree[key] = child
            return self._tree.get_node(key)

        def children(self):
            """
            Get the children of the node.
            """
            if self._key == FlatTree.LOGICAL_ROOT:
                return [self._tree.get_node(k) for k in self._tree if
                        self._tree[k].get(FlatTree.PARENT_KEY) is None]
            else:
                return [self._tree.get_node(k) for k in self._tree if
                        self._tree[k].get(FlatTree.PARENT_KEY) == self._key]

    def __init__(self, *args, **kwargs):
        """
        Initialize a FlatTree.

        Examples:
            FlatTree() # empty tree
            FlatTree({'a': {'parent': None}, 'b': {'parent': 'a'}})
            FlatTree(a={}, b={'parent': 'a'})
            FlatTree([('a', {'parent': None}), ('b', {'parent': 'a'})])
            FlatTree([('a', {}), ('b', {'parent': 'a'})])

        With the exception of the first, the other examples are equivalent.
        They create a tree with two nodes, 'a' and 'b', where 'b' is a child of 'a'
        and 'a' is a child of the logical root node (a special node that is not
        represented in the dictionary but is the parent of all nodes without a parent key).

        For instance:
            FlatTree(a={}, b={})
        creates a tree with two nodes, 'a' and 'b', where both are children of
        the logical root node. If the logical root node was not present, then
        technically this would be a forest of two trees. The logical root node
        is a convenience to represent a single tree structure. You can get
        a tree rooted at a node by calling `get_node` with the key of the node.
        This will return a ProxyNode object that represents the node and its children.

        :param args: Positional arguments to be passed to the dictionary constructor.
        :param kwargs: Keyword arguments to be passed to the dictionary constructor.
        """
        super().__init__(*args, **kwargs)

    def detach(self, key: str) -> None:
        """
        Detach each node in `keys` by setting its parent to `FlatTree.DETACHED_KEY`
        which refers to a special key that we assume doesn't exist in the tree.

        When we detach a node, we are effectively removing the subtree rooted at
        that node. It is easy to remove subtrees rooted at a particular node or
        key using the `prune` method,

        :param key: The key of the node to detach.
        :raises KeyError: If the node is not found in the tree.
        """

        if key not in self:
            raise KeyError(f"Node not found: {key!r}")
        self[key][FlatTree.PARENT_KEY] = FlatTree.DETACHED_KEY

    def prune_detached(self) -> None:
        """
        Prune all nodes that are detached.

        This is equivalent to removing all nodes that have a parent key that
        is `FlatTree.DETACHED_KEY`.
        """

        # find the nodes with parent key as FlatTree.DETACHED_KEY
        detached = [key for key, value in self.items() if value.get(FlatTree.PARENT_KEY) == FlatTree.DETACHED_KEY]
        for key in detached:
            self.prune(key)

    def prune(self, key: str) -> None:
        """
        Prune the subtree rooted at `key`.

        This is equivalent to removing the node and all its children from the tree.

        :param key: The key of the node to prune.
        :raises KeyError: If the node is not found in the tree.
        """
        def _post_del(node):
            childs = node.children()
            for child in childs:
                _post_del(child)  # post-order deletion
            del self[node._key]

        _post_del(self.get_node(key))
        
    @property
    def name(self) -> str:
        return self.LOGICAL_ROOT

    def get_root(self) -> ProxyNode:
        """
        Lazily computes a logical root. It is the parent of all nodes
        without a parent key or a parent key that maps to None.

        :return: The logical root node.
        """
        return FlatTree.ProxyNode(self, FlatTree.LOGICAL_ROOT)

    def get_data(self) -> dict:
        """
        Get the data of the root node ({})

        :return: Dictionary representing the data of the tree.
        """
        return self.get_root().get_data()
    
    def add_child(self, key: str = None, *args, **kwargs) -> ProxyNode:
        """
        Add a child node to the logical root.

        We tree `FlatTree` as the logical root node. It's not represented in the
        dictionary but is the parent of all nodes without a parent key.
        

        :param key: The unique key for the node.
        :param args: Positional arguments for the node.
        :param kwargs: Additional attributes for the node.
        :return: The newly added node.
        """
        return self.get_root().add_child(key, *args, **kwargs)
    
    def children(self) -> List[ProxyNode]:
        """
        Get the children of the logical root node.

        :return: List of children nodes.
        """
        return self.get_root().children()

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
            par_key = self[key].get(FlatTree.PARENT_KEY, None)
            if par_key is not None:
                _check_cycle(par_key, visited)

        for key, value in self.items():
            if not isinstance(value, dict):
                raise ValueError(f"Node {key}'s value must be a dictionary: {value=}")

            par_key = value.get(FlatTree.PARENT_KEY, None)
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
        return FlatTree.ProxyNode(self, key)