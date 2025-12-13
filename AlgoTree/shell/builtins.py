"""
Built-in shell commands for navigation, file operations, and tree manipulation.

This module contains all the core commands that make up the tree shell.
"""

from typing import List, Any, Optional
import os
from datetime import datetime

from AlgoTree.node import Node, node
from AlgoTree.tree import Tree
from AlgoTree.pretty_tree import pretty_tree
from AlgoTree.shell.core import ShellContext, Forest, TreePath
from AlgoTree.shell.commands import Command, CommandResult


# ANSI color codes
COLORS = {
    'black': '\033[0;30m',
    'red': '\033[0;31m',
    'green': '\033[0;32m',
    'yellow': '\033[0;33m',
    'blue': '\033[0;34m',
    'magenta': '\033[0;35m',
    'cyan': '\033[0;36m',
    'white': '\033[0;37m',
    'reset': '\033[0m',
    'dir_blue': '\033[1;34m',  # Bold blue for directories
}


def colorize(text: str, color: str) -> str:
    """Apply ANSI color to text."""
    color_code = COLORS.get(color, '')
    reset = COLORS['reset']
    return f"{color_code}{text}{reset}" if color_code else text


def get_timestamp() -> str:
    """Get current timestamp in ISO 8601 format."""
    return datetime.now().isoformat()


def add_creation_metadata(attrs: dict) -> dict:
    """Add creation timestamp to attributes."""
    now = get_timestamp()
    new_attrs = attrs.copy()
    new_attrs['.creation_time'] = now
    new_attrs['.modified_time'] = now
    new_attrs['.accessed_time'] = now
    return new_attrs


def add_modification_metadata(attrs: dict) -> dict:
    """Add/update modification timestamp."""
    new_attrs = attrs.copy()
    new_attrs['.modified_time'] = get_timestamp()
    return new_attrs


def add_access_metadata(attrs: dict) -> dict:
    """Add/update access timestamp."""
    new_attrs = attrs.copy()
    new_attrs['.accessed_time'] = get_timestamp()
    return new_attrs


# ============================================================================
# Navigation Commands
# ============================================================================

class PwdCommand(Command):
    """Print working directory."""

    @property
    def name(self) -> str:
        return "pwd"

    @property
    def description(self) -> str:
        return "Print working directory"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        # Build colored path
        if not context.current_tree_name:
            return CommandResult.ok(output="/", context=context)

        # Start with tree name
        colored_path = colorize(context.current_tree_name, 'dir_blue')

        # Add each path component with its color
        if context._current_path:
            current_node = context.forest.get(context.current_tree_name).root
            for component in context._current_path:
                # Find the child node
                for child in current_node.children:
                    if child.name == component:
                        if '.color' in child.attrs:
                            colored_component = colorize(component, child.attrs['.color'])
                        else:
                            colored_component = colorize(component, 'dir_blue')
                        colored_path += "/" + colored_component
                        current_node = child
                        break

        return CommandResult.ok(output="/" + colored_path, context=context)


class CdCommand(Command):
    """Change directory."""

    @property
    def name(self) -> str:
        return "cd"

    @property
    def description(self) -> str:
        return "Change directory"

    @property
    def usage(self) -> str:
        return "cd <path>"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            # cd with no args goes to forest root
            new_context = ShellContext(context.forest)
            return CommandResult.ok(context=new_context)

        path = args[0]

        try:
            new_context = context.cd(path)
            return CommandResult.ok(context=new_context)
        except ValueError as e:
            return CommandResult.fail(str(e), context=context)

    def complete(self, context: ShellContext, args: List[str], incomplete: str) -> List[str]:
        """Complete directory/node names."""
        completions = []

        # At forest root, complete tree names
        if not context.current_tree_name:
            for tree_name in context.forest.tree_names():
                if tree_name.startswith(incomplete):
                    completions.append(tree_name)
            return completions

        # Within a tree, complete child node names
        current = context.current_node
        if current:
            for child in current.children:
                if child.name.startswith(incomplete):
                    completions.append(child.name)

        # Add special completions
        if '..'.startswith(incomplete):
            completions.append('..')

        return completions


