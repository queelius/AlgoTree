"""
Core abstractions for the AlgoTree shell.

This module provides the foundational classes for managing forests of trees,
parsing paths, and maintaining navigation state.
"""

from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, replace
import re

from AlgoTree.node import Node
from AlgoTree.tree import Tree


class Forest:
    """
    A collection of named trees.

    Immutable container that holds multiple trees, each identified by a unique name.
    All operations return new Forest instances.

    Examples:
        >>> from AlgoTree import node
        >>> f = Forest()
        >>> f = f.set("my_tree", node("root", "child1", "child2"))
        >>> tree = f.get("my_tree")
        >>> f.tree_names()
        ['my_tree']
    """

    def __init__(self, trees: Optional[Dict[str, Union[Node, Tree]]] = None):
        """
        Initialize a forest with optional trees.

        Args:
            trees: Dictionary mapping tree names to Node or Tree instances
        """
        self._trees: Dict[str, Tree] = {}
        if trees:
            for name, tree in trees.items():
                self._trees[name] = tree if isinstance(tree, Tree) else Tree(tree)

    def get(self, name: str) -> Optional[Tree]:
        """
        Get a tree by name.

        Args:
            name: The tree name

        Returns:
            The Tree instance, or None if not found
        """
        return self._trees.get(name)

    def set(self, name: str, tree: Union[Node, Tree]) -> 'Forest':
        """
        Add or replace a tree in the forest.

        Args:
            name: The tree name
            tree: Node or Tree instance

        Returns:
            New Forest with the tree added/replaced
        """
        new_trees = self._trees.copy()
        new_trees[name] = tree if isinstance(tree, Tree) else Tree(tree)
        return Forest(new_trees)

    def remove(self, name: str) -> 'Forest':
        """
        Remove a tree from the forest.

        Args:
            name: The tree name

        Returns:
            New Forest with the tree removed
        """
        if name not in self._trees:
            raise KeyError(f"Tree '{name}' not found")
        new_trees = self._trees.copy()
        del new_trees[name]
        return Forest(new_trees)

    def tree_names(self) -> List[str]:
        """
        Get all tree names in the forest.

        Returns:
            Sorted list of tree names
        """
        return sorted(self._trees.keys())

    def __contains__(self, name: str) -> bool:
        """Check if a tree name exists in the forest."""
        return name in self._trees

    def __len__(self) -> int:
        """Get the number of trees in the forest."""
        return len(self._trees)

    def __repr__(self) -> str:
        """String representation of the forest."""
        return f"Forest(trees={self.tree_names()})"


@dataclass(frozen=True)
class TreePath:
    """
    Represents an absolute or relative path within a forest.

    Paths have the format:
    - Absolute: /tree_name/node1/node2/...
    - Relative: node1/node2/... or ./node1 or ../sibling
    - Forest root: /

    Special path components:
    - . : current node
    - .. : parent node
    - [N] : Nth child (0-indexed)
    - @id:value : node with specific ID in metadata

    Examples:
        >>> TreePath.parse("/my_tree")
        TreePath(tree_name='my_tree', components=[], is_absolute=True)

        >>> TreePath.parse("/my_tree/child1/child2")
        TreePath(tree_name='my_tree', components=['child1', 'child2'], is_absolute=True)

        >>> TreePath.parse("child/grandchild")
        TreePath(tree_name=None, components=['child', 'grandchild'], is_absolute=False)
    """

    tree_name: Optional[str]
    components: Tuple[str, ...]
    is_absolute: bool

    @classmethod
    def parse(cls, path: str) -> 'TreePath':
        """
        Parse a path string into a TreePath.

        Args:
            path: Path string (e.g., "/tree/child1/child2" or "child/grandchild")

        Returns:
            TreePath instance

        Raises:
            ValueError: If path format is invalid
        """
        if not path:
            raise ValueError("Path cannot be empty")

        # Normalize slashes
        path = path.strip()

        # Check if absolute
        is_absolute = path.startswith('/')

        # Handle forest root
        if path == '/':
            return cls(tree_name=None, components=tuple(), is_absolute=True)

        # Remove leading slash for processing
        if is_absolute:
            path = path[1:]

        # Split into components
        parts = [p for p in path.split('/') if p and p != '.']

        if not parts:
            return cls(tree_name=None, components=tuple(), is_absolute=is_absolute)

        # Extract tree name if absolute
        tree_name = None
        if is_absolute:
            tree_name = parts[0]
            components = tuple(parts[1:])
        else:
            components = tuple(parts)

        return cls(tree_name=tree_name, components=components, is_absolute=is_absolute)

    def join(self, *parts: str) -> 'TreePath':
        """
        Join additional path components.

        Args:
            parts: Path components to append

        Returns:
            New TreePath with components appended
        """
        new_components = list(self.components)
        for part in parts:
            if part and part != '.':
                new_components.append(part)

        return replace(self, components=tuple(new_components))

    def parent(self) -> Optional['TreePath']:
        """
        Get the parent path.

        Returns:
            TreePath to parent, or None if at root
        """
        if not self.components:
            if self.is_absolute and self.tree_name:
                # Tree root -> forest root
                return TreePath(tree_name=None, components=tuple(), is_absolute=True)
            return None

        return replace(self, components=self.components[:-1])

    def __str__(self) -> str:
        """String representation of the path."""
        if self.is_absolute:
            if not self.tree_name and not self.components:
                return '/'
            parts = [self.tree_name] if self.tree_name else []
            parts.extend(self.components)
            return '/' + '/'.join(parts)
        else:
            return '/'.join(self.components) if self.components else '.'

    def __repr__(self) -> str:
        return f"TreePath('{self}')"


