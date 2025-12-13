"""
Command infrastructure for the AlgoTree shell.

Provides base classes for commands, command registry, and result types.
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

from AlgoTree.shell.core import ShellContext, Forest


@dataclass
class CommandResult:
    """
    Result of executing a command.

    Attributes:
        success: Whether the command succeeded
        output: Command output (for display or piping)
        context: Updated shell context (may be same as input)
        error: Error message if command failed
    """
    success: bool
    output: Any = None
    context: Optional[ShellContext] = None
    error: Optional[str] = None

    @classmethod
    def ok(cls, output: Any = None, context: Optional[ShellContext] = None) -> 'CommandResult':
        """Create a successful result."""
        return cls(success=True, output=output, context=context)

    @classmethod
    def fail(cls, error: str, context: Optional[ShellContext] = None) -> 'CommandResult':
        """Create a failed result."""
        return cls(success=False, error=error, context=context)


class Command(ABC):
    """
    Base class for all shell commands.

    Commands should be stateless and operate only on the provided context.
    All state changes should be reflected in the returned CommandResult.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name (e.g., 'ls', 'cd', 'pwd')."""
        pass

    @property
    def aliases(self) -> List[str]:
        """Command aliases."""
        return []

    @property
    def description(self) -> str:
        """Short description of what the command does."""
        return ""

    @property
    def usage(self) -> str:
        """Usage string showing command syntax."""
        return self.name

    def supports_piping(self) -> bool:
        """
        Whether this command can receive piped input.

        Commands that support piping should handle the `pipe_input` parameter.
        """
        return False

    @abstractmethod
    def execute(
        self,
        context: ShellContext,
        args: List[str],
        pipe_input: Any = None
    ) -> CommandResult:
        """
        Execute the command.

        Args:
            context: Current shell context
            args: Command arguments (not including command name)
            pipe_input: Input from previous command in pipeline (if any)

        Returns:
            CommandResult with output and updated context
        """
        pass

    def complete(self, context: ShellContext, args: List[str], incomplete: str) -> List[str]:
        """
        Provide tab completions for this command.

        Args:
            context: Current shell context
            args: Arguments provided so far
            incomplete: Incomplete text to complete

        Returns:
            List of completion suggestions
        """
        return []

    def __repr__(self) -> str:
        return f"<Command: {self.name}>"


class CommandRegistry:
    """
    Registry for managing available commands.

    Supports lookup by name or alias, and provides command listing.
    """

    def __init__(self):
        """Initialize empty command registry."""
        self._commands: Dict[str, Command] = {}
        self._aliases: Dict[str, str] = {}

    def register(self, command: Command) -> None:
        """
        Register a command.

        Args:
            command: Command instance to register

        Raises:
            ValueError: If command name or alias conflicts with existing command
        """
        name = command.name

        if name in self._commands:
            raise ValueError(f"Command '{name}' already registered")

        self._commands[name] = command

        # Register aliases
        for alias in command.aliases:
            if alias in self._aliases or alias in self._commands:
                raise ValueError(f"Alias '{alias}' conflicts with existing command")
            self._aliases[alias] = name

    def get(self, name: str) -> Optional[Command]:
        """
        Get command by name or alias.

        Args:
            name: Command name or alias

        Returns:
            Command instance or None if not found
        """
        # Check if it's an alias first
        if name in self._aliases:
            name = self._aliases[name]

        return self._commands.get(name)

    def all_commands(self) -> List[Command]:
        """
        Get all registered commands.

        Returns:
            List of Command instances
        """
        return list(self._commands.values())

    def command_names(self) -> List[str]:
        """
        Get all command names (including aliases).

        Returns:
            Sorted list of command names and aliases
        """
        names = set(self._commands.keys())
        names.update(self._aliases.keys())
        return sorted(names)

    def __contains__(self, name: str) -> bool:
        """Check if command exists."""
        return name in self._commands or name in self._aliases

    def __len__(self) -> int:
        """Get number of registered commands."""
        return len(self._commands)


class Pipeline:
    """
    Represents a pipeline of commands connected by pipes.

    Example:
        ls | grep pattern | sort
    """

    def __init__(self, commands: List[tuple]):
        """
        Initialize pipeline.

        Args:
            commands: List of (command, args) tuples
        """
        self.commands = commands

    def execute(self, context: ShellContext) -> CommandResult:
        """
        Execute the pipeline.

        Each command's output becomes the next command's pipe_input.

        Args:
            context: Initial shell context

        Returns:
            Final CommandResult
        """
        current_input = None
        current_context = context

        for i, (command, args) in enumerate(self.commands):
            # Execute command
            result = command.execute(current_context, args, pipe_input=current_input)

            if not result.success:
                return result

            # Update context if changed
            if result.context:
                current_context = result.context

            # Pass output to next command
            current_input = result.output

        # Return final result
        return CommandResult.ok(output=current_input, context=current_context)

    @classmethod
    def parse(cls, command_line: str, registry: CommandRegistry) -> Optional['Pipeline']:
        """
        Parse a command line into a pipeline.

        Args:
            command_line: Command line string (may contain pipes)
            registry: Command registry for lookup

        Returns:
            Pipeline instance or None if parsing fails
        """
        # Split by pipe character
        segments = command_line.split('|')

        commands = []
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue

            # Parse command and args - use shlex for quote handling
            import shlex
            try:
                parts = shlex.split(segment)
            except ValueError:
                # Fallback to simple split if shlex fails
                parts = segment.split()

            if not parts:
                continue

            cmd_name = parts[0]
            args = parts[1:]

            # Look up command
            command = registry.get(cmd_name)
            if not command:
                return None

            commands.append((command, args))

        if not commands:
            return None

        return cls(commands)
