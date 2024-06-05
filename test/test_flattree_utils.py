import unittest
from treekit.flattree import FlatTree
from treekit.flattree_node import FlatTreeNode
from treekit.utils import (
    visit, map, descendants, ancestors, siblings, leaves, height, depth,
    is_root, is_leaf, is_internal, is_ancestor, is_descendant, is_sibling,
    breadth_first, find_nodes, find_node
)

class TestTreeUtils(unittest.TestCase):

    def setUp(self):
        self.root = FlatTreeNode(name="root", data=0)
        self.node1 = FlatTreeNode(name="node1", parent=self.root, data=1)
        self.node2 = FlatTreeNode(name="node2", parent=self.root, data=2)
        self.node3 = FlatTreeNode(name="node3", parent=self.root, data=3)
        self.node4 = FlatTreeNode(name="node4", parent=self.node3, data=4)
        self.node5 = FlatTreeNode(name="node5", parent=self.node3, data=5)
        self.node6 = FlatTreeNode(name="node6", parent=self.node3, data=6)
        self.node7 = FlatTreeNode(name="node7", parent=self.node3, data=7)
        self.node8 = FlatTreeNode(name="node8", parent=self.node3, data=8)
        self.node9 = FlatTreeNode(name="node9", parent=self.node6, data=9)

    def test_visit_pre_order(self):
        result = []
        visit(self.root, lambda n: result.append(n.name) or False, order='pre')
        self.assertEqual(result, ['root', 'node1', 'node2', 'node3', 'node4', 'node5', 'node6', 'node9', 'node7', 'node8'])

    def test_visit_level_order(self):
        result = []
        visit(self.root, lambda n, **kwargs: result.append((n.name, kwargs['level'])) or False, order='level')
        self.assertEqual(result, [
            ('root', 0), ('node1', 1), ('node2', 1), ('node3', 1),
            ('node4', 2), ('node5', 2), ('node6', 2), ('node7', 2), ('node8', 2),
            ('node9', 3)
        ])

    def test_visit_stop_on_match(self):
        result = []
        visit(self.root, lambda n: result.append(n.name) or n.name == 'node6', order='pre')
        self.assertEqual(result, ['root', 'node1', 'node2', 'node3', 'node4', 'node5', 'node6'])

    def test_map(self):
        def increment_data(node):
            node['data'] += 1
            return node
        
        map(self.root, increment_data)
        self.assertEqual(self.root['data'], 1)
        self.assertEqual(self.node1['data'], 2)
        self.assertEqual(self.node9['data'], 10)

    def test_descendants(self):
        desc = [n.name for n in descendants(self.node3)]
        self.assertEqual(desc, ['node3', 'node4', 'node5', 'node6', 'node9', 'node7', 'node8'])

    def test_ancestors(self):
        node9 = self.root.tree.node("node9", "root")
        anc = [n.name for n in ancestors(node9)]
        self.assertEqual(anc, ['node6', 'node3', 'root'])

    def test_siblings(self):
        sib = [n.name for n in siblings(self.node6)]
        self.assertEqual(sib, ['node4', 'node5', 'node7', 'node8'])

    def test_leaves(self):
        leaf = [n.name for n in leaves(self.root)]
        self.assertEqual(leaf, ['node1', 'node2', 'node4', 'node5', 'node9', 'node7', 'node8'])

    def test_height(self):
        self.assertEqual(height(self.root), 3)
        self.assertEqual(height(self.node3), 2)
        self.assertEqual(height(self.node9), 0)

    def test_depth(self):
        self.assertEqual(depth(self.root), 0)
        self.assertEqual(depth(self.node3), 1)
        self.assertEqual(depth(self.node9), 3)

    def test_is_root(self):
        self.assertTrue(is_root(self.root))
        self.assertFalse(is_root(self.node1))

    def test_is_leaf(self):
        self.assertTrue(is_leaf(self.node9))
        self.assertFalse(is_leaf(self.node3))

    def test_is_internal(self):
        self.assertTrue(is_internal(self.node3))
        self.assertFalse(is_internal(self.node1))

    def test_is_ancestor(self):
        self.assertTrue(is_ancestor(self.root, self.node9))
        self.assertFalse(is_ancestor(self.node1, self.node9))

    def test_is_descendant(self):
        self.assertTrue(is_descendant(self.node9, self.root))
        self.assertFalse(is_descendant(self.node1, self.node9))

    def test_is_sibling(self):
        self.assertTrue(is_sibling(self.node1, self.node2))
        self.assertFalse(is_sibling(self.node1, self.node9))

    def test_breadth_first(self):
        result = []
        breadth_first(self.root, lambda n, **kwargs: result.append((n.name, kwargs['level'])) or False)
        self.assertEqual(result, [
            ('root', 0), ('node1', 1), ('node2', 1), ('node3', 1),
            ('node4', 2), ('node5', 2), ('node6', 2), ('node7', 2), ('node8', 2),
            ('node9', 3)
        ])

    def test_find_nodes(self):
        nodes = find_nodes(self.root, lambda n: n['data'] > 3)
        self.assertCountEqual([n.name for n in nodes], ['node4', 'node5', 'node6', 'node7', 'node8', 'node9'])

    def test_find_node(self):
        node = find_node(self.root, lambda n, **_: n['data'] == 7)
        self.assertEqual(node.name, 'node7')

if __name__ == '__main__':
    unittest.main()
