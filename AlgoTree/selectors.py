"""
Composable selector system for tree pattern matching.

This module provides a type-safe, composable selector system
that can be combined using logical operators.
"""

from typing import Callable, Iterator, Optional, Union
from abc import ABC, abstractmethod
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

    def select(self, tree: Union[Node, Tree]) -> Iterator[Node]:
        """Select all matching nodes from tree."""
        root = tree.root if isinstance(tree, Tree) else tree
        for node in root.walk():
            if self.matches(node):
                yield node

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
        return ChildOfSelector(self, parent_selector)

    def parent_of(self, child_selector: 'Selector') -> 'Selector':
        """Match nodes that are direct parents of children matching selector."""
        return ParentOfSelector(self, child_selector)

    def descendant_of(self, ancestor_selector: 'Selector') -> 'Selector':
        """Match nodes that are descendants of nodes matching selector."""
        return DescendantOfSelector(self, ancestor_selector)

    def ancestor_of(self, descendant_selector: 'Selector') -> 'Selector':
        """Match nodes that are ancestors of nodes matching selector."""
        return AncestorOfSelector(self, descendant_selector)

    def sibling_of(self, sibling_selector: 'Selector') -> 'Selector':
        """Match nodes that are siblings of nodes matching selector."""
        return SiblingOfSelector(self, sibling_selector)

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
    """Select nodes by name pattern."""

    def __init__(self, pattern: str):
        self.pattern = pattern
        # Check if it's a glob pattern (* or ?)
        self._is_glob = ('*' in pattern or '?' in pattern)
        # Check if it's a regex pattern (has other regex chars)
        self._is_regex = bool(re.search(r'[\\^$+{}[\]|()\s]', pattern)) and not self._is_glob

        if self._is_regex:
            self._regex = re.compile(pattern)

    def matches(self, node: Node) -> bool:
        if self._is_glob:
            return fnmatch.fnmatch(node.name, self.pattern)
        elif self._is_regex:
            return bool(self._regex.match(node.name))
        else:
            return node.name == self.pattern

    def __repr__(self) -> str:
        return f"NameSelector({self.pattern!r})"


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
        node_depth = node.depth
        if isinstance(self.depth, range):
            return node_depth in self.depth
        return node_depth == self.depth

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
        return node.is_root

    def __repr__(self) -> str:
        return "RootSelector()"


# Logical combinators

class AndSelector(Selector):
    """Selector that matches if all sub-selectors match."""

    def __init__(self, *selectors: Selector):
        self.selectors = selectors

    def matches(self, node: Node) -> bool:
        return all(s.matches(node) for s in self.selectors)

    def __repr__(self) -> str:
        return f"({' & '.join(repr(s) for s in self.selectors)})"


class OrSelector(Selector):
    """Selector that matches if any sub-selector matches."""

    def __init__(self, *selectors: Selector):
        self.selectors = selectors

    def matches(self, node: Node) -> bool:
        return any(s.matches(node) for s in self.selectors)

    def __repr__(self) -> str:
        return f"({' | '.join(repr(s) for s in self.selectors)})"


class NotSelector(Selector):
    """Selector that matches if sub-selector doesn't match."""

    def __init__(self, selector: Selector):
        self.selector = selector

    def matches(self, node: Node) -> bool:
        return not self.selector.matches(node)

    def __repr__(self) -> str:
        return f"~{repr(self.selector)}"


class XorSelector(Selector):
    """Selector that matches if exactly one sub-selector matches."""

    def __init__(self, *selectors: Selector):
        self.selectors = selectors

    def matches(self, node: Node) -> bool:
        matches = sum(1 for s in self.selectors if s.matches(node))
        return matches == 1

    def __repr__(self) -> str:
        return f"({' ^ '.join(repr(s) for s in self.selectors)})"


# Structural combinators

class ChildOfSelector(Selector):
    """Select nodes that are children of parent matching selector."""

    def __init__(self, child_selector: Selector, parent_selector: Selector):
        self.child_selector = child_selector
        self.parent_selector = parent_selector

    def matches(self, node: Node) -> bool:
        if not self.child_selector.matches(node):
            return False
        return node.parent and self.parent_selector.matches(node.parent)

    def __repr__(self) -> str:
        return f"{repr(self.child_selector)}.child_of({repr(self.parent_selector)})"


class ParentOfSelector(Selector):
    """Select nodes that are parents of children matching selector."""

    def __init__(self, parent_selector: Selector, child_selector: Selector):
        self.parent_selector = parent_selector
        self.child_selector = child_selector

    def matches(self, node: Node) -> bool:
        if not self.parent_selector.matches(node):
            return False
        return any(self.child_selector.matches(child) for child in node.children)

    def __repr__(self) -> str:
        return f"{repr(self.parent_selector)}.parent_of({repr(self.child_selector)})"


class DescendantOfSelector(Selector):
    """Select nodes that are descendants of ancestor matching selector."""

    def __init__(self, descendant_selector: Selector, ancestor_selector: Selector):
        self.descendant_selector = descendant_selector
        self.ancestor_selector = ancestor_selector

    def matches(self, node: Node) -> bool:
        if not self.descendant_selector.matches(node):
            return False
        for ancestor in node.ancestors():
            if self.ancestor_selector.matches(ancestor):
                return True
        return False

    def __repr__(self) -> str:
        return f"{repr(self.descendant_selector)}.descendant_of({repr(self.ancestor_selector)})"


class AncestorOfSelector(Selector):
    """Select nodes that are ancestors of descendant matching selector."""

    def __init__(self, ancestor_selector: Selector, descendant_selector: Selector):
        self.ancestor_selector = ancestor_selector
        self.descendant_selector = descendant_selector

    def matches(self, node: Node) -> bool:
        if not self.ancestor_selector.matches(node):
            return False
        for descendant in node.descendants():
            if self.descendant_selector.matches(descendant):
                return True
        return False

    def __repr__(self) -> str:
        return f"{repr(self.ancestor_selector)}.ancestor_of({repr(self.descendant_selector)})"


class SiblingOfSelector(Selector):
    """Select nodes that are siblings of node matching selector."""

    def __init__(self, node_selector: Selector, sibling_selector: Selector):
        self.node_selector = node_selector
        self.sibling_selector = sibling_selector

    def matches(self, node: Node) -> bool:
        if not self.node_selector.matches(node):
            return False
        for sibling in node.siblings():
            if self.sibling_selector.matches(sibling):
                return True
        return False

    def __repr__(self) -> str:
        return f"{repr(self.node_selector)}.sibling_of({repr(self.sibling_selector)})"


# Factory functions for common selectors

def name(pattern: str) -> NameSelector:
    """Create name selector."""
    return NameSelector(pattern)


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
            # Try to parse value
            try:
                value = eval(value)
            except Exception:
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

    # Name selector (with wildcard support)
    return name(selector_str)
