"""
Behavioral law tests for the Transformer algebra.

Covers:
  - identity unit: (identity >> t)(x) == t(x) and (t >> identity)(x) == t(x)
  - composition order: (a >> b)(x) == b(a(x))
  - associativity: ((a >> b) >> c)(x) == (a >> (b >> c))(x)
  - works on a bare Node AND on a Tree (same logical result)
  - .repeat(n) applies n times
  - .when(cond) applies conditionally
"""
import unittest

from AlgoTree.node import Node
from AlgoTree.tree import Tree
from AlgoTree.transformers import (
    Transformer, identity,
    map_, filter_, prune, annotate, normalize,
    reduce_, fold, extract, to_dict, to_paths,
)


def _sample_tree():
    """Return a fresh sample tree (Tree wrapper)."""
    return Tree(Node("root",
        Node("a", attrs={"value": 1}),
        Node("b", attrs={"value": 2}),
        Node("c", attrs={"value": 3}),
    ))


def _sample_node():
    """Return a fresh bare root Node (same structure)."""
    return Node("root",
        Node("a", attrs={"value": 1}),
        Node("b", attrs={"value": 2}),
        Node("c", attrs={"value": 3}),
    )


def _root_eq(result):
    """Normalize a result to a Node for structural equality checks."""
    if isinstance(result, Tree):
        return result.root
    return result  # bare Node


# ---------------------------------------------------------------------------
# Identity unit laws
# ---------------------------------------------------------------------------

class TestIdentityUnit(unittest.TestCase):
    """(identity >> t)(x) == t(x)  and  (t >> identity)(x) == t(x)."""

    def _verify_identity_laws(self, t, x):
        left = (identity >> t)(x)
        right = (t >> identity)(x)
        direct = t(x)
        self.assertEqual(_root_eq(left), _root_eq(direct),
                         "left unit: (identity >> t)(x) != t(x)")
        self.assertEqual(_root_eq(right), _root_eq(direct),
                         "right unit: (t >> identity)(x) != t(x)")

    def test_identity_unit_map_on_tree(self):
        t = map_(lambda n: {"value": n.get("value", 0) * 2})
        self._verify_identity_laws(t, _sample_tree())

    def test_identity_unit_map_on_node(self):
        t = map_(lambda n: {"value": n.get("value", 0) * 2})
        self._verify_identity_laws(t, _sample_node())

    def test_identity_unit_prune_on_tree(self):
        t = prune("a")
        self._verify_identity_laws(t, _sample_tree())

    def test_identity_unit_prune_on_node(self):
        t = prune("a")
        self._verify_identity_laws(t, _sample_node())

    def test_identity_unit_annotate_on_tree(self):
        t = annotate(tagged=True)
        self._verify_identity_laws(t, _sample_tree())

    def test_identity_unit_annotate_on_node(self):
        t = annotate(tagged=True)
        self._verify_identity_laws(t, _sample_node())

    def test_identity_self(self):
        """identity >> identity == identity (same result on a sample)."""
        x = _sample_tree()
        result = (identity >> identity)(x)
        self.assertEqual(_root_eq(result), _root_eq(identity(x)))


# ---------------------------------------------------------------------------
# Composition order: (a >> b)(x) == b(a(x))
# ---------------------------------------------------------------------------

class TestCompositionOrder(unittest.TestCase):
    """(a >> b)(x) == b(a(x))."""

    def _check(self, a, b, x):
        composed = (a >> b)(x)
        manual = b(a(x))
        # For tree-to-scalar shapers, compare directly; otherwise compare roots.
        if isinstance(composed, (list, dict, int, float, str, bool, type(None))):
            self.assertEqual(composed, manual)
        else:
            self.assertEqual(_root_eq(composed), _root_eq(manual))

    def test_map_then_filter_on_tree(self):
        a = map_(lambda n: {"value": n.get("value", 0) * 2})
        b = filter_(lambda n: n.get("value", 0) > 2)
        self._check(a, b, _sample_tree())

    def test_map_then_filter_on_node(self):
        a = map_(lambda n: {"value": n.get("value", 0) * 2})
        b = filter_(lambda n: n.get("value", 0) > 2)
        self._check(a, b, _sample_node())

    def test_filter_then_annotate_on_tree(self):
        a = filter_(lambda n: n.get("value", 0) != 2)
        b = annotate(processed=True)
        self._check(a, b, _sample_tree())

    def test_filter_then_annotate_on_node(self):
        a = filter_(lambda n: n.get("value", 0) != 2)
        b = annotate(processed=True)
        self._check(a, b, _sample_node())

    def test_map_then_extract_on_tree(self):
        """Composition ending with a shaper (tree->list) still obeys order."""
        a = map_(lambda n: {"value": n.get("value", 0) + 10})
        b = extract(lambda n: n.get("value"), selector=None)
        self._check(a, b, _sample_tree())

    def test_prune_then_normalize_on_tree(self):
        a = prune("b")
        b = normalize(sort_children=True)
        self._check(a, b, _sample_tree())

    def test_prune_then_normalize_on_node(self):
        a = prune("b")
        b = normalize(sort_children=True)
        self._check(a, b, _sample_node())


