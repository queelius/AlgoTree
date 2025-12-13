#!/usr/bin/env python
"""
Example: Building trees interactively from scratch using the AlgoTree shell.

This demonstrates that you can start with an empty forest and build
trees completely using shell commands, without needing to load a file.
"""

from AlgoTree.shell import TreeShell


def example1_simple_tree():
    """Build a simple file system tree from scratch."""
    print("=" * 70)
    print("Example 1: Building a Simple File System")
    print("=" * 70)
    print()

    shell = TreeShell()

    commands = [
        ("pwd", "Start at forest root"),
        ("mktree filesystem", "Create a new tree called 'filesystem'"),
        ("ls", "List trees in forest"),
        ("cd filesystem", "Enter the tree"),
        ("mkdir home", "Create home directory"),
        ("mkdir var", "Create var directory"),
        ("ls", "List directories"),
        ("cd home", "Enter home directory"),
        ("mkdir alice", "Create alice's home"),
        ("mkdir bob", "Create bob's home"),
        ("ls", "List users"),
        ("cd alice", "Enter alice's directory"),
        ("touch documents", "Create documents folder"),
        ("touch photos", "Create photos folder"),
        ("ls", "List alice's folders"),
        ("cd ../..", "Go back to filesystem root"),
        ("tree", "Show final structure"),
    ]

    for cmd, description in commands:
        print(f"# {description}")
        print(f"$ {cmd}")
        shell.execute_line(cmd)
        print()

    print()


def example2_organization_chart():
    """Build an organization chart from scratch."""
    print("=" * 70)
    print("Example 2: Building an Organization Chart")
    print("=" * 70)
    print()

    shell = TreeShell()

    commands = [
        ("mktree company 'Acme Corp'", "Create company tree with custom root"),
        ("cd company", "Enter company"),
        ("mkdir Engineering", "Create Engineering department"),
        ("mkdir Marketing", "Create Marketing department"),
        ("mkdir Sales", "Create Sales department"),
        ("tree", "Show departments"),
        ("cd Engineering", "Enter Engineering"),
        ("mkdir Frontend", "Create Frontend team"),
        ("mkdir Backend", "Create Backend team"),
        ("cd Frontend", "Enter Frontend team"),
        ("touch Alice", "Add Alice to Frontend"),
        ("touch Bob", "Add Bob to Frontend"),
        ("cd ../Backend", "Go to Backend team"),
        ("touch Charlie", "Add Charlie to Backend"),
        ("touch Diana", "Add Diana to Backend"),
        ("cd ../..", "Return to company root"),
        ("tree", "Show complete org chart"),
        ("size", "Count total employees"),
    ]

    for cmd, description in commands:
        print(f"# {description}")
        print(f"$ {cmd}")
        shell.execute_line(cmd)
        print()

    print()


def example3_project_structure():
    """Build a project directory structure."""
    print("=" * 70)
    print("Example 3: Building a Project Structure")
    print("=" * 70)
    print()

    shell = TreeShell()

    commands = [
        ("mktree myproject", "Create project"),
        ("cd myproject", "Enter project"),
        ("mkdir src", "Create source directory"),
        ("mkdir test", "Create test directory"),
        ("mkdir docs", "Create documentation directory"),
        ("cd src", "Enter source directory"),
        ("touch __init__.py", "Add init file"),
        ("touch main.py", "Add main module"),
        ("touch utils.py", "Add utilities module"),
        ("mkdir models", "Add models package"),
        ("cd models", "Enter models"),
        ("touch __init__.py", "Add models init"),
        ("touch user.py", "Add user model"),
        ("touch product.py", "Add product model"),
        ("cd ../../test", "Go to test directory"),
        ("touch test_main.py", "Add main tests"),
        ("touch test_utils.py", "Add utils tests"),
        ("cd ..", "Return to project root"),
        ("tree", "Show complete project structure"),
        ("find .*\\.py$", "Find all Python files"),
    ]

    for cmd, description in commands:
        print(f"# {description}")
        print(f"$ {cmd}")
        shell.execute_line(cmd)
        print()

    print()


def example4_multiple_trees():
    """Work with multiple trees in the same forest."""
    print("=" * 70)
    print("Example 4: Managing Multiple Trees")
    print("=" * 70)
    print()

    shell = TreeShell()

    commands = [
        ("mktree tree1", "Create first tree"),
        ("mktree tree2", "Create second tree"),
        ("mktree tree3", "Create third tree"),
        ("ls", "List all trees"),
        ("cd tree1", "Enter first tree"),
        ("mkdir a", "Add some nodes"),
        ("mkdir b", ""),
        ("cd /tree2", "Jump to second tree"),
        ("mkdir x", "Add different nodes"),
        ("mkdir y", ""),
        ("cd /", "Return to forest root"),
        ("ls", "See all trees"),
        ("cd tree1", "Go to tree1"),
        ("tree", "Show tree1 structure"),
        ("cd /tree2", "Go to tree2"),
        ("tree", "Show tree2 structure"),
        ("cd /", "Return to root"),
        ("rmtree tree3", "Remove unused tree"),
        ("ls", "Verify tree3 is gone"),
    ]

    for cmd, description in commands:
        if description:  # Only print if description exists
            print(f"# {description}")
        print(f"$ {cmd}")
        shell.execute_line(cmd)
        print()

    print()


def example5_interactive_exploration():
    """Show how to explore and query a built tree."""
    print("=" * 70)
    print("Example 5: Exploring and Querying Trees")
    print("=" * 70)
    print()

    shell = TreeShell()

    # Build a tree with some structure
    build_commands = [
        "mktree data",
        "cd data",
        "mkdir level1",
        "cd level1",
        "mkdir level2a",
        "mkdir level2b",
        "cd level2a",
        "touch leaf1",
        "touch leaf2",
        "cd ../level2b",
        "touch leaf3",
        "touch leaf4",
        "cd ../..",
    ]

    print("# Building a sample tree...")
    for cmd in build_commands:
        shell.execute_line(cmd)
    print()

    # Now explore it
    commands = [
        ("pwd", "Current location"),
        ("tree", "Visualize structure"),
        ("leaves", "Find all leaf nodes"),
        ("descendants", "Show all descendants"),
        ("size", "Count total nodes"),
        ("height", "Get tree height"),
        ("cd level1", "Navigate down"),
        ("depth", "Current depth"),
        ("siblings", "Show siblings (none)"),
        ("cd level2a", "Go deeper"),
        ("depth", "Current depth now"),
        ("ancestors", "Show path to root"),
        ("ls", "List children"),
        ("stat", "Detailed node info"),
        ("select n.is_leaf", "Select only leaves"),
        ("find leaf.*", "Find nodes matching pattern"),
    ]

    for cmd, description in commands:
        print(f"# {description}")
        print(f"$ {cmd}")
        shell.execute_line(cmd)
        print()

    print()


if __name__ == "__main__":
    example1_simple_tree()
    example2_organization_chart()
    example3_project_structure()
    example4_multiple_trees()
    example5_interactive_exploration()

    print("=" * 70)
    print("All examples completed!")
    print()
    print("To try these interactively, run:")
    print("  algotree shell")
    print()
    print("Or:")
    print("  python -m AlgoTree.shell.shell")
    print("=" * 70)
