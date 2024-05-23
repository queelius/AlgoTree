from functools import singledispatch
from treekit.treenode import TreeNode
from treekit.flattree import FlatTree
from anytree import Node
from treekit.tree_converter import TreeConverter as tc
from typing import Union

# Dispatch functions for converting between tree representations
@singledispatch
def to_treenode(tree) -> TreeNode:
    raise TypeError(f"Unsupported type: {type(tree)}")

@to_treenode.register
def _(tree: Union[FlatTree, Node]) -> TreeNode:
    """
    Convert a tree to a TreeNode representation.

    :param tree: The FlatTree.
    :return: TreeNode representation of the tree.
    """
    return tc.to_treenode(tree)

@to_treenode.register
def _(tree: TreeNode) -> TreeNode:
    """
    No conversion needed because the input is already a TreeNode.

    :param tree: The TreeNode.
    :return: TreeNode representation of the tree.
    """
    return tree

@singledispatch
def to_flattree(tree) -> FlatTree:
    raise TypeError(f"Unsupported type: {type(tree)}")

@to_flattree.register
def _(tree: Union[Node, TreeNode]) -> FlatTree:
    """
    Convert a tree a FlatTree representation.

    :param tree: The anytree.Node.
    :return: FlatTree representation of the tree.
    """
    return tc.to_flattree(tree)

@to_flattree.register
def _(tree: FlatTree) -> FlatTree:
    """
    No conversion needed because the input is already a FlatTree.

    :param tree: The FlatTree.
    :return: FlatTree representation of the tree.
    """
    return tree

@singledispatch
def to_anytree(tree) -> Node:
    raise TypeError(f"Unsupported type: {type(tree)}")

@to_anytree.register
def _(tree: Union[TreeNode, FlatTree]) -> Node:
    """
    Convert a tree a anytree.Node representation.

    :param tree: The TreeNode.
    :return: anytree.Node representation of the tree.
    """
    return tc.to_anytree(tree)

@to_anytree.register
def _(tree: Node) -> Node:
    """
    No conversion needed because the input is already an anytree.Node.

    :param tree: The root anytree.Node.
    :return: anytree.Node representation of the tree.
    """
    return tree
