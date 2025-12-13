"""
AlgoTree Shell - A Linux-like command-line interface for navigating and manipulating tree structures.

This module provides:
- Forest: A collection of named trees
- TreePath: Path parsing and resolution
- ShellContext: Navigation state and operations
- TreeShell: Interactive REPL using prompt_toolkit
- CLI tool: Stateless operations on tree files
"""

from AlgoTree.shell.core import Forest, TreePath, ShellContext
from AlgoTree.shell.shell import TreeShell
from AlgoTree.shell.commands import Command, CommandRegistry

__all__ = [
    'Forest',
    'TreePath',
    'ShellContext',
    'TreeShell',
    'Command',
    'CommandRegistry',
]
