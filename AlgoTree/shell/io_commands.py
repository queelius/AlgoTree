"""
I/O commands for saving and loading trees.

Provides commands to persist trees to files and load them back,
as well as interoperability with AlgoGraph.
"""

from typing import List, Any
import os

from AlgoTree.shell.core import ShellContext
from AlgoTree.shell.commands import Command, CommandResult

# Check if AlgoGraph is available
try:
    from AlgoGraph import Graph
    ALGOGRAPH_AVAILABLE = True
except ImportError:
    ALGOGRAPH_AVAILABLE = False


class SaveCommand(Command):
    """Save current tree to a file."""

    @property
    def name(self) -> str:
        return "save"

    @property
    def description(self) -> str:
        return "Save current tree to a file"

    @property
    def usage(self) -> str:
        return "save <filename> [tree_name]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: save <filename> [tree_name]", context=context)

        filename = args[0]

        # Determine which tree to save
        if len(args) > 1:
            # Save specified tree
            tree_name = args[1]
            tree = context.forest.get(tree_name)
            if not tree:
                return CommandResult.fail(f"Tree '{tree_name}' not found", context=context)
        else:
            # Save current tree
            if not context.current_tree_name:
                return CommandResult.fail("Not in a tree. Use: save <filename> <tree_name>", context=context)
            tree_name = context.current_tree_name
            tree = context.current_tree

        if not tree:
            return CommandResult.fail("No tree to save", context=context)

        # Save tree to file
        try:
            from AlgoTree.serialization import save
            save(tree.root, filename)
            return CommandResult.ok(output=f"Saved tree '{tree_name}' to {filename}", context=context)
        except Exception as e:
            return CommandResult.fail(f"Error saving tree: {e}", context=context)


class LoadCommand(Command):
    """Load a tree from a file.

    At forest root: Loads as new tree into forest.
    Inside a tree: Loads as subtree at current node.
    """

    @property
    def name(self) -> str:
        return "load"

    @property
    def description(self) -> str:
        return "Load a tree from a file (as tree or subtree)"

    @property
    def usage(self) -> str:
        return "load <filename> [name]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail("Usage: load <filename> [name]", context=context)

        filename = args[0]

        # Load tree from file
        try:
            from AlgoTree.serialization import load
            from AlgoTree.tree import Tree
            from AlgoTree.shell.builtins import MkdirCommand

            loaded_node = load(filename)

            # At forest root: Add as new tree
            if not context.current_tree_name:
                # Determine tree name
                if len(args) > 1:
                    tree_name = args[1]
                else:
                    # Use filename without extension or node's name
                    tree_name = loaded_node.name if hasattr(loaded_node, 'name') and loaded_node.name else \
                                os.path.splitext(os.path.basename(filename))[0]

                tree = Tree(loaded_node)
                new_forest = context.forest.set(tree_name, tree)
                new_context = context.update_forest(new_forest)

                return CommandResult.ok(
                    output=f"Loaded tree '{tree_name}' from {filename}",
                    context=new_context
                )

            # Inside a tree: Add as subtree (child node)
            else:
                current = context.current_node
                if not current:
                    return CommandResult.fail("Invalid current location", context=context)

                # Optionally rename the loaded node
                if len(args) > 1:
                    new_name = args[1]
                    loaded_node = loaded_node.with_name(new_name)

                # Add loaded node as child
                new_node = current.with_child(loaded_node)

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
                    output=f"Loaded subtree '{loaded_node.name}' from {filename}",
                    context=new_context
                )

        except FileNotFoundError:
            return CommandResult.fail(f"File not found: {filename}", context=context)
        except Exception as e:
            return CommandResult.fail(f"Error loading tree: {e}", context=context)


