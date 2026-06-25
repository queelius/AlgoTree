"""
Refined immutable-by-default Node implementation.

This module provides the core Node class for AlgoTree with:
- Immutability by default for safer, more predictable code
- Structural sharing for efficient memory usage
- Clean, composable API
- Full type hints for IDE support
"""

from typing import Any, Dict, Iterator, Optional, Union, Callable, TypeVar, Tuple, List, TYPE_CHECKING
from collections import deque

from ._utils import make_predicate as _make_predicate_fn

if TYPE_CHECKING:
    from .selectors import Selector

T = TypeVar('T')
NodeType = TypeVar('NodeType', bound='Node')


class Node:
    """
    Immutable tree node with functional operations.

    All operations return new trees, preserving immutability.
    Uses structural sharing for efficiency.
    """

    __slots__ = ('_name', '_attrs', '_children', '_hash')

    def __init__(
        self,
        name: str,
        *children: 'Node',
        attrs: Optional[Dict[str, Any]] = None
    ):
        """
        Create an immutable, context-free node.

        Args:
            name: Node name/identifier
            *children: Child nodes
            attrs: Node attributes/payload
        """
        self._name = name
        self._attrs = attrs or {}
        self._children = tuple(children)
        self._hash = None  # Cached hash

    @property
    def name(self) -> str:
        """Node name (immutable)."""
        return self._name

    @property
    def attrs(self) -> Dict[str, Any]:
        """Node attributes (returns copy to prevent mutation)."""
        return self._attrs.copy()

    @property
    def children(self) -> Tuple['Node', ...]:
        """Children nodes (immutable tuple)."""
        return self._children

    # Attribute access shortcuts

    def __getitem__(self, key: str) -> Any:
        """Get attribute value."""
        return self._attrs.get(key)

    def get(self, key: str, default: Any = None) -> Any:
        """Get attribute with default."""
        return self._attrs.get(key, default)

    # Immutable transformations

    def with_name(self, name: str) -> 'Node':
        """Return new node with different name."""
        if name == self._name:
            return self
        return self._rebuild(name=name)

    def with_attrs(self, **attrs) -> 'Node':
        """Return new node with updated attributes."""
        new_attrs = {**self._attrs, **attrs}
        if new_attrs == self._attrs:
            return self
        return self._rebuild(attrs=new_attrs)

    def without_attrs(self, *keys: str) -> 'Node':
        """Return new node with attributes removed."""
        new_attrs = {k: v for k, v in self._attrs.items() if k not in keys}
        if new_attrs == self._attrs:
            return self
        return self._rebuild(attrs=new_attrs)

    def with_child(self, child: Union['Node', str], **attrs) -> 'Node':
        """Return new node with child added."""
        if isinstance(child, str):
            child = Node(child, attrs=attrs)
        return self._rebuild(children=self._children + (child,))

    def with_children(self, *children: 'Node') -> 'Node':
        """Return new node with children replaced."""
        return self._rebuild(children=tuple(children))

    def without_child(self, child: Union['Node', str, int]) -> 'Node':
        """Return new node with child removed."""
        if isinstance(child, int):
            if 0 <= child < len(self._children):
                new_children = self._children[:child] + self._children[child + 1:]
            else:
                return self
        elif isinstance(child, str):
            new_children = tuple(c for c in self._children if c.name != child)
        else:
            new_children = tuple(c for c in self._children if c != child)

        if len(new_children) == len(self._children):
            return self
        return self._rebuild(children=new_children)

    def map_children(self, fn: Callable[['Node'], 'Node']) -> 'Node':
        """Return new node with function applied to all children."""
        new_children = tuple(fn(child) for child in self._children)
        if new_children == self._children:
            return self
        return self._rebuild(children=new_children)

    def filter_children(self, predicate: Callable[['Node'], bool]) -> 'Node':
        """Return new node with only children matching predicate."""
        new_children = tuple(child for child in self._children if predicate(child))
        if new_children == self._children:
            return self
        return self._rebuild(children=new_children)

    # Tree-wide transformations

    def map(self, fn: Callable[['Node'], 'Node']) -> 'Node':
        """Apply function to all nodes in tree (bottom-up)."""
        # First map children
        new_children = tuple(child.map(fn) for child in self._children)

        # Create new node with mapped children
        if new_children != self._children:
            new_node = self._rebuild(children=new_children)
        else:
            new_node = self

        # Then apply function to this node
        return fn(new_node)

    def filter(self, predicate: Callable[['Node'], bool]) -> Optional['Node']:
        """
        Filter tree to nodes matching predicate.

        Returns None if this node doesn't match and has no matching descendants.
        Preserves structure for matching nodes and their ancestors.
        """
        # Filter children first
        filtered_children = []
        for child in self._children:
            filtered_child = child.filter(predicate)
            if filtered_child is not None:
                filtered_children.append(filtered_child)

        # Check if this node or any descendant matches
        if predicate(self) or filtered_children:
            return self._rebuild(children=tuple(filtered_children))
        return None

    def render(self, fmt: str = "unicode", **opts) -> str:
        """
        Render this node as a string using the named format.

        Delegates to :func:`AlgoTree.render.render`.  Built-in formats are
        ``"ascii"`` and ``"unicode"``; additional backends can be registered
        with :func:`AlgoTree.render.register`.

        Args:
            fmt: Render format name (default: ``"unicode"``).
            **opts: Format-specific keyword arguments.

        Returns:
            String representation of this subtree.
        """
        from . import render as _render_mod
        return _render_mod.render(self, fmt, **opts)

    def _repr_html_(self) -> str:
        """Return an HTML representation for Jupyter/Quarto notebook display.

        Delegates to :func:`AlgoTree.render.render` with ``fmt='html'``.
        All node names and attribute values are HTML-escaped, so this method
        is safe to use with untrusted node names.
        """
        from . import render as _render_mod
        return _render_mod.render(self, "html")

    def _repr_mermaid_(self) -> str:
        """Return a Mermaid diagram string for notebook display.

        Delegates to :func:`AlgoTree.render.render` with ``fmt='mermaid'``.
        """
        from . import render as _render_mod
        return _render_mod.render(self, "mermaid")

    def fold(self, fn: Callable[['Node', List[T]], T]) -> T:
        """
        Catamorphism: reduce the tree bottom-up.

        Calls fn(node, child_results) for every node, where child_results is
        the list of results already computed for that node's children, in
        order. This is the single recursion primitive: size, height, to_dict,
        rendering, and evaluation are all folds with a different combine step.

        Args:
            fn: Combine step (node, [child_results]) -> result.

        Returns:
            The result of folding the whole subtree rooted at this node.
        """
        child_results = [child.fold(fn) for child in self._children]
        return fn(self, child_results)

    def find(self, selector: Union[str, Callable[['Node'], bool], 'Selector']) -> Optional['Node']:
        """Find first node matching selector."""
        if hasattr(selector, 'matches_at'):
            from .cursor import Cursor, walk_cursors
            for cursor in walk_cursors(Cursor(self)):
                if selector.matches_at(cursor):
                    return cursor.node
            return None
        predicate = self._make_predicate(selector)
        if predicate(self):
            return self
        for node in self.descendants():
            if predicate(node):
                return node
        return None

    def find_all(self, selector: Union[str, Callable[['Node'], bool], 'Selector']) -> List['Node']:
        """Find all nodes matching selector."""
        if hasattr(selector, 'matches_at'):
            from .cursor import Cursor, walk_cursors
            return [c.node for c in walk_cursors(Cursor(self)) if selector.matches_at(c)]
        predicate = self._make_predicate(selector)
        return [node for node in self.walk() if predicate(node)]

    # Iteration methods

    def walk(self, order: str = 'preorder') -> Iterator['Node']:
        """
        Walk tree in specified order.

        Args:
            order: 'preorder', 'postorder', or 'levelorder'
        """
        if order == 'preorder':
            yield self
            for child in self._children:
                yield from child.walk('preorder')
        elif order == 'postorder':
            for child in self._children:
                yield from child.walk('postorder')
            yield self
        elif order == 'levelorder':
            queue = deque([self])
            while queue:
                node = queue.popleft()
                yield node
                queue.extend(node.children)
        else:
            raise ValueError(f"Unknown order: {order}")

    def descendants(self) -> Iterator['Node']:
        """Iterate over all descendants (not including self)."""
        for child in self._children:
            yield child
            yield from child.descendants()

    def leaves(self) -> Iterator['Node']:
        """Iterate over all leaf nodes."""
        if not self._children:
            yield self
        else:
            for child in self._children:
                yield from child.leaves()

    # Conversion methods

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tree to nested dictionary.

        Returns:
            Dictionary with 'name', attributes, and 'children' list.
        """
        return self.fold(
            lambda node, child_results: {
                'name': node.name,
                **node.attrs,
                **({'children': child_results} if child_results else {}),
            }
        )

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Node':
        """
        Create node tree from nested dictionary.

        Args:
            data: Dictionary with 'name', optional attributes, and optional 'children' list

        Returns:
            Root node of reconstructed tree
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data)}")

        if 'name' not in data:
            raise ValueError("Dictionary must contain 'name' key")

        name = data['name']

        # Extract children if present
        children_data = data.get('children', [])
        children = [Node.from_dict(child) for child in children_data]

        # Extract attributes (everything except 'name' and 'children')
        attrs = {k: v for k, v in data.items() if k not in ('name', 'children')}

        return Node(name, *children, attrs=attrs)

    # Query properties

    @property
    def is_leaf(self) -> bool:
        """Check if this is leaf node."""
        return len(self._children) == 0

    @property
    def height(self) -> int:
        """Get height of subtree rooted at this node."""
        return self.fold(
            lambda _node, child_results: 0 if not child_results else 1 + max(child_results)
        )

    @property
    def size(self) -> int:
        """Get total number of nodes in subtree."""
        return self.fold(lambda _node, child_results: 1 + sum(child_results))

    # Helper methods

    def _rebuild(
        self,
        name: Optional[str] = None,
        attrs: Optional[Dict[str, Any]] = None,
        children: Optional[Tuple['Node', ...]] = None
    ) -> 'Node':
        """Rebuild node with specified changes."""
        new_name = name if name is not None else self._name
        new_attrs = attrs if attrs is not None else self._attrs
        new_children = children if children is not None else self._children

        return Node(new_name, *new_children, attrs=new_attrs)

    def _make_predicate(
        self,
        selector: Union[str, Callable[['Node'], bool], 'Selector']
    ) -> Callable[['Node'], bool]:
        """Convert selector to predicate function."""
        return _make_predicate_fn(selector)

    # Comparison and hashing

    def __hash__(self) -> int:
        """Compute hash (cached for performance)."""
        if self._hash is None:
            # Include name, attrs, and children in hash
            attrs_items = tuple(sorted(self._attrs.items()))
            self._hash = hash((self._name, attrs_items, self._children))
        return self._hash

    def __eq__(self, other: Any) -> bool:
        """Check equality (structure and attributes)."""
        if not isinstance(other, Node):
            return False
        return (
            self._name == other._name
            and self._attrs == other._attrs
            and self._children == other._children
        )

    def __repr__(self) -> str:
        """String representation."""
        if self._attrs:
            attrs_str = ', '.join(f'{k}={v!r}' for k, v in self._attrs.items())
            return f"Node({self._name!r}, attrs={{{attrs_str}}}, children={len(self._children)})"
        return f"Node({self._name!r}, children={len(self._children)})"

    def __str__(self) -> str:
        """Simple string representation."""
        return self._name

    # Pickle support

    def __getstate__(self):
        """Get state for pickling."""
        return {
            'name': self._name,
            'attrs': self._attrs,
            'children': self._children,
        }

    def __setstate__(self, state):
        """Restore state from pickling."""
        object.__setattr__(self, '_name', state['name'])
        object.__setattr__(self, '_attrs', state['attrs'])
        object.__setattr__(self, '_children', state['children'])
        object.__setattr__(self, '_hash', None)


def node(name: str, *children: Union[Node, str], **attrs) -> Node:
    """
    Convenience function to create a node.

    Allows mixing Node objects and strings as children.
    Strings are converted to nodes automatically.

    Example:
        tree = node('root',
            node('child1', value=1),
            'child2',
            node('child3',
                'grandchild1',
                'grandchild2'
            )
        )
    """
    converted_children = []
    for child in children:
        if isinstance(child, str):
            converted_children.append(Node(child))
        else:
            converted_children.append(child)

    return Node(name, *converted_children, attrs=attrs)
