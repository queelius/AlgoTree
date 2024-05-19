from anytree import Node, PreOrderIter
from treekit.treenode import TreeNode
from treekit.flattree import FlatTree
from functools import singledispatch as sd
import hashlib

class TreeConverter:
    """
    Utility class for converting between tree representations.
    """
    
    @staticmethod
    def treenode_to_flattree(root : TreeNode,
                            uniq_key : callable = None) -> FlatTree:
        """
        Convert a TreeNode representation to a FlatTree.

        :param root: The root TreeNode of the tree.
        :param uniq_key: The function to map TreeNodes to unique keys.
        :return: FlatTree representation of the tree.
        """
        if uniq_key is None:
            def _hash_key(node):
                hash = hashlib.sha256()
                hash.update(str(node).encode())
                while hash.hexdigest() in flat_tree:
                    hash.update(b'_')
                return hash.hexdigest()
            uniq_key = _hash_key

        flat_tree = FlatTree()
        def add(node, parent_key=None):
            key = uniq_key(node)
            flat_tree[key] = {'parent': parent_key, **{k: v for k, v in node.items() if k != 'children'}}
            for child in node.children():
                add(child, key)

        add(root)
        return flat_tree

    @staticmethod
    def flattree_to_treenode(flat_tree : FlatTree) -> TreeNode:
        """
        Convert a FlatTree to a TreeNode representation.

        :param flat_tree: A FlatTree object.
        :return: TreeNode representation of the tree.
        """
        def build(node_key):
            node_data = flat_tree[node_key].copy()
            node_data.pop('parent', None)
            node = TreeNode(**node_data)
            children_keys = flat_tree.children(node_key)
            for child_key in children_keys:
                node.add_child(build(child_key))
            return node

        root_key = next((k for k, v in flat_tree.items() if v.get('parent') is None), None)
        return build(root_key) if root_key else None

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