class ExportCommand(Command):
    """Export current tree to various formats."""

    @property
    def name(self) -> str:
        return "export"

    @property
    def description(self) -> str:
        return "Export tree to various formats"

    @property
    def usage(self) -> str:
        return "export <filename> [--format FORMAT] [tree_name]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not args:
            return CommandResult.fail(
                "Usage: export <filename> [--format FORMAT] [tree_name]\n"
                "Formats: json, flat, yaml, xml, dot, mermaid",
                context=context
            )

        filename = args[0]
        export_format = None
        tree_name = None

        # Parse options
        i = 1
        while i < len(args):
            if args[i] == '--format' and i + 1 < len(args):
                export_format = args[i + 1]
                i += 2
            else:
                tree_name = args[i]
                i += 1

        # Auto-detect format from extension if not specified
        if not export_format:
            ext = os.path.splitext(filename)[1].lower()
            format_map = {
                '.json': 'json',
                '.yaml': 'yaml',
                '.yml': 'yaml',
                '.xml': 'xml',
                '.dot': 'dot',
                '.gv': 'dot',
                '.mmd': 'mermaid',
            }
            export_format = format_map.get(ext, 'json')

        # Determine which tree to export
        if tree_name:
            tree = context.forest.get(tree_name)
            if not tree:
                return CommandResult.fail(f"Tree '{tree_name}' not found", context=context)
        else:
            if not context.current_tree:
                return CommandResult.fail("Not in a tree. Use: export <filename> <tree_name>", context=context)
            tree = context.current_tree
            tree_name = context.current_tree_name

        # Export tree
        try:
            from AlgoTree.exporters import export_tree

            output = export_tree(tree.root, export_format)

            with open(filename, 'w') as f:
                f.write(output)

            return CommandResult.ok(
                output=f"Exported tree '{tree_name}' to {filename} ({export_format})",
                context=context
            )
        except Exception as e:
            return CommandResult.fail(f"Error exporting tree: {e}", context=context)


class ToGraphCommand(Command):
    """Convert current tree/node to AlgoGraph Graph.

    Requires AlgoGraph to be installed or in PYTHONPATH.
    """

    @property
    def name(self) -> str:
        return "tograph"

    @property
    def description(self) -> str:
        return "Convert tree to AlgoGraph (requires AlgoGraph)"

    @property
    def usage(self) -> str:
        return "tograph [--undirected] [tree_name]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not ALGOGRAPH_AVAILABLE:
            return CommandResult.fail(
                "AlgoGraph not available. Install AlgoGraph or add it to PYTHONPATH.",
                context=context
            )

        # Parse options
        directed = True
        tree_name = None

        for arg in args:
            if arg == '--undirected':
                directed = False
            else:
                tree_name = arg

        # Determine which tree to convert
        if tree_name:
            tree = context.forest.get(tree_name)
            if not tree:
                return CommandResult.fail(f"Tree '{tree_name}' not found", context=context)
            node = tree.root
        else:
            node = context.current_node
            if not node:
                return CommandResult.fail("Not in a tree", context=context)
            tree_name = context.current_tree_name or "tree"

        # Convert to graph
        try:
            from AlgoTree.interop import tree_to_graph
            graph = tree_to_graph(node, directed=directed)

            # Display graph info
            lines = [
                f"Converted '{tree_name}' to AlgoGraph:",
                f"  Vertices: {graph.vertex_count}",
                f"  Edges: {graph.edge_count}",
                f"  Directed: {directed}",
            ]

            return CommandResult.ok(output='\n'.join(lines), context=context)
        except Exception as e:
            return CommandResult.fail(f"Error converting to graph: {e}", context=context)


class FromGraphCommand(Command):
    """Convert AlgoGraph Graph to tree (requires root vertex).

    Requires AlgoGraph to be installed or in PYTHONPATH.
    This command loads a graph from a JSON file and converts it to a tree.
    """

    @property
    def name(self) -> str:
        return "fromgraph"

    @property
    def description(self) -> str:
        return "Load graph from file and convert to tree"

    @property
    def usage(self) -> str:
        return "fromgraph <filename> <root_vertex> [tree_name]"

    def execute(self, context: ShellContext, args: List[str], pipe_input: Any = None) -> CommandResult:
        if not ALGOGRAPH_AVAILABLE:
            return CommandResult.fail(
                "AlgoGraph not available. Install AlgoGraph or add it to PYTHONPATH.",
                context=context
            )

        if len(args) < 2:
            return CommandResult.fail(
                "Usage: fromgraph <filename> <root_vertex> [tree_name]",
                context=context
            )

        filename = args[0]
        root_vertex = args[1]
        tree_name = args[2] if len(args) > 2 else root_vertex

        # Load graph from file
        try:
            from AlgoGraph import load_graph
            from AlgoTree.interop import graph_to_tree
            from AlgoTree.tree import Tree

            graph = load_graph(filename)
            node = graph_to_tree(graph, root_vertex)
            tree = Tree(node)

            # Add to forest
            new_forest = context.forest.set(tree_name, tree)
            new_context = context.update_forest(new_forest)

            return CommandResult.ok(
                output=f"Loaded graph from {filename} as tree '{tree_name}' (root: {root_vertex})",
                context=new_context
            )
        except FileNotFoundError:
            return CommandResult.fail(f"File not found: {filename}", context=context)
        except ValueError as e:
            return CommandResult.fail(str(e), context=context)
        except Exception as e:
            return CommandResult.fail(f"Error loading graph: {e}", context=context)
