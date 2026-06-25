"""
Shared internal utilities for AlgoTree.

These are private helpers — not part of the public API.
"""

from typing import Callable


def make_predicate(selector) -> Callable:
    """
    Convert a selector (string, callable, or Selector object) to a predicate function.

    Bare strings lift to EXACT name match (node.name == s). There is no
    wildcard sniffing at this boundary; use glob() or regex() selectors for
    pattern-based matching.

    Args:
        selector: A node name (str, exact match), a callable predicate,
                  or a Selector object with a .matches() method.

    Returns:
        A callable that takes a Node and returns bool.
    """
    # Selector object (has .matches method)
    if hasattr(selector, 'matches'):
        return selector.matches

    # Already a callable predicate
    if callable(selector):
        return selector

    # String selector -- exact name match only (no wildcard sniffing)
    s = selector
    return lambda node: node.name == s


def matches_selector(node, selector) -> bool:
    """
    Check if a node matches a selector.

    Args:
        node: A Node instance.
        selector: A string, callable, or Selector object.

    Returns:
        True if the node matches.
    """
    return make_predicate(selector)(node)
