from typing import List
import uuid
import collections.abc

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

    class ProxyNode(collections.abc.MutableMapping):
        __slots__ = ('_tree', '_key')

        def __init__(self, tree: 'FlatTree', key: str):
            self._tree = tree
            self._key = key

        def name(self):
            return self._key
        
        def get_parent(self) -> 'FlatTree.ProxyNode':
            if self._key == '__logical_root__':
                return None
            parent_key = self._tree[self._key].get('parent', None)
            return self._tree.get_node(parent_key) if parent_key is not None else None

        def __repr__(self):
            if self._key == '__logical_root__':
                return f"ProxyNode(key=__logical_root__)"
            else:
                return f"ProxyNode({self._key}: {self._tree[self._key]})"

        def __getitem__(self, key):
            if self._key == '__logical_root__':
                raise TypeError("__logical_root__ is empty")
            return self._tree[self._key][key]

        def __setitem__(self, key, value):
            if self._key == '__logical_root__':
                raise TypeError("__logical_root__ is immutable")
            self._tree[self._key][key] = value

        def __delitem__(self, key):
            if self._key == '__logical_root__':
                raise TypeError("__logical_root__ is immutable")
            del self._tree[self._key][key]

        def __iter__(self):
            return iter([]) if self._key == '__logical_root__' else iter(self._tree[self._key])

        def __len__(self):
            return 0 if self._key == '__logical_root__' else len(self._tree[self._key])

        def add_child(self, key=None, **kwargs) -> 'FlatTree.ProxyNode':
            """
            Add a child node. If the key is None, a UUID is generated.

            :param key: The unique key for the node.
            :param kwargs: Additional attributes for the node.
            :return: The newly added node.
            """
            if key is None:
                key = str(uuid.uuid4())

            if key in self._tree:
                raise KeyError("Node key already exists")
            if 'parent' in kwargs and kwargs['parent'] != self._key:
                raise ValueError("Cannot set a different parent")
            
            if self._key == '__logical_root__':
                kwargs['parent'] = None
            else:
                kwargs['parent'] = self._key
            self._tree[key] = kwargs
            return self._tree.get_node(key)

        def children(self):
            if self._key == '__logical_root__':
                return [self._tree.get_node(k) for k in self._tree if self._tree[k].get('parent') is None]
            else:
                return [self._tree.get_node(k) for k in self._tree if self._tree[k].get('parent') == self._key]


    def get_schema(self) -> dict:
        """
        Get the schema of the tree.

        :return: Dictionary representing the schema of the tree.
        """
        return {
            'unique_node_key':
            {
                'parent': 'parent_node_key|None',
                # Additional data
            }
            # More nodes
        }    

    def __init__(self, *args, **kwargs):
        """
        Initialize a FlatTree.

        :param args: Arguments to be passed to the dictionary constructor.
        :param kwargs: Keyword arguments to be passed to the dictionary constructor.
        """
        super().__init__(*args, **kwargs)
        self.check_valid()

    def get_root(self) -> ProxyNode:
        """
        Get the root node of the tree.

        If there is a single node without a 'parent' key, it is the root node.
        Otherwise, the tree has a logical root node that is not represented in
        the dictionary.

        :return: The key of the root node.
        """
        root_keys = [k for k, v in self.items() if v.get('parent', None) is None]
        if len(root_keys) == 1:
            return FlatTree.ProxyNode(self, root_keys[0])
        else:
            return FlatTree.ProxyNode(self, '__logical_root__')
    
    def check_valid(self) -> None:
        """
        Validate the tree structure to ensure the structural integrity of the tree.

        Ensures that all keys are unique and that parent references are valid.
        Raises a ValueError if the tree structure is invalid.
        """
        if len(self) != len(set(self.keys())):  # check for duplicate keys
            raise ValueError("Duplicate node key")

        for key, value in self.items():
            if 'parent' in value:
                parent = value['parent']
                if parent is not None and parent not in self:
                    raise ValueError(f"Parent key not found: {parent!r}")
                if parent == key:
                    raise ValueError(f"Node cannot be its own parent: {key!r}")

    def __setitem__(self, key, value):
        """
        Set a node in the tree.

        :param key: The unique key for the node.
        :param value: A dictionary representing the node's attributes.
        """
        super().__setitem__(key, value)
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