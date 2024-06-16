from typing import TYPE_CHECKING, Any, List, Optional, Union
from AlgoTree import utils

if TYPE_CHECKING:
    from flattree_node import FlatTreeNode

class FlatTree(dict):
    """
    A tree class that is also a standard dictionary.

    This class represents a tree using a flat dictionary structure where each node
    has a unique key and an optional 'parent' key to reference its parent node.

    The first node found that is without a  'parent' key is
    the root node. If there are multiple nodes without a 'parent' key, the
    structure is technically a forrest. You may get all of the trees
    with the `forest` method, which returns a list of the root nodes.

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
        and 'a' is the root node.

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
        keys = [FlatTree.DETACHED_KEY]
        keys += list(self.keys())
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

        return [k for k, v in self.items() if v.get(FlatTree.PARENT_KEY) == key]

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

        root_count = 0
        for key, value in tree.items():
            if not isinstance(value, dict):
                raise ValueError(
                    f"Node {key!r} does not have dictionary: {value=}")

            par_key = value.get(FlatTree.PARENT_KEY)
            if par_key == FlatTree.DETACHED_KEY:
                continue

            if par_key is None:
                root_count = root_count + 1
                if root_count > 1:
                    raise ValueError(
                        "Multiple root nodes found in tree: {root_count}")

            if par_key is not None and par_key not in tree:
                raise KeyError(
                    f"Parent {par_key!r} not in tree for node {key!r}")

            _check_cycle(key, set())

    def node(self, name: str) -> "FlatTreeNode":
        """
        Reposition the current node in the to the node with name `name`. The
        tree is not changed, only the current node pointer.

        Note: This behaves differenyly than you might expect. We return a
        proxy of a node in the tree, not the actual node. In particular, this
        returns a `FlatTreeNode` object which represents the entire `FlatTree`
        as the sub-tree with the current node set to the node with key `name`.
        Subsequently, you can use `node`, `subtree`, `root`, and other methods
        on the `FlatTreeNode` object to navigate the tree.

        :param name: The name of the node (in the FlatTree, it is a unique key)
        :return: FlatTreeNode proxy representing the node.
        :raises KeyError: If the name (key) is not found in the tree.
        """
        from .flattree_node import FlatTreeNode

        if name not in self.unique_keys():
            raise KeyError(f"Key not found: {name!r}")

        return FlatTreeNode.proxy(
            tree=self, node_key=name, root_key=self.root_key
        )

    def subtree(self, name: Optional[str] = None) -> "FlatTreeNode":
        """
        Get sub-tree rooted at the node with the name `name` with the current
        node also set to the node with name `name`.

        :param name: The unique key of the node.
        :return: FlatTreeNode proxy representing the node.
        """
        from .flattree_node import FlatTreeNode

        if name not in self.unique_keys():
            raise KeyError(f"Name (unique key) not found: {name!r}")

        if name is None:
            name = self.root_key

        return FlatTreeNode.proxy(tree=self, node_key=name, root_key=name)

    @property
    def root(self) -> "FlatTreeNode":
        """
        Retrive the root of the tree. The represents the entire tree
        structure.

        :return: The root node.
        """
        return self.subtree(self.root_key)
    
    @property
    def root_key(self) -> str:
        """
        Retrieve the key of the root node.

        :return: The key of the root node.
        """
        # find the first node without a parent key or a parent key
        # that is None
        for key, value in self.items():
            if value.get(FlatTree.PARENT_KEY) is None:
                return key
            
        raise ValueError("No root node found in tree")
    
    @property
    def parent(self) -> "FlatTreeNode":
        """
        Retrieve the parent of the current node.

        :return: The parent node.
        """
        return self.root.parent

    @property
    def payload(self) -> Any:
        """
        Retrieve the payload of the current node.

        :return: The payload of the current node.
        """
        return self.root.payload

    @property
    def name(self) -> str:
        """
        Retrieve the name of the current node.

        :return: The name of the current node.
        """
        return self.root_key

    @property
    def detached(self) -> "FlatTreeNode":
        """
        Retrieve the detached tree. (This is detached from the "true" root
        and is rooted at a logical node with the key `FlatTree.DETACHED_KEY`.)

        :return: The detached logical root node.
        """
        return self.subtree(FlatTree.DETACHED_KEY)


    @property
    def children(self) -> List["FlatTreeNode"]:
        """
        Retrieve the children of the current node.

        :return: List of children nodes.
        """
        return self.root.children

    def __repr__(self) -> str:
        return f"FlatTree({dict(self)})"

    def to_dict(self) -> dict:
        """
        Convert the tree to a dictionary. This is already a dictionary, so
        we just return the tree itself recasted as a dictionary.

        :return: The tree as a dictionary.
        """
        return dict(self)
    
    def __str__(self) -> str:
        if self.parent is None:
            return f"FlatTree(name={self.name}, payload={self.payload}, num_children={len(self.children)})"
        else:
            return f"FlatTree(name={self.name}, payload={self.payload}), parent={self.parent.name}, num_children={len(self.children)})"
        