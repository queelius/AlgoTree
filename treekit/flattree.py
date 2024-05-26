from typing import List
import uuid
import collections.abc
from typing import Dict, Any, List, Union, Optional, Iterator

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
        
        @property
        def parent(self) -> Optional['FlatTree.ProxyNode']:
            if self._key == FlatTree.LOGICAL_ROOT:
                return None
            key = self.parent_key
            return self._tree.get_node(key) if key is not None else self._tree.root
        
        @property
        def parent_key(self) -> Optional[str]:
            return None if self._key == FlatTree.LOGICAL_ROOT else \
                self._tree[self._key].get(FlatTree.PARENT_KEY)

        def __repr__(self):
            return f"{__class__.__name__}({dict(self)})"

        def __getitem__(self, key) -> Dict[str, Any]:
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

        @property
        def payload(self) -> Dict[str, Any]:
            """
            Get the payload data of the node.

            :return: Dictionary representing the data of the node.
            """
            return self._tree.payload if self._key == FlatTree.LOGICAL_ROOT else self._tree[self._key]

        def __iter__(self) -> Iterator[Any]:
            if self._key == FlatTree.LOGICAL_ROOT:
                return iter([])
            return iter(self._tree[self._key])

        def __len__(self) -> int:
            if self._key == FlatTree.LOGICAL_ROOT:
                return 0
            return len(self._tree[self._key])
        
        def add_child(self, key: Optional[str] = None, *args, **kwargs) -> 'FlatTree.ProxyNode':
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
        
        @property
        def children(self) -> List['FlatTree.ProxyNode']:
            """
            Get the children of the node.
            """
            if self._key == FlatTree.LOGICAL_ROOT:
                return [self._tree.get_node(k) for k in self._tree if
                        self._tree[k].get(FlatTree.PARENT_KEY) is None]
            else:
                return [self._tree.get_node(k) for k in self._tree if
                        self._tree[k].get(FlatTree.PARENT_KEY) == self._key]

        def remove_children(self, child: Optional[List['FlatTree.ProxyNode']] = None) -> List['FlatTree.ProxyNode']:
            """
            Remove a child node.

            This actually only **detaches** the nodes. If you want to prune
            them, you can call `prune_detached` on the underlying tree that
            this proxy node refers to.

            We implement this interface to be consistent with the general
            API of a tree node. Other alogorithms may use the API to perform
            operations on the tree without knowing the underlying implementation.

            Note that any descendants of the detached nodes are also detached, but we only include
            the direct children in the list of detached nodes.

            :param children: The child node to remove.
            :return: List of detached child nodes of the parent. If `child` is None, all children are detached.
            """

            if child is None:
                childs = self.children
                for c in childs:
                    c.detach()
                return childs

            # check that all children are actually children of the parent
            for c in child:
                if c.parent != self:
                    raise ValueError(f"Node {c} is not a child of {self}")

            results: List[FlatTree.ProxyNode] = []
            for c in child:
                c.detach()
                results.append(c)

            return results

    def __init__(self, *args,
                 #metadata: Optional[Dict[str, Any]] = None,
                 **kwargs):
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
        :param metadata: Metadata to be associated with the tree. We associate this data
                         with the logical root node.
        :param kwargs: Keyword arguments to be passed to the dictionary constructor.
        """
        super().__init__(*args, **kwargs)
        #self.metadata = metadata or {}

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
            for child in node.children:
                _post_del(child)
            del self[node._key]

        _post_del(self.get_node(key))
        
    @property
    def name(self) -> str:
        """
        Get the name of the tree (logical root).
        """
        return self.LOGICAL_ROOT
    
    @property
    def parent(self):
        """
        Get the parent of the tree (None).
        """
        return None
    
    @property
    def root(self) -> ProxyNode:
        """
        Lazily computes a logical root. It is the parent of all nodes
        without a parent key or a parent key that maps to None.

        :return: The logical root node.
        """
        return FlatTree.ProxyNode(self, FlatTree.LOGICAL_ROOT)

    @property
    def payload(self) -> dict:
        """
        Get the data of the root node ({})

        :return: Dictionary representing the data of the tree.
        """
        return {} #self._metadata
    
    def add_child(self, key: Optional[str] = None, *args, **kwargs) -> ProxyNode:
        """
        Add a child node to the logical root.

        We tree `FlatTree` as the logical root node. It's not represented in the
        dictionary but is the parent of all nodes without a parent key.
        

        :param key: The unique key for the node.
        :param args: Positional arguments for the node.
        :param kwargs: Additional attributes for the node.
        :return: The newly added node.
        """
        return self.root.add_child(key, *args, **kwargs)
    
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
            par_key = self[key].get(FlatTree.PARENT_KEY, None)
            if par_key is not None and par_key != FlatTree.DETACHED_KEY:
                _check_cycle(par_key, visited)

        for key, value in self.items():
            if not isinstance(value, dict):
                raise ValueError(f"Node {key}'s value must be a dictionary: {value=}")

            par_key = value.get(FlatTree.PARENT_KEY, None)
            if par_key == FlatTree.DETACHED_KEY:
                continue

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