from typing import TYPE_CHECKING, Any, List, Optional, Union

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

    We provide a `FlatTreeNode` class which provides an interface to the
    underlying `FlatTree` object centered around nodes. See `flattree_node.py`
    for more details.
    """

    LOGICAL_ROOT = "__ROOT__"
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

    PARENT_KEY = "parent"
    """
    The key used to store the parent key of a node. Modify this if you want to
    use a different key to store the parent key.
    """

    DETACHED_KEY = "__DETACHED__"
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
        # we must exclude None, since it is not a valid key
        keys += [
            v.get(FlatTree.PARENT_KEY)
            for v in self.values()
            if v.get(FlatTree.PARENT_KEY) is not None
        ]
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

    def detach(self, key: str) -> "FlatTreeNode":
        """
        Detach node with key `key` by setting its parent to `FlatTree.DETACHED_KEY`
        which refers to a special key that we assume doesn't exist in the tree.

        :param key: The key of the node to detach.
        :return: The detached subtree rooted at the node.
        :raises KeyError: If the node is not found in the tree.
        """
        if key not in self:
            raise KeyError(f"Node not found: {key!r}")
        self[key][FlatTree.PARENT_KEY] = FlatTree.DETACHED_KEY
        return self.node(key)

    def prune(self, node: Union[str, "FlatTreeNode"]) -> List[str]:
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
            return False

        pruned = []
        utils.visit(node=node, func=_prune, order="post")
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
                raise ValueError(
                    f"Node {key!r} does not have dictionary: {value=}")

            par_key = value.get(FlatTree.PARENT_KEY, None)
            if par_key == FlatTree.DETACHED_KEY:
                continue

            if par_key is not None and par_key not in tree:
                raise KeyError(
                    f"Parent {par_key!r} not in tree for node {key!r}")

            _check_cycle(key, set())

    def node(self, key: str, root: Optional[str] = None) -> "FlatTreeNode":
        """
        Get sub-tree rooted at `root` node, with the current node set
        to the node with key `key`. Default root is current key.

        :param key: The unique key of the node.
        :param root: The key of the root node of the sub-tree.
        :return: FlatTreeNode proxy representing the node.
        """
        from .flattree_node import FlatTreeNode

        if key not in self.unique_keys():
            raise KeyError(f"Key not found: {key!r}")

        return FlatTreeNode.proxy(
            tree=self, node_key=key, root_key=key if root is None else root
        )

    @property
    def root(self) -> "FlatTreeNode":
        """
        Retrive the logical root of the tree. The represents the entire tree
        structure.

        :return: The logical root node.
        """
        return self.node(FlatTree.LOGICAL_ROOT)

    @property
    def detached(self) -> "FlatTreeNode":
        """
        Retrieve the detached tree. (This is detached from the logical root
        and is rooted at the logical node with the key `FlatTree.DETACHED_KEY`.)

        :return: The detached logical root node.
        """
        return self.node(FlatTree.DETACHED_KEY)
