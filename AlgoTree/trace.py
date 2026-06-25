"""
Trace: a parallel Node tree produced by Node.fold_traced.

Each trace node has the same name and tree structure as the original node,
but its attrs record:
  - step  (int): post-order visit index, 0-based
  - value (Any): the synthesized result returned by fn at that node
  - arity (int): number of children of the original node
"""

from typing import Any, Iterator, List, Optional, Set, Union


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

    def frontier(self, step: int) -> Set[int]:
        """Return the set of step indices for nodes with step index <= *step*.

        Returns step indices (not names) so that identity-based highlighting
        works correctly even when multiple nodes share the same name.
        """
        return {n['step'] for n in self._root.walk() if n['step'] <= step}

    def __len__(self) -> int:
        """Number of nodes in the trace (equals the original tree size)."""
        return self._root.size

    def render(self, fmt: str = 'unicode', **opts: Any) -> str:
        """Render the trace tree using the given format."""
        return self._root.render(fmt, **opts)

    # ------------------------------------------------------------------
    # Task 2: step-through rendering
    # ------------------------------------------------------------------

    def to_mermaid(
        self,
        direction: str = "TD",
        highlight: Optional[Union[List[str], Set[str]]] = None,
        highlight_steps: Optional[Set[int]] = None,
    ) -> str:
        """Render trace as a Mermaid diagram with ``name = value`` labels.

        Each node is labelled ``<name> = <value>`` so readers can follow the
        fold evaluation.

        Highlighting priority (first match wins):

        1. *highlight_steps* – a set of step indices; nodes whose ``step``
           attribute is in the set are highlighted.  This is identity-based
           and therefore correct for trees that contain duplicate node names.
        2. *highlight* – a collection of node *names* (legacy, kept for
           backward compatibility).  Any node whose name is in the set is
           highlighted; for trees with unique names this is equivalent to
           *highlight_steps*, but for duplicate names it highlights every node
           sharing a matched name.

        Args:
            direction: Mermaid graph direction (default: ``"TD"``).
            highlight: Names of nodes to mark with the ``highlighted`` class.
                       Ignored when *highlight_steps* is provided.
            highlight_steps: Step indices of nodes to mark.  Preferred over
                             *highlight* because matching is identity-based.

        Returns:
            Mermaid diagram string.
        """
        from .render import _mermaid_escape  # reuse P2a escaper

        use_step_ids = highlight_steps is not None
        step_ids: Set[int] = highlight_steps if use_step_ids else set()
        highlight_names: Set[str] = set() if use_step_ids else (set(highlight) if highlight else set())

        any_highlight = bool(step_ids or highlight_names)

        lines: List[str] = [f"graph {direction}"]

        if any_highlight:
            lines.append("    classDef highlighted fill:#ffffaa,stroke:#888,stroke-width:2px")

        counter = [0]

        def _visit(n: Any) -> str:
            node_id = f"T{counter[0]}"
            counter[0] += 1

            name_esc = _mermaid_escape(n.name)
            value_esc = _mermaid_escape(str(n['value']))
            label = f"{name_esc} = {value_esc}"
            lines.append(f'    {node_id}["{label}"]')

            should_highlight = (
                (use_step_ids and n['step'] in step_ids)
                or (not use_step_ids and n.name in highlight_names)
            )
            if should_highlight:
                lines.append(f"    class {node_id} highlighted")

            for child in n.children:
                child_id = _visit(child)
                lines.append(f"    {node_id} --> {child_id}")

            return node_id

        _visit(self._root)
        return "\n".join(lines)

    def to_html(self, include_styles: bool = True) -> str:
        """Render trace as an HTML tree with ``name = value`` labels.

        All text is routed through the P2a HTML escaper so node names and
        values are safe even when they contain HTML special characters.

        Args:
            include_styles: Whether to include inline CSS (default: True).

        Returns:
            HTML string.
        """
        from .render import _html_escape  # reuse P2a escaper

        parts: List[str] = []

        if include_styles:
            parts.append("""<style>
    .trace-tree { font-family: monospace; }
    .trace-tree ul { list-style-type: none; padding-left: 20px; }
    .trace-tree li { padding: 3px 0; }
    .trace-tree .trace-node {
        display: inline-block; padding: 2px 6px;
        border: 1px solid #aaa; border-radius: 3px;
        background: #f0f8ff;
    }
    .trace-tree .trace-step { color: #888; font-size: 0.85em; margin-left: 6px; }
</style>
""")

        parts.append('<div class="trace-tree">')

        def _render_node(n: Any) -> str:
            node_parts: List[str] = []
            safe_name = _html_escape(n.name)
            safe_value = _html_escape(str(n['value']))
            safe_step = _html_escape(str(n['step']))

            node_parts.append(
                f'<li><div class="trace-node">'
                f'{safe_name} = {safe_value}'
                f'<span class="trace-step">#{safe_step}</span>'
                f'</div>'
            )

            if n.children:
                node_parts.append("<ul>")
                for child in n.children:
                    node_parts.append(_render_node(child))
                node_parts.append("</ul>")

            node_parts.append("</li>")
            return "".join(node_parts)

        parts.append("<ul>")
        parts.append(_render_node(self._root))
        parts.append("</ul>")
        parts.append("</div>")

        return "".join(parts)

    def frames(self, direction: str = "TD") -> Iterator[str]:
        """Yield step-by-step Mermaid snapshots of the fold evaluation.

        For step *k* (0-based), the snapshot renders the whole trace tree
        with the frontier up to and including step *k* highlighted.  This
        produces a filmstrip showing the fold evaluation one node at a time.

        Args:
            direction: Mermaid graph direction (default: ``"TD"``).

        Yields:
            Mermaid diagram strings, one per step (``len(self)`` total).
        """
        n = len(self)
        for step in range(n):
            yield self.to_mermaid(direction=direction, highlight_steps=self.frontier(step))
