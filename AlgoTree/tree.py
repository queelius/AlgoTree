"""
Tree wrapper providing functional operations and consistent API.

This module provides a clean, composable API for tree manipulation
following functional programming principles.
"""

from typing import Any, Callable, Iterator, Optional, Union, TypeVar, List, Dict, TYPE_CHECKING
from functools import reduce
from .node import Node

if TYPE_CHECKING:
    from .selectors import Selector

T = TypeVar('T')
TreeType = TypeVar('TreeType', bound='Tree')


class Tree:
    """
    Immutable tree wrapper with fluent, composable API.

    All operations return new Tree instances, enabling chaining.
    The tree itself is never mutated.
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
        """
        def build_node(d: Dict[str, Any]) -> Node:
            children_data = d.pop(children_key, [])
            name = d.pop('name', 'node')

            children = [build_node(child) for child in children_data]
            return Node(name, *children, attrs=d)

        return cls(build_node(data))

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
        if not paths:
            return cls(Node('root'))

        # Build tree structure using dict
        tree_dict = {}

        for path in paths:
            parts = [p for p in path.split(delimiter) if p]
            if not parts:
                continue

            # Build nested dict structure
            current = tree_dict
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]

        # Convert dict to Node tree
        def dict_to_node(name: str, children_dict: dict) -> Node:
            if not children_dict:
                return Node(name)

            children = [
                dict_to_node(child_name, child_dict)
                for child_name, child_dict in sorted(children_dict.items())
            ]
            return Node(name, *children)

        # Get root name (first part of first path)
        root_name = paths[0].split(delimiter)[0] if paths else 'root'

        # If root_name is in tree_dict, use it as root
        if root_name in tree_dict:
            root = dict_to_node(root_name, tree_dict[root_name])
        else:
            # Otherwise create root with all top-level entries as children
            children = [
                dict_to_node(name, children_dict)
                for name, children_dict in sorted(tree_dict.items())
            ]
            root = Node(root_name, *children)

        return cls(root)

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
        Filter tree to nodes matching predicate.

        Preserves tree structure - keeps ancestors of matching nodes.

        Args:
            predicate: Function that returns True for nodes to keep

        Returns:
            New filtered tree
        """
        filtered = self._root.filter(predicate)
        if filtered is None:
            # Return empty tree if nothing matches
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
        nodes = self._root.walk(order)
        return reduce(fn, nodes, initial)

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
        def fold_node(node: Node) -> T:
            child_results = [fold_node(child) for child in node.children]
            return fn(node, child_results)

        return fold_node(self._root)

    # Tree structure operations

    def prune(self, selector: Union[str, Callable[[Node], bool]]) -> 'Tree':
        """
        Remove nodes matching selector.

        Args:
            selector: Node selector (string pattern or predicate)

        Returns:
            New tree with nodes pruned
        """
        return self.filter(lambda n: not self._matches(n, selector))

    def graft(
        self,
        selector: Union[str, Callable[[Node], bool]],
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
        if isinstance(subtree, Tree):
            subtree = subtree.root

        def add_subtree(node: Node) -> Node:
            if self._matches(node, selector):
                return node.with_child(subtree)
            return node

        return Tree(self._root.map(add_subtree))

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
        def collect_descendants(node: Node) -> List[Node]:
            """Collect all descendants as leaf nodes (no children)."""
            if not node.children:
                return [Node(node.name, attrs=node.attrs)]
            result = []
            for child in node.children:
                result.extend(collect_descendants(child))
            return result

        def flatten_node(node: Node, current_depth: int = 0) -> Node:
            if max_depth is not None and current_depth >= max_depth:
                # At max depth, collect all descendants as direct children
                all_descendants = []
                for child in node.children:
                    all_descendants.extend(collect_descendants(child))
                if all_descendants:
                    return Node(node.name, *all_descendants, attrs=node.attrs)
                return node

            # Not at max depth yet, recursively flatten children
            new_children = [flatten_node(child, current_depth + 1) for child in node.children]
            if new_children:
                return Node(node.name, *new_children, attrs=node.attrs)
            return node

        return Tree(flatten_node(self._root, 0))

    # Query operations

    def find(self, selector: Union[str, Callable[[Node], bool]]) -> Optional[Node]:
        """Find first node matching selector."""
        return self._root.find(selector)

    def find_all(self, selector: Union[str, Callable[[Node], bool]]) -> List[Node]:
        """Find all nodes matching selector."""
        return self._root.find_all(selector)

    def exists(self, selector: Union[str, Callable[[Node], bool]]) -> bool:
        """Check if any node matches selector."""
        return self.find(selector) is not None

    def count(self, selector: Optional[Union[str, Callable[[Node], bool]]] = None) -> int:
        """Count nodes matching selector (or all nodes if None)."""
        if selector is None:
            return self._root.size
        return len(self.find_all(selector))

    def select(self, selector: Union[str, Callable[[Node], bool]]) -> Iterator[Node]:
        """Select nodes matching selector (returns iterator)."""
        predicate = self._make_predicate(selector)
        return (node for node in self._root.walk() if predicate(node))

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
        parts = path.split(delimiter)
        current = self._root

        for part in parts:
            if part == current.name:
                continue  # Skip if it's the current node

            found = False
            for child in current.children:
                if child.name == part:
                    current = child
                    found = True
                    break

            if not found:
                return None

        return current

    def paths(self, to_leaves_only: bool = True) -> List[str]:
        """
        Get all paths in tree.

        Args:
            to_leaves_only: If True, only return paths to leaves

        Returns:
            List of path strings
        """
        paths = []

        if to_leaves_only:
            for leaf in self._root.leaves():
                paths.append(leaf.path)
        else:
            for node in self._root.walk():
                paths.append(node.path)

        return paths

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
        return list(self.walk())

    # Export operations

    def to_dict(self, children_key: str = 'children') -> Dict[str, Any]:
        """
        Export tree to nested dictionary.

        Args:
            children_key: Key name for children list

        Returns:
            Nested dictionary representation
        """
        def node_to_dict(node: Node) -> Dict[str, Any]:
            d = {'name': node.name, **node.attrs}

            if node.children:
                d[children_key] = [node_to_dict(child) for child in node.children]

            return d

        return node_to_dict(self._root)

    def to_paths(self, delimiter: str = '/') -> List[str]:
        """Export tree as list of paths."""
        return self.paths(to_leaves_only=False)

    # Operators for composition

    def __or__(self, transformer: Callable[['Tree'], 'Tree']) -> 'Tree':
        """Pipe tree through transformer with | operator."""
        return transformer(self)

    def __rshift__(self, transformer: Callable[['Tree'], Any]) -> Any:
        """Transform tree with >> operator (can change type)."""
        return transformer(self)

    # Helper methods

    def _matches(self, node: Node, selector: Union[str, Callable[[Node], bool], 'Selector']) -> bool:
        """Check if node matches selector."""
        # Check if it's a Selector object (has matches method)
        if hasattr(selector, 'matches'):
            return selector.matches(node)

        if callable(selector):
            return selector(node)

        return node.name == selector or (
            '*' in selector and self._wildcard_match(node.name, selector)
        )

    def _wildcard_match(self, name: str, pattern: str) -> bool:
        """Simple wildcard matching."""
        import fnmatch
        return fnmatch.fnmatch(name, pattern)

    def _make_predicate(
        self,
        selector: Union[str, Callable[[Node], bool], 'Selector']
    ) -> Callable[[Node], bool]:
        """Convert selector to predicate function."""
        # Check if it's a Selector object (has matches method)
        if hasattr(selector, 'matches'):
            return selector.matches

        if callable(selector):
            return selector

        return lambda node: self._matches(node, selector)

    # String representations

    def __repr__(self) -> str:
        """String representation."""
        return f"Tree(root={self._root.name!r}, size={self.size})"

    def __str__(self) -> str:
        """Pretty string representation."""
        return self._simple_tree_str()

    def _simple_tree_str(self) -> str:
        """Generate simple ASCII tree representation."""
        lines = []

        def add_node(node: Node, prefix: str = '', is_last: bool = True):
            # Add current node
            connector = '└── ' if is_last else '├── '
            lines.append(prefix + connector + node.name)

            # Add children
            if node.children:
                extension = '    ' if is_last else '│   '
                for i, child in enumerate(node.children):
                    is_last_child = i == len(node.children) - 1
                    add_node(child, prefix + extension, is_last_child)

        # Start with root
        lines.append(self._root.name)
        for i, child in enumerate(self._root.children):
            is_last = i == len(self._root.children) - 1
            add_node(child, '', is_last)

        return '\n'.join(lines)
