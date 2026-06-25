"""
Tests for Node.fold_traced and the Trace structure.
"""
import pytest
from AlgoTree import Node


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _eval_fn(n, cs):
    """Evaluate arithmetic tree: leaves are ints, inner nodes are op names."""
    if n.is_leaf:
        return int(n.name)
    ops = {'add': sum, 'mul': lambda xs: xs[0] * xs[1]}
    return ops[n.name](cs)


# The tree represents:  add(1, mul(3, 2))  == 7
# post-order step numbering:
#   step 0 -> '1'     (leaf, value 1,  arity 0)
#   step 1 -> '3'     (leaf, value 3,  arity 0)
#   step 2 -> '2'     (leaf, value 2,  arity 0)
#   step 3 -> 'mul'   (inner, value 6, arity 2)
#   step 4 -> 'add'   (root,  value 7, arity 2)
ARITH_TREE = Node('add', Node('1'), Node('mul', Node('3'), Node('2')))


# ---------------------------------------------------------------------------
# Task 1: Node.fold_traced + Trace structure
# ---------------------------------------------------------------------------

class TestFoldTracedBasic:
    """Node.fold_traced returns (result, Trace)."""

    def test_result_value(self):
        result, trace = ARITH_TREE.fold_traced(_eval_fn)
        assert result == 7

    def test_trace_length_equals_tree_size(self):
        _, trace = ARITH_TREE.fold_traced(_eval_fn)
        # 5 nodes in the tree
        assert len(trace) == 5

    def test_trace_value_equals_result(self):
        result, trace = ARITH_TREE.fold_traced(_eval_fn)
        assert trace.value() == result


class TestFoldTracedSteps:
    """steps() is post-order (leaves before parents; root last)."""

    def setup_method(self):
        self.result, self.trace = ARITH_TREE.fold_traced(_eval_fn)

    def test_steps_length(self):
        assert len(self.trace.steps()) == 5

    def test_steps_ascending_order(self):
        steps_seq = [n['step'] for n in self.trace.steps()]
        assert steps_seq == sorted(steps_seq)

    def test_steps_start_at_zero(self):
        steps_seq = [n['step'] for n in self.trace.steps()]
        assert steps_seq[0] == 0

    def test_steps_end_at_size_minus_one(self):
        steps_seq = [n['step'] for n in self.trace.steps()]
        assert steps_seq[-1] == 4  # 0-based, 5 nodes

    def test_leaves_come_before_parents(self):
        # The three leaf steps are 0,1,2; the two inner-node steps are 3,4
        steps = self.trace.steps()
        leaf_steps = [n['step'] for n in steps if n['arity'] == 0]
        inner_steps = [n['step'] for n in steps if n['arity'] > 0]
        assert all(ls < min(inner_steps) for ls in leaf_steps)

    def test_root_step_is_last(self):
        # Root of trace mirrors root of tree ('add'), step == 4
        root_of_trace = self.trace.root
        assert root_of_trace['step'] == 4


class TestFoldTracedNodeAttrs:
    """Each trace node carries step / value / arity."""

    def setup_method(self):
        self.result, self.trace = ARITH_TREE.fold_traced(_eval_fn)

    def _nodes_by_name(self, name):
        return [n for n in self.trace.root.walk() if n.name == name]

    def test_leaf_1_attrs(self):
        node_1 = self._nodes_by_name('1')[0]
        assert node_1['step'] == 0
        assert node_1['value'] == 1
        assert node_1['arity'] == 0

    def test_leaf_3_attrs(self):
        node_3 = self._nodes_by_name('3')[0]
        assert node_3['step'] == 1
        assert node_3['value'] == 3
        assert node_3['arity'] == 0

    def test_leaf_2_attrs(self):
        node_2 = self._nodes_by_name('2')[0]
        assert node_2['step'] == 2
        assert node_2['value'] == 2
        assert node_2['arity'] == 0

    def test_mul_node_attrs(self):
        mul_node = self._nodes_by_name('mul')[0]
        assert mul_node['step'] == 3
        assert mul_node['value'] == 6
        assert mul_node['arity'] == 2

    def test_add_root_attrs(self):
        add_node = self._nodes_by_name('add')[0]
        assert add_node['step'] == 4
        assert add_node['value'] == 7
        assert add_node['arity'] == 2


class TestTraceHelpers:
    """Trace.at() and Trace.frontier()."""

    def setup_method(self):
        self.result, self.trace = ARITH_TREE.fold_traced(_eval_fn)

    def test_at_step_0(self):
        n = self.trace.at(0)
        assert n.name == '1'
        assert n['step'] == 0

    def test_at_step_4_is_root(self):
        n = self.trace.at(4)
        assert n.name == 'add'

    def test_frontier_step_0(self):
        # Only the first leaf is visible
        f = self.trace.frontier(0)
        assert '1' in f
        assert len(f) == 1

    def test_frontier_step_2(self):
        # Leaves 1, 3, 2 are all visited
        f = self.trace.frontier(2)
        assert set(f) == {'1', '3', '2'}

    def test_frontier_step_4_is_all(self):
        f = self.trace.frontier(4)
        assert len(f) == 5  # all 5 nodes


class TestTraceRender:
    """Trace.render() delegates to Node.render() and produces a string."""

    def test_render_unicode(self):
        _, trace = ARITH_TREE.fold_traced(_eval_fn)
        s = trace.render('unicode')
        assert isinstance(s, str)
        assert 'add' in s

    def test_render_ascii(self):
        _, trace = ARITH_TREE.fold_traced(_eval_fn)
        s = trace.render('ascii')
        assert isinstance(s, str)
        assert 'add' in s


class TestFoldTracedTrivialTree:
    """Degenerate cases: single node."""

    def test_single_leaf(self):
        leaf = Node('42')
        result, trace = leaf.fold_traced(lambda n, cs: int(n.name) if n.is_leaf else sum(cs))
        assert result == 42
        assert len(trace) == 1
        root = trace.root
        assert root['step'] == 0
        assert root['value'] == 42
        assert root['arity'] == 0
