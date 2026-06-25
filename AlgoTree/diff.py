"""
Structural diff for AlgoTree trees.

`diff(before, after) -> DiffTree` computes a position-aligned structural diff
between two Node trees.  Children are aligned by index (position-based, not
name-based).  Each node in the resulting DiffTree carries:

    - diff_status (str): one of 'unchanged', 'added', 'removed', 'changed'
    - attr_delta  (dict): keys whose values differ between before and after
                          (empty for added/removed nodes)

`DiffTree` wraps a Node and provides:
    - .root         -> the underlying Node tree
    - .summary()    -> dict with counts per status
    - .changed_nodes() -> list of nodes with status != 'unchanged'
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .node import Node as _Node


def _attr_delta(before_attrs: Dict[str, Any], after_attrs: Dict[str, Any]) -> Dict[str, Any]:
    """Compute which attribute keys changed, were added, or were removed.

    Returns a dict of the affected keys mapped to a tuple ``(before_val, after_val)``
    where a missing key is represented by ``None``.  An empty dict means the
    attrs are identical.
    """
    delta: Dict[str, Any] = {}
    all_keys = set(before_attrs) | set(after_attrs)
    for k in all_keys:
        bv = before_attrs.get(k)
        av = after_attrs.get(k)
        if bv != av:
            delta[k] = (bv, av)
    return delta


def diff(before: Optional[Any], after: Optional[Any]) -> 'DiffTree':
    """Compute a structural diff between two Node trees.

    Children are aligned by position (index).  Status rules:

    - ``'added'``     when *before* is ``None`` (new subtree in *after*)
    - ``'removed'``   when *after* is ``None`` (subtree absent in *after*)
    - ``'changed'``   when names differ OR ``_attr_delta`` is non-empty
    - ``'unchanged'`` otherwise

    Args:
        before: The original Node tree (or ``None``).
        after:  The new Node tree (or ``None``).

    Returns:
        A :class:`DiffTree` wrapping the annotated diff tree.
    """
    from .node import Node

    def go(b: Optional[Any], a: Optional[Any]) -> 'Node':
        if b is None:
            # Entire subtree is new
            name: str = a.name
            status: str = 'added'
            delta: Dict[str, Any] = {}
        elif a is None:
            # Entire subtree was removed
            name = b.name
            status = 'removed'
            delta = {}
        else:
            # Both exist -- compare
            name = a.name
            delta = _attr_delta(b.attrs, a.attrs)
            status = 'changed' if (b.name != a.name or delta) else 'unchanged'

        bc = b.children if b is not None else ()
        ac = a.children if a is not None else ()
        m = max(len(bc), len(ac))
        kids = [
            go(bc[i] if i < len(bc) else None,
               ac[i] if i < len(ac) else None)
            for i in range(m)
        ]

        return Node(name, *kids, attrs={'diff_status': status, 'attr_delta': delta})

    return DiffTree(go(before, after))


class DiffTree:
    """A tree annotated with per-node diff status.

    Each node in ``.root`` carries two attrs:

    - ``diff_status`` (str): ``'unchanged'``, ``'added'``, ``'removed'``, or
      ``'changed'``.
    - ``attr_delta``  (dict): keys that changed; maps to ``(before_val, after_val)``
      tuples.  Empty for added/removed nodes.

    Because ``.root`` is a plain :class:`~AlgoTree.node.Node`, all standard
    Node operations (walk, fold, render, etc.) work on a ``DiffTree`` via its
    root.
    """

    __slots__ = ('_root',)

    def __init__(self, root: Any) -> None:
        """Wrap the given annotated Node as a DiffTree."""
        self._root = root

    @property
    def root(self) -> Any:
        """The underlying annotated Node tree."""
        return self._root

    def summary(self) -> Dict[str, int]:
        """Return a count of nodes per diff status.

        Returns:
            Dict with keys ``'added'``, ``'removed'``, ``'changed'``,
            ``'unchanged'`` mapping to non-negative integer counts.
        """
        counts: Dict[str, int] = {'added': 0, 'removed': 0, 'changed': 0, 'unchanged': 0}
        for n in self._root.walk():
            status = n['diff_status']
            if status in counts:
                counts[status] += 1
        return counts

    def changed_nodes(self) -> List[Any]:
        """Return all nodes whose status is not ``'unchanged'``.

        This includes nodes with status ``'added'``, ``'removed'``, or
        ``'changed'``.

        Returns:
            List of annotated Nodes (in pre-order).
        """
        return [n for n in self._root.walk() if n['diff_status'] != 'unchanged']

    def render(self, fmt: str = 'unicode', **opts: Any) -> str:
        """Render the diff tree using the given format.

        Delegates to :func:`AlgoTree.render.render` on ``.root``.
        """
        return self._root.render(fmt, **opts)
