import pytest
from treekit.flattree import FlatTree

def test_add_node():
    tree = FlatTree()
    tree.add_node('root')
    tree.add_node('child1', parent='root')
    assert 'root' in tree
    assert 'child1' in tree
    assert tree['child1']['parent'] == 'root'

def test_children():
    tree = FlatTree()
    tree.add_node('root')
    tree.add_node('child1', parent='root')
    tree.add_node('child2', parent='root')
    children = tree.children('root')
    assert 'child1' in children
    assert 'child2' in children

def test_leaves():
    tree = FlatTree()
    tree.add_node('root')
    tree.add_node('child1', parent='root')
    tree.add_node('child2', parent='root')
    tree.add_node('child1.1', parent='child1')
    leaves = tree.leaves()
    assert 'child1.1' in leaves
    assert 'child2' in leaves

def test_delete_node():
    tree = FlatTree()
    tree.add_node('root')
    tree.add_node('child1', parent='root')
    tree.add_node('child2', parent='root')
    tree.add_node('child1.1', parent='child1')
    del tree['child1']
    assert 'child1' not in tree
    assert 'child1.1' not in tree
