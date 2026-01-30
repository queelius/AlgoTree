"""
Shared internal utilities for AlgoTree.

These are private helpers — not part of the public API.
"""

import fnmatch
from typing import Callable


def make_predicate(selector) -> Callable:
    """
    Convert a selector (string, callable, or Selector object) to a predicate function.

    Args:
        selector: A node name (str, supports wildcards), a callable predicate,
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

    # String selector — match by name
    pattern = selector
    if '*' in pattern or '?' in pattern:
        return lambda node: fnmatch.fnmatch(node.name, pattern)
    else:
        return lambda node: node.name == pattern


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
