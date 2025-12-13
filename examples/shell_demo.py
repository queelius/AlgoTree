#!/usr/bin/env python
"""
Demo of AlgoTree Shell functionality.

This script demonstrates:
1. Creating a forest with multiple trees
2. Navigating through trees using shell commands
3. Querying and transforming trees
4. Using the interactive shell
"""

from AlgoTree.node import Node
from AlgoTree.shell import Forest, ShellContext, TreeShell
from AlgoTree.shell.builtins import create_builtin_registry


def create_demo_forest():
    """Create a demo forest with example trees."""

    # Create a file system-like tree
    filesystem = Node("root",
        Node("home",
            Node("alice",
                Node("documents", attrs={"size": 1024}),
                Node("photos", attrs={"size": 2048}),
            ),
            Node("bob",
                Node("projects", attrs={"size": 512}),
            )
        ),
        Node("var",
            Node("log", attrs={"size": 256}),
            Node("tmp", attrs={"size": 128}),
        )
    )

    # Create an organization tree
    org = Node("Company",
        Node("Engineering",
            Node("Frontend",
                Node("Alice", attrs={"role": "Senior Dev"}),
                Node("Bob", attrs={"role": "Junior Dev"}),
            ),
            Node("Backend",
                Node("Charlie", attrs={"role": "Tech Lead"}),
                Node("Diana", attrs={"role": "Senior Dev"}),
            )
        ),
        Node("Marketing",
            Node("Eve", attrs={"role": "Manager"}),
            Node("Frank", attrs={"role": "Analyst"}),
        )
    )

    # Create a taxonomy tree
    taxonomy = Node("Animals",
        Node("Mammals",
            Node("Primates",
                Node("Humans"),
                Node("Apes"),
            ),
            Node("Felines",
                Node("Lion", attrs={"habitat": "savanna"}),
                Node("Tiger", attrs={"habitat": "jungle"}),
            )
        ),
        Node("Birds",
            Node("Raptors",
                Node("Eagle", attrs={"wingspan": 2.3}),
                Node("Hawk", attrs={"wingspan": 1.5}),
            )
        )
    )

    # Create forest
    forest = Forest({
        "filesystem": filesystem,
        "organization": org,
        "taxonomy": taxonomy,
    })

    return forest


def demo_programmatic_api():
    """Demonstrate programmatic shell API."""
    print("=" * 70)
    print("DEMO: Programmatic Shell API")
    print("=" * 70)
    print()

    # Create forest
    forest = create_demo_forest()

    # Create context at forest root
    ctx = ShellContext(forest)
    print(f"Starting at: {ctx.pwd()}")
    print()

    # Navigate to filesystem tree
    print(">>> cd filesystem")
    ctx = ctx.cd("filesystem")
    print(f"Now at: {ctx.pwd()}")
    print()

    # List children
    print(">>> ls")
    from AlgoTree.shell.builtins import LsCommand
    ls_cmd = LsCommand()
    result = ls_cmd.execute(ctx, [])
    print(result.output)
    print()

    # Navigate deeper
    print(">>> cd home/alice")
    ctx = ctx.cd("home")
    ctx = ctx.cd("alice")
    print(f"Now at: {ctx.pwd()}")
    print()

    # Show tree structure
    print(">>> tree")
    from AlgoTree.shell.builtins import TreeCommand
    tree_cmd = TreeCommand()
    result = tree_cmd.execute(ctx, [])
    print(result.output)
    print()

    # Go to organization tree
    print(">>> cd /organization/Engineering")
    ctx = ctx.cd("/organization/Engineering")
    print(f"Now at: {ctx.pwd()}")
    print()

    # Find all nodes with "Senior" in role
    print(">>> select n.get('role', '').startswith('Senior')")
    from AlgoTree.shell.advanced import SelectCommand
    select_cmd = SelectCommand()
    result = select_cmd.execute(ctx, ["n.get('role', '').startswith('Senior')"])
    print(result.output)
    print()

    # Show all leaves
    print(">>> leaves")
    from AlgoTree.shell.advanced import LeavesCommand
    leaves_cmd = LeavesCommand()
    result = leaves_cmd.execute(ctx, [])
    print(result.output)
    print()

    # Get stats
    print(">>> stat")
    from AlgoTree.shell.builtins import StatCommand
    stat_cmd = StatCommand()
    result = stat_cmd.execute(ctx, [])
    print(result.output)
    print()


def demo_command_execution():
    """Demonstrate executing commands from strings."""
    print("=" * 70)
    print("DEMO: Command Execution")
    print("=" * 70)
    print()

    # Create forest
    forest = create_demo_forest()

    # Create shell
    shell = TreeShell(forest)

    # Execute commands
    commands = [
        "cd taxonomy",
        "pwd",
        "ls -l",
        "cd Mammals/Felines",
        "tree",
        "find .*Tiger.*",
        "stat Lion",
    ]

    for cmd in commands:
        print(f">>> {cmd}")
        shell.execute_line(cmd)
        print()


def demo_tree_operations():
    """Demonstrate tree transformation operations."""
    print("=" * 70)
    print("DEMO: Tree Operations")
    print("=" * 70)
    print()

    # Create a simple tree
    tree = Node("root",
        Node("a", attrs={"value": 10}),
        Node("b", attrs={"value": 20}),
        Node("c", attrs={"value": 30}),
    )

    forest = Forest({"numbers": tree})
    ctx = ShellContext(forest, "numbers")

    print("Original tree:")
    from AlgoTree.shell.builtins import TreeCommand
    tree_cmd = TreeCommand()
    result = tree_cmd.execute(ctx, [])
    print(result.output)
    print()

    # Add a new node
    print(">>> mkdir d")
    from AlgoTree.shell.builtins import MkdirCommand
    mkdir_cmd = MkdirCommand()
    result = mkdir_cmd.execute(ctx, ["d"])
    ctx = result.context
    print(result.output)
    print()

    print("After adding node:")
    result = tree_cmd.execute(ctx, [])
    print(result.output)
    print()

    # Select nodes with value > 15
    print(">>> select n.get('value', 0) > 15")
    from AlgoTree.shell.advanced import SelectCommand
    select_cmd = SelectCommand()
    result = select_cmd.execute(ctx, ["n.get('value', 0) > 15"])
    print(result.output)
    print()


def run_interactive_shell():
    """Run the interactive shell."""
    print("=" * 70)
    print("DEMO: Interactive Shell")
    print("=" * 70)
    print()
    print("Creating demo forest and launching interactive shell...")
    print("Try these commands:")
    print("  - help              # Show all commands")
    print("  - ls                # List trees in forest")
    print("  - cd filesystem     # Enter a tree")
    print("  - tree              # Show tree structure")
    print("  - cd home/alice     # Navigate deeper")
    print("  - pwd               # Show current path")
    print("  - stat              # Show node details")
    print("  - find .*           # Find all nodes")
    print("  - select n.depth > 1  # Select by predicate")
    print("  - exit              # Quit shell")
    print()

    # Create forest and shell
    forest = create_demo_forest()
    shell = TreeShell(forest)

    # Run shell
    shell.run()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        # Run interactive shell
        run_interactive_shell()
    else:
        # Run demos
        demo_programmatic_api()
        print("\n\n")
        demo_command_execution()
        print("\n\n")
        demo_tree_operations()
        print("\n\n")
        print("=" * 70)
        print("To try the interactive shell, run:")
        print("  python examples/shell_demo.py --interactive")
        print("=" * 70)
