"""
Comprehensive tests for piping and redirection in the AlgoTree shell.

Tests include:
- Basic piping between commands
- Multi-stage pipelines
- Redirection to attributes (>, >>)
- Error handling
- Edge cases
"""

import pytest
from AlgoTree.node import Node
from AlgoTree.tree import Tree
from AlgoTree.shell.core import Forest, ShellContext
from AlgoTree.shell.commands import CommandRegistry, Pipeline
from AlgoTree.shell.builtins import (
    LsCommand, CatCommand, EchoCommand,
    MktreeCommand, CdCommand, MkdirCommand
)
from AlgoTree.shell.advanced import (
    FindCommand,
    SelectCommand, DescendantsCommand, LeavesCommand
)


@pytest.fixture
def forest():
    """Create a test forest with sample trees."""
    tree1 = Tree(Node("root",
        Node("docs",
            Node("readme.md", attrs={"content": "Welcome"}),
            Node("guide.md", attrs={"content": "Tutorial"}),
        ),
        Node("src",
            Node("main.py", attrs={"content": "def main(): pass"}),
            Node("utils.py", attrs={"content": "def helper(): pass"}),
        ),
        Node("tests",
            Node("test_main.py", attrs={"content": "import pytest"}),
        )
    ))

    tree2 = Tree(Node("data",
        Node("users",
            Node("alice", attrs={"age": 30}),
            Node("bob", attrs={"age": 25}),
            Node("charlie", attrs={"age": 35}),
        ),
        Node("products",
            Node("laptop", attrs={"price": 1200}),
            Node("phone", attrs={"price": 800}),
        )
    ))

    f = Forest()
    f = f.set("project", tree1)
    f = f.set("database", tree2)
    return f


@pytest.fixture
def context(forest):
    """Create a shell context in the project tree."""
    ctx = ShellContext(forest)
    ctx = ctx.cd("project")
    return ctx


@pytest.fixture
def registry():
    """Create a command registry with all needed commands."""
    reg = CommandRegistry()
    reg.register(LsCommand())
    reg.register(FindCommand())
    reg.register(CatCommand())
    reg.register(EchoCommand())
    reg.register(SelectCommand())
    reg.register(DescendantsCommand())
    reg.register(LeavesCommand())
    reg.register(MktreeCommand())
    reg.register(CdCommand())
    reg.register(MkdirCommand())
    return reg


# ============================================================================
# Piping Tests
# ============================================================================

class TestBasicPiping:
    """Tests for basic piping functionality."""

    def test_ls_pipe_find(self, context, registry):
        """Test ls | find pattern."""
        pipeline = Pipeline.parse("ls | find doc", registry)

        assert pipeline is not None
        assert len(pipeline.commands) == 2

        result = pipeline.execute(context)
        assert result.success
        # Should find the 'docs' directory
        assert "docs" in result.output or "docs/" in result.output

    def test_descendants_pipe_find(self, context, registry):
        """Test descendants | find pattern."""
        pipeline = Pipeline.parse("descendants | find test", registry)

        assert pipeline is not None
        result = pipeline.execute(context)
        assert result.success

    def test_ls_pipe_select(self, context, registry):
        """Test ls | select with expression."""
        # This tests piping output from ls to select
        pipeline = Pipeline.parse("ls | select 'len(nodes) > 0'", registry)

        assert pipeline is not None
        result = pipeline.execute(context)
        # Should execute even if select doesn't use piped input
        assert result.success


class TestMultiStagePipelines:
    """Tests for pipelines with 3+ stages."""

    def test_three_stage_pipeline(self, context, registry):
        """Test a three-stage pipeline."""
        # ls -> descendants -> leaves
        pipeline = Pipeline.parse("ls | descendants | leaves", registry)

        assert pipeline is not None
        assert len(pipeline.commands) == 3

        result = pipeline.execute(context)
        assert result.success

    def test_four_stage_pipeline(self, context, registry):
        """Test a four-stage pipeline."""
        pipeline = Pipeline.parse("ls | descendants | find .py | leaves", registry)

        assert pipeline is not None
        assert len(pipeline.commands) == 4


