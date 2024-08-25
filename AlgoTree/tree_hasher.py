
from typing import Any
from AlgoTree.tree_converter import TreeConverter

class TreeHasher:
    """
    A class that provides various hash functions for trees, with a default hashing strategy.
    """

    def __init__(self, hash_fn=None):
        """
        Initialize the TreeHasher with a specified hash function.
        
        :param hash_function: A hash function to use for trees. If None, defaults to `self.tree`.
        """
        self.hash_fn = hash_fn or self.tree

    def __call__(self, tree: Any) -> int:
        """
        Make TreeHasher callable, using the default hash function.
        
        :param tree: The tree to hash.
        :return: The hash value for the tree.
        """
        return self.hash_fn(tree)

    @staticmethod
    def tree(tree: Any) -> int:
        """
        Hash based on the entire tree structure.

        :param tree: The tree to hash.
        :return: The hash value for the tree.
        """
        if tree is None:
            raise ValueError("Tree cannot be None")
        
        return hash(str(TreeConverter.to_dict(tree)))

    @staticmethod
    def isomorphic(tree: Any) -> int:
        """Hash based on tree structure only, ignoring node names and payloads."""
        if tree is None:
            raise ValueError("Tree cannot be None")

        def build(node):            
            child_nums = [TreeHasher.isomorphic(child) for child in tree.children]
            return [len(node.children), child_nums]

        return build(tree)
