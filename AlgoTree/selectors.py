"""
Composable selector system for tree pattern matching.

This module provides a type-safe, composable selector system
that can be combined using logical operators.
"""

from typing import Callable, Iterator, Optional, Union
from abc import ABC, abstractmethod
import ast
import re
import fnmatch
from .node import Node
from .tree import Tree


class Selector(ABC):
    """
    Abstract base class for tree node selectors.

    Selectors can be composed using operators:
    - & for AND
    - | for OR
    - ~ for NOT
    - ^ for XOR
    """

    @abstractmethod
    def matches(self, node: Node) -> bool:
        """Check if node matches this selector."""
        pass

    def matches_at(self, cursor) -> bool:
        """Position-aware match. Default ignores position (value-local)."""
        return self.matches(cursor.node)

    def select(self, tree: Union[Node, Tree]) -> Iterator[Node]:
        """Select all matching nodes from tree (position-aware)."""
        root = tree.root if isinstance(tree, Tree) else tree
        from .cursor import Cursor, walk_cursors
        for cursor in walk_cursors(Cursor(root)):
            if self.matches_at(cursor):
                yield cursor.node

    def first(self, tree: Union[Node, Tree]) -> Optional[Node]:
        """Get first matching node or None."""
        for node in self.select(tree):
            return node
        return None

    def count(self, tree: Union[Node, Tree]) -> int:
        """Count matching nodes."""
        return sum(1 for _ in self.select(tree))

    def exists(self, tree: Union[Node, Tree]) -> bool:
        """Check if any node matches."""
        return self.first(tree) is not None

    # Logical operators for composition

    def __and__(self, other: 'Selector') -> 'Selector':
        """Combine selectors with AND."""
        return AndSelector(self, other)

    def __or__(self, other: 'Selector') -> 'Selector':
        """Combine selectors with OR."""
        return OrSelector(self, other)

    def __invert__(self) -> 'Selector':
        """Negate selector."""
        return NotSelector(self)

    def __xor__(self, other: 'Selector') -> 'Selector':
        """Combine selectors with XOR (exclusive or)."""
        return XorSelector(self, other)

    # Structural combinators

    def child_of(self, parent_selector: 'Selector') -> 'Selector':
        """Match nodes that are direct children of parent matching selector."""
        return AxisSelector(self, 'child_of', parent_selector)

    def parent_of(self, child_selector: 'Selector') -> 'Selector':
        """Match nodes that are direct parents of children matching selector."""
        return AxisSelector(self, 'parent_of', child_selector)

    def descendant_of(self, ancestor_selector: 'Selector') -> 'Selector':
        """Match nodes that are descendants of nodes matching selector."""
        return AxisSelector(self, 'descendant_of', ancestor_selector)

    def ancestor_of(self, descendant_selector: 'Selector') -> 'Selector':
        """Match nodes that are ancestors of nodes matching selector."""
        return AxisSelector(self, 'ancestor_of', descendant_selector)

    def sibling_of(self, sibling_selector: 'Selector') -> 'Selector':
        """Match nodes that are siblings of nodes matching selector."""
        return AxisSelector(self, 'sibling_of', sibling_selector)

    def at_depth(self, depth: int) -> 'Selector':
        """Match nodes at specific depth."""
        return self & DepthSelector(depth)

    def at_level(self, level: int) -> 'Selector':
        """Alias for at_depth."""
        return self.at_depth(level)

    # Convenience methods

    def where(self, **attrs) -> 'Selector':
        """Add attribute constraints."""
        return self & AttrsSelector(**attrs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


# Basic selectors

class NameSelector(Selector):
    """Select nodes by exact name match."""

    def __init__(self, pattern: str):
        self.pattern = pattern

    def matches(self, node: Node) -> bool:
        return node.name == self.pattern

    def __repr__(self) -> str:
        return f"NameSelector({self.pattern!r})"


class GlobSelector(Selector):
    """Select nodes by glob pattern (fnmatch semantics)."""

    def __init__(self, pattern: str):
        self.pattern = pattern

    def matches(self, node: Node) -> bool:
        return fnmatch.fnmatch(node.name, self.pattern)

    def __repr__(self) -> str:
        return f"GlobSelector({self.pattern!r})"


class RegexSelector(Selector):
    """Select nodes by regex pattern (re.fullmatch semantics)."""

    def __init__(self, pattern: str):
        self.pattern = pattern
        self._regex = re.compile(pattern)

    def matches(self, node: Node) -> bool:
        return self._regex.fullmatch(node.name) is not None

    def __repr__(self) -> str:
        return f"RegexSelector({self.pattern!r})"


class AttrsSelector(Selector):
    """Select nodes by attributes."""

    def __init__(self, **attrs):
        self.attrs = attrs

    def matches(self, node: Node) -> bool:
        for key, value in self.attrs.items():
            node_value = node.get(key)

            if callable(value):
                # Value is a predicate function
                if not value(node_value):
                    return False
            elif value is None:
                # Check for existence
                if key not in node.attrs:
                    return False
            else:
                # Check for equality
                if node_value != value:
                    return False
        return True

    def __repr__(self) -> str:
        attrs_str = ', '.join(f'{k}={v!r}' for k, v in self.attrs.items())
        return f"AttrsSelector({attrs_str})"


class TypeSelector(Selector):
    """Select nodes by type attribute."""

    def __init__(self, node_type: str):
        self.node_type = node_type

    def matches(self, node: Node) -> bool:
        return node.get('type') == self.node_type

    def __repr__(self) -> str:
        return f"TypeSelector({self.node_type!r})"


class PredicateSelector(Selector):
    """Select nodes using custom predicate function."""

    def __init__(self, predicate: Callable[[Node], bool], name: str = "custom"):
        self.predicate = predicate
        self.name = name

    def matches(self, node: Node) -> bool:
        return self.predicate(node)

    def __repr__(self) -> str:
        return f"PredicateSelector({self.name})"


class DepthSelector(Selector):
    """Select nodes at specific depth."""

    def __init__(self, depth: Union[int, range]):
        self.depth = depth

    def matches(self, node: Node) -> bool:
        raise NotImplementedError(
            "DepthSelector is position-dependent; use .select()/.first() "
            "or matches_at(cursor)"
        )

    def matches_at(self, cursor) -> bool:
        d = cursor.depth
        if isinstance(self.depth, range):
            return d in self.depth
        return d == self.depth

    def __repr__(self) -> str:
        return f"DepthSelector({self.depth!r})"


class LeafSelector(Selector):
    """Select leaf nodes."""

    def matches(self, node: Node) -> bool:
        return node.is_leaf

    def __repr__(self) -> str:
        return "LeafSelector()"


class RootSelector(Selector):
    """Select root node."""

    def matches(self, node: Node) -> bool:
        raise NotImplementedError(
            "RootSelector is position-dependent; use .select()/.first() "
            "or matches_at(cursor)"
        )

    def matches_at(self, cursor) -> bool:
        return cursor.is_root

    def __repr__(self) -> str:
        return "RootSelector()"


# Logical combinators

class AndSelector(Selector):
    """Selector that matches if all sub-selectors match."""

    def __init__(self, *selectors: Selector):
        self.selectors = selectors

    def matches(self, node: Node) -> bool:
        return all(s.matches(node) for s in self.selectors)

    def matches_at(self, cursor) -> bool:
        return all(s.matches_at(cursor) for s in self.selectors)

    def __repr__(self) -> str:
        return f"({' & '.join(repr(s) for s in self.selectors)})"


class OrSelector(Selector):
    """Selector that matches if any sub-selector matches."""

    def __init__(self, *selectors: Selector):
        self.selectors = selectors

    def matches(self, node: Node) -> bool:
        return any(s.matches(node) for s in self.selectors)

    def matches_at(self, cursor) -> bool:
        return any(s.matches_at(cursor) for s in self.selectors)

    def __repr__(self) -> str:
        return f"({' | '.join(repr(s) for s in self.selectors)})"


class NotSelector(Selector):
    """Selector that matches if sub-selector doesn't match."""

    def __init__(self, selector: Selector):
        self.selector = selector

    def matches(self, node: Node) -> bool:
        return not self.selector.matches(node)

    def matches_at(self, cursor) -> bool:
        return not self.selector.matches_at(cursor)

    def __repr__(self) -> str:
        return f"~{repr(self.selector)}"


class XorSelector(Selector):
    """Selector that matches if exactly one sub-selector matches."""

    def __init__(self, *selectors: Selector):
        self.selectors = selectors

    def matches(self, node: Node) -> bool:
        matches = sum(1 for s in self.selectors if s.matches(node))
        return matches == 1

    def matches_at(self, cursor) -> bool:
        return sum(1 for s in self.selectors if s.matches_at(cursor)) == 1

    def __repr__(self) -> str:
        return f"({' ^ '.join(repr(s) for s in self.selectors)})"


# Structural combinators

_VALID_AXES = frozenset({
    'child_of', 'parent_of', 'descendant_of', 'ancestor_of', 'sibling_of'
})


class AxisSelector(Selector):
    """
    Unified structural selector that replaces the five separate axis classes.

    ``inner.matches_at(cursor)`` is evaluated first; if it passes, the axis
    relation against ``other`` is checked using cursor navigation.

    Parameters
    ----------
    inner : Selector
        The selector applied to the focus node itself.
    axis : str
        One of ``'child_of'``, ``'parent_of'``, ``'descendant_of'``,
        ``'ancestor_of'``, ``'sibling_of'``.
    other : Selector
        The selector evaluated against the related position(s).
    """

    def __init__(self, inner: Selector, axis: str, other: Selector):
        if axis not in _VALID_AXES:
            raise ValueError(
                f"axis must be one of {sorted(_VALID_AXES)!r}, got {axis!r}"
            )
        self.inner = inner
        self.axis = axis
        self.other = other

    def matches(self, node: Node) -> bool:
        raise NotImplementedError(
            "AxisSelector is position-dependent; use .select()/.first() "
            "or matches_at(cursor)"
        )

    def matches_at(self, cursor) -> bool:
        if not self.inner.matches_at(cursor):
            return False

        if self.axis == 'child_of':
            if cursor.is_root:
                return False
            return self.other.matches_at(cursor.up())

        elif self.axis == 'parent_of':
            return any(
                self.other.matches_at(cursor.down(i))
                for i in range(len(cursor.node.children))
            )

        elif self.axis == 'descendant_of':
            return any(
                self.other.matches_at(ancestor)
                for ancestor in cursor.ancestors()
            )

        elif self.axis == 'ancestor_of':
            from .cursor import walk_cursors
            descendants = walk_cursors(cursor)
            next(descendants)  # skip the focus itself
            return any(self.other.matches_at(d) for d in descendants)

        else:  # sibling_of
            return any(
                self.other.matches_at(sib) for sib in cursor.siblings()
            )

    def __repr__(self) -> str:
        return f"AxisSelector({self.inner!r}, {self.axis!r}, {self.other!r})"


# Factory functions for common selectors

def name(pattern: str) -> NameSelector:
    """Create exact name selector (matches node.name == pattern literally)."""
    return NameSelector(pattern)


def glob(pattern: str) -> GlobSelector:
    """Create glob selector (fnmatch.fnmatch semantics; * and ? are wildcards)."""
    return GlobSelector(pattern)


def regex(pattern: str) -> RegexSelector:
    """Create regex selector (re.fullmatch semantics; full-string match)."""
    return RegexSelector(pattern)


def attrs(**kwargs) -> AttrsSelector:
    """Create attributes selector."""
    return AttrsSelector(**kwargs)


def type_(node_type: str) -> TypeSelector:
    """Create type selector."""
    return TypeSelector(node_type)


def predicate(fn: Callable[[Node], bool], name: str = "custom") -> PredicateSelector:
    """Create predicate selector."""
    return PredicateSelector(fn, name)


def depth(d: Union[int, range]) -> DepthSelector:
    """Create depth selector."""
    return DepthSelector(d)


def leaf() -> LeafSelector:
    """Create leaf selector."""
    return LeafSelector()


def root() -> RootSelector:
    """Create root selector."""
    return RootSelector()


def any_() -> Selector:
    """Select any node."""
    return PredicateSelector(lambda _: True, "any")


def none() -> Selector:
    """Select no nodes."""
    return PredicateSelector(lambda _: False, "none")


# CSS-like selector parser (simplified)

def parse(selector_str: str) -> Selector:
    """
    Parse CSS-like selector string.

    Examples:
        'node'           - Select by name
        '*.txt'          - Wildcard pattern
        '[type=file]'    - Attribute selector
        'parent > child' - Direct child
        'ancestor child' - Descendant
        ':leaf'          - Pseudo-selectors
        ':root'
    """
    # This is a simplified parser - could be extended
    selector_str = selector_str.strip()

    # Pseudo-selectors
    if selector_str == ':leaf':
        return leaf()
    elif selector_str == ':root':
        return root()

    # Attribute selector
    if selector_str.startswith('[') and selector_str.endswith(']'):
        attr_str = selector_str[1:-1]
        if '=' in attr_str:
            key, value = attr_str.split('=', 1)
            # Try to parse value as a Python literal (safe)
            try:
                value = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                pass  # Keep as string
            return attrs(**{key: value})
        else:
            # Just check existence
            return attrs(**{attr_str: None})

    # Direct child selector
    if ' > ' in selector_str:
        parts = selector_str.split(' > ', 1)
        parent_sel = parse(parts[0])
        child_sel = parse(parts[1])
        return child_sel.child_of(parent_sel)

    # Descendant selector
    if ' ' in selector_str:
        parts = selector_str.split(' ', 1)
        ancestor_sel = parse(parts[0])
        descendant_sel = parse(parts[1])
        return descendant_sel.descendant_of(ancestor_sel)

    # Name/glob selector: glob for tokens with wildcards, else exact name.
    # Sniffing wildcard syntax is acceptable inside the string DSL parser.
    if '*' in selector_str or '?' in selector_str:
        return glob(selector_str)
    return name(selector_str)
