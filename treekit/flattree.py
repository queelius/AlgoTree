from typing import List
import uuid
import collections.abc
from typing import Dict, Any

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

    LOGICAL_ROOT = '__logical_root__'
    PARENT_KEY = 'parent'

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
            par_key = self._tree[self._key].get(FlatTree.PARENT_KEY, None)
            return self._tree.get_node(par_key) if par_key is not None else self._tree.get_root()

        def __repr__(self):
            if self._key == FlatTree.LOGICAL_ROOT:
                return f"{__class__.__name__}({self._key})"
            else:
                return f"{__class__.__name__}({self._key}: {self._tree[self._key]})"

        def __getitem__(self, key):
            if self._key == FlatTree.LOGICAL_ROOT:
                return {}
            return self._tree[self._key][key]

        def __setitem__(self, key, value):
            if self._key == FlatTree.LOGICAL_ROOT:
                raise TypeError(f"{self} is immutable")
            
            self._tree[self._key][key] = value
            self._tree.check_valid()

        def __delitem__(self, key):
            if self._key == FlatTree.LOGICAL_ROOT:
                raise TypeError(f"{self} is immutable")
            del self._tree[self._key][key]

        def get_data(self):
            if self._key == FlatTree.LOGICAL_ROOT:
                return {}
            return self._tree[self._key]

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
                raise KeyError("Node key already exists")
            
            child = dict(*args, **kwargs)
            if self._key == FlatTree.LOGICAL_ROOT:
                if FlatTree.PARENT_KEY in child and child[FlatTree.PARENT_KEY] is not None:
                    raise ValueError(f"Child of {self} cannot set a parent that is not None")
            else:
                if FlatTree.PARENT_KEY in child and child[FlatTree.PARENT_KEY] != self._key:
                    raise ValueError("Child of {self} cannot set a parent that is different from the node's key")
                child[FlatTree.PARENT_KEY] = self._key
            
            self._tree[key] = child
            return self._tree.get_node(key)

        def children(self):
            if self._key == FlatTree.LOGICAL_ROOT:
                return [self._tree.get_node(k) for k in self._tree if
                        self._tree[k].get(FlatTree.PARENT_KEY) is None]
            else:
                return [self._tree.get_node(k) for k in self._tree if
                        self._tree[k].get(FlatTree.PARENT_KEY) == self._key]


    def get_schema(self) -> dict:
        """
        Get the schema of the tree.

        :return: Dictionary representing the schema of the tree.
        """
        return {
            '<unique_node_key>':
            {
                # if the parent key doesn't exist, node is a child of logical root
                FlatTree.PARENT_KEY: '<parent_node_key|None>',

                # Additional data
            }
            # More nodes
        }    

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

        :param check: whether to check the tree structure for validity on each modification.
        :param args: Positional arguments to be passed to the dictionary constructor.
        :param kwargs: Keyword arguments to be passed to the dictionary constructor.
        """
        super().__init__(*args, **kwargs)

        self.check = True
        self.check_valid()

    def get_root(self) -> ProxyNode:
        """
        Lazily computes a logical root. It is the parent of all nodes
        without a parent key or a parent key that maps to None.

        :return: The logical root node.
        """
        return FlatTree.ProxyNode(self, FlatTree.LOGICAL_ROOT)
    
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

    def set_check(self, check: bool) -> None:
        """
        Set whether to check the tree structure for validity on each modification.

        :param check: Whether to check the tree structure.
        """
        self.check = check

    def check_valid(self) -> None:
        """
        Validate the tree structure to ensure the structural integrity of the tree.

        Ensures that all keys are unique and that parent references are valid.
        Raises a ValueError if the tree structure is invalid.
        """

        if not self.check:
            return

        # X -> Y  <=> Y is a child of X
        # ... -> A -> B -> ... -> A -> ...
        # is a cycle and thus not a tree    
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

    def __setitem__(self, key, value):
        """
        Set a node in the tree.

        :param key: The unique key for the node.
        :param value: A dictionary representing the node's attributes.
        """
        super().__setitem__(key, value)
        #if not isinstance(value, dict):
        #    raise ValueError("Value must be a dictionary")
        self.check_valid()

    def get_node(self, key) -> ProxyNode:
        """
        Get a node from the tree.

        :param key: The unique key of the node.
        :return: ProxyNode representing the node.
        """
        if key not in self:
            raise KeyError(f"Node not found: {key!r}")
        return FlatTree.ProxyNode(self, key)

    def __delitem__(self, key):
        """
        Remove a node and all its children recursively.

        :param key: The unique key of the node to remove.
        """
        children = self.get_node(key).children()
        for child in children:
            del self[child]
        super().__delitem__(key)