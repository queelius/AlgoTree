from typing import List, TYPE_CHECKING, Union, Callable, Any, Optional
from treekit import utils

if TYPE_CHECKING:
    from flattree_node import FlatTreeNode

class FlatTree(dict):
    """
    A tree class that is also a standard dictionary.

    This class represents a tree using a flat dictionary structure where each node
    has a unique key and an optional 'parent' key to reference its parent node.

    If there is a single node without a  'parent' key, it is
    the root node. If there are multiple nodes without a 'parent' key, the
    tree conceptually has a logical root node that is not represented in the
    dictionary but is the parent of all nodes without a 'parent' key.

    The `FlatTree` class is a dictionary whose data represents a tree-like
    structure. It provides methods to manipulate the tree structure and
    validation methods to check the integrity of the tree structure, but is
    essentially a view of the `dict` object passed into it (or created with it).
    A major use-case is passing in an entire dictionary representing a tree
    structure and then using the `FlatTree` object to manipulate the tree
    structure. You can then convert the `FlatTree` object back to a dictionary
    using the `dict` constructor.

    # FlatTree Specification

    The `dict` should have the following structure:

    ```python
    {
        "<node_key>": {
        
            # Parent key (optional). If blank or null/None, parent is the
            # logical root node.
            "parent": "<parent_node_key>",
            
            # Node payload (optional key-value pairs)
            "<key>": "<value>",
            <key>: <value>,
            # ... more key-value pairs representing the node's payload
        }
        # ... more key-value pairs representing the tree's nodes
    }
    ```

    Finally, and perhaps most powerfully, we provide a `FlatTreeNode` class
    which provides an interface to the underlying `FlatTree` object centered
    around nodes. See ``flattree_node.py`` for more details. 
    """

    LOGICAL_ROOT = '__ROOT__'
    """
    The key of the logical root node. This node is always the root node of
    FlatTree objects. the logical root node is a convenience to represent a
    single tree structure, even when there are multiple nodes without a parent
    specified. It is not represented in the dictionary but is the parent of all
    nodes without a parent key (or with a parent key that maps to None). The
    logical root node is lazily computed when needed. See the `root` property.
    Note that it returns a FlatTreeNode object, which is a proxy for the
    nodes in the tree.
    """

    PARENT_KEY = 'parent'
    """
    The key used to store the parent key of a node. Modify this if you want to
    use a different key to store the parent key.
    """

    DETACHED_KEY = '__DETACHED__'
    """
    The key used to represent a detached node. This is a special key that is
    assumed to not exist in the tree. When a node is detached, its parent key
    is set to this value. Any descendants of the detached node are also
    detached.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
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
        and 'a' is a child of the logical root node.

        :param args: Positional arguments to be passed to the dictionary constructor.
        :param kwargs: Keyword arguments to be passed to the dictionary constructor.
        """
        super().__init__(*args, **kwargs)

    def unique_keys(self) -> List[str]:
        """
        Get the unique keys in the tree, even if they are not nodes in the tree
        but only parent keys without corresponding nodes.

        :return: List of unique keys in the tree.
        """
        keys = [FlatTree.LOGICAL_ROOT, FlatTree.DETACHED_KEY]
        keys += list(self.keys())
        keys += [v.get(FlatTree.PARENT_KEY) for v in self.values()]
        return list(set(keys))

    def child_keys(self, key: str) -> List[str]:
        """
        Get the children keys of a node with key `key`.

        :param key: The key of the node.
        :return: List of keys of the children of the node.
        """

        if key not in self.unique_keys():
            raise KeyError(f"Key not found: {key!r}")
        par_key = None if key == FlatTree.LOGICAL_ROOT else key
        return [k for k, v in self.items() if v.get(FlatTree.PARENT_KEY) == par_key]

    def detach(self, key: str) -> 'FlatTreeNode':
        """
        Detach node with key `key` by setting its parent to `FlatTree.DETACHED_KEY`
        which refers to a special key that we assume doesn't exist in the tree.

        NOTE: Cannot detach purely logical nodes like the logical root node
              and the root of all detached nodes. They are lazily generated
              and are not part of the tree structure.

        :param key: The key of the node to detach.
        :return: The detached subtree rooted at the node.
        :raises KeyError: If the node is not found in the tree.
        """
        if key not in self:
            raise KeyError(f"Node not found: {key!r}")
        self[key][FlatTree.PARENT_KEY] = FlatTree.DETACHED_KEY
        return self.root_under(key, key, self.child_keys(key))
       
    def prune(self, node: Union[str, 'FlatTreeNode']) -> List[str]:
        """
        Prune the subtree rooted at the given node (`node` can be a
        unique key for the node or a `FlatTreeNode` object).

        :param node: The node to prune.
        :return: The list of keys pruned (in post-order).
        :raises KeyError: If the node is not found in the tree.
        """

        if isinstance(node, str):
            node = self.node(node)

        def _prune(node):
            nonlocal pruned
            if node._key in self:
                pruned.append(node._key)
                del self[node._key]

        pruned = []
        utils.visit(node=node, func=_prune, order='post')
        return pruned
    
    @staticmethod
    def check_valid(tree) -> None:
        """
        Validate the tree structure to ensure the structural integrity of the tree.

        This function performs the following validation checks:

         1) No cycles exist in the tree structure.
         2) All keys (unique node identifiers) map to dictionary values.
         3) All nodes have a parent key that is either None or a valid key
            in the tree.

        Note: This function ignores detached nodes, since they are not part of
        the tree structure and represent a separate tree structure rooted
        under `FlatTree.DETACHED_KEY`. 

        Raises a ValueError if the tree structure is invalid.

        TODO: Move check_valid to FlatTreeNode.check_valid, so that it
              checks to see if the sub-tree rooted at the node is valid.
              Then, check_valid for the FlatTree is just:
                FlatTreeNode.check_valid(root),
              but we have more granularity and flexibility in checking the
              validity of tree structures, e.g., we can apply it to detached
              trees or, any sub-tree, and other logical groupings of nodes
              rooted at some logical node.

        """
        def _check_cycle(key, visited):
            if key in visited:
                raise ValueError(f"Cycle detected: {visited}")
            visited.add(key)
            par_key = tree[key].get(FlatTree.PARENT_KEY, None)
            if par_key is not None and par_key != FlatTree.DETACHED_KEY:
                _check_cycle(par_key, visited)

        for key, value in tree.items():
            if not isinstance(value, dict):
                raise ValueError(f"Node {key!r} does not have dictionary: {value=}")

            par_key = value.get(FlatTree.PARENT_KEY, None)
            if par_key == FlatTree.DETACHED_KEY:
                continue

            if par_key is not None and par_key not in tree:
                raise KeyError(f"Parent {par_key!r} not in tree for node {key!r}")
            
            _check_cycle(key, set())
    
    def root_under(self,
                   key: str,
                   root_key: str,
                   root_child_keys: Optional[List[str]] = None) -> 'FlatTreeNode':
        """
        Create a node view of sub-tree rooted at a logical root with key
        'root_key' with the nodes in 'root_child_keys' as its children. The
        current node in this subtree is set to node with the key `key`.

        :param key: The key of the node that is a descendant of the root.
        :param root_key: The key of the root node.
        :param root_child_keys: The keys which are children of the root.
        :return: The node with key `key` in the sub-tree rooted at `root_key`
                 which has children `root_child_keys`.
        """
        from .flattree_node import FlatTreeNode
        return FlatTreeNode.proxy(self, key, root_key, root_child_keys)

    def node(self, key: str, rooted_at: Optional[str] = None) -> 'FlatTreeNode':
        """
        Get sub-tree rooted at `rooted_at` node, with the current node set
        to the node with key `key`. If `rooted_at` is None, the root of the
        subtree is set to the node with key `key`.

        The reason we allow for the `rooted_at` to differ from the `key` is
        so that we can view the tree structure from the perspective of a
        different node, but we want the current node in this tree view to be
        the node with key `key`.

        :param key: The unique key of the node.
        :param rooted_at: The key of the root node of the sub-tree.
        :return: FlatTreeNode proxy representing the node.
        """
        from .flattree_node import FlatTreeNode

        if key not in self.unique_keys():
            raise KeyError(f"Key not found: {key!r}")
        
        if rooted_at is None:
            rooted_at = key

        root_child_keys = self.child_keys(key)
        return FlatTreeNode.proxy(self, key, rooted_at, root_child_keys)

    @property
    def root(self) -> 'FlatTreeNode':
        """
        Retrive the logical root of the tree. The represents the entire tree
        structure.

        :return: The logical root node.
        """
        from .flattree_node import FlatTreeNode
        return FlatTreeNode.proxy(self, FlatTree.LOGICAL_ROOT, FlatTree.LOGICAL_ROOT,
                                  None)
            #self.child_keys(FlatTree.LOGICAL_ROOT))

    @property
    def detached(self) -> 'FlatTreeNode':
        """
        Retrieve the detached tree. (This is detached from the logical root
        and is rooted at the logical node with the key `FlatTree.DETACHED_KEY`.)

        :return: The detached logical tree.
        """
        from .flattree_node import FlatTreeNode
        return FlatTreeNode.proxy(self, FlatTree.DETACHED_KEY, FlatTree.DETACHED_KEY,
                                  None)
            #self.child_keys(FlatTree.DETACHED_KEY))

