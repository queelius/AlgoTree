"""
Advanced tree operation and query commands.

This module contains commands for:
- Tree transformations (map, filter, select, prune)
- Tree queries (find, ancestors, descendants, leaves)
- Analysis commands (depth, height, size)
"""

from typing import List, Any, Callable
import re

from AlgoTree.node import Node
from AlgoTree.tree import Tree
from AlgoTree.shell.core import ShellContext
from AlgoTree.shell.commands import Command, CommandResult


# ============================================================================
# Query Commands
# ============================================================================

class FindCommand(Command):
    """Find nodes matching a pattern."""

    @property
    def name(self) -> str:
        return "find"

    @property
    def description(self) -> str:
        return "Find nodes matching a pattern"

    @property
    def usage(self) -> str:
        return "find <pattern> [-type {name,attr}]"

    def supports_piping(self) -> bool:
        return True

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: find <pattern>", context=context)

        pattern = args[0]
        search_type = "name"  # default

        # Parse options
        if "-type" in args:
            idx = args.index("-type")
            if idx + 1 < len(args):
                search_type = args[idx + 1]

        current = context.current_node
        if not current:
            return CommandResult.fail("Not in a tree", context=context)

        # Compile pattern as regex
        try:
            regex = re.compile(pattern)
        except re.error as e:
            return CommandResult.fail(f"Invalid regex: {e}", context=context)

        # Find matching nodes
        matches = []
        for node in current.walk("preorder"):
            if search_type == "name":
                if regex.search(node.name):
                    matches.append(node)
            elif search_type == "attr":
                # Search in attribute values
                for value in node.attrs.values():
                    if regex.search(str(value)):
                        matches.append(node)
                        break

        # Format output
        if not matches:
            return CommandResult.ok(output="", context=context)

        lines = [node.name for node in matches]
        output = '\n'.join(lines)

        return CommandResult.ok(output=output, context=context)


class AncestorsCommand(Command):
    """Show ancestors of current node."""

    @property
    def name(self) -> str:
        return "ancestors"

    @property
    def description(self) -> str:
        return "Show ancestors of current node"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        current = context.current_node
        if not current:
            return CommandResult.fail("Not in a tree", context=context)

        ancestors = list(current.ancestors())

        if not ancestors:
            return CommandResult.ok(output="(root node has no ancestors)", context=context)

        lines = [node.name for node in ancestors]
        output = '\n'.join(lines)

        return CommandResult.ok(output=output, context=context)


class DescendantsCommand(Command):
    """Show descendants of current node."""

    @property
    def name(self) -> str:
        return "descendants"

    @property
    def description(self) -> str:
        return "Show descendants of current node"

    @property
    def usage(self) -> str:
        return "descendants [-d depth]"

    def supports_piping(self) -> bool:
        return True

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        current = context.current_node
        if not current:
            return CommandResult.fail("Not in a tree", context=context)

        # Parse depth option
        max_depth = None
        if "-d" in args:
            idx = args.index("-d")
            if idx + 1 < len(args):
                try:
                    max_depth = int(args[idx + 1])
                except ValueError:
                    return CommandResult.fail("Invalid depth value", context=context)

        # Get descendants
        descendants = []
        for node in current.descendants():
            if max_depth is not None and node.depth - current.depth > max_depth:
                continue
            descendants.append(node)

        if not descendants:
            return CommandResult.ok(output="(no descendants)", context=context)

        lines = [node.name for node in descendants]
        output = '\n'.join(lines)

        return CommandResult.ok(output=output, context=context)


class LeavesCommand(Command):
    """Show all leaf nodes in subtree."""

    @property
    def name(self) -> str:
        return "leaves"

    @property
    def description(self) -> str:
        return "Show all leaf nodes in subtree"

    def supports_piping(self) -> bool:
        return True

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        current = context.current_node
        if not current:
            return CommandResult.fail("Not in a tree", context=context)

        leaves = list(current.leaves())

        if not leaves:
            return CommandResult.ok(output="(no leaves)", context=context)

        lines = [node.name for node in leaves]
        output = '\n'.join(lines)

        return CommandResult.ok(output=output, context=context)


