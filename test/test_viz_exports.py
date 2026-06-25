"""
Task 5: import-surface tests for Trace, diff, DiffTree.

Verifies that the public API is exported correctly from AlgoTree and
that the worked example script exits 0.
"""
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Import-surface: these must work from the top-level package
# ---------------------------------------------------------------------------

class TestImportSurface:
    """All three P3 symbols are importable from AlgoTree."""

    def test_import_trace(self):
        from AlgoTree import Trace
        assert Trace is not None

    def test_import_diff(self):
        from AlgoTree import diff
        assert callable(diff)

    def test_import_difftree(self):
        from AlgoTree import DiffTree
        assert DiffTree is not None

    def test_trace_in_all(self):
        import AlgoTree
        assert 'Trace' in AlgoTree.__all__

    def test_diff_in_all(self):
        import AlgoTree
        assert 'diff' in AlgoTree.__all__

    def test_difftree_in_all(self):
        import AlgoTree
        assert 'DiffTree' in AlgoTree.__all__


class TestFoldTracedCallable:
    """Node.fold_traced is a callable method accessible from the public API."""

    def test_fold_traced_is_callable(self):
        from AlgoTree import Node
        n = Node('root', Node('child'))
        assert callable(n.fold_traced)

    def test_fold_traced_returns_tuple(self):
        from AlgoTree import Node
        n = Node('root', Node('child'))
        result = n.fold_traced(lambda node, cs: node.name if not cs else cs[0])
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_fold_traced_returns_trace(self):
        from AlgoTree import Node, Trace
        n = Node('root', Node('child'))
        _, trace = n.fold_traced(lambda node, cs: node.name if not cs else cs[0])
        assert isinstance(trace, Trace)

    def test_fold_traced_result_correct(self):
        from AlgoTree import Node
        arith = Node('add', Node('3'), Node('4'))
        result, _ = arith.fold_traced(
            lambda n, cs: int(n.name) if n.is_leaf else sum(cs)
        )
        assert result == 7


class TestDiffCallable:
    """diff() and DiffTree work as expected through public imports."""

    def test_diff_returns_difftree(self):
        from AlgoTree import Node, diff, DiffTree
        t = Node('root', Node('child'))
        dt = diff(t, t)
        assert isinstance(dt, DiffTree)

    def test_diff_summary(self):
        from AlgoTree import Node, diff
        before = Node('root', Node('a'))
        after = Node('root', Node('b'))
        dt = diff(before, after)
        s = dt.summary()
        assert 'changed' in s
        assert 'unchanged' in s
        assert 'added' in s
        assert 'removed' in s


# ---------------------------------------------------------------------------
# Worked example script exits 0
# ---------------------------------------------------------------------------

class TestExampleScript:
    """The worked example script must run without errors."""

    def test_example_script_exists(self):
        example = Path(__file__).parent.parent / 'examples' / 'visualize_fold_and_diff.py'
        assert example.exists(), f"Example script not found: {example}"

    def test_example_script_exits_zero(self):
        example = Path(__file__).parent.parent / 'examples' / 'visualize_fold_and_diff.py'
        result = subprocess.run(
            [sys.executable, str(example)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"Example script exited with code {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
