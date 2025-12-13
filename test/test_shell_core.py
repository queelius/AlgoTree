"""
Unit tests for AlgoTree shell core abstractions.

Tests Forest, TreePath, and ShellContext classes.
"""

import pytest

from AlgoTree.node import Node, node
from AlgoTree.tree import Tree
from AlgoTree.shell.core import Forest, TreePath, ShellContext


class TestForest:
    """Tests for Forest class."""

    def test_empty_forest(self):
        """Test creating an empty forest."""
        forest = Forest()
        assert len(forest) == 0
        assert forest.tree_names() == []

    def test_forest_with_trees(self):
        """Test creating a forest with initial trees."""
        tree1 = node("root1", "child1")
        tree2 = node("root2", "child2")

        forest = Forest({"tree1": tree1, "tree2": tree2})

        assert len(forest) == 2
        assert "tree1" in forest
        assert "tree2" in forest
        assert forest.tree_names() == ["tree1", "tree2"]

    def test_get_tree(self):
        """Test getting a tree from forest."""
        tree = node("root", "child")
        forest = Forest({"my_tree": tree})

        result = forest.get("my_tree")
        assert result is not None
        assert isinstance(result, Tree)
        assert result.root.name == "root"

    def test_get_nonexistent_tree(self):
        """Test getting a tree that doesn't exist."""
        forest = Forest()
        assert forest.get("nonexistent") is None

    def test_set_tree(self):
        """Test adding/replacing a tree."""
        forest = Forest()
        tree = node("root", "child")

        new_forest = forest.set("my_tree", tree)

        assert len(new_forest) == 1
        assert "my_tree" in new_forest
        assert len(forest) == 0  # Original unchanged

    def test_set_replaces_tree(self):
        """Test that set replaces existing tree."""
        tree1 = node("root1")
        tree2 = node("root2")

        forest = Forest({"my_tree": tree1})
        new_forest = forest.set("my_tree", tree2)

        assert new_forest.get("my_tree").root.name == "root2"

    def test_remove_tree(self):
        """Test removing a tree from forest."""
        tree = node("root")
        forest = Forest({"my_tree": tree})

        new_forest = forest.remove("my_tree")

        assert "my_tree" not in new_forest
        assert "my_tree" in forest  # Original unchanged

    def test_remove_nonexistent_tree(self):
        """Test removing a tree that doesn't exist."""
        forest = Forest()

        with pytest.raises(KeyError):
            forest.remove("nonexistent")

    def test_immutability(self):
        """Test that forest operations are immutable."""
        forest1 = Forest()
        forest2 = forest1.set("tree1", node("root"))
        forest3 = forest2.set("tree2", node("root"))

        assert len(forest1) == 0
        assert len(forest2) == 1
        assert len(forest3) == 2


class TestTreePath:
    """Tests for TreePath class."""

    def test_parse_forest_root(self):
        """Test parsing forest root path."""
        path = TreePath.parse("/")

        assert path.is_absolute
        assert path.tree_name is None
        assert path.components == ()

    def test_parse_tree_root(self):
        """Test parsing tree root path."""
        path = TreePath.parse("/my_tree")

        assert path.is_absolute
        assert path.tree_name == "my_tree"
        assert path.components == ()

    def test_parse_absolute_path(self):
        """Test parsing absolute path with components."""
        path = TreePath.parse("/my_tree/child1/child2")

        assert path.is_absolute
        assert path.tree_name == "my_tree"
        assert path.components == ("child1", "child2")

    def test_parse_relative_path(self):
        """Test parsing relative path."""
        path = TreePath.parse("child1/child2")

        assert not path.is_absolute
        assert path.tree_name is None
        assert path.components == ("child1", "child2")

    def test_parse_current_dir(self):
        """Test parsing current directory."""
        path = TreePath.parse(".")

        assert not path.is_absolute
        assert path.components == ()

    def test_parse_with_dots(self):
        """Test parsing path with . components (filtered out)."""
        path = TreePath.parse("/tree/./child/./grandchild")

        assert path.components == ("child", "grandchild")

    def test_parse_empty_path(self):
        """Test parsing empty path raises error."""
        with pytest.raises(ValueError):
            TreePath.parse("")

    def test_join_components(self):
        """Test joining additional components."""
        path = TreePath.parse("/tree/child1")
        new_path = path.join("child2", "child3")

        assert new_path.components == ("child1", "child2", "child3")
        assert path.components == ("child1",)  # Original unchanged

    def test_parent_path(self):
        """Test getting parent path."""
        path = TreePath.parse("/tree/child1/child2")
        parent = path.parent()

        assert parent is not None
        assert parent.components == ("child1",)

    def test_parent_of_tree_root(self):
        """Test parent of tree root is forest root."""
        path = TreePath.parse("/tree")
        parent = path.parent()

        assert parent is not None
        assert parent.tree_name is None
        assert parent.components == ()

    def test_parent_of_forest_root(self):
        """Test parent of forest root is None."""
        path = TreePath.parse("/")
        parent = path.parent()

        assert parent is None

    def test_path_string_representation(self):
        """Test converting path back to string."""
        paths = [
            ("/", "/"),
            ("/tree", "/tree"),
            ("/tree/child", "/tree/child"),
            ("child/grandchild", "child/grandchild"),
            (".", "."),
        ]

        for path_str, expected in paths:
            path = TreePath.parse(path_str)
            assert str(path) == expected


