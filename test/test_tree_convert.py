import pytest
from treekit.treenode import TreeNode
from treekit.flattree import FlatTree
from treekit.tree_convert import (
    treenode_to_flattree,
    flattree_to_treenode,
    treenode_to_anytree,
    anytree_to_treenode,
    anytree_to_flattree,
    flattree_to_anytree,
)
from anytree import Node

def test_treenode_to_flattree():
    treenode = TreeNode(name="root")
    treenode.add_child(name="child1")
    treenode.add_child(name="child2")
    flat_tree = treenode_to_flattree(treenode)
    assert "root" in flat_tree
    assert "child1" in flat_tree
    assert "child2" in flat_tree
    assert flat_tree["child1"]["parent"] == "root"
    assert flat_tree["child2"]["parent"] == "root"

def test_flattree_to_treenode():
    flat_tree = FlatTree()
    flat_tree.add_node('root')
    flat_tree.add_node('child1', parent='root')
    flat_tree.add_node('child2', parent='root')
    treenode = flattree_to_treenode(flat_tree)
    assert treenode['name'] == 'root'
    assert len(treenode.children()) == 2

def test_treenode_to_anytree():
    treenode = TreeNode(name="root")
    treenode.add_child(name="child1")
    treenode.add_child(name="child2")
    anytree_root = treenode_to_anytree(treenode)
    assert anytree_root.name.startswith("root_")
    assert len(anytree_root.children) == 2

def test_anytree_to_treenode():
    root = Node("root")
    child1 = Node("child1", parent=root)
    child2 = Node("child2", parent=root)
    treenode = anytree_to_treenode(root)
    assert treenode['name'] == "root"
    assert len(treenode.children()) == 2

def test_anytree_to_flattree():
    root = Node("root")
    child1 = Node("child1", parent=root)
    child2 = Node("child2", parent=root)
    flat_tree = anytree_to_flattree(root)
    assert "root" in flat_tree
    assert "child1" in flat_tree
    assert "child2" in flat_tree
    assert flat_tree["child1"]["parent"] == "root"
    assert flat_tree["child2"]["parent"] == "root"

def test_flattree_to_anytree():
    flat_tree = FlatTree()
    flat_tree.add_node('root')
    flat_tree.add_node('child1', parent='root')
    flat_tree.add_node('child2', parent='root')
    anytree_root = flattree_to_anytree(flat_tree)
    assert anytree_root.name.startswith("root_")
    assert len(anytree_root.children) == 2
