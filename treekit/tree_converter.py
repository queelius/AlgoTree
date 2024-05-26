from anytree import Node
from treekit.treenode import TreeNode
from treekit.flattree import FlatTree
from typing import Optional, Callable, Any
from copy import deepcopy
import uuid

class TreeConverter:
    """
    Utility class for converting between tree representations.
    """
    @staticmethod
    def to_flattree(node,
                    node_name: Callable = lambda _: str(uuid.uuid4()),
                    data_extractor: Optional[Callable] = lambda n: n) -> FlatTree:
        """
        Convert a tree rooted at `node` to a FlatTree representation

        :param node: The (sub-tree) rooted at `node` to convert.
        :param node_name: The function to map nodes to unique keys.
        :return: FlatTree representation of the tree.
        """

        if data_extractor is None:
            data_extractor = lambda x: x

        flat_tree = FlatTree()
        def _build(cur, flat_node : FlatTree.ProxyNode):
            data = deepcopy(data_extractor(cur))
            if FlatTree.PARENT_KEY in data:
                del data[FlatTree.PARENT_KEY]
            new_node = flat_node.add_child(key=node_name(cur), **data)
            for child in cur.children:
                _build(child, new_node)

        _build(node, flat_tree.root)
        return flat_tree

    @staticmethod
    def to_treenode(node,
                    node_name: Optional[Callable] = None,
                    data_extractor: Optional[Callable] = lambda n: n) -> TreeNode:
        """
        Convert a tree rooted at `node` to a TreeNode representation.

        Example:

        ```python
        def anytree_data_extractor(node):
            return {
                'name': node.name,
                'data': node.get_data if hasattr(node, 'get_data') else None
            }
        ```

        :param none: The tree to convert.
        :param node_name: The function to map nodes to names, if appropriate
        :param data_extractor: The function to extract relevant data from nodes
        :return: TreeNode representation of the tree.
        """

        def _build(cur, tree_node: TreeNode) -> TreeNode:
            if tree_node.name_key is not None and node_name is not None:
                tree_node[tree_node.name_key] = node_name(cur)
            if data_extractor is not None:
                tree_node.update(data_extractor(cur))
            tree_node[tree_node.children_key] = [_build(child, TreeNode()) for child in cur.children]
            return tree_node

        return _build(node, TreeNode())

    @staticmethod
    def to_anytree(node,
                   node_name: Callable = lambda n: n.name,
                   data_extractor: Optional[Callable] = lambda n: n) -> Node:
        """
        Convert a TreeNode to an anytree Node.

        :param node: The root of the TreeNode.
        :param node_name: A callable to generate node names.
        :return: The root anytree Node.
        """

        def _build(cur, parent) -> Node:
            data = deepcopy(data_extractor(cur)) if data_extractor else {}
            if 'parent' in data:
                del data['parent']
            if 'children' in data:
                del data['children']
            if 'name' in data:
                name = "_" + data['name'] + "_"
                del data['name']
                new_key = "_" + name + "_"
                while new_key in data:
                    new_key = "_" + new_key + "_"
                data[new_key] = name

            new_node = Node(name=node_name(cur), parent=parent, **data)
            for child in cur.children:
                _build(child, new_node)

            return new_node

        return _build(node, None)


        