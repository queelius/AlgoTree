from anytree import Node, PreOrderIter
from treekit.treenode import TreeNode
from treekit.flattree import FlatTree
from typing import Optional
import uuid
import json
from copy import deepcopy

class TreeConverter:
    """
    Utility class for converting between tree representations.
    """
    @staticmethod
    def to_flattree(tree, node_name : Optional[callable] = None) -> FlatTree:
        """
        Convert a tree to a FlatTree representation

        :param tree: The tree to convert.
        :param node_name: The function to map TreeNodes to unique keys.
        :return: FlatTree representation of the tree.
        """
        if node_name is None:
            node_name = lambda _: str(uuid.uuid4())

        flat_tree = FlatTree()
        def _build(node, flat_node : FlatTree.ProxyNode):
            # remove the "parent" key from node if it exists
            node = deepcopy(node)
            if 'parent' in node:
                del node['parent']
            children = node.pop('children', [])
            new_node = flat_node.add_child(key=node_name(node), **node)
            for child in children:
                _build(child, new_node)

        _build(tree.get_root(), flat_tree.get_root())
        return flat_tree

    @staticmethod
    def to_treenode(tree) -> TreeNode:
        """
        Convert a tree to a TreeNode representation.

        :param tree: The tree to convert.
        :return: TreeNode representation of the tree.
        """
        def _build(node, tree_node: TreeNode) -> TreeNode:
            tree_node.update(node)
            tree_node['children'] = [_build(child, TreeNode()) for child in node.children()]
            return tree_node

        return _build(tree.get_root(), TreeNode())

    @staticmethod
    def to_anytree(tree, node_name : callable = None, parent=None) -> Node:
        """
        Convert a TreeNode to an anytree node.

        :param root: The root of the tree.
        :param parent: The parent anytree node, if any.
        :return: The root anytree node.
        """

        if node_name is None:
            node_name = str(uuid.uuid4())

        anynode = Node(node_name(tree), parent=parent, **tree)
        for child in tree.children():
            TreeConverter.to_anytree(child, node_name, parent=anynode)
        return anynode

    @staticmethod
    def anytree_to_treenode(node : Node) -> TreeNode:
        """
        Convert an anytree node to a TreeNode.

        :param node: An anytree node.
        :return: A TreeNode object.
        """
        def _build(node):
            node_data = {key: value for key, value in node.__dict__.items() if not key.startswith('_')}
            children = [_build(child) for child in node.children]
            treenode = TreeNode(**node_data)
            for child in children:
                treenode.add_child(child)
            return treenode

        return _build(node)

    @staticmethod
    def anytree_to_flattree(node : Node,
                            uniq_key : callable = lambda node: node.name) -> FlatTree:
        """
        Construct a FlatTree from an anytree node.

        :param node: An anytree node.
        :param uniq_key: The function to map anytree nodes to unique keys.
        :return: A FlatTree object.
        """
        flat_tree = FlatTree()
        for n in PreOrderIter(node):
            node_data = {key: value for key, value in n.__dict__.items() if not key.startswith('_')}
            flat_tree[n.name] = {
                'parent': n.parent.name if n.parent else None,
                **node_data
            }
        flat_tree.check_valid()
        return flat_tree

    @staticmethod
    def flattree_to_anytree(flat_tree : FlatTree,
                            node_name : callable = lambda node: node.name) -> Node:
        """
        Convert a FlatTree to an anytree node.

        :param flat_tree: A FlatTree object.
        :return: The root anytree node.
        """
        return TreeConverter.treenode_to_anytree(
            TreeConverter.flattree_to_treenode(flat_tree), node_name=node_name)
