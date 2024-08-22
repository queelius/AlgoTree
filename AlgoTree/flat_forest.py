from typing import TYPE_CHECKING, Any, List, Optional, Dict

if TYPE_CHECKING:
    from flat_forest_node import FlatForestNode

class FlatForest(dict):
    """
    A forest class that is also a standard dictionary.

    This class represents a forest using a flat dictionary structure where each
    node has a unique name (key) and an optional 'parent' name (keY) to
    reference its parent node.

    Nodes without a 'parent' key (or with a 'parent' key set to None) are
    root nodes of trees in the forest. Nodes with a 'parent' key set to a valid
    name (key) in the forest are children of the node with that name. Each
    node represents a tree rooted at that node, which we expose through the
    `FlatForestNode` class, which provides a proxy interface to the structure
    centered around nodes abstracted away from the dictionary structure.

    The `FlatForest` class is a dictionary whose data represents a forest-like
    structure. It provides methods to manipulate the forest structure and
    validation methods to check its integrity, but is essentially a view of the
    `dict` object passed into it (or created with it).

    We provide a `FlatForestNode` class which provides an interface centered
    around nodes in a tree. See `flat_forest_node.py` for more details.
    """

    PARENT_KEY = "parent"
    """
    The key used to store the parent key of a node. Modify this if you want to
    use a different key to store the parent key.
    """

    DETACHED_KEY = "__DETACHED__"
    """
    The name used to represent a detached node. This is a special name that is
    assumed to not exist in the tree. When a node is detached, its parent name
    is set to this value. Any descendants of the detached node are also
    detached.
    """

    @staticmethod
    def spec() -> dict:
        """
        Get the JSON specification of the FlatForest data structure.
        
        This method returns a dictionary representing the structure of the
        FlatForest. This is useful for documentation purposes and for
        understanding the structure of the data. The structure is as follows:

        {
            "<node_key>": {
                "parent" | None: "<parent_key>" | None,
                "<any_key>": "<any_value>",
                "...": "...",
                "<any_key>": "<any_value>"
            },
            "...": "...",
            "<node_key>": {
                "parent" | None: "<parent_key>" | None,
                "<any_key>": "<any_value>",
                "...": "...",
                "<any_key>": "<any_value>"
            }
        }

        :return: A dict pattern representing the structure of the FlatForest.
        """

        return {
            "<node_key>": {
                "parent" | None: "<parent_key>" | None,
                "<any_key>": "<any_value>",
                "...": "...",
                "<any_key>": "<any_value>"
            },
            "...": "...",
            "<node_key>": {
                "parent" | None: "<parent_key>" | None,
                "<any_key>": "<any_value>",
                "...": "...",
                "<any_key>": "<any_value>"
            }
        }
    
    @staticmethod
    def is_valid(data) -> bool:
        """
        Check if the given data is a valid FlatForest.

        :param data: The data to check.
        :return: True if the data is a valid FlatForest, False otherwise.
        """
        try:
            FlatForest.check_valid(data)
            return True
        except ValueError:
            return False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize a FlatForest.

        An empty FlatForest can be created by calling `FlatForest()`.

        Since dictionaries can be created in multiple ways, we have multiple
        ways to create a FlatForest:

        Examples:
            FlatForest('a': {'parent': None}, 'b': {'parent': None}, 'c': {'parent': 'a'})
            FlatForest({'a': {}, 'b': {}, 'c': {'parent': 'a'}})
            FlatForest(a={}, b={}, c={'parent': 'a'})
            FlatForest([('a', {}), ('b', {}), ('c', {'parent': 'a'})])

        These examples are equivalent. They create a forest with 3 nodes,
        'a', 'b', and 'c', where 'a' and 'b' are root nodes and 'c' is a child
        of 'a'. The second example is the most common way to create a FlatForest,
        where we pass a dictionary to the constructor. Since the FlatForest is
        a subclass of the dictionary class, we can use all the methods of the
        dictionary class on the FlatForest. The FlatForest class provides
        additional methods to manipulate the tree structure. The FlatForest
        class also provides a `FlatForestNode` class that provides an interface
        to the tree structure centered around nodes, abstracting away the
        dictionary structure.

        :param args: Positional arguments to be passed to the dictionary constructor.
        :param kwargs: Keyword arguments to be passed to the dictionary constructor.
        """
        super().__init__(*args, **kwargs)
        self._preferred_root = None

    def unique_names(self) -> List[str]:
        """
        Get the unique names in the tree, even if they are not nodes in the tree
        but only parent names without corresponding nodes.

        :return: List of unique names in the tree.
        """
        names = [FlatForest.DETACHED_KEY]
        names += list(self.keys())
        names += [
            v.get(FlatForest.PARENT_KEY)
            for v in self.values()
            if v.get(FlatForest.PARENT_KEY) is not None
        ]
        return list(set(names))

    def child_names(self, name: str) -> List[str]:
        """
        Get the children names of a node with the given name.

        :param name: The name of the node to get the children of.
        :return: List of names of the children of the node.
        """

        #if name not in self.unique_names():
        #    raise KeyError(f"Node name not found: {name!r}")

        return [k for k, v in self.items() if v.get(FlatForest.PARENT_KEY) == name]

    def detach(self, name: str) -> "FlatForestNode":
        """
        Detach subtree rooted at node with the given name by setting its parent
        to `FlatForest.DETACHED_KEY`, which denotes a special name (key) that we
        assume doesn't exist in the forest.

        :param name: The name of the node to detach.
        :return: The detached subtree rooted at the node.
        :raises KeyError: If the node is not found in the tree.
        """
        if name not in self:
            raise KeyError(f"Node not found: {name!r}")
        self[name][FlatForest.PARENT_KEY] = FlatForest.DETACHED_KEY
        return self.subtree(name)

    @staticmethod
    def check_valid(data) -> None:
        """
        Validate the forest structure to ensure the structural integrity of the
        trees.

        This function performs the following validation checks:

         1) No cycles exist in any trees.
         2) All names (unique node identifiers) map to dictionary values.
         3) All nodes have a parent key that is either None or a valid key
            in the tree.

        :param data: The forest data to validate.
        :return: None
        :raises ValueError: If the forest structure is invalid.
        """

        if not isinstance(data, dict):
            raise ValueError(f"Data is not a dictionary: {data=}")
        
        def _check_cycle(key, visited):
            if key in visited:
                raise ValueError(f"Cycle detected: {visited}")
            visited.add(key)
            par_key = data[key].get(FlatForest.PARENT_KEY, None)
            if par_key is not None:
                _check_cycle(par_key, visited)

        for key, value in data.items():
            if not isinstance(value, dict):
                raise ValueError(
                    f"Node {key!r} does not have a payload dictionary: {value!r}")

            par_key = value.get(FlatForest.PARENT_KEY)
            if par_key == FlatForest.DETACHED_KEY:
                continue

            if par_key is not None and par_key != FlatForest.DETACHED_KEY and par_key not in data:
                raise KeyError(
                    f"Parent {par_key!r} not in forest for node {key!r}")

            _check_cycle(key, set())

    def as_tree(self, root_name = "__ROOT__") -> "FlatForestNode":
        """
        Retrieve the forest as a single tree rooted at a logical root node.
        """

        from .flat_forest_node import FlatForestNode
        import copy
        new_dict = {}
        new_dict[root_name] = {FlatForest.PARENT_KEY: None}
        for key in self.keys():
            #new_dict[key] = copy.deepcopy(self[key])
            new_dict[key] = self[key].copy()
            if self[key].get(FlatForest.PARENT_KEY) is None:
                new_dict[key][FlatForest.PARENT_KEY] = root_name
        return FlatForestNode(forest=FlatForest(new_dict), name=root_name)
        

    def root_key(self, name: str) -> str:
        """
        Get the root key of the node with given name.

        :param key: The key of the node.
        :return: The key of the root node.
        :raises KeyError: If the key is not found in the tree.
        """
        if key not in self.unique_names():
            raise KeyError(f"Key not found: {key!r}")

        while self[key].get(FlatForest.PARENT_KEY) is not None:
            key = self[key][FlatForest.PARENT_KEY]
        return key

    def subtree(self, name: Optional[str] = None) -> "FlatForestNode":
        """
        Get sub-tree rooted at the node with the name `name` with the current
        node also set to that node. If `name` is None, the preferred root node
        is used.

        :param name: The unique name of the node.
        :return: FlatForestNode proxy representing the node.
        """
        from .flat_forest_node import FlatForestNode

        if name is None:
            name = self.preferred_root

        if name not in self.unique_names():
            raise KeyError(f"Name not found: {name!r}")
        
        return FlatForestNode.proxy(forest=self, node_key=name, root_key=name)

    @property
    def trees(self) -> List["FlatForestNode"]:
        """
        Retrieve the trees in the forest.

        :return: The trees in the forest.
        """
        return [self.subtree(root_name) for root_name in self.root_names]
    
    @property
    def root_names(self) -> List[str]:
        """
        Retrieve the names of the root nodes. These are the nodes that have no
        parent.

        :return: The names of the root nodes.
        """
        keys = [k for k, v in self.items() if v.get(FlatForest.PARENT_KEY) is None]
        if any(v.get(FlatForest.PARENT_KEY) == FlatForest.DETACHED_KEY for v in self.values()):
            keys.append(FlatForest.DETACHED_KEY)

        return keys
        
    def purge(self) -> List[str]:
        """
        Purge detached nodes (tree rooted at `FlatForest.DETACHED_KEY`).

        :return: The keys of the purged nodes.
        """
        purge_keys = [k for k, v in self.items() if v.get(FlatForest.PARENT_KEY) == FlatForest.DETACHED_KEY]
        def _purge(key, purge_keys):
            for child in self.child_names(key):
                _purge(child)
            purge_keys.append(key)
            del self[key]
        
        for key in purge_keys:
            _purge(key, purge_keys)

        return purge_keys

    @property
    def detached(self) -> "FlatForestNode":
        """
        Retrieve the detached tree. This is a special tree for which detached
        nodes are rooted at a logical node with the name `FlatForest.DETACHED_KEY`.

        :return: The detached logical root node.
        """
        return self.subtree(FlatForest.DETACHED_KEY)

    def __repr__(self) -> str:
        return f"FlatForest({dict(self)})"

    def __str__(self) -> str:
        return f"FlatForest(root_names={self.root_names})"

    #### implementation of node-centric methods, we treat the forest as a tree
    #### and either raise an exception if it is a forest, or return the first
    #### root node if that is desired.

    @property
    def children(self):
        """
        Get the children of the preferred root node.

        :return: The children of the preferred root node.
        """
        return self.subtree().children
    
    def add_child(self, name: Optional[str] = None, *args, **kwargs) -> "FlatForestNode":
        """
        Add a child node to the preferred root node.

        :param name: The name of the child node.
        :param payload: The payload of the child node.
        :return: The child node.
        """
        return self.subtree().add_child(name=name, *args, **kwargs)
    
    def parent(self) -> Optional["FlatForestNode"]:
        """
        Get the parent of the preferred root node. This is always None
        since the preferred root node is a root node.
        """
        return self.subtree().parent

    @property
    def preferred_root(self) -> str:
        """
        Get the preferred root node of the forest.

        :return: The preferred root node.
        :raises KeyError: If the preferred root node is not found.
        """

        if self._preferred_root is not None:
            return self._preferred_root
        elif len(self.root_names) == 0:
            raise KeyError("No root nodes and no explicit preferred root set")
        else:
            return self.root_names[0]
        
    @preferred_root.setter
    def preferred_root(self, name: Optional[str]) -> None:
        """
        Set the preferred root node of the forest.

        :param name: The name of the preferred root node.
        :return: None
        :raises KeyError: If the preferred root node is not found.
        """
        self._preferred_root = name

    @property
    def root(self) -> "FlatForestNode":
        """
        Get the tree rooted at the preferred root node.

        :return: The root node.
        """
        return self.subtree().root
    
    @property    
    def payload(self) -> dict:
        """
        Get the payload of the preferred root node.

        :return: The payload of the preferred root node.
        """
        return self.subtree().payload
    

    @payload.setter
    def payload(self, data: Dict) -> None:
        """
        Set the payload of the preferred root node.

        :param payload: The payload to set.
        :return: None
        """
        self.subtree().payload = data

    @property
    def name(self) -> str:
        """
        Get the name of the preferred root node. This is just
        self.preferred_root.

        :return: The name of the preferred root node.
        """
        return self.subtree().name
    
    @name.setter
    def name(self, name: str) -> None:
        """
        Set the name of the preferred root node.

        :param name: The name to set.
        :return: None
        """
        self.subtree().name = name
        self.preferred_root = name
    

