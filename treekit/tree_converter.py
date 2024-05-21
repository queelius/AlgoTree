from anytree import Node
from treekit.treenode import TreeNode
from treekit.flattree import FlatTree
from typing import Optional, Callable
from copy import deepcopy

class TreeConverter:
    """
    Utility class for converting between tree representations.
    """
    @staticmethod
    def to_flattree(node, node_name : Optional[Callable] = None) -> FlatTree:
        """
        Convert a tree rooted at `node` to a FlatTree representation

        :param node: The (sub-tree) rooted at `node` to convert.
        :param node_name: The function to map nodes to unique keys.
        :return: FlatTree representation of the tree.
        """
        if node_name is None:
            node_name = lambda node: node.name

        flat_tree = FlatTree()
        def _build(cur, flat_node : FlatTree.ProxyNode):
            cur = deepcopy(cur)
            #childs = cur.pop('children', [])
            if FlatTree.PARENT_KEY in cur:
                del cur[FlatTree.PARENT_KEY]
            new_node = flat_node.add_child(key=node_name(cur), **cur.get_data())
            for child in cur.children():
                _build(child, new_node)

        _build(node, flat_tree.get_root())
        return flat_tree

    @staticmethod
    def to_treenode(node, node_name : Optional[Callable] = None) -> TreeNode:
        """
        Convert a tree rooted at `node` to a TreeNode representation.

        :param tree: The tree to convert.
        :return: TreeNode representation of the tree.
        """

        if node_name is None:
            node_name = lambda n: n.name

        def _build(cur, tree_node: TreeNode) -> TreeNode:
            tree_node[tree_node.NAME_KEY] = node_name(cur)
            # tree_node[tree_node.CHILDREN_KEY] = node_name(cur) fails with an error
            tree_node.update(cur.get_data())
            tree_node['children'] = [_build(child, TreeNode()) for child in cur.children()]
            return tree_node

        return _build(node, TreeNode())

    @staticmethod
    def to_anytree(node, node_name : Optional[Callable] = None) -> Node:
        """
        Convert a node to an anytree node.

        :param root: The root of the tree.
        :param parent: The parent anytree node, if any.
        :return: The root anytree node.
        """

        if node_name is None:
            node_name = lambda node: node.name

        def _build(cur, parent):
            cur = deepcopy(cur)
            #childs = cur.children()
            if 'parent' in cur:
                del cur['parent']
            new_node = Node(node_name(cur), parent=parent, **cur.get_data())
            for child in cur.children():
                _build(child, new_node)

            return new_node

        return _build(node, None)

        