class LsCommand(Command):
    """List directory contents."""

    @property
    def name(self) -> str:
        return "ls"

    @property
    def description(self) -> str:
        return "List directory contents"

    @property
    def usage(self) -> str:
        return "ls [path] [-l] [-a]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        # Parse options
        long_format = '-l' in args
        show_all = '-a' in args or '-la' in args or '-al' in args
        args = [a for a in args if not a.startswith('-')]

        # Determine target path
        if args:
            target_path = args[0]
            try:
                target_context = context.cd(target_path)
            except ValueError as e:
                return CommandResult.fail(str(e), context=context)
        else:
            target_context = context

        # At forest root, list trees (no file metaphor here)
        if not target_context.current_tree_name:
            trees = target_context.forest.tree_names()
            lines = []

            # Add . and .. if -a
            if show_all:
                lines.append("\033[1;34m.\033[0m")  # blue
                lines.append("\033[1;34m..\033[0m")  # blue

            for tree_name in trees:
                # Hide dot-prefixed trees unless -a flag
                if tree_name.startswith('.') and not show_all:
                    continue

                if long_format:
                    tree = target_context.forest.get(tree_name)
                    root = tree.root if tree else None
                    if root:
                        num_children = len(list(root.descendants()))
                        lines.append(f"\033[1;34m{tree_name}/\033[0m  ({num_children} nodes)")
                    else:
                        lines.append(f"\033[1;34m{tree_name}/\033[0m")
                else:
                    lines.append(f"\033[1;34m{tree_name}/\033[0m")

            output = '\n'.join(lines)
            return CommandResult.ok(output=output, context=context)

        # Within a tree, list children (directories) AND attributes (files)
        current = target_context.current_node
        if not current:
            return CommandResult.fail("Invalid path", context=context)

        lines = []

        # Add . and .. if -a
        if show_all:
            lines.append("\033[1;34m.\033[0m")
            if context._current_path:  # Not at tree root
                lines.append("\033[1;34m..\033[0m")

        # Add child nodes as directories
        for child in current.children:
            # Hide dot-prefixed subtrees unless -a flag
            if child.name.startswith('.') and not show_all:
                continue

            # Check for custom color attribute (dot-prefixed)
            if '.color' in child.attrs:
                colored_name = colorize(f"{child.name}/", child.attrs['.color'])
            else:
                colored_name = colorize(f"{child.name}/", 'dir_blue')

            if long_format:
                num_children = len(child.children)
                lines.append(f"{colored_name}  ({num_children} children)")
            else:
                lines.append(colored_name)

        # Add attributes as files
        if current.attrs:
            for key, value in current.attrs.items():
                # Skip dot-prefixed (hidden) attributes unless -a flag
                if key.startswith('.') and not show_all:
                    continue

                if long_format:
                    # Show file size (length of value)
                    size = len(str(value))
                    lines.append(f"\033[0m{key}\033[0m  ({size} bytes)")
                else:
                    lines.append(f"\033[0m{key}\033[0m")

        output = '\n'.join(lines) if lines else ""
        return CommandResult.ok(output=output, context=context)

    def complete(self, context: ShellContext, args: List[str], incomplete: str) -> List[str]:
        """Complete directory/node names."""
        # Reuse cd completion logic
        cd_cmd = CdCommand()
        return cd_cmd.complete(context, args, incomplete)


# ============================================================================
# Read Commands
# ============================================================================

class CatCommand(Command):
    """Display node attributes or specific attribute value (file-like)."""

    @property
    def name(self) -> str:
        return "cat"

    @property
    def description(self) -> str:
        return "Display node attributes or specific attribute value"

    @property
    def usage(self) -> str:
        return "cat [path|attribute_key]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        # Determine target
        if args:
            # First, check if arg is an attribute key of current node
            if context.current_node and args[0] in context.current_node.attrs:
                # Treat as attribute key (file-like access)
                value = context.current_node.attrs[args[0]]
                return CommandResult.ok(output=str(value), context=context)

            # Otherwise try as path
            try:
                target_context = context.cd(args[0])
            except ValueError as e:
                return CommandResult.fail(str(e), context=context)
            target_node = target_context.current_node
        else:
            target_node = context.current_node

        if not target_node:
            return CommandResult.fail("Not in a tree", context=context)

        # Format output (full node display)
        lines = [f"name: {target_node.name}"]

        if target_node.attrs:
            lines.append("attrs:")
            for key, value in target_node.attrs.items():
                lines.append(f"  {key}: {value}")
        else:
            lines.append("attrs: {}")

        lines.append(f"children: {len(target_node.children)}")
        lines.append(f"is_leaf: {target_node.is_leaf}")

        return CommandResult.ok(output='\n'.join(lines), context=context)


