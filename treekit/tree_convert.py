from functools import singledispatch as sd
from treekit.treenode import TreeNode
from treekit.flattree import FlatTree
from anytree import Node
from treekit.tree_converter import TreeConverter as tc

# Dispatch functions for converting between tree representations
@sd.singledispatch
def to_treenode(tree):
    raise TypeError(f"Unsupported type: {type(tree)}")

@to_treenode.register(FlatTree)
def to_treenode(tree: FlatTree) -> TreeNode:
    """
    Convert a FlatTree to a TreeNode representation.

    :param tree: The FlatTree.
    :return: TreeNode representation of the tree.
    """
    return tc.flattree_to_treenode(tree)

@to_treenode.register(Node)
def to_treenode(tree: Node) -> TreeNode:
    """
    Convert an anytree node to a TreeNode representation.

    :param tree: The anytree.Node.
    :return: TreeNode representation of the tree.
    """
    return tc.anytree_to_treenode(tree)


@to_treenode.register(TreeNode)
def to_treenode(tree: TreeNode) -> TreeNode:
    """
    No conversion needed because the input is already a TreeNode.

    :param tree: The TreeNode.
    :return: TreeNode representation of the tree.
    """
    return tree

@sd.singledispatch
def to_flattree(tree):
    raise TypeError(f"Unsupported type: {type(tree)}")

@to_flattree.register(TreeNode)
def to_flattree(tree: TreeNode) -> FlatTree:
    """
    Convert a TreeNode to a FlatTree representation.

    :param tree: The TreeNode.
    :return: FlatTree representation of the tree.
    """
    return tc.treenode_to_flattree(tree)

@to_flattree.register(Node)
def to_flattree(tree: Node) -> FlatTree:
    """
    Convert an anytree node to a FlatTree representation.

    :param tree: The anytree.Node.
    :return: FlatTree representation of the tree.
    """
    return tc.anytree_to_flattree(tree)

@to_flattree.register(FlatTree)
def to_flattree(tree: FlatTree) -> FlatTree:
    """
    No conversion needed because the input is already a FlatTree.

    :param tree: The FlatTree.
    :return: FlatTree representation of the tree.
    """
    return tree

@sd.singledispatch
def to_anytree(tree):
    raise TypeError(f"Unsupported type: {type(tree)}")

@to_anytree.register(TreeNode)
def to_anytree(tree: TreeNode) -> Node:
    """
    Convert the TreeNode to an anytree.Node representation.

    :param tree: The TreeNode.
    :return: anytree.Node representation of the tree.
    """
    return tc.treenode_to_anytree(tree)

@to_anytree.register(FlatTree)
def to_anytree(tree: FlatTree) -> Node:
    """
    Convert the FlatTree to an anytree.Node representation.

    :param tree: The FlatTree.
    :return: anytree.Node representation of the tree.
    """
    return tc.flattree_to_anytree(tree)

@to_anytree.register(Node)
def to_anytree(tree: Node) -> Node:
    """
    No conversion needed because the input is already an anytree.Node.

    :param tree: The root anytree.Node.
    :return: anytree.Node representation of the tree.
    """
    return tree