class ShellContext:
    """
    Maintains navigation state and provides operations within a forest.

    The context tracks:
    - Current forest (collection of trees)
    - Current tree (if navigated into a tree)
    - Current node (if navigated within a tree)
    - Working directory path

    All operations return new ShellContext instances (immutable).

    Examples:
        >>> from AlgoTree import node
        >>> forest = Forest({"tree1": node("root", "child1", "child2")})
        >>> ctx = ShellContext(forest)
        >>> ctx.pwd()
        '/'
        >>> ctx2 = ctx.cd("tree1")
        >>> ctx2.pwd()
        '/tree1'
    """

    def __init__(
        self,
        forest: Forest,
        current_tree: Optional[str] = None,
        current_path: Optional[List[str]] = None
    ):
        """
        Initialize shell context.

        Args:
            forest: The forest to operate on
            current_tree: Name of current tree (None = forest root)
            current_path: Path components within current tree
        """
        self._forest = forest
        self._current_tree = current_tree
        self._current_path = current_path or []

    @property
    def forest(self) -> Forest:
        """Get the current forest."""
        return self._forest

    @property
    def current_tree_name(self) -> Optional[str]:
        """Get the name of the current tree."""
        return self._current_tree

    @property
    def current_tree(self) -> Optional[Tree]:
        """Get the current tree object."""
        if not self._current_tree:
            return None
        return self._forest.get(self._current_tree)

    @property
    def current_node(self) -> Optional[Node]:
        """
        Get the current node within the tree.

        Returns:
            Current Node, or None if at forest root or tree root
        """
        tree = self.current_tree
        if not tree:
            return None

        if not self._current_path:
            return tree.root

        # Navigate to current path
        node = tree.root
        for component in self._current_path:
            # Handle indexed access: child[0], child[1], etc.
            match = re.match(r'^(.+)\[(\d+)\]$', component)
            if match:
                name, index = match.groups()
                matching = [c for c in node.children if c.name == name]
                idx = int(index)
                if idx >= len(matching):
                    return None
                node = matching[idx]
            else:
                # Find child by name
                child = next((c for c in node.children if c.name == component), None)
                if not child:
                    return None
                node = child

        return node

    def pwd(self) -> str:
        """
        Get current working directory path.

        Returns:
            Absolute path string
        """
        if not self._current_tree:
            return '/'

        if not self._current_path:
            return f'/{self._current_tree}'

        return f'/{self._current_tree}/{"/".join(self._current_path)}'

    def cd(self, path: str) -> 'ShellContext':
        """
        Change directory to the specified path.

        Args:
            path: Absolute or relative path

        Returns:
            New ShellContext at the target location

        Raises:
            ValueError: If path is invalid or doesn't exist
        """
        tree_path = TreePath.parse(path)

        # Handle absolute paths
        if tree_path.is_absolute:
            # Navigate to forest root
            if not tree_path.tree_name:
                return ShellContext(self._forest)

            # Navigate to tree
            if tree_path.tree_name not in self._forest:
                raise ValueError(f"Tree '{tree_path.tree_name}' not found")

            # Verify path exists
            new_ctx = ShellContext(self._forest, tree_path.tree_name, list(tree_path.components))
            if tree_path.components and new_ctx.current_node is None:
                raise ValueError(f"Path not found: {path}")

            return new_ctx

        # Handle relative paths
        if not self._current_tree:
            # At forest root, can only cd into a tree
            if len(tree_path.components) == 1:
                tree_name = tree_path.components[0]
                if tree_name not in self._forest:
                    raise ValueError(f"Tree '{tree_name}' not found")
                return ShellContext(self._forest, tree_name, [])
            else:
                raise ValueError("Cannot use relative path with multiple components at forest root")

        # Within a tree, navigate relative to current path
        new_path = list(self._current_path)

        for component in tree_path.components:
            if component == '..':
                if new_path:
                    new_path.pop()
                else:
                    # At tree root, go to forest root
                    return ShellContext(self._forest)
            else:
                new_path.append(component)

        # Verify path exists
        new_ctx = ShellContext(self._forest, self._current_tree, new_path)
        if new_path and new_ctx.current_node is None:
            raise ValueError(f"Path not found: {path}")

        return new_ctx

    def resolve_path(self, path: str) -> Tuple[Optional[str], Optional[Node]]:
        """
        Resolve a path to a tree name and node.

        Args:
            path: Absolute or relative path

        Returns:
            Tuple of (tree_name, node) or (None, None) if not found
        """
        try:
            ctx = self.cd(path)
            return ctx._current_tree, ctx.current_node
        except ValueError:
            return None, None

    def update_forest(self, forest: Forest) -> 'ShellContext':
        """
        Update the forest while maintaining current position if possible.

        Args:
            forest: New forest

        Returns:
            New ShellContext with updated forest
        """
        # Check if current tree still exists
        if self._current_tree and self._current_tree not in forest:
            # Tree was removed, go to forest root
            return ShellContext(forest)

        return ShellContext(forest, self._current_tree, self._current_path)

    def __repr__(self) -> str:
        return f"ShellContext(pwd='{self.pwd()}')"