class StatCommand(Command):
    """Display detailed node information."""

    @property
    def name(self) -> str:
        return "stat"

    @property
    def description(self) -> str:
        return "Display detailed node information"

    @property
    def usage(self) -> str:
        return "stat [path]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        # Determine target
        if args:
            try:
                target_context = context.cd(args[0])
            except ValueError as e:
                return CommandResult.fail(str(e), context=context)
            target_node = target_context.current_node
        else:
            target_node = context.current_node

        if not target_node:
            return CommandResult.fail("Not in a tree", context=context)

        # Collect stats
        lines = [
            f"Name: {target_node.name}",
            f"Path: {context.pwd() if not args else target_context.pwd()}",
            f"Type: {'directory' if target_node.children else 'file'}",
        ]

        # Show metadata (dot-prefixed attributes)
        metadata_keys = ['.color', '.permissions', '.creation_time', '.modified_time', '.accessed_time', '.order']
        has_metadata = False
        for key in metadata_keys:
            if key in target_node.attrs:
                if not has_metadata:
                    lines.append("\nMetadata:")
                    has_metadata = True
                display_key = key[1:]  # Remove dot prefix for display
                lines.append(f"  {display_key}: {target_node.attrs[key]}")

        # Tree stats
        lines.append("\nTree Statistics:")
        lines.append(f"  Depth: {target_node.depth}")
        lines.append(f"  Height: {target_node.height}")
        lines.append(f"  Children: {len(target_node.children)}")
        lines.append(f"  Descendants: {len(list(target_node.descendants()))}")

        # Regular attributes (non-dot-prefixed)
        regular_attrs = {k: v for k, v in target_node.attrs.items() if not k.startswith('.')}
        if regular_attrs:
            lines.append("\nAttributes:")
            for key, value in regular_attrs.items():
                lines.append(f"  {key}: {repr(value)}")

        return CommandResult.ok(output='\n'.join(lines), context=context)


class TreeCommand(Command):
    """Display tree structure."""

    @property
    def name(self) -> str:
        return "tree"

    @property
    def description(self) -> str:
        return "Display tree structure"

    @property
    def usage(self) -> str:
        return "tree [path] [-d depth]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        # Parse options
        max_depth = None
        path_args = []

        i = 0
        while i < len(args):
            if args[i] == '-d' and i + 1 < len(args):
                try:
                    max_depth = int(args[i + 1])
                    i += 2
                except ValueError:
                    return CommandResult.fail("Invalid depth value", context=context)
            else:
                path_args.append(args[i])
                i += 1

        # Determine target
        if path_args:
            try:
                target_context = context.cd(path_args[0])
            except ValueError as e:
                return CommandResult.fail(str(e), context=context)
            target_node = target_context.current_node
        else:
            target_node = context.current_node

        if not target_node:
            return CommandResult.fail("Not in a tree", context=context)

        # Generate tree output with color support
        def colored_node_name(node):
            """Return colored node name if .color attribute exists."""
            if '.color' in node.attrs:
                return colorize(node.name, node.attrs['.color'])
            return node.name

        output = pretty_tree(target_node, max_depth=max_depth, node_name=colored_node_name)

        return CommandResult.ok(output=output, context=context)


# ============================================================================
# Write Commands
# ============================================================================

