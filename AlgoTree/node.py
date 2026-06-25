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
from functools import reduce as _functools_reduce

from ._utils import make_predicate as _make_predicate_fn

if TYPE_CHECKING:
    from .selectors import Selector
    from .cursor import Cursor

T = TypeVar('T')
NodeType = TypeVar('NodeType', bound='Node')


def _default_scalar(s: str):
    """Try to parse s as int, then float, else return it as a str."""
    try:
        return int(s)
    except (ValueError, TypeError):
        pass
    try:
        return float(s)
    except (ValueError, TypeError):
        pass
    return s


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

    def filter(
        self,
        predicate: Union[Callable[['Node'], bool], 'Selector']
    ) -> Optional['Node']:
        """
        Filter tree to nodes matching predicate or Selector.

        For position-aware Selectors, uses cursor id-membership (identical
        to Tree.filter behaviour).

        Returns None if this node doesn't match and has no matching descendants.
        Preserves structure for matching nodes and their ancestors.
        """
        if hasattr(predicate, 'matches_at'):
            from .cursor import Cursor, walk_cursors
            matched = {id(c.node) for c in walk_cursors(Cursor(self))
                       if predicate.matches_at(c)}
            pred: Callable[['Node'], bool] = lambda n: id(n) in matched
        else:
            pred = predicate

        # Filter children first
        filtered_children = []
        for child in self._children:
            filtered_child = child.filter(pred)
            if filtered_child is not None:
                filtered_children.append(filtered_child)

        # Check if this node or any descendant matches
        if pred(self) or filtered_children:
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

    def fold_traced(self, fn: Callable[['Node', List[T]], T]) -> Tuple[T, Any]:
        """
        Instrumented catamorphism: same recursion as fold, but also builds a
        parallel trace tree recording per-node step/value/arity information.

        Each trace node mirrors the original in name and children structure,
        and carries attrs:
          - step  (int): post-order visit index, 0-based
          - value (Any): the result of fn at that node
          - arity (int): number of children

        Args:
            fn: Combine step (node, [child_results]) -> result.

        Returns:
            A tuple (result, Trace) where result is the same value fold(fn)
            would return, and Trace is a parallel annotated tree.
        """
        from .trace import Trace
        counter = [0]

        def go(node: 'Node') -> Tuple[T, 'Node']:
            child_results, child_traces = [], []
            for c in node._children:
                r, t = go(c)
                child_results.append(r)
                child_traces.append(t)
            value = fn(node, child_results)
            step = counter[0]
            counter[0] += 1
            tnode = Node(
                node._name,
                *child_traces,
                attrs={'step': step, 'value': value, 'arity': len(node._children)},
            )
            return value, tnode

        result, troot = go(self)
        return result, Trace(troot)

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

    # List-AST bridge (name-as-operator convention)

    @staticmethod
    def from_list(data, parse_scalar=str) -> 'Node':
        """
        Build a Node tree from a nested-list AST (name-as-operator).

        ``['op', child, ...]`` becomes ``Node('op', *[from_list(c) for c in children])``.
        A non-list scalar is treated as a nullary leaf: ``42`` becomes ``Node('42')``.

        Args:
            data: A nested list or scalar.  An empty list raises ValueError.
            parse_scalar: Only used in the signature for symmetry with to_list;
                          names are always stringified via str().

        Returns:
            Root Node of the constructed tree.

        Raises:
            ValueError: If data is an empty list.
        """
        if isinstance(data, list):
            if not data:
                raise ValueError("cannot build a Node from an empty list")
            head, *rest = data
            return Node(str(head), *[Node.from_list(x, parse_scalar) for x in rest])
        return Node(str(data))

    def to_list(self, parse_scalar=None):
        """
        Inverse of from_list.

        Leaf nodes are converted by parse_scalar (default: try int, then float,
        then return the name as a str).  Internal nodes become
        ``[name, *[c.to_list() for c in children]]``.

        Args:
            parse_scalar: Callable(str) -> value for leaves; default tries
                          int then float then str.

        Returns:
            A scalar (for leaf nodes) or a list (for internal nodes).
        """
        ps = parse_scalar if parse_scalar is not None else _default_scalar
        if not self._children:
            return ps(self._name)
        return [self._name] + [c.to_list(parse_scalar) for c in self._children]

    # Conversion methods

    def to_dict(self, children_key: str = 'children') -> Dict[str, Any]:
        """
        Convert tree to nested dictionary.

        Args:
            children_key: Key name for children list (default: 'children')

        Returns:
            Dictionary with 'name', attributes, and children list under children_key.
        """
        def _to_dict_node(node: 'Node', child_results):
            d = {'name': node.name, **node.attrs}
            if child_results:
                d[children_key] = child_results
            return d

        return self.fold(_to_dict_node)

    @staticmethod
    def from_dict(data: Dict[str, Any], children_key: str = 'children') -> 'Node':
        """
        Create node tree from nested dictionary.

        Args:
            data: Dictionary with 'name', optional attributes, and optional children list
            children_key: Key name for children list (default: 'children')

        Returns:
            Root node of reconstructed tree

        Note:
            This method does NOT mutate the input dictionary (unlike Tree.from_dict).
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data)}")

        if 'name' not in data:
            raise ValueError("Dictionary must contain 'name' key")

        name = data['name']

        # Extract children if present (non-mutating read)
        children_data = data.get(children_key, [])
        children = [Node.from_dict(child, children_key=children_key) for child in children_data]

        # Extract attributes (everything except 'name' and the children key)
        attrs = {k: v for k, v in data.items() if k not in ('name', children_key)}

        return Node(name, *children, attrs=attrs)

    @classmethod
    def from_paths(cls, paths: List[str], delimiter: str = '/') -> 'Node':
        """
        Create node tree from list of paths.

        Args:
            paths: List of path strings
            delimiter: Path delimiter (default: '/')

        Returns:
            Root node of constructed tree
        """
        if not paths:
            return cls('root')

        # Build tree structure using nested dicts
        tree_dict: Dict[str, Any] = {}

        for path in paths:
            parts = [p for p in path.split(delimiter) if p]
            if not parts:
                continue

            current = tree_dict
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]

        # Convert dict to Node tree
        def dict_to_node(name: str, children_dict: dict) -> 'Node':
            if not children_dict:
                return cls(name)
            children = [
                dict_to_node(child_name, child_dict)
                for child_name, child_dict in sorted(children_dict.items())
            ]
            return cls(name, *children)

        # Get root name (first part of first path)
        root_name = paths[0].split(delimiter)[0] if paths else 'root'

        if root_name in tree_dict:
            return dict_to_node(root_name, tree_dict[root_name])
        else:
            children = [
                dict_to_node(name, children_dict)
                for name, children_dict in sorted(tree_dict.items())
            ]
            return cls(root_name, *children)

    # Tree-equivalent operations (ported from Tree, returning Node instead of Tree)

    def reduce(
        self,
        fn: Callable[[T, 'Node'], T],
        initial: T,
        order: str = 'preorder'
    ) -> T:
        """
        Reduce tree to a single value by iterating in the given order.

        Args:
            fn: Reduction function (accumulator, node) -> new_accumulator
            initial: Initial accumulator value
            order: Traversal order ('preorder', 'postorder', 'levelorder')

        Returns:
            Final reduced value
        """
        return _functools_reduce(fn, self.walk(order), initial)

    def prune(
        self,
        selector: Union[str, Callable[['Node'], bool], 'Selector']
    ) -> Optional['Node']:
        """
        Remove nodes matching selector from this tree.

        Uses cursor id-membership for position-aware Selectors.

        Args:
            selector: Nodes to prune (predicate, exact name (str), or Selector)

        Returns:
            Pruned tree, or None if everything was pruned.
        """
        if hasattr(selector, 'matches_at'):
            from .cursor import Cursor, walk_cursors
            matched = {id(c.node) for c in walk_cursors(Cursor(self))
                       if selector.matches_at(c)}
            return self.filter(lambda n: id(n) not in matched)
        predicate = _make_predicate_fn(selector)
        return self.filter(lambda n: not predicate(n))

    def graft(
        self,
        selector: Union[str, Callable[['Node'], bool], 'Selector'],
        subtree: Union['Node', Any]
    ) -> 'Node':
        """
        Add subtree as a child to every node matching selector.

        Uses cursor id-membership for position-aware Selectors.

        Args:
            selector: Where to graft (predicate, exact name (str), or Selector)
            subtree: Node (or Tree) to graft; if a Tree, its .root is used

        Returns:
            New tree with subtrees grafted
        """
        # Accept Tree objects by unwrapping
        if hasattr(subtree, 'root'):
            subtree = subtree.root

        if hasattr(selector, 'matches_at'):
            from .cursor import Cursor, walk_cursors
            matched = {id(c.node) for c in walk_cursors(Cursor(self))
                       if selector.matches_at(c)}
            predicate = lambda n: id(n) in matched
        else:
            predicate = _make_predicate_fn(selector)

        def add_subtree(node: 'Node') -> 'Node':
            if predicate(node):
                return node.with_child(subtree)
            return node

        return self.map(add_subtree)

    def flatten(self, max_depth: Optional[int] = None) -> 'Node':
        """
        Flatten tree to specified depth.

        Nodes beyond max_depth have their descendants moved up to become
        direct children of the node at max_depth.

        Args:
            max_depth: Maximum depth (None for complete flattening)

        Returns:
            New flattened tree
        """
        def collect_descendants(node: 'Node') -> List['Node']:
            if not node.children:
                return [Node(node.name, attrs=node.attrs)]
            result = []
            for child in node.children:
                result.extend(collect_descendants(child))
            return result

        def flatten_node(node: 'Node', current_depth: int = 0) -> 'Node':
            if max_depth is not None and current_depth >= max_depth:
                all_descendants: List['Node'] = []
                for child in node.children:
                    all_descendants.extend(collect_descendants(child))
                if all_descendants:
                    return Node(node.name, *all_descendants, attrs=node.attrs)
                return node

            new_children = [flatten_node(child, current_depth + 1) for child in node.children]
            if new_children:
                return Node(node.name, *new_children, attrs=node.attrs)
            return node

        return flatten_node(self, 0)

    def select(
        self,
        selector: Union[str, Callable[['Node'], bool], 'Selector']
    ) -> Iterator['Node']:
        """
        Select nodes matching selector (returns iterator).

        Uses cursor id-membership for position-aware Selectors.

        Args:
            selector: Nodes to select (predicate, exact name (str), or Selector)

        Returns:
            Iterator of matching nodes
        """
        if hasattr(selector, 'matches_at'):
            from .cursor import Cursor, walk_cursors
            return (c.node for c in walk_cursors(Cursor(self))
                    if selector.matches_at(c))
        predicate = _make_predicate_fn(selector)
        return (node for node in self.walk() if predicate(node))

    def locate(
        self,
        selector: Union[str, Callable[['Node'], bool], 'Selector']
    ) -> Optional['Cursor']:
        """
        Return a Cursor at the first node matching selector, or None.

        Args:
            selector: Match criterion (predicate, exact name (str), or Selector)

        Returns:
            Cursor at matching position, or None
        """
        from .cursor import Cursor, walk_cursors
        for cursor in walk_cursors(Cursor(self)):
            if self._cursor_matches(cursor, selector):
                return cursor
        return None

    def cursors_at(
        self,
        selector: Union[str, Callable[['Node'], bool], 'Selector']
    ) -> List['Cursor']:
        """
        Return a Cursor at every node matching selector.

        Args:
            selector: Match criterion (predicate, exact name (str), or Selector)

        Returns:
            List of Cursors at matching positions
        """
        from .cursor import Cursor, walk_cursors
        return [c for c in walk_cursors(Cursor(self))
                if self._cursor_matches(c, selector)]

    @staticmethod
    def _cursor_matches(cursor: 'Cursor', selector) -> bool:
        """Check if cursor matches selector (position-aware)."""
        if hasattr(selector, 'matches_at'):
            return selector.matches_at(cursor)
        return _make_predicate_fn(selector)(cursor.node)

    def exists(
        self,
        selector: Union[str, Callable[['Node'], bool], 'Selector']
    ) -> bool:
        """
        Check if any node matches selector.

        Args:
            selector: Match criterion

        Returns:
            True if at least one node matches
        """
        return self.find(selector) is not None

    def count(
        self,
        selector: Optional[Union[str, Callable[['Node'], bool], 'Selector']] = None
    ) -> int:
        """
        Count nodes matching selector (or all nodes if None).

        Args:
            selector: Match criterion, or None to count all nodes

        Returns:
            Number of matching nodes
        """
        if selector is None:
            return self.size
        return len(self.find_all(selector))

    def get_path(self, path: str, delimiter: str = '/') -> Optional['Node']:
        """
        Get node at path (e.g., 'root/child/grandchild').

        Args:
            path: Path string
            delimiter: Path delimiter (default: '/')

        Returns:
            Node at path, or None if not found
        """
        parts = path.split(delimiter)
        current: 'Node' = self

        for part in parts:
            if part == current.name:
                continue

            found = False
            for child in current.children:
                if child.name == part:
                    current = child
                    found = True
                    break

            if not found:
                return None

        return current

    def paths(self, to_leaves_only: bool = True, delimiter: str = '/') -> List[str]:
        """
        Get all paths in this tree.

        Args:
            to_leaves_only: If True, only return paths to leaves
            delimiter: Path segment separator (default: '/')

        Returns:
            List of path strings joined by delimiter
        """
        from .cursor import Cursor, walk_cursors
        result = []
        for cursor in walk_cursors(Cursor(self)):
            if to_leaves_only and cursor.node.children:
                continue
            result.append(delimiter.join(cursor.path))
        return result

    def to_paths(self, delimiter: str = '/') -> List[str]:
        """Export tree as list of paths (all nodes, not just leaves)."""
        return self.paths(to_leaves_only=False, delimiter=delimiter)

    def nodes(self) -> List['Node']:
        """Get all nodes as a list (preorder)."""
        return list(self.walk())

    def update_attrs(self, **kw) -> 'Node':
        """
        Return new node with updated attributes (named helper for with_attrs).

        This is an alias of with_attrs, provided as a named convenience for
        the common attr-delta pattern.

        Args:
            **kw: Attribute key-value pairs to add/update

        Returns:
            New node with updated attributes
        """
        return self.with_attrs(**kw)

    def __or__(self, transformer: Callable[['Node'], Any]) -> Any:
        """Pipe node through transformer with | operator."""
        return transformer(self)

    def __rshift__(self, transformer: Callable[['Node'], Any]) -> Any:
        """Transform node with >> operator (can change type)."""
        return transformer(self)

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