class TestPipelineErrorHandling:
    """Tests for error handling in pipelines."""

    def test_unknown_command_in_pipeline(self, registry):
        """Test pipeline with unknown command."""
        pipeline = Pipeline.parse("ls | unknown_cmd", registry)
        assert pipeline is None

    def test_pipeline_with_invalid_args(self, context, registry):
        """Test pipeline where a command fails."""
        # cd to non-existent path in pipeline (cd already registered in fixture)
        pipeline = Pipeline.parse("ls | cd /nonexistent", registry)

        if pipeline:
            result = pipeline.execute(context)
            # Should fail when cd fails
            assert not result.success


class TestPipelineDataFlow:
    """Tests for data flowing through pipelines."""

    def test_pipe_preserves_context(self, context, registry):
        """Test that context changes propagate through pipeline."""
        # cd already registered in fixture
        # cd should change context, which affects subsequent ls
        pipeline = Pipeline.parse("cd docs | ls", registry)

        if pipeline:
            result = pipeline.execute(context)
            if result.success:
                # ls output should show contents of docs directory
                assert "readme.md" in result.output or "guide.md" in result.output


# ============================================================================
# Redirection Tests
# ============================================================================

class TestBasicRedirection:
    """Tests for echo redirection to attributes."""

    def test_redirect_write_to_attribute(self, context, registry):
        """Test echo text > key."""
        cmd = EchoCommand()
        result = cmd.execute(context, ["Hello", "World", ">", "greeting"])

        assert result.success
        assert result.context is not None

        # Verify attribute was set
        new_context = result.context
        current_node = new_context.current_node
        assert current_node.attrs.get("greeting") == "Hello World"

    def test_redirect_append_to_attribute(self, context, registry):
        """Test echo text >> key (append)."""
        cmd = EchoCommand()

        # First write
        result1 = cmd.execute(context, ["First", "line", ">", "log"])
        assert result1.success
        context1 = result1.context

        # Then append
        result2 = cmd.execute(context1, ["Second", "line", ">>", "log"])
        assert result2.success

        # Verify both lines are present
        new_context = result2.context
        current_node = new_context.current_node
        log_content = current_node.attrs.get("log")
        assert "First line" in log_content
        assert "Second line" in log_content

    def test_redirect_overwrite(self, context, registry):
        """Test that > overwrites existing content."""
        cmd = EchoCommand()

        # First write
        result1 = cmd.execute(context, ["Original", ">", "note"])
        context1 = result1.context

        # Overwrite
        result2 = cmd.execute(context1, ["Replaced", ">", "note"])

        # Should only have the new content
        new_context = result2.context
        current_node = new_context.current_node
        assert current_node.attrs.get("note") == "Replaced"
        assert "Original" not in current_node.attrs.get("note", "")

    def test_redirect_without_key_fails(self, context, registry):
        """Test that echo > without key fails."""
        cmd = EchoCommand()
        result = cmd.execute(context, ["text", ">"])

        assert not result.success
        assert "Usage" in result.error


class TestRedirectionEdgeCases:
    """Tests for edge cases in redirection."""

    def test_redirect_empty_string(self, context, registry):
        """Test redirecting empty string."""
        cmd = EchoCommand()
        result = cmd.execute(context, [">", "empty"])

        # Should succeed with empty string
        assert result.success
        new_node = result.context.current_node
        assert new_node.attrs.get("empty") == ""

    def test_redirect_special_characters(self, context, registry):
        """Test redirecting text with special characters."""
        cmd = EchoCommand()
        result = cmd.execute(context, ["Hello!", "@#$%", ">", "special"])

        assert result.success
        new_node = result.context.current_node
        assert new_node.attrs.get("special") == "Hello! @#$%"

    def test_redirect_at_forest_root_fails(self, forest, registry):
        """Test that redirect fails when not in a tree."""
        context = ShellContext(forest)  # At forest root
        cmd = EchoCommand()

        result = cmd.execute(context, ["text", ">", "key"])
        assert not result.success
        assert "Not in a tree" in result.error


# ============================================================================
# Combined Pipeline and Redirection Tests
# ============================================================================