class MkdirCommand(Command):
    """Create a new child node."""

    @property
    def name(self) -> str:
        return "mkdir"

    @property
    def description(self) -> str:
        return "Create a new child node"

    @property
    def usage(self) -> str:
        return "mkdir <name> [key=value ...]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: mkdir <name> [key=value ...]", context=context)

        name = args[0]

        # Parse attributes from remaining args (key=value format)
        attrs = {}
        for arg in args[1:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                # Try to parse as number, otherwise keep as string
                try:
                    if '.' in value:
                        attrs[key] = float(value)
                    else:
                        attrs[key] = int(value)
                except ValueError:
                    # Keep as string
                    attrs[key] = value
            else:
                return CommandResult.fail(f"Invalid attribute format: {arg}. Use key=value", context=context)

        # Must be in a tree
        if not context.current_tree_name:
            return CommandResult.fail("Cannot create node at forest root", context=context)

        current = context.current_node
        if not current:
            return CommandResult.fail("Invalid current location", context=context)

        # Add creation metadata (timestamps)
        attrs = add_creation_metadata(attrs)

        # Create new child with attributes
        new_child = Node(name, attrs=attrs)
        new_node = current.with_child(new_child)

        # Update tree
        tree = context.current_tree
        if not tree:
            return CommandResult.fail("Current tree not found", context=context)

        # Replace the node in the tree
        new_tree = self._replace_node_in_tree(tree.root, context._current_path, new_node)

        # Update forest
        new_forest = context.forest.set(context.current_tree_name, new_tree)
        new_context = context.update_forest(new_forest)

        return CommandResult.ok(output=f"Created node: {name}", context=new_context)

    def _replace_node_in_tree(self, root: Node, path: List[str], new_node: Node) -> Node:
        """Replace a node at the given path."""
        if not path:
            return new_node

        # Navigate to parent and replace child
        component = path[0]
        remaining = path[1:]

        new_children = []
        for child in root.children:
            if child.name == component:
                if remaining:
                    # Recurse deeper
                    new_child = self._replace_node_in_tree(child, remaining, new_node)
                    new_children.append(new_child)
                else:
                    # This is the node to replace
                    new_children.append(new_node)
            else:
                new_children.append(child)

        return root.with_children(*new_children)


class TouchCommand(Command):
    """Create empty attribute(s) (file metaphor)."""

    @property
    def name(self) -> str:
        return "touch"

    @property
    def description(self) -> str:
        return "Create empty attribute(s) (files)"

    @property
    def usage(self) -> str:
        return "touch <name> [name2 ...]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: touch <name> [name2 ...]", context=context)

        # Must be in a tree
        if not context.current_tree_name:
            return CommandResult.fail("Not in a tree", context=context)

        current = context.current_node
        if not current:
            return CommandResult.fail("Invalid current location", context=context)

        # Create empty attributes for each name
        new_attrs = {}
        for name in args:
            # If attribute already exists, just update access/modified time
            if name in current.attrs:
                new_attrs[name] = current.attrs[name]
            else:
                new_attrs[name] = ""

        # Add/update modification and access timestamps
        timestamp_attrs = add_modification_metadata(current.attrs)
        timestamp_attrs = add_access_metadata(timestamp_attrs)

        # Merge with new attributes
        timestamp_attrs.update(new_attrs)

        # Update node with new attributes
        new_node = current.with_attrs(**timestamp_attrs)

        # Update tree
        tree = context.current_tree
        if not tree:
            return CommandResult.fail("Current tree not found", context=context)

        # Replace node in tree
        mkdir_cmd = MkdirCommand()
        new_tree = mkdir_cmd._replace_node_in_tree(tree.root, context._current_path, new_node)

        # Update forest
        new_forest = context.forest.set(context.current_tree_name, new_tree)
        new_context = context.update_forest(new_forest)

        files_str = ", ".join(args)
        return CommandResult.ok(output=f"Created file(s): {files_str}", context=new_context)


