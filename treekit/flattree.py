from treekit.treenode import TreeNode
from anytree import Node
import treekit.tree_convert as tc
from typing import List
import treekit.tree_viz

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

    def get_root(self) -> dict:
        """
        Get the root node of the tree.

        If there is a single node without a 'parent' key, it is the root node.
        Otherwise, the tree has a logical root node that is not represented in
        the dictionary.

        :return: The key of the root node.
        """
        root_keys = [k for k, v in self.items() if v.get('parent') is None]
        if len(root_keys) == 1:
            return self[root_keys[0]]
        elif len(root_keys) == 0:
            raise ValueError("No root found")
        return {'parent': None, 'children': root_keys}

    def check_valid(self) -> None:
        """
        Validate the tree structure to ensure the structural integrity of the tree.

        Ensures that all keys are unique and that parent references are valid.
        Raises a ValueError if the tree structure is invalid.
        """
        if len(self) != len(set(self.keys())):  # check for duplicate keys
            raise ValueError("Duplicate node key")

        # there must be at least one node without a parent
        if not any('parent' not in value for value in self.values()):
            raise ValueError("No root node found")

        for key, value in self.items():
            if 'parent' in value:
                parent = value['parent']
                if parent is not None and parent not in self:
                    raise ValueError(f"Parent key not found: {parent!r}")
                if parent == key:
                    raise ValueError(f"Node cannot be its own parent: {key!r}")

    def add_node(self, key, parent=None, **kwargs) -> dict:
        """
        Add a node to the tree.

        :param key: The unique key for the node.
        :param parent: The unique key of the parent node.
        :param kwargs: Additional attributes for the node.
        :return: The newly added node.
        """
        self[key] = {'parent': parent, **kwargs}
        self.check_valid()
        return self[key]

    def __setitem__(self, key, value):
        """
        Set a node in the tree.

        :param key: The unique key for the node.
        :param value: A dictionary representing the node's attributes.
        """
        if isinstance(value, dict):
            super().__setitem__(key, value)
        else:
            raise ValueError("Value must be a dictionary")
        self.check_valid()

    def parent(self, key):
        """
        Get the parent of a node.

        :param key: The unique key of the child node.
        :return: The key of the parent node.
        """
        if key not in self:
            raise KeyError(f"Node key not found: {key!r}")
        elif 'parent' not in self[key]:
            return self.get_root()
        else:
            return self[key].get('parent')

    def children(self, key):
        """
        Get the children of a node.

        :param key: The unique key of the parent node.
        :return: List of keys representing the children nodes.
        """
        return [k for k, v in self.items() if v.get('parent') == key]

    def leaves(self) -> List[str]
        """
        Return the leaf nodes of the tree.

        :return: List of keys representing the leaf nodes.
        """
        return [k for k, v in self.items() if not self.children(k)]

    def __delitem__(self, key):
        """
        Remove a node and all its children recursively.

        :param key: The unique key of the node to remove.
        """
        children = self.children(key)
        for child in children:
            del self[child]
        super().__delitem__(key)

    def to_treenode(self) -> TreeNode:
        """
        Convert the FlatTree to a TreeNode representation.

        :return: TreeNode representation of the tree.
        """
        return tc.flatree_to_treenode(self)
    
    def to_anytree(self) -> Node:
        """
        Convert the FlatTree to an anytree representation.

        :return: The root anytree node.
        """
        return tc.flatree_to_anytree(self)

    @staticmethod
    def from_anytree(root : Node, uniq_key=None) -> 'FlatTree':
        """
        Construct a FlatTree from any anytree node. `node` will be the new
        root of the tree.

        :param root: An anytree node.
        :param uniq_key: The function to map anytree nodes to unique keys.
        :return: A FlatTree object.
        """
        return tc.anytree_to_flatree(root, uniq_key)
    
    @staticmethod
    def from_treenode(node : TreeNode, uniq_key=None) -> 'FlatTree':
        """
        Convert a TreeNode representation to a FlatTree.

        :param treenode: The root TreeNode of the tree.
        :param uniq_key: The function to map TreeNodes to unique keys.
        :return: FlatTree representation of the tree.
        """
        return tc.treenode_to_flatree(node, uniq_key)

    def to_fancy_string(self,
                        node_name=lambda node: node.name,
                        style=anytree.ContStyle()) -> str:
        """
        Generate a fancy string representation of the tree.

        :param node_name: Function to generate node names.
        :return: str
        """

        tree_viz.to_text(self.to_anytree())

    def to_image(self, out: str, node_name=lambda node: node.name) -> None:
        """
        Save the tree to an image or dot file. The outfile should include the format extension (e.g., 'tree.png' or 'tree.dot').