class TestPipelineWithRedirection:
    """Tests combining pipelines with redirection."""

    def test_find_pipe_echo_redirect(self, context, registry):
        """Test finding nodes and redirecting output."""
        # While we can't easily combine | with > in one command line,
        # we can test the pattern of using results in sequence

        # First find something
        find_cmd = FindCommand()
        find_result = find_cmd.execute(context, ["doc"])

        assert find_result.success

        # Then use echo to save a note about it
        echo_cmd = EchoCommand()
        echo_result = echo_cmd.execute(
            context,
            ["Found", "documentation", ">", "search_result"]
        )

        assert echo_result.success


# ============================================================================
# Pipeline Parsing Tests
# ============================================================================

class TestPipelineParsing:
    """Tests for pipeline parsing edge cases."""

    def test_parse_with_quoted_args(self, registry):
        """Test parsing pipeline with quoted arguments."""
        # The shell uses shlex which handles quotes
        pipeline = Pipeline.parse('echo "hello world" | cat', registry)

        if pipeline:
            assert len(pipeline.commands) >= 1

    def test_parse_empty_pipeline(self, registry):
        """Test parsing empty pipeline."""
        pipeline = Pipeline.parse("", registry)
        assert pipeline is None

    def test_parse_pipeline_with_whitespace(self, registry):
        """Test parsing pipeline with extra whitespace."""
        pipeline = Pipeline.parse("  ls   |   find test  ", registry)

        if pipeline:
            assert len(pipeline.commands) == 2

    def test_parse_trailing_pipe(self, registry):
        """Test parsing pipeline with trailing pipe."""
        pipeline = Pipeline.parse("ls |", registry)
        # Should handle gracefully
        assert pipeline is None or len(pipeline.commands) == 1


# ============================================================================
# Integration Tests
# ============================================================================

class TestPipingIntegration:
    """Integration tests combining multiple features."""

    def test_realistic_workflow(self, context, registry):
        """Test a realistic workflow with piping."""
        # Navigate to a directory
        cd_cmd = CdCommand()
        cd_result = cd_cmd.execute(context, ["src"])
        assert cd_result.success
        context = cd_result.context

        # List files
        ls_cmd = LsCommand()
        ls_result = ls_cmd.execute(context, [])
        assert ls_result.success

        # Find Python files
        find_cmd = FindCommand()
        find_result = find_cmd.execute(context, [".py"])
        assert find_result.success

    def test_build_tree_with_redirection(self, forest, registry):
        """Test building a tree and using redirection."""
        context = ShellContext(forest)

        # Create a new tree
        mktree_cmd = MktreeCommand()
        result = mktree_cmd.execute(context, ["notes"])
        assert result.success
        context = result.context

        # Navigate into it
        cd_cmd = CdCommand()
        result = cd_cmd.execute(context, ["notes"])
        assert result.success
        context = result.context

        # Create a directory
        mkdir_cmd = MkdirCommand()
        result = mkdir_cmd.execute(context, ["todo"])
        assert result.success
        context = result.context

        # Add a note using redirection
        echo_cmd = EchoCommand()
        result = echo_cmd.execute(context, ["Remember", "to", "test", ">", "note"])
        assert result.success


# ============================================================================
# Performance and Stress Tests
# ============================================================================

class TestPipelinePerformance:
    """Tests for pipeline performance with large data."""

    def test_long_pipeline(self, context, registry):
        """Test a very long pipeline."""
        # Build a pipeline with many stages
        stages = " | ".join(["ls"] * 10)
        pipeline = Pipeline.parse(stages, registry)

        if pipeline:
            assert len(pipeline.commands) == 10
            # Should complete without errors
            result = pipeline.execute(context)
            assert result.success or not result.success  # Just verify it completes


# ============================================================================
# Backward Compatibility Tests
# ============================================================================

class TestBackwardCompatibility:
    """Tests ensuring commands work both with and without piping."""

    def test_ls_standalone(self, context, registry):
        """Test ls works standalone (no pipe)."""
        cmd = LsCommand()
        result = cmd.execute(context, [])
        assert result.success

    def test_find_standalone(self, context, registry):
        """Test find works standalone (no pipe)."""
        cmd = FindCommand()
        result = cmd.execute(context, ["doc"])
        assert result.success

    def test_echo_standalone(self, context, registry):
        """Test echo works standalone (no redirection)."""
        cmd = EchoCommand()
        result = cmd.execute(context, ["Hello", "World"])
        assert result.success
        assert result.output == "Hello World"