class MktreeCommand(Command):
    """Create a new tree in the forest."""

    @property
    def name(self) -> str:
        return "mktree"

    @property
    def description(self) -> str:
        return "Create a new tree in the forest"

    @property
    def usage(self) -> str:
        return "mktree <name> [root_name] [key=value ...]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: mktree <name> [root_name] [key=value ...]", context=context)

        tree_name = args[0]

        if tree_name in context.forest:
            return CommandResult.fail(f"Tree '{tree_name}' already exists", context=context)

        # Check if second arg is root name or attribute
        # Default: root node name matches tree name
        root_name = tree_name
        attr_start = 1

        if len(args) > 1 and '=' not in args[1]:
            root_name = args[1]
            attr_start = 2

        # Parse attributes from remaining args
        attrs = {}
        for arg in args[attr_start:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                # Try to parse as number, otherwise keep as string
                try:
                    if '.' in value:
                        attrs[key] = float(value)
                    else:
                        attrs[key] = int(value)
                except ValueError:
                    attrs[key] = value
            else:
                return CommandResult.fail(f"Invalid attribute format: {arg}. Use key=value", context=context)

        # Create new tree with attributes
        root = Node(root_name, attrs=attrs) if attrs else Node(root_name)
        new_forest = context.forest.set(tree_name, Tree(root))
        new_context = context.update_forest(new_forest)

        return CommandResult.ok(output=f"Created tree: {tree_name}", context=new_context)


class SetAttrCommand(Command):
    """Set or update node attributes."""

    @property
    def name(self) -> str:
        return "setattr"

    @property
    def description(self) -> str:
        return "Set or update node attributes"

    @property
    def usage(self) -> str:
        return "setattr <key>=<value> [key2=value2 ...]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: setattr key=value [key2=value2 ...]", context=context)

        # Must be in a tree
        if not context.current_tree_name:
            return CommandResult.fail("Not in a tree", context=context)

        current = context.current_node
        if not current:
            return CommandResult.fail("Invalid current location", context=context)

        # Parse attributes
        new_attrs = dict(current.attrs)  # Copy existing attrs
        for arg in args:
            if '=' not in arg:
                return CommandResult.fail(f"Invalid format: {arg}. Use key=value", context=context)

            key, value = arg.split('=', 1)
            # Try to parse as number, otherwise keep as string
            try:
                if '.' in value:
                    new_attrs[key] = float(value)
                else:
                    new_attrs[key] = int(value)
            except ValueError:
                # Keep as string
                new_attrs[key] = value

        # Update node with new attributes
        new_node = current.with_attrs(**new_attrs)

        # Update tree
        tree = context.current_tree
        if not tree:
            return CommandResult.fail("Current tree not found", context=context)

        # Replace node in tree
        mkdir_cmd = MkdirCommand()
        new_tree = mkdir_cmd._replace_node_in_tree(tree.root, context._current_path, new_node)

        # Update forest
        new_forest = context.forest.set(context.current_tree_name, new_tree)
        new_context = context.update_forest(new_forest)

        return CommandResult.ok(output=f"Updated attributes: {list(new_attrs.keys())}", context=new_context)


class RmAttrCommand(Command):
    """Remove node attributes."""

    @property
    def name(self) -> str:
        return "rmattr"

    @property
    def description(self) -> str:
        return "Remove node attributes"

    @property
    def usage(self) -> str:
        return "rmattr <key> [key2 ...]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: rmattr key [key2 ...]", context=context)

        # Must be in a tree
        if not context.current_tree_name:
            return CommandResult.fail("Not in a tree", context=context)

        current = context.current_node
        if not current:
            return CommandResult.fail("Invalid current location", context=context)

        # Remove specified attributes
        new_node = current.without_attrs(*args)

        # Update tree
        tree = context.current_tree
        if not tree:
            return CommandResult.fail("Current tree not found", context=context)

        # Replace node in tree
        mkdir_cmd = MkdirCommand()
        new_tree = mkdir_cmd._replace_node_in_tree(tree.root, context._current_path, new_node)

        # Update forest
        new_forest = context.forest.set(context.current_tree_name, new_tree)
        new_context = context.update_forest(new_forest)

        return CommandResult.ok(output=f"Removed attributes: {args}", context=new_context)


class ColorCommand(Command):
    """Set color attribute for current node or path."""

    @property
    def name(self) -> str:
        return "color"

    @property
    def description(self) -> str:
        return "Set color attribute for node"

    @property
    def usage(self) -> str:
        return "color <color_name> [path]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail(
                "Usage: color <color_name> [path]\n"
                "Colors: red, green, yellow, blue, magenta, cyan, white",
                context=context
            )

        color_name = args[0]

        # Validate color (basic ANSI colors)
        valid_colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'black']
        if color_name not in valid_colors:
            return CommandResult.fail(
                f"Invalid color: {color_name}\n"
                f"Valid colors: {', '.join(valid_colors)}",
                context=context
            )

        # Determine target node
        if len(args) > 1:
            # Color a specific path
            try:
                target_context = context.cd(args[1])
            except ValueError as e:
                return CommandResult.fail(str(e), context=context)
            target_node = target_context.current_node
            target_path = target_context._current_path
        else:
            # Color current node
            target_node = context.current_node
            target_path = context._current_path

        if not target_node:
            return CommandResult.fail("Not in a tree", context=context)

        # Set color attribute (using dot-prefix for hidden metadata)
        new_node = target_node.with_attrs(**{'.color': color_name})

        # Update tree
        tree = context.current_tree
        if not tree:
            return CommandResult.fail("Current tree not found", context=context)

        # Replace node in tree
        mkdir_cmd = MkdirCommand()
        new_tree = mkdir_cmd._replace_node_in_tree(tree.root, target_path, new_node)

        # Update forest
        new_forest = context.forest.set(context.current_tree_name, new_tree)
        new_context = context.update_forest(new_forest)

        return CommandResult.ok(
            output=f"Set color '{color_name}' for {target_node.name}",
            context=new_context
        )


