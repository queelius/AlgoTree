import uuid
from copy import deepcopy
from typing import Any, Callable, Type

from treekit.flattree import FlatTree


class TreeConverter:
    """
    Utility class for converting between tree representations.
    """

    @staticmethod
    def default_extract(node):
        return node.payload if hasattr(node, "payload") else {}

    @staticmethod
    def default_node_name(node):
        return node.name if hasattr(node, "name") else str(uuid.uuid4())

    @staticmethod
    def copy_under(
        node,
        under,
        node_name: Callable = default_node_name,
        extract: Callable = default_extract,
    ):
        """
        Copy the subtree rooted at `node` as a child of `under`, where
        the copy takes on the node type of `under`.

        :param node: The (sub-tree) rooted at `node` to copy.
        :param under: The node to copy the subtree under.
        :param node_name: The function to map nodes to unique keys.
        :param extract: A callable to extract relevant data from a node.
        :return: A copy of the subtree rooted at `node` as a child of `under`.
        """
        node_type = type(under)

        def _build(cur, par):
            if cur.name != FlatTree.LOGICAL_ROOT:
                data = deepcopy(extract(cur))
                node = node_type(name=node_name(cur), parent=par, **data)
                for child in cur.children:
                    _build(child, node)
            else:
                for child in cur.children:
                    _build(child, par)

        _build(node, under)
        return under

    @staticmethod
    def convert(
        source_node,
        target_type: Type[Any],
        node_name: Callable = default_node_name,
        extract: Callable = default_extract,
    ):
        """
        Convert a tree rooted at `node` to a target tree type representation.

        :param src_node: The root node of the tree to convert.
        :param target_type: The target tree type to convert to.
        :param node_name: The function to map nodes to unique keys.
        :param extract: A callable to extract relevant data from a node.
        :return: The converted tree.
        """
        target_root = target_type(name=node_name(
            source_node), **extract(source_node))

        for child in source_node.children:
            TreeConverter.copy_under(child, target_root, node_name, extract)

        return target_root