class SiblingsCommand(Command):
    """Show sibling nodes."""

    @property
    def name(self) -> str:
        return "siblings"

    @property
    def description(self) -> str:
        return "Show sibling nodes"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        current = context.current_node
        if not current or current.is_root:
            return CommandResult.ok(output="(root node has no siblings)", context=context)

        parent = current.parent
        if not parent:
            return CommandResult.ok(output="(no parent)", context=context)

        siblings = [child for child in parent.children if child != current]

        if not siblings:
            return CommandResult.ok(output="(no siblings)", context=context)

        lines = [node.name for node in siblings]
        output = '\n'.join(lines)

        return CommandResult.ok(output=output, context=context)


# ============================================================================
# Analysis Commands
# ============================================================================

class DepthCommand(Command):
    """Show depth of current node."""

    @property
    def name(self) -> str:
        return "depth"

    @property
    def description(self) -> str:
        return "Show depth of current node"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        current = context.current_node
        if not current:
            return CommandResult.fail("Not in a tree", context=context)

        return CommandResult.ok(output=str(current.depth), context=context)


class HeightCommand(Command):
    """Show height of current subtree."""

    @property
    def name(self) -> str:
        return "height"

    @property
    def description(self) -> str:
        return "Show height of current subtree"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        current = context.current_node
        if not current:
            return CommandResult.fail("Not in a tree", context=context)

        return CommandResult.ok(output=str(current.height), context=context)


class SizeCommand(Command):
    """Count nodes in current subtree."""

    @property
    def name(self) -> str:
        return "size"

    @property
    def description(self) -> str:
        return "Count nodes in current subtree"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        current = context.current_node
        if not current:
            return CommandResult.fail("Not in a tree", context=context)

        size = 1 + len(list(current.descendants()))

        return CommandResult.ok(output=str(size), context=context)


# ============================================================================
# Tree Operation Commands
# ============================================================================

class SelectCommand(Command):
    """Select nodes matching a predicate."""

    @property
    def name(self) -> str:
        return "select"

    @property
    def description(self) -> str:
        return "Select nodes matching a predicate"

    @property
    def usage(self) -> str:
        return "select <expression>"

    def supports_piping(self) -> bool:
        return True

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: select <expression>", context=context)

        expr = ' '.join(args)

        current = context.current_node
        if not current:
            return CommandResult.fail("Not in a tree", context=context)

        # Create predicate function
        try:
            predicate = self._create_predicate(expr)
        except Exception as e:
            return CommandResult.fail(f"Invalid expression: {e}", context=context)

        # Find matching nodes
        matches = []
        for node in current.walk("preorder"):
            try:
                if predicate(node):
                    matches.append(node)
            except Exception:
                # Ignore errors in predicate evaluation
                pass

        # Format output
        if not matches:
            return CommandResult.ok(output="", context=context)

        lines = [node.name for node in matches]
        output = '\n'.join(lines)

        return CommandResult.ok(output=output, context=context)

    def _create_predicate(self, expr: str) -> Callable[[Node], bool]:
        """
        Create a predicate function from an expression.

        Supports:
        - n.name, n.depth, n.height, n.is_leaf, n.is_root
        - n.attrs, n.get(key)
        - Comparison operators: ==, !=, <, >, <=, >=
        - Logical operators: and, or, not
        """
        # Create safe globals/locals
        safe_globals = {
            '__builtins__': {
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
            }
        }

        def predicate(n: Node) -> bool:
            safe_locals = {
                'n': n,
                'node': n,
            }
            return eval(expr, safe_globals, safe_locals)

        return predicate