class ChmodCommand(Command):
    """Set permissions for node."""

    @property
    def name(self) -> str:
        return "chmod"

    @property
    def description(self) -> str:
        return "Set permissions for node"

    @property
    def usage(self) -> str:
        return "chmod <permissions> [path]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail(
                "Usage: chmod <permissions> [path]\n"
                "Examples: chmod rwx, chmod r-x, chmod 755",
                context=context
            )

        permissions = args[0]

        # Determine target node
        if len(args) > 1:
            # Set permissions on specific path
            try:
                target_context = context.cd(args[1])
            except ValueError as e:
                return CommandResult.fail(str(e), context=context)
            target_node = target_context.current_node
            target_path = target_context._current_path
        else:
            # Set permissions on current node
            target_node = context.current_node
            target_path = context._current_path

        if not target_node:
            return CommandResult.fail("Not in a tree", context=context)

        # Set permissions attribute (using dot-prefix for hidden metadata)
        new_node = target_node.with_attrs(**{'.permissions': permissions})

        # Update tree
        tree = context.current_tree
        if not tree:
            return CommandResult.fail("Current tree not found", context=context)

        # Replace node in tree
        mkdir_cmd = MkdirCommand()
        new_tree = mkdir_cmd._replace_node_in_tree(tree.root, target_path, new_node)

        # Update forest
        new_forest = context.forest.set(context.current_tree_name, new_tree)
        new_context = context.update_forest(new_forest)

        return CommandResult.ok(
            output=f"Set permissions '{permissions}' for {target_node.name}",
            context=new_context
        )


class ConfigCommand(Command):
    """Manage tree configuration via .config subtree."""

    @property
    def name(self) -> str:
        return "config"

    @property
    def description(self) -> str:
        return "Manage tree configuration"

    @property
    def usage(self) -> str:
        return "config [key] [value]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        # Must be in a tree
        if not context.current_tree_name:
            return CommandResult.fail("Not in a tree", context=context)

        tree = context.current_tree
        if not tree:
            return CommandResult.fail("Current tree not found", context=context)

        # Find or create .config node
        config_node = None
        for child in tree.root.children:
            if child.name == '.config':
                config_node = child
                break

        # No args: show all config
        if not args:
            if not config_node:
                return CommandResult.ok(output="No configuration set", context=context)

            lines = ["Configuration:"]
            for key, value in config_node.attrs.items():
                if not key.startswith('.'):  # Skip metadata
                    lines.append(f"  {key}: {value}")

            return CommandResult.ok(output='\n'.join(lines), context=context)

        # One arg: show specific config value
        if len(args) == 1:
            if not config_node:
                return CommandResult.fail(f"Config key not found: {args[0]}", context=context)

            key = args[0]
            if key in config_node.attrs:
                return CommandResult.ok(output=str(config_node.attrs[key]), context=context)
            else:
                return CommandResult.fail(f"Config key not found: {key}", context=context)

        # Two args: set config value
        key, value = args[0], args[1]

        # Auto-parse value
        try:
            if value.lower() in ('true', 'false'):
                parsed_value = value.lower() == 'true'
            elif '.' in value:
                parsed_value = float(value)
            else:
                parsed_value = int(value)
        except ValueError:
            parsed_value = value  # Keep as string

        # Create or update .config node
        if not config_node:
            # Create .config node
            config_node = Node('.config', attrs={key: parsed_value})
            new_root = tree.root.with_child(config_node)
        else:
            # Update existing .config node
            new_config = config_node.with_attrs(**{key: parsed_value})
            # Replace .config in tree
            new_children = []
            for child in tree.root.children:
                if child.name == '.config':
                    new_children.append(new_config)
                else:
                    new_children.append(child)
            new_root = tree.root.with_children(*new_children)

        # Update forest
        new_forest = context.forest.set(context.current_tree_name, Tree(new_root))
        new_context = context.update_forest(new_forest)

        return CommandResult.ok(
            output=f"Set config '{key}' = {parsed_value}",
            context=new_context
        )


