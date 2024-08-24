"""
Node Hash Functions
~~~~~~~~~~~~~~~~~~~

This module provides hash functions for tree-like structures that implement the
node-centric API defined in this project.

The hash functions in this module are designed to handle different aspects of
tree node comparison, such as node equality or position equality within the tree. 
They can be used to answer questions like "are these two nodes the same?", 
and "is this node in the same position in these two trees?".

Note: Hash functions provide an approximation of equality, with a potential for
false positives due to hash collisions. Always consider this when using these
functions for node or tree comparison.

Philosophical Perspective - The Ship of Theseus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Ship of Theseus is a thought experiment that raises questions about the
nature of identity and whether an object that has had all of its components
replaced remains fundamentally the same object.

In the context of tree nodes, this experiment highlights that identity is
often a convention and can depend on the context.

For instance, a node may be considered the "same" if it has the same name and
payload (intrinsic properties), even if its position in the tree changes
(extrinsic properties). Conversely, a node's identity might be tied to its
position within a specific tree structure, reflecting a different aspect of equality.

Identity vs. Equality:
1. Identity:
   - Two nodes are considered identical if they are the same instance in memory.
   - Use Case: Checking if two variables point to the exact same node object.
   - Since an object can chage its state, it does not make for a
     good hash function. It is better to use the `id` function directly.

   Example
   ^^^^^^^
   node1 is node2

2. Equality:
   - Equality can be defined in various ways depending on the context.
   - Name Equality: Two nodes are equal if they have the same name.
   - Payload Equality: Two nodes are equal if they have the same payload.
   - Structural Equality: Two nodes are equal if they have the same structure, name, and payload.
   - Positional Equality: Two nodes are equal if they occupy the same position in
     isomorphic trees (node labels and payloads are irrelevant).
   - Tree Equality: Two trees are equal if they have the same structure and the
     same data at each node.

   Examples
   ^^^^^^^^

   name_hash(node1) == name_hash(node2)
   payload_hash(node1) == payload_hash(node2)
   node_hash(node1) == node_hash(node2)
   path_hash(node1) == path_hash(node2)
   tree_hash(node1) == tree_hash(node2)
"""

from typing import Any
import AlgoTree.utils as utils
from AlgoTree.tree_converter import TreeConverter

class NodeHash:
    """
    A class providing various hash functions for tree nodes and tree structures.
    """

    @staticmethod
    def name_hash(node: Any) -> int:
        """
        Compute a hash based on the name of the node.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's name.

        Use Case:
        - Useful when you want to compare nodes solely based on their names, ignoring their position and other attributes.

        Example:
        - Checking if two nodes represent the same entity based on their name.
        """
        if node is None or not hasattr(node, 'name'):
            raise ValueError("Node must have a 'name' attribute")
        return hash(node.name)

    @staticmethod
    def payload_hash(node: Any) -> int:
        """
        Compute a hash based on the payload of the node.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's payload.

        Use Case:
        - Useful when comparing nodes based on their payload, ignoring their name and position in the tree.

        Example:
        - Identifying nodes that carry the same data.
        """
        if node is None or not hasattr(node, 'payload'):
            raise ValueError("Node must have a 'payload' attribute")
        
        try:
            return hash(node.payload)
        except TypeError:
            return hash(str(node.payload))
    

    @staticmethod
    def node_hash(node: Any) -> int:
        """
        Compute a hash based on the name and payload of the node.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's name and payload.

        Use Case:
        - This is the most common notion of node equality, focusing on the node's intrinsic properties and ignoring its position in the tree.
        - Useful when you want to compare nodes by both name and payload, but not their position in the tree.

        Example:
        - Checking if two nodes are equivalent in terms of both their name and the data they carry, without considering their location in the tree structure.
        """
        if node is None or not hasattr(node, 'name') or not hasattr(node, 'payload'):
            raise ValueError("Node must have 'name' and 'payload' attributes")
        
        try:
            return hash((node.name, node.payload))
        except TypeError:
            return hash(str((node.name, node.payload)))

    @staticmethod
    def path_hash(node: Any) -> int:
        """
        Compute a hash based on the path of the node in the tree.

        :param node: The node for which to compute the hash.
        :return: The hash value for the node's path in the tree.

        Use Case:
        - Useful when the position of the node in the tree is more important than its name or payload.

        Example:
        - Determining if two nodes occupy the same position in different trees.
        """
        if node is None:
            raise ValueError("Node cannot be None")
        p = utils.path(node)
        path = [n.name for n in p]
        return hash(str(path))

    @staticmethod
    def tree_hash(node: Any) -> int:
        """
        Compute a hash based on the entire tree structure rooted at the node.

        :param node: The node for which to compute the hash.
        :return: The hash value for the entire tree structure.

        Use Case:
        - Useful when you need to compare entire tree structures, considering both node attributes and their positions.

        Example:
        - Verifying if two trees are structurally identical and contain the same data in corresponding positions.
        """
        if node is None:
            raise ValueError("Node cannot be None")
        return hash(str(TreeConverter.to_dict(node)))
