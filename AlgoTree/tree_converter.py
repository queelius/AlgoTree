import uuid
from copy import deepcopy
from typing import Any, Callable, Type, Dict

from AlgoTree.flattree import FlatTree


class TreeConverter:
    """
    Utility class for converting between tree representations.
    """

    @staticmethod
    def default_extract(node):
        """
        Default extractor of relevant payload from a node.

        :param node: The node to extract payload data from.
        :return: The extracted data.
        """
        return node.payload if hasattr(node, "payload") else {}

    @staticmethod
    def default_node_name(node):
        """
        Default function to map nodes to unique keys. If the node has a
        `name` attribute, then it is used as the unique key. Otherwise,
        a random UUID is generated.

        :param node: The node to map to a unique key.
        :return: The unique key for the node.
        """
        return node.name if hasattr(node, "name") else str(uuid.uuid4())


    @staticmethod
    def copy_under(
        node,
        under,
        node_name: Callable = default_node_name,
        extract: Callable = default_extract,
        max_tries: int = 1
    ):
        """
        Copy the subtree rooted at `node` as a child of `under`, where
        the copy takes on the node type of `under`. It returns the subtree
        that contains `under` with current node at `under`.

        :param node: The subtree rooted at `node` to copy.
        :param under: The node to copy the subtree under.
        :param node_name: The function to map nodes to names.
        :param extract: A callable to extract relevant data from a node.
        :return: A subtree extending `under` with the copied nodes.
        """
        node_type = type(under)
        tries: int = 0
        def _build(cur, und):
            nonlocal tries
            data = deepcopy(extract(cur))
            name = node_name(cur)
            base_name = name
            while tries <= max_tries:
                try:
                    node = node_type(name=name, parent=und, **data)
                except KeyError:
                    tries += 1
                    if tries > max_tries:
                        break
                    name = f"{base_name}_{tries}"

            if tries >= max_tries:
                raise ValueError("Max tries exceeded")

            for child in cur.children:
                _build(child, node)
            return node

        return _build(node, under)

    @staticmethod
    def convert(
        source,
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

        if source is None:
            return None

        root = target_type(
            name=node_name(source.root),
            parent=None,
            **extract(source.root))

        for child in source.children:
            TreeConverter.copy_under(child, root, node_name, extract)

        return root
        
    @staticmethod
    def to_dict(node,
                node_name: Callable = default_node_name,
                extract = default_extract,
                **kwargs) -> Dict:
        """
        Convert the subtree rooted at `node` to a dictionary.

        :param node: The root node of the subtree to convert.
        :param node_name: The function to map nodes to unique keys.
        :param extract: A callable to extract relevant data from a node.
        :return: A dictionary representation of the subtree.
        """

        def _build(node):
            return {
                "name": node_name(node),
                "payload": extract(node, **kwargs),
                "children": [_build(child, **kwargs) for child in node.children]
            }
        
        return _build(node)

