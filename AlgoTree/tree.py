"""
Tree wrapper providing functional operations and consistent API.

This module provides a clean, composable API for tree manipulation
following functional programming principles.

Tree is a thin forwarder over Node: every method body delegates to the
corresponding Node method and wraps the result back into a Tree where the
old API returned a Tree.  All traversal and transformation logic lives in
Node; this class adds only the empty-sentinel convention and the
Node|dict|None sniffing in map().
"""

from typing import Any, Callable, Iterator, Optional, Union, TypeVar, List, Dict, TYPE_CHECKING
from .node import Node

if TYPE_CHECKING:
    from .selectors import Selector
    from .cursor import Cursor

T = TypeVar('T')
TreeType = TypeVar('TreeType', bound='Tree')


class Tree:
    """
    Immutable tree wrapper with fluent, composable API.

    All operations return new Tree instances, enabling chaining.
    The tree itself is never mutated.

    Tree is a thin forwarder: all logic resides in Node.  The only
    Tree-specific concerns are:
      - the ``<empty>`` sentinel for filter/prune results,
      - the Node|dict|None runtime sniffing in map() for back-compat.
    """

    __slots__ = ('_root',)

    def __init__(self, root: Union[Node, str]):
        """
        Initialize tree with root node.

        Args:
            root: Root node or name for new root
        """
        if isinstance(root, str):
            self._root = Node(root)
        else:
            self._root = root

    @property
    def root(self) -> Node:
        """Get root node (immutable)."""
        return self._root

    # Factory methods

    @classmethod
    def from_dict(cls, data: Dict[str, Any], children_key: str = 'children') -> 'Tree':
        """
        Create tree from nested dictionary.

        Args:
            data: Dictionary with 'name' and optional children
            children_key: Key name for children list

        Example:
            tree = Tree.from_dict({
                'name': 'root',
                'value': 1,
                'children': [
                    {'name': 'child1', 'value': 2},
                    {'name': 'child2', 'value': 3}
                ]
            })

        Note:
            Uses Node.from_dict internally (non-mutating).  The old
            Tree.from_dict mutated the input dict via pop(); the new
            implementation does not.
        """
        import copy
        return cls(Node.from_dict(copy.deepcopy(data), children_key=children_key))

    @classmethod
    def from_paths(cls, paths: List[str], delimiter: str = '/') -> 'Tree':
        """
        Create tree from list of paths.

        Args:
            paths: List of path strings
            delimiter: Path delimiter

        Example:
            tree = Tree.from_paths([
                'root/a/b',
                'root/a/c',
                'root/d'
            ])
        """
        return cls(Node.from_paths(paths, delimiter=delimiter))

    # Core functional operations

    def map(self, fn: Callable[[Node], Union[Node, Dict[str, Any]]]) -> 'Tree':
        """
        Map function over all nodes.

        Args:
            fn: Function that takes a node and returns either:
                - A new node to replace it
                - A dict of attributes to update
                - None to keep node unchanged

        Returns:
            New tree with mapped values

        Note:
            The Node|dict|None sniffing is preserved here for back-compat;
            Node.map is strict (Node -> Node only).
        """
        def transform_node(node: Node) -> Node:
            result = fn(node)
            if result is None:
                return node
            elif isinstance(result, dict):
                return node.with_attrs(**result)
            elif isinstance(result, Node):
                return result
            else:
                return node

        return Tree(self._root.map(transform_node))

    def filter(self, predicate: Callable[[Node], bool]) -> 'Tree':
        """
        Filter tree to nodes matching predicate (or Selector).

        Preserves tree structure - keeps ancestors of matching nodes.
        Returns a Tree wrapping the ``<empty>`` sentinel when nothing matches.
        """
        filtered = self._root.filter(predicate)
        if filtered is None:
            return Tree(Node('<empty>'))
        return Tree(filtered)

    def reduce(
        self,
        fn: Callable[[T, Node], T],
        initial: T,
        order: str = 'preorder'
    ) -> T:
        """
        Reduce tree to single value.

        Args:
            fn: Reduction function (accumulator, node) -> new_accumulator
            initial: Initial accumulator value
            order: Traversal order ('preorder', 'postorder', 'levelorder')

        Returns:
            Final reduced value
        """
        return self._root.reduce(fn, initial, order=order)

    def fold(
        self,
        fn: Callable[[Node, List[T]], T]
    ) -> T:
        """
        Fold tree bottom-up, combining child results.

        Args:
            fn: Function (node, child_results) -> result

        Returns:
            Final folded value
        """
        return self._root.fold(fn)

    # Tree structure operations

    def prune(self, selector: Union[str, Callable[[Node], bool]]) -> 'Tree':
        """
        Remove nodes matching selector.
        """
        result = self._root.prune(selector)
        if result is None:
            return Tree(Node('<empty>'))
        return Tree(result)

    def graft(
        self,
        selector: Union[str, Callable[[Node], bool], 'Selector'],
        subtree: Union[Node, 'Tree']
    ) -> 'Tree':
        """
        Add subtree to nodes matching selector.

        Args:
            selector: Where to graft
            subtree: Tree or node to graft

        Returns:
            New tree with subtrees grafted
        """
        return Tree(self._root.graft(selector, subtree))

    def flatten(self, max_depth: Optional[int] = None) -> 'Tree':
        """
        Flatten tree to specified depth.

        Nodes beyond max_depth have their descendants moved up to become
        direct children of the node at max_depth.

        Args:
            max_depth: Maximum depth (None for complete flattening to root's children)

        Returns:
            New flattened tree
        """
        return Tree(self._root.flatten(max_depth=max_depth))

    # Query operations

    def find(self, selector: Union[str, Callable[[Node], bool]]) -> Optional[Node]:
        """Find first node matching selector."""
        return self._root.find(selector)

    def find_all(self, selector: Union[str, Callable[[Node], bool]]) -> List[Node]:
        """Find all nodes matching selector."""
        return self._root.find_all(selector)

    def exists(self, selector: Union[str, Callable[[Node], bool]]) -> bool:
        """Check if any node matches selector."""
        return self._root.exists(selector)

    def count(self, selector: Optional[Union[str, Callable[[Node], bool]]] = None) -> int:
        """Count nodes matching selector (or all nodes if None)."""
        return self._root.count(selector)

    def select(self, selector: Union[str, Callable[[Node], bool]]) -> Iterator[Node]:
        """Select nodes matching selector (returns iterator)."""
        return self._root.select(selector)

    def locate(self, selector: Union[str, Callable[[Node], bool]]) -> Optional['Cursor']:
        """Return a Cursor at the first node matching selector, or None."""
        return self._root.locate(selector)

    def cursors_at(self, selector: Union[str, Callable[[Node], bool]]) -> List['Cursor']:
        """Return a Cursor at every node matching selector."""
        return self._root.cursors_at(selector)

    @staticmethod
    def _cursor_matches(cursor: 'Cursor', selector) -> bool:
        return Node._cursor_matches(cursor, selector)

    # Path operations

    def get_path(self, path: str, delimiter: str = '/') -> Optional[Node]:
        """
        Get node at path.

        Args:
            path: Path string (e.g., 'root/child/grandchild')
            delimiter: Path delimiter

        Returns:
            Node at path or None
        """
        return self._root.get_path(path, delimiter=delimiter)

    def paths(self, to_leaves_only: bool = True, delimiter: str = '/') -> List[str]:
        """
        Get all paths in tree.

        Args:
            to_leaves_only: If True, only return paths to leaves
            delimiter: Path segment separator (default: '/')

        Returns:
            List of path strings joined by delimiter
        """
        return self._root.paths(to_leaves_only=to_leaves_only, delimiter=delimiter)

    # Tree properties

    @property
    def size(self) -> int:
        """Total number of nodes."""
        return self._root.size

    @property
    def height(self) -> int:
        """Height of tree."""
        return self._root.height

    @property
    def leaves(self) -> List[Node]:
        """Get all leaf nodes."""
        return list(self._root.leaves())

    @property
    def is_empty(self) -> bool:
        """Check if tree is empty."""
        return self._root.name == '<empty>' and not self._root.children

    # Iteration

    def walk(self, order: str = 'preorder') -> Iterator[Node]:
        """Walk tree in specified order."""
        return self._root.walk(order)

    def nodes(self) -> List[Node]:
        """Get all nodes as list."""
        return self._root.nodes()

    # Export operations

    def to_dict(self, children_key: str = 'children') -> Dict[str, Any]:
        """
        Export tree to nested dictionary.

        Args:
            children_key: Key name for children list

        Returns:
            Nested dictionary representation
        """
        return self._root.to_dict(children_key=children_key)

    def to_paths(self, delimiter: str = '/') -> List[str]:
        """Export tree as list of paths."""
        return self._root.to_paths(delimiter=delimiter)

    # Operators for composition

    def __or__(self, transformer: Callable[['Tree'], 'Tree']) -> 'Tree':
        """Pipe tree through transformer with | operator."""
        return transformer(self)

    def __rshift__(self, transformer: Callable[['Tree'], Any]) -> Any:
        """Transform tree with >> operator (can change type)."""
        return transformer(self)

    # String representations

    def __repr__(self) -> str:
        """String representation."""
        return f"Tree(root={self._root.name!r}, size={self.size})"

    def __str__(self) -> str:
        """Pretty string representation (Unicode box-drawing tree)."""
        from .render import render as _render
        return _render(self._root, "unicode")