class RmtreeCommand(Command):
    """Remove a tree from the forest."""

    @property
    def name(self) -> str:
        return "rmtree"

    @property
    def description(self) -> str:
        return "Remove a tree from the forest"

    @property
    def usage(self) -> str:
        return "rmtree <name>"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: rmtree <name>", context=context)

        tree_name = args[0]

        if tree_name not in context.forest:
            return CommandResult.fail(f"Tree '{tree_name}' not found", context=context)

        # Remove tree
        new_forest = context.forest.remove(tree_name)
        new_context = ShellContext(new_forest)  # Go to forest root

        return CommandResult.ok(output=f"Removed tree: {tree_name}", context=new_context)


class EchoCommand(Command):
    """Print text or write to attributes (file-like)."""

    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Print text or write to attributes (use > key or >> key)"

    @property
    def usage(self) -> str:
        return "echo <text> [> key | >> key]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.ok(output="", context=context)

        # Check for redirection operators
        redirect_mode = None
        redirect_key = None

        # Find > or >> in args
        if '>' in args:
            idx = args.index('>')
            redirect_mode = 'write'
            if idx + 1 < len(args):
                redirect_key = args[idx + 1]
                args = args[:idx]
            else:
                return CommandResult.fail("Usage: echo <text> > <key>", context=context)
        elif '>>' in args:
            idx = args.index('>>')
            redirect_mode = 'append'
            if idx + 1 < len(args):
                redirect_key = args[idx + 1]
                args = args[:idx]
            else:
                return CommandResult.fail("Usage: echo <text> >> <key>", context=context)

        # Join remaining args as text
        text = ' '.join(args)

        # If no redirection, just print
        if not redirect_mode:
            return CommandResult.ok(output=text, context=context)

        # Must be in a tree to write attributes
        if not context.current_tree_name:
            return CommandResult.fail("Not in a tree", context=context)

        current = context.current_node
        if not current:
            return CommandResult.fail("Invalid current location", context=context)

        # Handle redirection
        if redirect_mode == 'write':
            # Overwrite attribute
            new_node = current.with_attrs(**{redirect_key: text})
        else:  # append
            # Append to existing value with newline separator
            existing = current.attrs.get(redirect_key, "")
            if existing:
                new_value = existing + '\n' + text
            else:
                new_value = text
            new_node = current.with_attrs(**{redirect_key: new_value})

        # Update tree
        tree = context.current_tree
        if not tree:
            return CommandResult.fail("Current tree not found", context=context)

        # Replace node in tree
        mkdir_cmd = MkdirCommand()
        new_tree = mkdir_cmd._replace_node_in_tree(tree.root, context._current_path, new_node)

        # Update forest
        new_forest = context.forest.set(context.current_tree_name, new_tree)
        new_context = context.update_forest(new_forest)

        return CommandResult.ok(output=None, context=new_context)


