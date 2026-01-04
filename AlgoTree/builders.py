"""
Fluent builder API for constructing trees.

This module provides an elegant, chainable API for building trees
with a focus on clarity and ease of use.
"""

from typing import Any, Optional, Union, List, Dict, Callable
from contextlib import contextmanager
from .node import Node
from .tree import Tree


class TreeBuilder:
    """
    Fluent builder for constructing trees.

    Example:
        tree = (
            TreeBuilder('root')
            .attr(type='directory')
            .child('src',
                TreeBuilder('main.py', type='file', size=1024),
                TreeBuilder('utils.py', type='file', size=512)
            )
            .child('docs',
                TreeBuilder('README.md', type='file')
            )
            .build()
        )
    """

    def __init__(self, name: str, **attrs):
        """
        Initialize builder with root node.

        Args:
            name: Node name
            **attrs: Initial attributes
        """
        self._name = name
        self._attrs = attrs
        self._children: List[Union['TreeBuilder', Node]] = []
        self._parent: Optional['TreeBuilder'] = None

    def attr(self, **attrs) -> 'TreeBuilder':
        """
        Add or update attributes.

        Args:
            **attrs: Attributes to add/update

        Returns:
            Self for chaining
        """
        self._attrs.update(attrs)
        return self

    def attrs(self, attrs: Dict[str, Any]) -> 'TreeBuilder':
        """
        Set attributes from dictionary.

        Args:
            attrs: Dictionary of attributes

        Returns:
            Self for chaining
        """
        self._attrs.update(attrs)
        return self

    def child(
        self,
        name_or_builder: Union[str, 'TreeBuilder', Node],
        *children: Union['TreeBuilder', Node],
        **attrs
    ) -> 'TreeBuilder':
        """
        Add child node(s).

        Args:
            name_or_builder: Child name, builder, or node
            *children: Additional children (if first arg is name)
            **attrs: Attributes (if first arg is name)

        Returns:
            Self for chaining
        """
        if isinstance(name_or_builder, str):
            # Create new child builder
            child_builder = TreeBuilder(name_or_builder, **attrs)
            child_builder._parent = self
            self._children.append(child_builder)

            # Add any additional children to the new child
            for extra_child in children:
                if isinstance(extra_child, (TreeBuilder, Node)):
                    child_builder._children.append(extra_child)
        else:
            # Add existing builder or node
            self._children.append(name_or_builder)
            # Add any additional children
            self._children.extend(children)

        return self

    def children(self, *children: Union[str, 'TreeBuilder', Node]) -> 'TreeBuilder':
        """
        Add multiple children.

        Args:
            *children: Children to add (names, builders, or nodes)

        Returns:
            Self for chaining
        """
        for child in children:
            if isinstance(child, str):
                self.child(child)
            else:
                self._children.append(child)
        return self

    def up(self) -> 'TreeBuilder':
        """
        Move up to parent builder.

        Returns:
            Parent builder (or self if root)
        """
        return self._parent if self._parent else self

    def root(self) -> 'TreeBuilder':
        """
        Move to root builder.

        Returns:
            Root builder
        """
        current = self
        while current._parent:
            current = current._parent
        return current

    def build(self) -> Tree:
        """
        Build the tree.

        Returns:
            Constructed Tree object
        """
        # Move to root first
        root_builder = self.root()
        root_node = root_builder._build_node()
        return Tree(root_node)

    def build_node(self) -> Node:
        """
        Build just the node (not wrapped in Tree).

        Returns:
            Constructed Node object
        """
        return self._build_node()

    def _build_node(self) -> Node:
        """Internal method to recursively build nodes."""
        # Build children
        children = []
        for child in self._children:
            if isinstance(child, TreeBuilder):
                children.append(child._build_node())
            elif isinstance(child, Node):
                children.append(child)
            else:
                # Assume it's a string name
                children.append(Node(str(child)))

        # Create node
        return Node(self._name, *children, attrs=self._attrs)

    # Context manager support for nested structure

    def __enter__(self) -> 'TreeBuilder':
        """Enter context (for with statement)."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        pass

    # Operator overloading for more fluent syntax

    def __lshift__(self, child: Union[str, 'TreeBuilder', Node]) -> 'TreeBuilder':
        """
        Add child using << operator.

        Example:
            builder << 'child1' << 'child2'
        """
        return self.child(child)

    def __call__(self, **attrs) -> 'TreeBuilder':
        """
        Add attributes using call syntax.

        Example:
            builder(type='file', size=1024)
        """
        return self.attr(**attrs)

    def __repr__(self) -> str:
        return f"TreeBuilder({self._name!r}, attrs={self._attrs}, children={len(self._children)})"


class FluentTree:
    """
    Fluent wrapper around Tree for chainable operations.

    This provides a more fluent API where every operation returns
    a FluentTree for continued chaining.
    """

    def __init__(self, tree: Union[Tree, Node, str]):
        """
        Initialize fluent wrapper.

        Args:
            tree: Tree, Node, or name for root
        """
        if isinstance(tree, Tree):
            self._tree = tree
        elif isinstance(tree, Node):
            self._tree = Tree(tree)
        else:
            self._tree = Tree(Node(str(tree)))

    @property
    def tree(self) -> Tree:
        """Get underlying tree."""
        return self._tree

    @property
    def root(self) -> Node:
        """Get root node."""
        return self._tree.root

    # Chainable operations

    def map(self, fn: Callable[[Node], Union[Node, Dict[str, Any]]]) -> 'FluentTree':
        """Map function over nodes."""
        return FluentTree(self._tree.map(fn))

    def filter(self, predicate: Callable[[Node], bool]) -> 'FluentTree':
        """Filter nodes."""
        return FluentTree(self._tree.filter(predicate))

    def prune(self, selector: Union[str, Callable[[Node], bool]]) -> 'FluentTree':
        """Prune nodes."""
        return FluentTree(self._tree.prune(selector))

    def graft(
        self,
        selector: Union[str, Callable[[Node], bool]],
        subtree: Union[Node, Tree]
    ) -> 'FluentTree':
        """Graft subtree."""
        return FluentTree(self._tree.graft(selector, subtree))

    def flatten(self, max_depth: Optional[int] = None) -> 'FluentTree':
        """Flatten tree."""
        return FluentTree(self._tree.flatten(max_depth))

    def transform(self, transformer: Callable[[Tree], Tree]) -> 'FluentTree':
        """Apply custom transformation."""
        return FluentTree(transformer(self._tree))

    # Terminal operations (don't return FluentTree)

    def find(self, selector: Union[str, Callable[[Node], bool]]) -> Optional[Node]:
        """Find first matching node."""
        return self._tree.find(selector)

    def find_all(self, selector: Union[str, Callable[[Node], bool]]) -> List[Node]:
        """Find all matching nodes."""
        return self._tree.find_all(selector)

    def reduce(self, fn: Callable[[Any, Node], Any], initial: Any) -> Any:
        """Reduce to single value."""
        return self._tree.reduce(fn, initial)

    def fold(self, fn: Callable[[Node, List[Any]], Any]) -> Any:
        """Fold bottom-up."""
        return self._tree.fold(fn)

    def to_dict(self, children_key: str = 'children') -> Dict[str, Any]:
        """Export to dictionary."""
        return self._tree.to_dict(children_key)

    def to_paths(self) -> List[str]:
        """Export to paths."""
        return self._tree.to_paths()

    # Operator overloading

    def __or__(self, transformer: Callable[[Tree], Tree]) -> 'FluentTree':
        """Pipe through transformer with | operator."""
        return FluentTree(transformer(self._tree))

    def __rshift__(self, transformer: Callable[[Tree], Any]) -> Any:
        """Transform with >> operator (can change type)."""
        return transformer(self._tree)

    def __repr__(self) -> str:
        return f"FluentTree({repr(self._tree)})"

    def __str__(self) -> str:
        return str(self._tree)


# DSL-style builder functions

def tree(name: str, *children, **attrs) -> TreeBuilder:
    """
    Create tree builder with DSL-style syntax.

    Example:
        my_tree = tree('root',
            tree('child1', type='leaf'),
            tree('child2',
                tree('grandchild1'),
                tree('grandchild2')
            )
        ).build()
    """
    builder = TreeBuilder(name, **attrs)
    for child in children:
        if isinstance(child, TreeBuilder):
            builder._children.append(child)
        elif isinstance(child, Node):
            builder._children.append(child)
        elif isinstance(child, str):
            builder.child(child)
    return builder


def branch(name: str, *children, **attrs) -> TreeBuilder:
    """Alias for tree() - creates a branch with children."""
    return tree(name, *children, **attrs)


def leaf(name: str, **attrs) -> TreeBuilder:
    """Create a leaf node (no children)."""
    return TreeBuilder(name, **attrs)


# Context manager for building trees

class ChildContext:
    """
    Helper context returned by TreeContext.child() for nested building.
    """

    def __init__(self, tree_context: 'TreeContext', builder: TreeBuilder):
        self._tree_context = tree_context
        self._builder = builder

    @contextmanager
    def child(self, name: str, **attrs):
        """Add nested child in context."""
        child_builder = TreeBuilder(name, **attrs)
        self._builder._children.append(child_builder)
        child_builder._parent = self._builder

        self._tree_context._stack.append(child_builder)
        try:
            yield ChildContext(self._tree_context, child_builder)
        finally:
            self._tree_context._stack.pop()

    def add_child(self, name: str, **attrs) -> 'ChildContext':
        """Add a leaf child directly (without context manager)."""
        child_builder = TreeBuilder(name, **attrs)
        self._builder._children.append(child_builder)
        child_builder._parent = self._builder
        return ChildContext(self._tree_context, child_builder)


class TreeContext:
    """
    Context manager for building trees with indented syntax.

    Example:
        with TreeContext('root') as ctx:
            with ctx.child('src') as src:
                with src.child('main.py', type='file'):
                    pass
                with src.child('utils.py', type='file'):
                    pass
            with ctx.child('docs') as docs:
                with docs.child('README.md', type='file'):
                    pass

        tree = ctx.build()
    """

    def __init__(self, name: str, **attrs):
        self.builder = TreeBuilder(name, **attrs)
        self._stack = [self.builder]

    @contextmanager
    def child(self, name: str, **attrs):
        """Add child in context."""
        child_builder = TreeBuilder(name, **attrs)
        self._current._children.append(child_builder)
        child_builder._parent = self._current

        self._stack.append(child_builder)
        try:
            yield ChildContext(self, child_builder)
        finally:
            self._stack.pop()

    @property
    def _current(self) -> TreeBuilder:
        """Get current builder in stack."""
        return self._stack[-1]

    def build(self) -> Tree:
        """Build the tree."""
        return self.builder.build()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# Quick builder for simple trees

class QuickBuilder:
    """
    Quick builder for simple tree structures using method chaining.

    Example:
        tree = (
            QuickBuilder()
            .root('app')
            .add('src/main.py', type='file')
            .add('src/utils.py', type='file')
            .add('docs/README.md', type='file')
            .add('tests/test_main.py', type='file')
            .build()
        )
    """

    def __init__(self):
        self._root: Optional[TreeBuilder] = None
        self._paths: List[tuple[str, Dict[str, Any]]] = []

    def root(self, name: str, **attrs) -> 'QuickBuilder':
        """Set root node."""
        self._root = TreeBuilder(name, **attrs)
        return self

    def add(self, path: str, **attrs) -> 'QuickBuilder':
        """Add node at path."""
        self._paths.append((path, attrs))
        return self

    def build(self, delimiter: str = '/') -> Tree:
        """Build tree from paths."""
        if not self._root:
            self._root = TreeBuilder('root')

        # Build tree from paths
        for path, attrs in self._paths:
            parts = path.split(delimiter)
            current = self._root

            # Navigate/create path
            for i, part in enumerate(parts):
                # Find or create child
                found = False
                for child in current._children:
                    if isinstance(child, TreeBuilder) and child._name == part:
                        current = child
                        found = True
                        break

                if not found:
                    # Create new child
                    new_child = TreeBuilder(part)
                    new_child._parent = current
                    current._children.append(new_child)
                    current = new_child

                # Add attributes to leaf
                if i == len(parts) - 1:
                    current._attrs.update(attrs)

        return self._root.build()
