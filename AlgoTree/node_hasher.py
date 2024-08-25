from typing import Any
import AlgoTree.utils as utils
from AlgoTree.tree_converter import TreeConverter

class NodeHasher:
    """
    A class providing various hash functions for tree nodes.
    """
    def __init__(self, hash_fn=None):
        """
        Initialize the NodeHasher with a specified hash function.

        :param hash_function: A hash function to use for nodes. If None, defaults to `self.node`.
        """
        self.hash_fn = hash_fn or self.node

    def __call__(self, node: Any) -> int:
        """
        Apply the hash function to a node.

        :param node: The node to hash.
        :return: The hash value for the node.
        """
        return self.hash_fn(node)

    @staticmethod
    def name(node: Any) -> int:
        """
        Compute a hash based on the name of the node.

        Use Case:
        - Useful when you want to compare nodes solely based on their names, ignoring their position and other attributes.

        Example:
        - Checking if two nodes represent the same entity based on their name.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's name.
        """
        if node is None or not hasattr(node, 'name'):
            raise ValueError("Node must have a 'name' attribute")
        return hash(str(node.name))

    @staticmethod
    def payload(node: Any) -> int:
        """
        Compute a hash based on the payload of the node.

        Use Case:
        - Useful when comparing nodes based on their payload, ignoring their name and position in the tree.

        Example:
        - Identifying nodes that carry the same data.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's payload.
        """
        if node is None or not hasattr(node, 'payload'):
            raise ValueError("Node must have a 'payload' attribute")
        return hash(str(node.payload))
    
    @staticmethod
    def node(node: Any) -> int:
        """
        Compute a hash based on the name and payload of the node.

        Use Case:
        - This is the most common notion of node equality, focusing on the node's intrinsic properties and ignoring its position in the tree.
        - Useful when you want to compare nodes by both name and payload, but not their position in the tree.

        Example:
        - Checking if two nodes are equivalent in terms of both their name and the data they carry, without considering their location in the tree structure.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's name and payload.
        """
        if node is None or not hasattr(node, 'name') or not hasattr(node, 'payload'):
            raise ValueError("Node must have 'name' and 'payload' attributes")
        
        return hash(str((node.name, node.payload)))

    @staticmethod
    def path(node: Any) -> int:
        """
        Compute a hash based on the path of the node in the tree.

        Use Case:
        - Useful when the position of the node in the tree is more important than its name or payload.

        Example:
        - Determining if two nodes occupy the same position in the same or different trees.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's path in the tree.
        """
        if node is None:
            raise ValueError("Node cannot be None")
        return hash(str([n.name for n in utils.path(node)]))