class ReadFileCommand(Command):
    """Load content from filesystem file into attribute."""

    @property
    def name(self) -> str:
        return "readfile"

    @property
    def aliases(self) -> List[str]:
        return []

    @property
    def description(self) -> str:
        return "Load content from filesystem file into attribute"

    @property
    def usage(self) -> str:
        return "readfile <filepath> <attribute_key>"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if len(args) < 2:
            return CommandResult.fail("Usage: readfile <filepath> <attribute_key>", context=context)

        filepath = args[0]
        attr_key = args[1]

        # Must be in a tree
        if not context.current_tree_name:
            return CommandResult.fail("Not in a tree", context=context)

        current = context.current_node
        if not current:
            return CommandResult.fail("Invalid current location", context=context)

        # Read file from filesystem
        try:
            with open(filepath, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            return CommandResult.fail(f"File not found: {filepath}", context=context)
        except Exception as e:
            return CommandResult.fail(f"Error reading file: {e}", context=context)

        # Set attribute
        new_node = current.with_attrs(**{attr_key: content})

        # Update tree
        tree = context.current_tree
        if not tree:
            return CommandResult.fail("Current tree not found", context=context)

        # Replace node in tree
        mkdir_cmd = MkdirCommand()
        new_tree = mkdir_cmd._replace_node_in_tree(tree.root, context._current_path, new_node)

        # Update forest
        new_forest = context.forest.set(context.current_tree_name, new_tree)
        new_context = context.update_forest(new_forest)

        return CommandResult.ok(
            output=f"Loaded {len(content)} characters from {filepath} into '{attr_key}'",
            context=new_context
        )


# ============================================================================
# Helper Commands
# ============================================================================

class HelpCommand(Command):
    """Display help information."""

    @property
    def name(self) -> str:
        return "help"

    @property
    def aliases(self) -> List[str]:
        return ["?"]

    @property
    def description(self) -> str:
        return "Display help information"

    @property
    def usage(self) -> str:
        return "help [command]"

    def __init__(self, registry=None):
        self._registry = registry

    def set_registry(self, registry):
        """Set the command registry for help lookups."""
        self._registry = registry

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not self._registry:
            return CommandResult.fail("Command registry not available", context=context)

        if args:
            # Show help for specific command
            cmd_name = args[0]
            cmd = self._registry.get(cmd_name)
            if not cmd:
                return CommandResult.fail(f"Unknown command: {cmd_name}", context=context)

            lines = [
                f"Command: {cmd.name}",
                f"Description: {cmd.description}",
                f"Usage: {cmd.usage}",
            ]

            if cmd.aliases:
                lines.append(f"Aliases: {', '.join(cmd.aliases)}")

            return CommandResult.ok(output='\n'.join(lines), context=context)

        # Show all commands
        lines = ["Available commands:", ""]

        for cmd in sorted(self._registry.all_commands(), key=lambda c: c.name):
            aliases_str = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
            lines.append(f"  {cmd.name}{aliases_str}: {cmd.description}")

        lines.append("")
        lines.append("Use 'help <command>' for detailed information.")

        return CommandResult.ok(output='\n'.join(lines), context=context)


class ExitCommand(Command):
    """Exit the shell."""

    @property
    def name(self) -> str:
        return "exit"

    @property
    def aliases(self) -> List[str]:
        return ["quit", "q"]

    @property
    def description(self) -> str:
        return "Exit the shell"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        # This will be handled specially by the shell
        return CommandResult.ok(output="exit", context=context)


# ============================================================================
# Command Registration
# ============================================================================

def create_builtin_registry():
    """Create a command registry with all built-in commands."""
    from AlgoTree.shell.commands import CommandRegistry
    from AlgoTree.shell.advanced import register_advanced_commands
    from AlgoTree.shell.io_commands import SaveCommand, LoadCommand, ExportCommand, ToGraphCommand, FromGraphCommand

    registry = CommandRegistry()

    # Navigation
    registry.register(PwdCommand())
    registry.register(CdCommand())
    registry.register(LsCommand())

    # Read
    registry.register(CatCommand())
    registry.register(StatCommand())
    registry.register(TreeCommand())

    # Write
    registry.register(MkdirCommand())
    registry.register(TouchCommand())
    registry.register(MktreeCommand())
    registry.register(RmtreeCommand())
    registry.register(SetAttrCommand())
    registry.register(RmAttrCommand())
    registry.register(ColorCommand())
    registry.register(ChmodCommand())
    registry.register(ConfigCommand())
    registry.register(EchoCommand())
    registry.register(ReadFileCommand())

    # I/O
    registry.register(SaveCommand())
    registry.register(LoadCommand())
    registry.register(ExportCommand())

    # AlgoGraph interop (available even if AlgoGraph not installed - will give helpful error)
    registry.register(ToGraphCommand())
    registry.register(FromGraphCommand())

    # Advanced commands (queries, transformations, analysis)
    register_advanced_commands(registry)

    # Helper
    help_cmd = HelpCommand()
    help_cmd.set_registry(registry)
    registry.register(help_cmd)
    registry.register(ExitCommand())

    return registry
