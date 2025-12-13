"""
Utility functions for the shell.

Provides common parsing and formatting utilities.
"""

import shlex
from typing import Dict, Any


def parse_attributes(args: list[str]) -> tuple[Dict[str, Any], list[str]]:
    """
    Parse key=value attributes from argument list.

    Handles quoted values: name="John Doe" age=30

    Args:
        args: List of arguments that may contain key=value pairs

    Returns:
        Tuple of (attributes_dict, remaining_args)
    """
    attrs = {}
    remaining = []

    for arg in args:
        if '=' in arg:
            key, value = arg.split('=', 1)

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            # Try to parse as number
            try:
                if '.' in value:
                    attrs[key] = float(value)
                else:
                    attrs[key] = int(value)
            except ValueError:
                # Keep as string
                attrs[key] = value
        else:
            remaining.append(arg)

    return attrs, remaining


def parse_shell_args(args_str: str) -> list[str]:
    """
    Parse shell arguments handling quotes properly.

    Uses shlex to handle quoted strings with spaces.

    Args:
        args_str: Raw argument string

    Returns:
        List of parsed arguments
    """
    try:
        return shlex.split(args_str)
    except ValueError:
        # Fallback to simple split if shlex fails
        return args_str.split()
