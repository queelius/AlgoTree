"""
Interactive tree shell using prompt_toolkit.

Provides a REPL with:
- Tab completion for commands and paths
- Command history
- Syntax highlighting
- Multi-line editing
"""

import sys
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

from AlgoTree.shell.core import Forest, ShellContext
from AlgoTree.shell.commands import CommandRegistry, Pipeline
from AlgoTree.shell.builtins import create_builtin_registry


class TreeShellCompleter(Completer):
    """
    Tab completion for tree shell commands and paths.
    """

    def __init__(self, registry: CommandRegistry, get_context):
        """
        Initialize completer.

        Args:
            registry: Command registry
            get_context: Callable that returns current ShellContext
        """
        self.registry = registry
        self.get_context = get_context

    def get_completions(self, document, complete_event):
        """
        Generate completions for the current input.

        Args:
            document: The current document
            complete_event: Completion event

        Yields:
            Completion objects
        """
        text = document.text_before_cursor
        words = text.split()

        # Empty input - complete commands
        if not words:
            for name in self.registry.command_names():
                yield Completion(name, start_position=0)
            return

        # First word - complete commands
        if len(words) == 1 and not text.endswith(' '):
            word = words[0]
            for name in self.registry.command_names():
                if name.startswith(word):
                    yield Completion(name, start_position=-len(word))
            return

        # Subsequent words - command-specific completion
        cmd_name = words[0]
        cmd = self.registry.get(cmd_name)

        if not cmd:
            return

        # Get context
        context = self.get_context()

        # Get incomplete text
        if text.endswith(' '):
            incomplete = ''
        else:
            incomplete = words[-1]

        # Get completions from command
        args = words[1:-1] if not text.endswith(' ') else words[1:]
        completions = cmd.complete(context, args, incomplete)

        for comp in completions:
            yield Completion(comp, start_position=-len(incomplete))


class TreeShell:
    """
    Interactive REPL for navigating and manipulating tree structures.

    Features:
    - Tab completion for commands and paths
    - Command history
    - Color output
    - Pipeline support
    """

    def __init__(
        self,
        forest: Optional[Forest] = None,
        registry: Optional[CommandRegistry] = None
    ):
        """
        Initialize tree shell.

        Args:
            forest: Initial forest (defaults to empty)
            registry: Command registry (defaults to built-in commands)
        """
        self.forest = forest or Forest()
        self.context = ShellContext(self.forest)
        self.registry = registry or create_builtin_registry()

        # Create prompt session
        self.history = InMemoryHistory()
        self.completer = TreeShellCompleter(self.registry, lambda: self.context)

        # Style for prompt
        self.style = Style.from_dict({
            'prompt': '#00aa00 bold',
            'path': '#0088ff bold',
        })

        self.session = PromptSession(
            history=self.history,
            completer=self.completer,
            complete_while_typing=True,
            style=self.style,
        )

        self.running = False

    def get_prompt(self) -> HTML:
        """
        Generate colored prompt string with node colors.

        Returns:
            Formatted prompt
        """
        # Build colored path
        if not self.context.current_tree_name:
            pwd_colored = '/'
        else:
            # Start with tree name
            pwd_colored = self.context.current_tree_name

            # Add each path component
            if self.context._current_path:
                pwd_colored += '/' + '/'.join(self.context._current_path)

        return HTML(f'<path>{pwd_colored}</path> <prompt>$</prompt> ')

    def execute_line(self, line: str) -> bool:
        """
        Execute a command line.

        Args:
            line: Command line to execute

        Returns:
            True to continue, False to exit
        """
        line = line.strip()

        if not line:
            return True

        # Check for exit commands
        if line in ('exit', 'quit', 'q'):
            return False

        # Try to parse as pipeline
        pipeline = Pipeline.parse(line, self.registry)

        if not pipeline:
            # Try as single command - use shlex for proper quote handling
            import shlex
            try:
                parts = shlex.split(line)
            except ValueError:
                # Fallback to simple split if shlex fails (e.g., unmatched quotes)
                parts = line.split()

            if not parts:
                return True

            cmd_name = parts[0]
            args = parts[1:]

            cmd = self.registry.get(cmd_name)
            if not cmd:
                print(f"Unknown command: {cmd_name}")
                print("Type 'help' for available commands.")
                return True

            # Execute single command
            result = cmd.execute(self.context, args)
        else:
            # Execute pipeline
            result = pipeline.execute(self.context)

        # Handle result
        if not result.success:
            print(f"Error: {result.error}")
        elif result.output:
            print(result.output)

        # Update context if changed
        if result.context:
            self.context = result.context

        return True

    def run(self):
        """
        Start the interactive REPL.

        Runs until user exits with 'exit', 'quit', or Ctrl+D.
        """
        self.running = True

        print("AlgoTree Shell")
        print("Type 'help' for available commands, 'exit' to quit.")
        print()

        try:
            while self.running:
                try:
                    # Get input
                    line = self.session.prompt(self.get_prompt())

                    # Execute
                    if not self.execute_line(line):
                        break

                except KeyboardInterrupt:
                    # Ctrl+C - cancel current line
                    print("^C")
                    continue

                except EOFError:
                    # Ctrl+D - exit
                    print()
                    break

        except Exception as e:
            print(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()

        print("Goodbye!")

    def load_tree(self, filename: str, tree_name: Optional[str] = None):
        """
        Load a tree from a file into the forest.

        Args:
            filename: Path to tree file (JSON, YAML, etc.)
            tree_name: Name for the tree (defaults to filename without extension)
        """
        import os
        from AlgoTree.serialization import load

        if not tree_name:
            tree_name = os.path.splitext(os.path.basename(filename))[0]

        try:
            tree = load(filename)
            self.forest = self.forest.set(tree_name, tree)
            self.context = self.context.update_forest(self.forest)
            print(f"Loaded tree '{tree_name}' from {filename}")
        except Exception as e:
            print(f"Error loading tree: {e}")

    def save_tree(self, tree_name: str, filename: str):
        """
        Save a tree from the forest to a file.

        Args:
            tree_name: Name of tree to save
            filename: Output file path
        """
        from AlgoTree.serialization import save

        tree = self.forest.get(tree_name)
        if not tree:
            print(f"Tree '{tree_name}' not found")
            return

        try:
            save(tree.root, filename)
            print(f"Saved tree '{tree_name}' to {filename}")
        except Exception as e:
            print(f"Error saving tree: {e}")


def main():
    """
    Entry point for the tree shell CLI.

    Usage:
        python -m AlgoTree.shell.shell [tree_file]
    """
    import argparse

    parser = argparse.ArgumentParser(description='Interactive tree shell')
    parser.add_argument('tree', nargs='?', help='Tree file to load')
    parser.add_argument('--name', help='Name for the loaded tree')

    args = parser.parse_args()

    # Create shell
    shell = TreeShell()

    # Load tree if specified
    if args.tree:
        shell.load_tree(args.tree, args.name)

    # Run interactive shell
    shell.run()


if __name__ == '__main__':
    main()
