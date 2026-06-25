"""
Behavioral lattice-law property tests for the AlgoTree selector algebra.

For selectors drawn from a representative sample, verifies:
  - Identity:     (any_() & x)  == x;  (none_() | x)  == x
  - Annihilator:  (none_() & x) matches nowhere;  (any_() | x) matches everywhere
  - Involution:   ~~x == x
  - De Morgan:    ~(x & y) == (~x | ~y);  ~(x | y) == (~x & ~y)

"Equality" is checked by comparing matched-node id sets over every cursor in
a representative sample tree, not by selector identity.
"""

import unittest
from AlgoTree.node import Node
from AlgoTree.tree import Tree
from AlgoTree.cursor import Cursor, walk_cursors
from AlgoTree.selectors import (
    any_, none, none_,
    name, glob, depth, leaf,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sample_tree() -> Tree:
    """A small but structurally varied tree for law verification."""
    return Tree(Node("root",
        Node("a", attrs={"v": 1}),
        Node("b",
            Node("c", attrs={"v": 2}),
            Node("d.txt", attrs={"v": 3}),
            attrs={"v": 10}
        ),
        Node("e.txt", attrs={"v": 4}),
    ))


def _all_cursors(tree):
    """Return list of all cursors in pre-order."""
    return list(walk_cursors(Cursor(tree.root)))


def _matched_ids(selector, cursors):
    """Return frozenset of id(cursor.node) for all cursors where selector matches."""
    return frozenset(
        id(c.node) for c in cursors if selector.matches_at(c)
    )


def _all_ids(cursors):
    return frozenset(id(c.node) for c in cursors)


# ---------------------------------------------------------------------------
# The test class
# ---------------------------------------------------------------------------

class TestSelectorLattice(unittest.TestCase):
    """Behavioral lattice-law tests over a representative sample tree."""

    def setUp(self):
        self.tree = _sample_tree()
        self.cursors = _all_cursors(self.tree)
        # Representative selectors (value-local, so matches_at == matches on cursor)
        self.selectors = [
            name("a"),
            name("b"),
            glob("*.txt"),
            depth(1),
            leaf(),
        ]
        # Pairs for De Morgan tests
        self.pairs = [
            (name("a"), name("b")),
            (glob("*.txt"), depth(1)),
            (leaf(), depth(1)),
            (name("a"), glob("*.txt")),
        ]

    # -----------------------------------------------------------------------
    # any_() and none_()/none() are top/bottom
    # -----------------------------------------------------------------------

    def test_any_is_top(self):
        """any_() must match every node."""
        sel = any_()
        matched = _matched_ids(sel, self.cursors)
        self.assertEqual(matched, _all_ids(self.cursors))

    def test_none_is_bottom(self):
        """none() must match no node."""
        sel = none()
        matched = _matched_ids(sel, self.cursors)
        self.assertEqual(matched, frozenset())

    def test_none_alias_matches_none(self):
        """none_() is the same bottom element as none()."""
        a_ids = _matched_ids(none_(), self.cursors)
        b_ids = _matched_ids(none(), self.cursors)
        self.assertEqual(a_ids, b_ids)

    # -----------------------------------------------------------------------
    # Identity laws
    # -----------------------------------------------------------------------

    def test_identity_and_top(self):
        """(any_() & x) matches exactly where x does."""
        for x in self.selectors:
            with self.subTest(x=x):
                lhs = _matched_ids(any_() & x, self.cursors)
                rhs = _matched_ids(x, self.cursors)
                self.assertEqual(lhs, rhs)

    def test_identity_or_bottom(self):
        """(none_() | x) matches exactly where x does."""
        for x in self.selectors:
            with self.subTest(x=x):
                lhs = _matched_ids(none_() | x, self.cursors)
                rhs = _matched_ids(x, self.cursors)
                self.assertEqual(lhs, rhs)

    # -----------------------------------------------------------------------
    # Annihilator laws
    # -----------------------------------------------------------------------

    def test_annihilator_and_bottom(self):
        """(none_() & x) matches nowhere."""
        for x in self.selectors:
            with self.subTest(x=x):
                matched = _matched_ids(none_() & x, self.cursors)
                self.assertEqual(matched, frozenset())

    def test_annihilator_or_top(self):
        """(any_() | x) matches everywhere."""
        for x in self.selectors:
            with self.subTest(x=x):
                matched = _matched_ids(any_() | x, self.cursors)
                self.assertEqual(matched, _all_ids(self.cursors))

    # -----------------------------------------------------------------------
    # Involution (double negation)
    # -----------------------------------------------------------------------

    def test_involution(self):
        """~~x matches exactly where x does."""
        for x in self.selectors:
            with self.subTest(x=x):
                lhs = _matched_ids(~~x, self.cursors)
                rhs = _matched_ids(x, self.cursors)
                self.assertEqual(lhs, rhs)

    # -----------------------------------------------------------------------
    # De Morgan laws
    # -----------------------------------------------------------------------

    def test_de_morgan_and(self):
        """~(x & y) matches exactly where (~x | ~y) does."""
        for x, y in self.pairs:
            with self.subTest(x=x, y=y):
                lhs = _matched_ids(~(x & y), self.cursors)
                rhs = _matched_ids(~x | ~y, self.cursors)
                self.assertEqual(lhs, rhs)

    def test_de_morgan_or(self):
        """~(x | y) matches exactly where (~x & ~y) does."""
        for x, y in self.pairs:
            with self.subTest(x=x, y=y):
                lhs = _matched_ids(~(x | y), self.cursors)
                rhs = _matched_ids(~x & ~y, self.cursors)
                self.assertEqual(lhs, rhs)
