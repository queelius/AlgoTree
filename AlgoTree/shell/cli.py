"""
Stateless CLI tool for tree operations.

Provides command-line operations on tree files without an interactive shell.

Usage:
    algotree <command> <tree_file>[:<path>] [args...]
    algotree shell [tree_file]

Examples:
    algotree ls tree.json:/root/child1
    algotree cat tree.json:/root/child1
    algotree tree tree.json
    algotree select 'n.depth > 2' tree.json --output filtered.json
    algotree shell tree.json
"""

import sys
import argparse
from typing import Optional

from AlgoTree.node import Node
from AlgoTree.tree import Tree
from AlgoTree.serialization import load as load_tree, save as save_tree
from AlgoTree.shell.core import Forest, ShellContext, TreePath
from AlgoTree.shell.commands import CommandRegistry
from AlgoTree.shell.builtins import create_builtin_registry


def parse_tree_path(path_spec: str) -> tuple[str, Optional[str]]:
    """
    Parse a tree path specification.

    Args:
        path_spec: Path in format "file.json" or "file.json:/path/to/node"

    Returns:
        Tuple of (filename, path_within_tree)
    """
    if ':' in path_spec:
        filename, tree_path = path_spec.split(':', 1)
        return filename, tree_path
    else:
        return path_spec, None


def load_tree_file(filename: str) -> Tree:
    """
    Load a tree from a file.

    Args:
        filename: Path to tree file

    Returns:
        Tree instance

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
    """
    try:
        node = load_tree(filename)
        return Tree(node)
    except Exception as e:
        raise ValueError(f"Error loading tree from {filename}: {e}")


def execute_command(
    command_name: str,
    tree: Tree,
    path: Optional[str],
    args: list[str]
) -> tuple[bool, str]:
    """
    Execute a command on a tree.

    Args:
        command_name: Name of command to execute
        tree: Tree to operate on
        path: Path within tree (or None for root)
        args: Command arguments

    Returns:
        Tuple of (success, output)
    """
    # Create forest with single tree
    forest = Forest({"main": tree})

    # Create context
    context = ShellContext(forest, "main")

    # Navigate to path if specified
    if path:
        try:
            context = context.cd(path)
        except ValueError as e:
            return False, f"Invalid path: {e}"

    # Get command
    registry = create_builtin_registry()
    command = registry.get(command_name)

    if not command:
        return False, f"Unknown command: {command_name}"

    # Execute command
    result = command.execute(context, args)

    if not result.success:
        return False, result.error or "Command failed"

    # Format output
    output = result.output if result.output else ""
    return True, str(output)


def main():
    """
    Entry point for the algotree CLI tool.
    """
    parser = argparse.ArgumentParser(
        description='AlgoTree CLI - Operate on tree files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  algotree ls tree.json
  algotree ls tree.json:/root/child1
  algotree cat tree.json:/root/child1
  algotree tree tree.json -d 3
  algotree find ".*test.*" tree.json
  algotree select 'n.depth > 2' tree.json
  algotree shell                 # Start empty shell
  algotree shell tree.json       # Start with tree loaded

Path Format:
  <file>[:<path>]

  file  - Path to tree file (JSON, YAML, etc.)
  path  - Optional path within tree (e.g., /root/child1)
        """
    )

    parser.add_argument(
        'command',
        help='Command to execute (or "shell" for interactive mode)'
    )

    parser.add_argument(
        'tree',
        nargs='?',
        help='Tree file path, optionally with path (file.json or file.json:/path). Optional for shell command.'
    )

    parser.add_argument(
        'args',
        nargs='*',
        help='Additional command arguments'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file (for commands that modify the tree)'
    )

    # Parse arguments
    args = parser.parse_args()

    # Special case: shell command
    if args.command == 'shell':
        from AlgoTree.shell.shell import TreeShell

        # Create shell
        shell = TreeShell()

        # Load tree if specified
        if args.tree:
            try:
                tree = load_tree_file(args.tree)
                import os
                tree_name = os.path.splitext(os.path.basename(args.tree))[0]
                shell.forest = shell.forest.set(tree_name, tree)
                shell.context = shell.context.update_forest(shell.forest)
                print(f"Loaded tree '{tree_name}' from {args.tree}")
            except Exception as e:
                print(f"Error loading tree: {e}")
                return 1

        # Run shell
        shell.run()
        return 0

    # For non-shell commands, tree file is required
    if not args.tree:
        print(f"Error: tree file is required for command '{args.command}'", file=sys.stderr)
        print(f"Usage: algotree {args.command} <tree_file> [args...]", file=sys.stderr)
        return 1

    # Parse tree path
    try:
        filename, tree_path = parse_tree_path(args.tree)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Load tree
    try:
        tree = load_tree_file(filename)
    except FileNotFoundError:
        print(f"Error: File not found: {filename}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Execute command
    success, output = execute_command(args.command, tree, tree_path, args.args)

    if not success:
        print(f"Error: {output}", file=sys.stderr)
        return 1

    # Print output
    if output:
        print(output)

    # Save output if requested
    if args.output:
        try:
            # Get modified tree from forest
            forest = Forest({"main": tree})
            context = ShellContext(forest, "main")
            if tree_path:
                context = context.cd(tree_path)

            # Execute command again to get modified context
            registry = create_builtin_registry()
            command = registry.get(args.command)
            result = command.execute(context, args.args)

            if result.context and result.context.current_tree:
                modified_tree = result.context.current_tree
                save_tree(modified_tree.root, args.output)
                print(f"Saved to {args.output}", file=sys.stderr)
            else:
                print("Warning: Command did not modify the tree", file=sys.stderr)

        except Exception as e:
            print(f"Error saving output: {e}", file=sys.stderr)
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
