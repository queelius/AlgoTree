"""
Refined immutable-by-default Node implementation.

This module provides the core Node class for AlgoTree with:
- Immutability by default for safer, more predictable code
- Structural sharing for efficient memory usage
- Clean, composable API
- Full type hints for IDE support
"""

from typing import Any, Dict, Iterator, Optional, Union, Callable, TypeVar, Tuple, List, TYPE_CHECKING
import weakref

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

    __slots__ = ('_name', '_attrs', '_children', '_parent_ref', '_hash', '__weakref__')

    def __init__(
        self,
        name: str,
        *children: 'Node',
        attrs: Optional[Dict[str, Any]] = None,
        parent: Optional['Node'] = None
    ):
        """
        Create an immutable node.

        Args:
            name: Node name/identifier
            *children: Child nodes
            attrs: Node attributes/payload
            parent: Parent node (internal use - managed automatically)
        """
        self._name = name
        self._attrs = attrs or {}
        self._children = tuple(children)
        self._parent_ref = weakref.ref(parent) if parent else lambda: None
        self._hash = None  # Cached hash

        # Set parent references for children
        for child in children:
            object.__setattr__(child, '_parent_ref', weakref.ref(self))

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

    @property
    def parent(self) -> Optional['Node']:
        """Parent node (weak reference)."""
        return self._parent_ref()

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

    def find(self, selector: Union[str, Callable[['Node'], bool], 'Selector']) -> Optional['Node']:
        """Find first node matching selector."""
        predicate = self._make_predicate(selector)

        # Check self first
        if predicate(self):
            return self

        # Then check descendants
        for node in self.descendants():
            if predicate(node):
                return node
        return None

    def find_all(self, selector: Union[str, Callable[['Node'], bool], 'Selector']) -> List['Node']:
        """Find all nodes matching selector."""
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
            queue = [self]
            while queue:
                node = queue.pop(0)
                yield node
                queue.extend(node.children)
        else:
            raise ValueError(f"Unknown order: {order}")

    def descendants(self) -> Iterator['Node']:
        """Iterate over all descendants (not including self)."""
        for child in self._children:
            yield child
            yield from child.descendants()

    def ancestors(self, include_self: bool = False) -> Iterator['Node']:
        """Iterate from this node up to root."""
        current = self if include_self else self.parent
        while current:
            yield current
            current = current.parent

    def leaves(self) -> Iterator['Node']:
        """Iterate over all leaf nodes."""
        if not self._children:
            yield self
        else:
            for child in self._children:
                yield from child.leaves()

    def siblings(self) -> Iterator['Node']:
        """Iterate over sibling nodes."""
        if self.parent:
            for child in self.parent.children:
                if child != self:
                    yield child

    # Conversion methods

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tree to nested dictionary.

        Returns:
            Dictionary with 'name', attributes, and 'children' list
        """
        result = {'name': self._name}
        result.update(self._attrs)

        if self._children:
            result['children'] = [child.to_dict() for child in self._children]

        return result

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
    def is_root(self) -> bool:
        """Check if this is root node."""
        return self.parent is None

    @property
    def is_leaf(self) -> bool:
        """Check if this is leaf node."""
        return len(self._children) == 0

    @property
    def depth(self) -> int:
        """Get depth from root (root has depth 0)."""
        return sum(1 for _ in self.ancestors())

    @property
    def height(self) -> int:
        """Get height of subtree rooted at this node."""
        if not self._children:
            return 0
        return 1 + max(child.height for child in self._children)

    @property
    def size(self) -> int:
        """Get total number of nodes in subtree."""
        return sum(1 for _ in self.walk())

    @property
    def path(self) -> str:
        """Get path from root as string."""
        parts = [node.name for node in self.ancestors(include_self=True)]
        return '/'.join(reversed(parts))

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
        # Check if it's a Selector object (has matches method)
        if hasattr(selector, 'matches'):
            return selector.matches

        if callable(selector):
            return selector

        # String selector - match by name
        pattern = selector
        if '*' in pattern:
            # Simple wildcard matching
            import fnmatch
            return lambda node: fnmatch.fnmatch(node.name, pattern)
        else:
            # Exact match
            return lambda node: node.name == pattern

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

    # Pickle support (handle weakrefs)

    def __getstate__(self):
        """Get state for pickling (exclude parent weakref)."""
        return {
            'name': self._name,
            'attrs': self._attrs,
            'children': self._children,
        }

    def __setstate__(self, state):
        """Restore state from pickling (reconstruct parent weakrefs)."""
        object.__setattr__(self, '_name', state['name'])
        object.__setattr__(self, '_attrs', state['attrs'])
        object.__setattr__(self, '_children', state['children'])
        object.__setattr__(self, '_parent_ref', lambda: None)
        object.__setattr__(self, '_hash', None)

        # Rebuild parent references for children
        for child in self._children:
            if hasattr(child, '_parent_ref'):
                object.__setattr__(child, '_parent_ref', weakref.ref(self))


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