# ---------------------------------------------------------------------------
# Associativity: ((a >> b) >> c)(x) == (a >> (b >> c))(x)
# ---------------------------------------------------------------------------

class TestAssociativity(unittest.TestCase):
    """((a >> b) >> c)(x) == (a >> (b >> c))(x)."""

    def _check_assoc(self, a, b, c, x):
        lhs = ((a >> b) >> c)(x)
        rhs = (a >> (b >> c))(x)
        if isinstance(lhs, (list, dict, int, float, str, bool, type(None))):
            self.assertEqual(lhs, rhs)
        else:
            self.assertEqual(_root_eq(lhs), _root_eq(rhs))

    def test_three_maps_on_tree(self):
        a = map_(lambda n: {"value": n.get("value", 0) + 1})
        b = map_(lambda n: {"value": n.get("value", 0) * 2})
        c = annotate(processed=True)
        self._check_assoc(a, b, c, _sample_tree())

    def test_three_maps_on_node(self):
        a = map_(lambda n: {"value": n.get("value", 0) + 1})
        b = map_(lambda n: {"value": n.get("value", 0) * 2})
        c = annotate(processed=True)
        self._check_assoc(a, b, c, _sample_node())

    def test_map_filter_prune_on_tree(self):
        a = map_(lambda n: {"value": n.get("value", 0) * 2})
        b = filter_(lambda n: n.get("value", 0) >= 2)
        c = prune("c")
        self._check_assoc(a, b, c, _sample_tree())

    def test_map_filter_prune_on_node(self):
        a = map_(lambda n: {"value": n.get("value", 0) * 2})
        b = filter_(lambda n: n.get("value", 0) >= 2)
        c = prune("c")
        self._check_assoc(a, b, c, _sample_node())

    def test_identity_is_neutral_in_chain(self):
        """identity is a neutral element inside a chain."""
        a = map_(lambda n: {"value": n.get("value", 0) + 5})
        b = annotate(step=True)
        x = _sample_tree()
        # (a >> identity >> b) should equal (a >> b)
        with_id = (a >> identity >> b)(x)
        without_id = (a >> b)(x)
        self.assertEqual(_root_eq(with_id), _root_eq(without_id))

    def test_four_transformers_on_tree(self):
        """Extend to four transformers: ((a >> b) >> (c >> d))."""
        a = map_(lambda n: {"value": n.get("value", 0) * 2})
        b = filter_(lambda n: n.get("value", 0) > 1)
        c = annotate(step1=True)
        d = annotate(step2=True)
        lhs = ((a >> b) >> (c >> d))(_sample_tree())
        rhs = (a >> (b >> (c >> d)))(_sample_tree())
        self.assertEqual(_root_eq(lhs), _root_eq(rhs))


# ---------------------------------------------------------------------------
# Node vs Tree symmetry
# ---------------------------------------------------------------------------

class TestNodeTreeSymmetry(unittest.TestCase):
    """Same logical result from bare Node and Tree wrapper."""

    def test_map_symmetry(self):
        t = map_(lambda n: {"value": n.get("value", 0) * 3})
        tree_r = t(_sample_tree())
        node_r = t(_sample_node())
        self.assertEqual(tree_r.root, node_r)

    def test_filter_symmetry(self):
        t = filter_(lambda n: n.get("value", 0) != 2)
        tree_r = t(_sample_tree())
        node_r = t(_sample_node())
        self.assertEqual(tree_r.root, node_r)

    def test_prune_symmetry(self):
        t = prune("b")
        tree_r = t(_sample_tree())
        node_r = t(_sample_node())
        self.assertEqual(tree_r.root, node_r)

    def test_annotate_symmetry(self):
        t = annotate(marked=True)
        tree_r = t(_sample_tree())
        node_r = t(_sample_node())
        self.assertEqual(tree_r.root, node_r)

    def test_normalize_symmetry(self):
        t = normalize(sort_children=True)
        tree_r = t(_sample_tree())
        node_r = t(_sample_node())
        self.assertEqual(tree_r.root, node_r)

    def test_composition_symmetry(self):
        """Composed pipeline yields same root from Tree and bare Node."""
        pipeline = (
            map_(lambda n: {"value": n.get("value", 0) + 1})
            >> filter_(lambda n: n.get("value", 0) > 1)
            >> annotate(done=True)
        )
        tree_r = pipeline(_sample_tree())
        node_r = pipeline(_sample_node())
        self.assertEqual(tree_r.root, node_r)


