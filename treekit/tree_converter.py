from anytree import Node
from treekit.treenode import TreeNode
from treekit.flattree import FlatTree
from treekit.flattree_node import FlatTreeNode
from typing import Optional, Callable, Any
from copy import deepcopy
import uuid

class TreeConverter:
    """
    Utility class for converting between tree representations.
    """
    @staticmethod
    def default_extract(node):
        return node.payload if hasattr(node, 'payload') else {}
    
    @staticmethod
    def default_node_name(node):
        return node.name if hasattr(node, 'name') else str(uuid.uuid4())

    @staticmethod
    def to_node(node,
                node_type,
                node_name: Callable = default_node_name,
                extract: Callable = default_extract):
        """
        Convert a tree rooted at `node` to a type(root) representation

        :param node: The (sub-tree) rooted at `node` to convert.
        :param node_name: The function to map nodes to unique keys.
        :param extract: A callable to extract relevant data from a node.
        :return: type(root) representation of the tree rooted at `node'
                 as a subtree of `root`.
        """

        def _build(cur, parent):
            data = deepcopy(extract(cur))
            try:
                del data['parent']
            except:
                pass
            new_node = node_type(name=node_name(cur), parent=parent, **data)
            for child in cur.children:
                _build(child, new_node)
            return new_node

        data = deepcopy(extract(node))
        new_node = node_type(name=node_name(node), parent=None, **data)
        return _build(node, new_node) 


    @staticmethod
    def to_treenode(node,
                    node_name: Callable = default_node_name,
                    extract: Callable = default_extract) -> TreeNode:
        """
        Convert a tree rooted at `node` to a TreeNode representation.

        :param none: The tree to convert.
        :param node_name: The function to map nodes to names, if appropriate
        :param extract: A callabe to extract relevant data from a node.
        :return: TreeNode representation of the tree.
        """

        def _build(cur, tree_node: TreeNode) -> TreeNode:
            if node_name is not None:
                tree_node[TreeNode.NAME_KEY] = node_name(cur)
            tree_node.update(extract(cur))
            tree_node[TreeNode.CHILDREN_KEY] = [_build(child, TreeNode()) for child in cur.children]
            return tree_node

        return _build(node, TreeNode())

    @staticmethod
    def to_anytree(node,
                   node_name: Callable = default_node_name,
                   extract: Callable = default_extract) -> Node:
        """
        Convert a node to an anytree Node.

        The node must have a 'children' property that is iterable and maps to the
        children of the node.

        :param node: The root of the node.
        :param node_name: A callable to generate node names.
        :param extractor: A callable to extract relevant data from a node.
        :return: The root anytree Node.
        """

        if not hasattr(node, 'children'):
            raise AttributeError("node must have a 'children' property")

        def _build(cur, parent) -> Node:
            data = deepcopy(extract(cur))
            if 'parent' in data:
                del data['parent']
            if 'children' in data:
                del data['children']
            if 'name' in data:
                name = data['name']
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


        