from anytree import Node, PreOrderIter
from treekit.treenode import TreeNode
from treekit.flattree import FlatTree
from functools import singledispatch as sd
import hashlib
from typing import Optional

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
        #if node_name is None:
        #    node_name = lambda node: node.name()

        tree = FlatTree()
        def _build(node):
            #key = node_name(node)
            import uuid
            key = uuid.uuid4()
            tree[key] = {'parent': node_name(node.get_parent()),
                         **{k: v for k, v in node.items() }}
            for child in node.children():
                _build(child)
        _build(tree.get_root())
        return tree

    @staticmethod
    def to_treenode(tree, node_name : Optional[callable] = None) -> TreeNode:
        """
        Convert a FlatTree to a TreeNode representation.

        :param flat_tree: A FlatTree object.
        :return: TreeNode representation of the tree.
        """
        if node_name is None:
            node_name = lambda node: node.name()

        def _build(tree: TreeNode, node) -> TreeNode:
            tree['__name__'] = node_name(node)
            tree.update(node)
            tree['children'] = [_build(TreeNode(), child) for child in node.children()]
            #for child in node.children():
            #    tree['children'].append(_build(TreeNode(), child))
            return tree

        return _build(TreeNode(), tree.get_root())

    @staticmethod
    def treenode_to_anytree(root : TreeNode,
                            node_name : callable = None,
                            parent=None) -> Node:
        """
        Convert a TreeNode to an anytree node.

        :param root: The root of the tree.
        :param parent: The parent anytree node, if any.
        :return: The root anytree node.
        """

        if node_name is None:
            def _hash_key(node):
                hash = hashlib.sha256()
                hash.update(str(node).encode())
                return hash.hexdigest()
            node_name = _hash_key

        anynode = Node(node_name(root), parent=parent, **root)
        for child in root.children():
            TreeConverter.treenode_to_anytree(child, parent=anynode)
        return anynode

    @staticmethod
    def anytree_to_treenode(node : Node) -> TreeNode:
        """
        Convert an anytree node to a TreeNode.

        :param node: An anytree node.
        :return: A TreeNode object.
        """
        def build_anytree(node):
            node_data = {key: value for key, value in node.__dict__.items() if not key.startswith('_')}
            children = [build_anytree(child) for child in node.children]
            treenode = TreeNode(**node_data)
            for child in children:
                treenode.add_child(child)
            return treenode

        return build_anytree(node)

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
