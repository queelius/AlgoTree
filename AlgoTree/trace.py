"""
Trace: a parallel Node tree produced by Node.fold_traced.

Each trace node has the same name and tree structure as the original node,
but its attrs record:
  - step  (int): post-order visit index, 0-based
  - value (Any): the synthesized result returned by fn at that node
  - arity (int): number of children of the original node
"""

from typing import Any, List


class Trace:
    """
    Parallel tree recording the step-by-step evaluation of a fold.

    The trace tree mirrors the original Node tree exactly in structure
    (name, children) but each node carries attrs: step, value, arity.
    This makes Trace reusable with all existing Node operations.
    """

    __slots__ = ('_root',)

    def __init__(self, root: Any) -> None:
        """Create a Trace wrapping the given (annotated) Node root."""
        self._root = root

    @property
    def root(self) -> Any:
        """The root trace Node."""
        return self._root

    def steps(self) -> List[Any]:
        """Return all trace nodes in post-order (ascending step index)."""
        return sorted(self._root.walk(), key=lambda n: n['step'])

    def value(self) -> Any:
        """Return the synthesized value at the root (last in post-order)."""
        return self.steps()[-1]['value']

    def at(self, step: int) -> Any:
        """Return the trace node with the given step index."""
        return next(n for n in self._root.walk() if n['step'] == step)

    def frontier(self, step: int) -> List[str]:
        """Return names of all nodes with step index <= *step*."""
        return [n.name for n in self._root.walk() if n['step'] <= step]

    def __len__(self) -> int:
        """Number of nodes in the trace (equals the original tree size)."""
        return self._root.size

    def render(self, fmt: str = 'unicode', **opts: Any) -> str:
        """Render the trace tree using the given format."""
        return self._root.render(fmt, **opts)