class MapCommand(Command):
    """Apply transformation to all nodes in subtree."""

    @property
    def name(self) -> str:
        return "map"

    @property
    def description(self) -> str:
        return "Apply transformation to all nodes"

    @property
    def usage(self) -> str:
        return "map <expression>"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: map <expression>", context=context)

        expr = ' '.join(args)

        if not context.current_tree_name:
            return CommandResult.fail("Not in a tree", context=context)

        current = context.current_node
        if not current:
            return CommandResult.fail("Invalid current location", context=context)

        # Create transformation function
        try:
            transform = self._create_transform(expr)
        except Exception as e:
            return CommandResult.fail(f"Invalid expression: {e}", context=context)

        # Apply transformation
        try:
            new_node = current.map(transform)
        except Exception as e:
            return CommandResult.fail(f"Error applying transformation: {e}", context=context)

        # Update tree
        tree = context.current_tree
        if not tree:
            return CommandResult.fail("Current tree not found", context=context)

        # Replace node in tree
        new_tree = self._replace_node_in_tree(tree.root, context._current_path, new_node)

        # Update forest
        new_forest = context.forest.set(context.current_tree_name, new_tree)
        new_context = context.update_forest(new_forest)

        return CommandResult.ok(output="Transformation applied", context=new_context)

    def _create_transform(self, expr: str) -> Callable[[Node], Node]:
        """Create a transformation function from an expression."""
        safe_globals = {
            '__builtins__': {
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
            },
            'Node': Node,
        }

        def transform(n: Node) -> Node:
            safe_locals = {
                'n': n,
                'node': n,
            }
            return eval(expr, safe_globals, safe_locals)

        return transform

    def _replace_node_in_tree(self, root: Node, path: List[str], new_node: Node) -> Node:
        """Replace a node at the given path."""
        if not path:
            return new_node

        component = path[0]
        remaining = path[1:]

        new_children = []
        for child in root.children:
            if child.name == component:
                if remaining:
                    new_child = self._replace_node_in_tree(child, remaining, new_node)
                    new_children.append(new_child)
                else:
                    new_children.append(new_node)
            else:
                new_children.append(child)

        return root.with_children(*new_children)


class FilterCommand(Command):
    """Filter nodes by predicate."""

    @property
    def name(self) -> str:
        return "filter"

    @property
    def description(self) -> str:
        return "Filter nodes by predicate"

    @property
    def usage(self) -> str:
        return "filter <expression>"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: filter <expression>", context=context)

        expr = ' '.join(args)

        if not context.current_tree_name:
            return CommandResult.fail("Not in a tree", context=context)

        current = context.current_node
        if not current:
            return CommandResult.fail("Invalid current location", context=context)

        # Create predicate
        try:
            predicate = SelectCommand()._create_predicate(expr)
        except Exception as e:
            return CommandResult.fail(f"Invalid expression: {e}", context=context)

        # Apply filter
        try:
            new_node = current.filter(predicate)
        except Exception as e:
            return CommandResult.fail(f"Error applying filter: {e}", context=context)

        # Update tree
        tree = context.current_tree
        if not tree:
            return CommandResult.fail("Current tree not found", context=context)

        # Replace node in tree
        map_cmd = MapCommand()
        new_tree = map_cmd._replace_node_in_tree(tree.root, context._current_path, new_node)

        # Update forest
        new_forest = context.forest.set(context.current_tree_name, new_tree)
        new_context = context.update_forest(new_forest)

        return CommandResult.ok(output="Filter applied", context=new_context)


# ============================================================================
# Command Registration Helper
# ============================================================================

def register_advanced_commands(registry):
    """
    Register all advanced commands to a registry.

    Args:
        registry: CommandRegistry to add commands to
    """
    # Query commands
    registry.register(FindCommand())
    registry.register(AncestorsCommand())
    registry.register(DescendantsCommand())
    registry.register(LeavesCommand())
    registry.register(SiblingsCommand())

    # Analysis commands
    registry.register(DepthCommand())
    registry.register(HeightCommand())
    registry.register(SizeCommand())

    # Tree operation commands
    registry.register(SelectCommand())
    registry.register(MapCommand())
    registry.register(FilterCommand())
