"""
Cursor: an immutable zipper over Node trees.

A Cursor is a *position* in a tree: a focus node plus the spine of context
needed to rebuild the path back to the root. Position lives here, not on
Node, so a Node stays a context-free value and structural sharing is sound.
All moves and edits return new Cursors; nothing is mutated.
"""
from typing import Any, Dict, NamedTuple, Tuple, Union
from .node import Node


class _Frame(NamedTuple):
    """One ancestor level: the parent's identity plus the siblings around the focus."""
    name: str
    attrs: Dict[str, Any]
    left: Tuple[Node, ...]   # siblings before the focus, in order
    right: Tuple[Node, ...]  # siblings after the focus, in order


class Cursor:
    """Immutable focused position in a tree."""

    __slots__ = ('_focus', '_spine')

    def __init__(self, focus: Node, spine: Tuple[_Frame, ...] = ()):
        self._focus = focus
        self._spine = spine

    # --- reads ---

    @property
    def node(self) -> Node:
        """The node currently in focus."""
        return self._focus

    @property
    def depth(self) -> int:
        """Distance from the root of this cursor's tree (root is 0)."""
        return len(self._spine)

    @property
    def is_root(self) -> bool:
        """True when the focus has no parent frame."""
        return not self._spine

    @property
    def path(self) -> Tuple[str, ...]:
        """Names from the root down to the focus, inclusive."""
        names = [frame.name for frame in reversed(self._spine)]
        names.append(self._focus.name)
        return tuple(names)

    # --- navigation ---

    def down(self, key: Union[int, str]) -> 'Cursor':
        """Move to a child by index or by name (first match)."""
        children = self._focus.children
        if isinstance(key, int):
            index = key if key >= 0 else len(children) + key
        else:
            index = next((i for i, c in enumerate(children) if c.name == key), -1)
        if not (0 <= index < len(children)):
            raise KeyError(f"no such child: {key!r}")
        frame = _Frame(self._focus.name, self._focus.attrs,
                       children[:index], children[index + 1:])
        return Cursor(children[index], (frame,) + self._spine)

    def up(self) -> 'Cursor':
        """Move to the parent, rebuilding it from the focus and its siblings."""
        if not self._spine:
            raise ValueError("cursor is already at the root")
        frame = self._spine[0]
        siblings = frame.left + (self._focus,) + frame.right
        parent = Node(frame.name, *siblings, attrs=frame.attrs)
        return Cursor(parent, self._spine[1:])

    def left(self) -> 'Cursor':
        """Move to the previous sibling."""
        if not self._spine or not self._spine[0].left:
            raise ValueError("no left sibling")
        frame = self._spine[0]
        new_focus = frame.left[-1]
        new_frame = _Frame(frame.name, frame.attrs,
                           frame.left[:-1], (self._focus,) + frame.right)
        return Cursor(new_focus, (new_frame,) + self._spine[1:])

    def right(self) -> 'Cursor':
        """Move to the next sibling."""
        if not self._spine or not self._spine[0].right:
            raise ValueError("no right sibling")
        frame = self._spine[0]
        new_focus = frame.right[0]
        new_frame = _Frame(frame.name, frame.attrs,
                           frame.left + (self._focus,), frame.right[1:])
        return Cursor(new_focus, (new_frame,) + self._spine[1:])

    def root(self) -> 'Cursor':
        """Move all the way up to the root."""
        cursor = self
        while cursor._spine:
            cursor = cursor.up()
        return cursor

    # --- identity ---

    def __eq__(self, other: Any) -> bool:
        return (isinstance(other, Cursor)
                and self._focus == other._focus
                and self._spine == other._spine)

    def __repr__(self) -> str:
        return f"Cursor(focus={self._focus.name!r}, depth={self.depth})"