class TestShellContext:
    """Tests for ShellContext class."""

    def test_initial_context(self):
        """Test creating initial context at forest root."""
        forest = Forest()
        ctx = ShellContext(forest)

        assert ctx.pwd() == "/"
        assert ctx.current_tree_name is None
        assert ctx.current_tree is None
        assert ctx.current_node is None

    def test_cd_to_tree(self):
        """Test cd into a tree."""
        tree = node("root", "child1", "child2")
        forest = Forest({"my_tree": tree})
        ctx = ShellContext(forest)

        new_ctx = ctx.cd("my_tree")

        assert new_ctx.pwd() == "/my_tree"
        assert new_ctx.current_tree_name == "my_tree"
        assert new_ctx.current_node.name == "root"

    def test_cd_to_child(self):
        """Test cd into a child node."""
        tree = node("root", node("child1", "grandchild"), "child2")
        forest = Forest({"my_tree": tree})
        ctx = ShellContext(forest, "my_tree")

        new_ctx = ctx.cd("child1")

        assert new_ctx.pwd() == "/my_tree/child1"
        assert new_ctx.current_node.name == "child1"

    def test_cd_absolute_path(self):
        """Test cd with absolute path."""
        tree = node("root", node("child1", "grandchild"))
        forest = Forest({"my_tree": tree})
        ctx = ShellContext(forest)

        new_ctx = ctx.cd("/my_tree/child1/grandchild")

        assert new_ctx.pwd() == "/my_tree/child1/grandchild"
        assert new_ctx.current_node.name == "grandchild"

    def test_cd_parent(self):
        """Test cd to parent with .."""
        tree = node("root", node("child1", "grandchild"))
        forest = Forest({"my_tree": tree})
        ctx = ShellContext(forest, "my_tree", ["child1", "grandchild"])

        new_ctx = ctx.cd("..")

        assert new_ctx.pwd() == "/my_tree/child1"
        assert new_ctx.current_node.name == "child1"

    def test_cd_parent_from_tree_root(self):
        """Test cd .. from tree root goes to forest root."""
        tree = node("root", "child1")
        forest = Forest({"my_tree": tree})
        ctx = ShellContext(forest, "my_tree")

        new_ctx = ctx.cd("..")

        assert new_ctx.pwd() == "/"
        assert new_ctx.current_tree_name is None

    def test_cd_to_forest_root(self):
        """Test cd to forest root."""
        tree = node("root", "child1")
        forest = Forest({"my_tree": tree})
        ctx = ShellContext(forest, "my_tree", ["child1"])

        new_ctx = ctx.cd("/")

        assert new_ctx.pwd() == "/"
        assert new_ctx.current_tree_name is None

    def test_cd_invalid_path(self):
        """Test cd to invalid path raises error."""
        tree = node("root", "child1")
        forest = Forest({"my_tree": tree})
        ctx = ShellContext(forest, "my_tree")

        with pytest.raises(ValueError):
            ctx.cd("nonexistent")

    def test_cd_invalid_tree(self):
        """Test cd to nonexistent tree raises error."""
        forest = Forest()
        ctx = ShellContext(forest)

        with pytest.raises(ValueError):
            ctx.cd("nonexistent_tree")

    def test_resolve_path(self):
        """Test resolving a path to tree and node."""
        tree = node("root", node("child1", "grandchild"))
        forest = Forest({"my_tree": tree})
        ctx = ShellContext(forest)

        tree_name, resolved_node = ctx.resolve_path("/my_tree/child1/grandchild")

        assert tree_name == "my_tree"
        assert resolved_node is not None
        assert resolved_node.name == "grandchild"

    def test_resolve_invalid_path(self):
        """Test resolving invalid path returns None."""
        forest = Forest()
        ctx = ShellContext(forest)

        tree_name, resolved_node = ctx.resolve_path("/nonexistent/path")

        assert tree_name is None
        assert resolved_node is None

    def test_update_forest(self):
        """Test updating forest."""
        forest1 = Forest({"tree1": node("root1")})
        ctx = ShellContext(forest1, "tree1")

        forest2 = Forest({"tree1": node("root1"), "tree2": node("root2")})
        new_ctx = ctx.update_forest(forest2)

        assert len(new_ctx.forest) == 2
        assert new_ctx.current_tree_name == "tree1"

    def test_update_forest_removes_current_tree(self):
        """Test update forest when current tree is removed."""
        forest1 = Forest({"tree1": node("root1")})
        ctx = ShellContext(forest1, "tree1")

        forest2 = Forest({"tree2": node("root2")})
        new_ctx = ctx.update_forest(forest2)

        assert new_ctx.pwd() == "/"
        assert new_ctx.current_tree_name is None

    def test_immutability(self):
        """Test that context operations are immutable."""
        tree = node("root", "child1", "child2")
        forest = Forest({"my_tree": tree})
        ctx1 = ShellContext(forest)

        ctx2 = ctx1.cd("my_tree")
        ctx3 = ctx2.cd("child1")

        assert ctx1.pwd() == "/"
        assert ctx2.pwd() == "/my_tree"
        assert ctx3.pwd() == "/my_tree/child1"