# ---------------------------------------------------------------------------
# .repeat(n)
# ---------------------------------------------------------------------------

class TestRepeatLaw(unittest.TestCase):
    """.repeat(n) applies the transformer exactly n times."""

    def test_repeat_zero_is_identity(self):
        """repeat(0) should be a no-op (applied 0 times == identity)."""
        t = map_(lambda n: {"value": n.get("value", 0) * 2})
        x = _sample_tree()
        result = t.repeat(0)(x)
        self.assertEqual(_root_eq(result), _root_eq(x))

    def test_repeat_one_equals_direct(self):
        """repeat(1)(x) == t(x)."""
        t = map_(lambda n: {"value": n.get("value", 0) * 2})
        x = _sample_tree()
        self.assertEqual(_root_eq(t.repeat(1)(x)), _root_eq(t(x)))

    def test_repeat_n_on_tree(self):
        """repeat(3) doubles value 3 times: value * 8."""
        t = map_(lambda n: {"value": n.get("value", 0) * 2})
        x = Tree(Node("root", attrs={"value": 1}))
        result = t.repeat(3)(x)
        self.assertEqual(result.root.get("value"), 8)

    def test_repeat_n_on_node(self):
        """Same as above but with a bare Node."""
        t = map_(lambda n: {"value": n.get("value", 0) * 2})
        x = Node("root", attrs={"value": 1})
        result = t.repeat(3)(x)
        self.assertIsInstance(result, Node)
        self.assertEqual(result.get("value"), 8)

    def test_repeat_composition_law(self):
        """t.repeat(2)(x) == (t >> t)(x)."""
        t = map_(lambda n: {"value": n.get("value", 0) + 1})
        x = _sample_tree()
        via_repeat = t.repeat(2)(x)
        via_compose = (t >> t)(x)
        self.assertEqual(_root_eq(via_repeat), _root_eq(via_compose))

    def test_repeat_returns_transformer(self):
        t = map_(lambda n: n)
        self.assertIsInstance(t.repeat(3), Transformer)


# ---------------------------------------------------------------------------
# .when(cond)
# ---------------------------------------------------------------------------

class TestWhenLaw(unittest.TestCase):
    """.when(cond) applies transformer only when cond is true."""

    def test_when_true_applies(self):
        t = map_(lambda n: {"value": 999})
        x = Tree(Node("root", attrs={"value": 10}))
        result = t.when(lambda tr: tr.root.get("value") > 5)(x)
        self.assertEqual(result.root.get("value"), 999)

    def test_when_false_is_passthrough(self):
        t = map_(lambda n: {"value": 999})
        x = Tree(Node("root", attrs={"value": 1}))
        result = t.when(lambda tr: tr.root.get("value") > 5)(x)
        self.assertEqual(result.root.get("value"), 1)

    def test_when_false_with_else(self):
        t = map_(lambda n: {"value": 999})
        else_t = map_(lambda n: {"value": -1})
        x = Tree(Node("root", attrs={"value": 1}))
        result = t.when(lambda tr: tr.root.get("value") > 5, else_=else_t)(x)
        self.assertEqual(result.root.get("value"), -1)

    def test_when_returns_transformer(self):
        t = map_(lambda n: n)
        self.assertIsInstance(t.when(lambda _: True), Transformer)

    def test_when_on_bare_node(self):
        t = map_(lambda n: {"value": 100})
        x = Node("root", attrs={"value": 42})
        result = t.when(lambda n: n.get("value", 0) > 10)(x)
        self.assertIsInstance(result, Node)
        self.assertEqual(result.get("value"), 100)


# ---------------------------------------------------------------------------
# Shaper transformers return the right type
# ---------------------------------------------------------------------------

class TestShaperReturnTypes(unittest.TestCase):
    """Shaper transformers (tree->value) return correct Python types."""

    def setUp(self):
        self.tree = _sample_tree()

    def test_reduce_returns_scalar(self):
        r = reduce_(lambda acc, n: acc + n.get("value", 0), 0)(self.tree)
        self.assertIsInstance(r, int)
        self.assertEqual(r, 6)

    def test_fold_returns_value(self):
        r = fold(lambda n, ch: n.get("value", 0) + sum(ch))(self.tree)
        self.assertEqual(r, 6)

    def test_extract_returns_list(self):
        r = extract(lambda n: n.name)(self.tree)
        self.assertIsInstance(r, list)
        self.assertIn("root", r)

    def test_to_dict_returns_dict(self):
        r = to_dict()(self.tree)
        self.assertIsInstance(r, dict)
        self.assertIn("name", r)

    def test_to_paths_returns_list(self):
        r = to_paths()(self.tree)
        self.assertIsInstance(r, list)
        self.assertEqual(len(r), 3)


if __name__ == "__main__":
    unittest.main()
