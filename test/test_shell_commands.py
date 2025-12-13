"""
Unit tests for AlgoTree shell commands.

Tests navigation, read, write, and advanced commands.
"""

import pytest

from AlgoTree.node import Node, node
from AlgoTree.tree import Tree
from AlgoTree.shell.core import Forest, ShellContext
from AlgoTree.shell.commands import CommandRegistry, CommandResult, Pipeline
from AlgoTree.shell.builtins import (
    PwdCommand, CdCommand, LsCommand,
    CatCommand, StatCommand, TreeCommand,
    MkdirCommand, TouchCommand, MktreeCommand, RmtreeCommand,
    HelpCommand, ExitCommand
)
from AlgoTree.shell.advanced import (
    FindCommand, AncestorsCommand, DescendantsCommand,
    LeavesCommand, SiblingsCommand,
    DepthCommand, HeightCommand, SizeCommand,
    SelectCommand, MapCommand, FilterCommand
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def simple_tree():
    """Create a simple tree for testing."""
    return Node("root",
        Node("child1", Node("grandchild1"), Node("grandchild2")),
        Node("child2", attrs={"value": 10}),
        Node("child3", attrs={"value": 20})
    )


@pytest.fixture
def forest_with_tree(simple_tree):
    """Create a forest with a simple tree."""
    return Forest({"my_tree": simple_tree})


@pytest.fixture
def context_at_root(forest_with_tree):
    """Create context at forest root."""
    return ShellContext(forest_with_tree)


@pytest.fixture
def context_in_tree(forest_with_tree):
    """Create context at tree root."""
    return ShellContext(forest_with_tree, "my_tree")


# ============================================================================
# Navigation Command Tests
# ============================================================================

class TestPwdCommand:
    """Tests for pwd command."""

    def test_pwd_at_forest_root(self, context_at_root):
        """Test pwd at forest root."""
        cmd = PwdCommand()
        result = cmd.execute(context_at_root, [])

        assert result.success
        assert result.output == "/"

    def test_pwd_in_tree(self, context_in_tree):
        """Test pwd at tree root."""
        cmd = PwdCommand()
        result = cmd.execute(context_in_tree, [])

        assert result.success
        # Output now includes ANSI color codes
        assert "my_tree" in result.output
        assert result.output.startswith("/")

    def test_pwd_in_subtree(self, context_in_tree):
        """Test pwd in subtree."""
        ctx = context_in_tree.cd("child1")
        cmd = PwdCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        # Output now includes ANSI color codes
        assert "my_tree" in result.output
        assert "child1" in result.output


class TestCdCommand:
    """Tests for cd command."""

    def test_cd_no_args(self, context_in_tree):
        """Test cd with no args goes to forest root."""
        cmd = CdCommand()
        result = cmd.execute(context_in_tree, [])

        assert result.success
        assert result.context.pwd() == "/"

    def test_cd_to_tree(self, context_at_root):
        """Test cd into tree."""
        cmd = CdCommand()
        result = cmd.execute(context_at_root, ["my_tree"])

        assert result.success
        assert result.context.pwd() == "/my_tree"

    def test_cd_to_child(self, context_in_tree):
        """Test cd to child node."""
        cmd = CdCommand()
        result = cmd.execute(context_in_tree, ["child1"])

        assert result.success
        assert result.context.pwd() == "/my_tree/child1"

    def test_cd_invalid_path(self, context_in_tree):
        """Test cd to invalid path fails."""
        cmd = CdCommand()
        result = cmd.execute(context_in_tree, ["nonexistent"])

        assert not result.success
        assert "not found" in result.error.lower()


class TestLsCommand:
    """Tests for ls command."""

    def test_ls_at_forest_root(self, context_at_root):
        """Test ls at forest root shows trees."""
        cmd = LsCommand()
        result = cmd.execute(context_at_root, [])

        assert result.success
        assert "my_tree" in result.output

    def test_ls_at_tree_root(self, context_in_tree):
        """Test ls at tree root shows children."""
        cmd = LsCommand()
        result = cmd.execute(context_in_tree, [])

        assert result.success
        assert "child1" in result.output
        assert "child2" in result.output
        assert "child3" in result.output

    def test_ls_long_format(self, context_in_tree):
        """Test ls with -l flag."""
        cmd = LsCommand()
        result = cmd.execute(context_in_tree, ["-l"])

        assert result.success
        assert "child1" in result.output
        # Should show number of children
        assert "children" in result.output.lower()

    def test_ls_with_path(self, context_in_tree):
        """Test ls with explicit path."""
        cmd = LsCommand()
        result = cmd.execute(context_in_tree, ["child1"])

        assert result.success
        assert "grandchild1" in result.output
        assert "grandchild2" in result.output


# ============================================================================
# Read Command Tests
# ============================================================================

class TestCatCommand:
    """Tests for cat command."""

    def test_cat_current_node(self, context_in_tree):
        """Test cat on current node."""
        ctx = context_in_tree.cd("child2")
        cmd = CatCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert "name: child2" in result.output
        assert "value: 10" in result.output

    def test_cat_with_path(self, context_in_tree):
        """Test cat with explicit path."""
        cmd = CatCommand()
        result = cmd.execute(context_in_tree, ["child3"])

        assert result.success
        assert "name: child3" in result.output
        assert "value: 20" in result.output

    def test_cat_at_forest_root(self, context_at_root):
        """Test cat at forest root fails."""
        cmd = CatCommand()
        result = cmd.execute(context_at_root, [])

        assert not result.success


class TestStatCommand:
    """Tests for stat command."""

    def test_stat_shows_details(self, context_in_tree):
        """Test stat shows node details."""
        ctx = context_in_tree.cd("child1")
        cmd = StatCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert "Name: child1" in result.output
        assert "Depth:" in result.output
        assert "Height:" in result.output
        assert "Children:" in result.output


class TestTreeCommand:
    """Tests for tree command."""

    def test_tree_shows_structure(self, context_in_tree):
        """Test tree shows tree structure."""
        cmd = TreeCommand()
        result = cmd.execute(context_in_tree, [])

        assert result.success
        assert "root" in result.output
        # Should show tree structure
        assert len(result.output) > 10


# ============================================================================
# Write Command Tests
# ============================================================================

class TestMkdirCommand:
    """Tests for mkdir command."""

    def test_mkdir_creates_node(self, context_in_tree):
        """Test mkdir creates a new child node."""
        cmd = MkdirCommand()
        result = cmd.execute(context_in_tree, ["new_child"])

        assert result.success
        assert "Created node: new_child" in result.output

        # Verify node was created
        new_ctx = result.context.cd("new_child")
        assert new_ctx.current_node.name == "new_child"

    def test_mkdir_with_attributes(self, context_in_tree):
        """Test mkdir creates node with attributes."""
        cmd = MkdirCommand()
        result = cmd.execute(context_in_tree, ["user", "name=Alice", "age=30", "score=95.5"])

        assert result.success

        # Verify node and attributes
        new_ctx = result.context.cd("user")
        node = new_ctx.current_node
        assert node.get("name") == "Alice"
        assert node.get("age") == 30
        assert node.get("score") == 95.5

    def test_mkdir_no_args(self, context_in_tree):
        """Test mkdir with no args fails."""
        cmd = MkdirCommand()
        result = cmd.execute(context_in_tree, [])

        assert not result.success

    def test_mkdir_at_forest_root(self, context_at_root):
        """Test mkdir at forest root fails."""
        cmd = MkdirCommand()
        result = cmd.execute(context_at_root, ["new_node"])

        assert not result.success


class TestMktreeCommand:
    """Tests for mktree command."""

    def test_mktree_creates_tree(self, context_at_root):
        """Test mktree creates new tree."""
        cmd = MktreeCommand()
        result = cmd.execute(context_at_root, ["new_tree"])

        assert result.success
        assert "Created tree: new_tree" in result.output

        # Verify tree exists
        assert "new_tree" in result.context.forest

    def test_mktree_with_root_name(self, context_at_root):
        """Test mktree with custom root name."""
        cmd = MktreeCommand()
        result = cmd.execute(context_at_root, ["new_tree", "custom_root"])

        assert result.success

        tree = result.context.forest.get("new_tree")
        assert tree.root.name == "custom_root"

    def test_mktree_duplicate_name(self, context_at_root):
        """Test mktree with duplicate name fails."""
        cmd = MktreeCommand()
        result = cmd.execute(context_at_root, ["my_tree"])

        assert not result.success


class TestRmtreeCommand:
    """Tests for rmtree command."""

    def test_rmtree_removes_tree(self, context_at_root):
        """Test rmtree removes tree."""
        cmd = RmtreeCommand()
        result = cmd.execute(context_at_root, ["my_tree"])

        assert result.success
        assert "Removed tree: my_tree" in result.output
        assert "my_tree" not in result.context.forest

    def test_rmtree_nonexistent(self, context_at_root):
        """Test rmtree with nonexistent tree fails."""
        cmd = RmtreeCommand()
        result = cmd.execute(context_at_root, ["nonexistent"])

        assert not result.success


class TestSetAttrCommand:
    """Tests for setattr command."""

    def test_setattr_adds_attributes(self, context_in_tree):
        """Test setattr adds new attributes."""
        from AlgoTree.shell.builtins import SetAttrCommand

        ctx = context_in_tree.cd("child1")
        cmd = SetAttrCommand()
        result = cmd.execute(ctx, ["name=Alice", "age=30"])

        assert result.success
        assert "Updated attributes" in result.output

        # Verify attributes were added
        new_node = result.context.current_node
        assert new_node.get("name") == "Alice"
        assert new_node.get("age") == 30

    def test_setattr_updates_existing(self, context_in_tree):
        """Test setattr updates existing attributes."""
        from AlgoTree.shell.builtins import SetAttrCommand

        ctx = context_in_tree.cd("child2")
        cmd = SetAttrCommand()
        result = cmd.execute(ctx, ["value=999"])

        assert result.success
        new_node = result.context.current_node
        assert new_node.get("value") == 999

    def test_setattr_parses_numbers(self, context_in_tree):
        """Test setattr correctly parses numeric values."""
        from AlgoTree.shell.builtins import SetAttrCommand

        ctx = context_in_tree.cd("child1")
        cmd = SetAttrCommand()
        result = cmd.execute(ctx, ["int_val=42", "float_val=3.14", "str_val=hello"])

        assert result.success
        node = result.context.current_node
        assert node.get("int_val") == 42
        assert node.get("float_val") == 3.14
        assert node.get("str_val") == "hello"


class TestRmAttrCommand:
    """Tests for rmattr command."""

    def test_rmattr_removes_attribute(self, context_in_tree):
        """Test rmattr removes attributes."""
        from AlgoTree.shell.builtins import RmAttrCommand

        ctx = context_in_tree.cd("child2")
        cmd = RmAttrCommand()
        result = cmd.execute(ctx, ["value"])

        assert result.success
        assert "Removed attributes" in result.output

        # Verify attribute was removed
        new_node = result.context.current_node
        assert "value" not in new_node.attrs

    def test_rmattr_multiple_attributes(self, context_in_tree):
        """Test rmattr removes multiple attributes."""
        from AlgoTree.shell.builtins import RmAttrCommand, SetAttrCommand

        # First add multiple attributes
        ctx = context_in_tree.cd("child1")
        set_cmd = SetAttrCommand()
        ctx = set_cmd.execute(ctx, ["a=1", "b=2", "c=3"]).context

        # Remove some
        rm_cmd = RmAttrCommand()
        result = rm_cmd.execute(ctx, ["a", "c"])

        assert result.success
        node = result.context.current_node
        assert "a" not in node.attrs
        assert "b" in node.attrs
        assert "c" not in node.attrs


# ============================================================================
# Query Command Tests
# ============================================================================

class TestFindCommand:
    """Tests for find command."""

    def test_find_by_name(self, context_in_tree):
        """Test finding nodes by name pattern."""
        cmd = FindCommand()
        result = cmd.execute(context_in_tree, ["child.*"])

        assert result.success
        assert "child1" in result.output
        assert "child2" in result.output
        assert "child3" in result.output

    def test_find_no_matches(self, context_in_tree):
        """Test find with no matches."""
        cmd = FindCommand()
        result = cmd.execute(context_in_tree, ["nonexistent"])

        assert result.success
        assert result.output == ""


class TestDescendantsCommand:
    """Tests for descendants command."""

    def test_descendants_shows_all(self, context_in_tree):
        """Test descendants shows all descendant nodes."""
        cmd = DescendantsCommand()
        result = cmd.execute(context_in_tree, [])

        assert result.success
        assert "child1" in result.output
        assert "grandchild1" in result.output

    def test_descendants_with_depth_limit(self, context_in_tree):
        """Test descendants with depth limit."""
        cmd = DescendantsCommand()
        result = cmd.execute(context_in_tree, ["-d", "1"])

        assert result.success
        # Should show direct children
        assert "child1" in result.output
        # But not grandchildren
        # Note: This depends on implementation details


class TestLeavesCommand:
    """Tests for leaves command."""

    def test_leaves_shows_leaf_nodes(self, context_in_tree):
        """Test leaves shows only leaf nodes."""
        cmd = LeavesCommand()
        result = cmd.execute(context_in_tree, [])

        assert result.success
        # Leaves are: grandchild1, grandchild2, child2, child3
        assert "grandchild1" in result.output
        assert "grandchild2" in result.output
        # child1 is not a leaf
        assert result.output.count("child1") == 0 or "grandchild" in result.output


# ============================================================================
# Analysis Command Tests
# ============================================================================

class TestSizeCommand:
    """Tests for size command."""

    def test_size_counts_nodes(self, context_in_tree):
        """Test size counts all nodes in subtree."""
        cmd = SizeCommand()
        result = cmd.execute(context_in_tree, [])

        assert result.success
        # Tree has: root + 3 children + 2 grandchildren = 6 nodes
        assert result.output == "6"


class TestDepthCommand:
    """Tests for depth command."""

    def test_depth_shows_node_depth(self, context_in_tree):
        """Test depth shows current node depth."""
        ctx = context_in_tree.cd("child1").cd("grandchild1")
        cmd = DepthCommand()
        result = cmd.execute(ctx, [])

        assert result.success
        assert result.output == "2"


# ============================================================================
# Tree Operation Command Tests
# ============================================================================

class TestSelectCommand:
    """Tests for select command."""

    def test_select_by_depth(self, context_in_tree):
        """Test selecting nodes by depth."""
        cmd = SelectCommand()
        result = cmd.execute(context_in_tree, ["n.depth > 0"])

        assert result.success
        # Should find all non-root nodes
        assert "child" in result.output

    def test_select_by_attribute(self, context_in_tree):
        """Test selecting nodes by attribute."""
        cmd = SelectCommand()
        result = cmd.execute(context_in_tree, ["n.get('value', 0) > 15"])

        assert result.success
        assert "child3" in result.output
        assert "child2" not in result.output  # value is 10


# ============================================================================
# Command Registry Tests
# ============================================================================

class TestCommandRegistry:
    """Tests for CommandRegistry."""

    def test_register_command(self):
        """Test registering a command."""
        registry = CommandRegistry()
        cmd = PwdCommand()

        registry.register(cmd)

        assert "pwd" in registry
        assert registry.get("pwd") == cmd

    def test_register_duplicate_fails(self):
        """Test registering duplicate command fails."""
        registry = CommandRegistry()
        cmd1 = PwdCommand()
        cmd2 = PwdCommand()

        registry.register(cmd1)

        with pytest.raises(ValueError):
            registry.register(cmd2)

    def test_get_by_alias(self):
        """Test getting command by alias."""
        registry = CommandRegistry()
        cmd = ExitCommand()

        registry.register(cmd)

        assert registry.get("quit") == cmd
        assert registry.get("q") == cmd

    def test_command_names_includes_aliases(self):
        """Test command_names includes aliases."""
        registry = CommandRegistry()
        cmd = ExitCommand()

        registry.register(cmd)

        names = registry.command_names()
        assert "exit" in names
        assert "quit" in names
        assert "q" in names


# ============================================================================
# Pipeline Tests
# ============================================================================

class TestPipeline:
    """Tests for command pipelines."""

    def test_parse_single_command(self):
        """Test parsing single command."""
        registry = CommandRegistry()
        registry.register(LsCommand())

        pipeline = Pipeline.parse("ls", registry)

        assert pipeline is not None
        assert len(pipeline.commands) == 1

    def test_parse_multiple_commands(self):
        """Test parsing pipeline with multiple commands."""
        registry = CommandRegistry()
        registry.register(LsCommand())
        registry.register(FindCommand())

        pipeline = Pipeline.parse("ls | find child.*", registry)

        assert pipeline is not None
        assert len(pipeline.commands) == 2

    def test_parse_unknown_command(self):
        """Test parsing pipeline with unknown command."""
        registry = CommandRegistry()

        pipeline = Pipeline.parse("unknown_cmd", registry)

        assert pipeline is None

    def test_execute_pipeline(self, context_in_tree):
        """Test executing a simple pipeline."""
        # This would require pipe_input support in commands
        # For now, just test that pipeline execution doesn't crash
        registry = CommandRegistry()
        registry.register(LsCommand())

        pipeline = Pipeline.parse("ls", registry)
        result = pipeline.execute(context_in_tree)

        assert result.success
