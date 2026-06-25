# AlgoTree v3 Phase 1: Cursor + Parent Removal (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce an immutable `Cursor` (zipper) as the home for position, remove the parent-weakref machinery from `Node` so a node becomes a context-free value, route position-aware selection through the cursor, and delete the shell and the dead `jt` CLI.

**Architecture:** Position moves out of the node value into a `Cursor` (focus node + spine of context frames). Navigation and edits rebuild only the spine (O(depth)), so structural sharing is finally sound. Selectors gain a position-aware `matches_at(cursor)` so the five positional selectors (depth, root, child_of, descendant_of, sibling_of) work from cursor context instead of a parent backpointer. The additive pieces land first (Tasks 1-4), then the single breaking change (Task 5) removes parent and reworks the two remaining consumers (`Tree.paths`, positional `matches`), then Task 6 deletes the shell and dead CLI.

**Tech Stack:** Python 3.8+, pytest. No new dependencies (this phase removes one: `prompt_toolkit`).

## Global Constraints

- Python floor `>=3.8` (from `setup.py`); no 3.9+-only syntax in `AlgoTree/`.
- Immutability: every operation returns a new value; never mutate an existing `Node` or `Cursor`.
- Tests live under `test/` (singular), run with `python -m pytest`.
- `Node` constructor keeps the `attrs=` (dict) calling convention in this phase; the `**attrs` ergonomic change is a later phase. Do NOT change it here.
- `Node.fold` (added in Phase 0) is the recursion primitive; do not reintroduce hand-rolled parent walks.
- Selector NAME matching keeps its current behavior in this phase (exact/glob/regex sniffing). Declared `name`/`glob`/`regex` is Phase 4; do NOT change it here.
- `find` / `find_all` return Nodes (values). Cursors are returned only by the explicit `locate` / `cursors_at`.
- Source of truth: `docs/superpowers/specs/2026-06-24-algotree-v3-fold-cursor-design.md` (sections 3.2, 3.4, 3.5, 7, 8, 9).

## Decisions already verified against the codebase (do not re-investigate)

- `test_selectors.py` exercises every selector via `selector.select(tree)` from the root, so making `select` cursor-based keeps it green with NO edits to that file.
- `test_node.py` has exactly four parent/positional spots: line 18 (`n.parent is None`), lines 38-40 (parent backrefs), `test_is_root` (241-248), `test_depth` (259-269). Nothing else in `test_node.py` touches the removed API.
- The only library consumers of the removed Node API are: `Node` itself (the positional properties), `selectors.py` (the five positional selectors), and `Tree.paths()` (`tree.py:377,380`, via `Node.path`). Exporters/pretty_tree use LOCAL `is_root`/`is_last` params, not the Node API.
- `serialization.py` pickles `Tree` (so `Node.__getstate__`/`__setstate__` must survive) and otherwise uses `to_dict`/`from_dict`.
- No live caller passes `parent=` to the `Node` constructor. The only hit is `bin/jt.py:60`, which is already-dead code (it imports `AlgoTree.fluent`, `AlgoTree.pattern_matcher`, `AlgoTree.tree_transformer`, `AlgoTree.tree_shaper`, none of which exist) and is deleted in Task 6.

---

### Task 1: `Cursor` navigation (new module, additive)

**Files:**
- Create: `AlgoTree/cursor.py`
- Modify: `AlgoTree/__init__.py` (export `Cursor`)
- Test: `test/test_cursor.py` (create)

**Interfaces:**
- Consumes: `Node` (existing), its `name`, `attrs`, `children`, constructor `Node(name, *children, attrs=...)`.
- Produces: `Cursor(focus: Node, spine=())` with properties `node`, `depth`, `is_root`, `path`; methods `down(key)`, `up()`, `left()`, `right()`, `root()`; value equality.

- [ ] **Step 1: Write the failing test**

Create `test/test_cursor.py`:

```python
import pytest
from AlgoTree import Node
from AlgoTree.cursor import Cursor


def _tree():
    # root
    #   a
    #     x
    #   b
    return Node("root",
                Node("a", Node("x")),
                Node("b"))


def test_focus_and_root_depth():
    cur = Cursor(_tree())
    assert cur.node.name == "root"
    assert cur.depth == 0
    assert cur.is_root
    assert cur.path == ("root",)


def test_down_by_name_and_index():
    cur = Cursor(_tree())
    assert cur.down("a").node.name == "a"
    assert cur.down(1).node.name == "b"
    assert cur.down("a").depth == 1
    assert cur.down("a").path == ("root", "a")
    assert not cur.down("a").is_root


def test_down_missing_child_raises():
    cur = Cursor(_tree())
    with pytest.raises(KeyError):
        cur.down("nope")


def test_up_inverts_down():
    cur = Cursor(_tree())
    assert cur.down("a").up() == cur            # up . down == identity
    assert cur.down("a").down("x").up().up() == cur


def test_up_at_root_raises():
    with pytest.raises(ValueError):
        Cursor(_tree()).up()


def test_left_right_siblings():
    cur = Cursor(_tree())
    a = cur.down("a")
    b = a.right()
    assert b.node.name == "b"
    assert b.left().node.name == "a"


def test_left_at_first_raises():
    with pytest.raises(ValueError):
        Cursor(_tree()).down(0).left()


def test_root_returns_to_top():
    cur = Cursor(_tree())
    deep = cur.down("a").down("x")
    assert deep.depth == 2
    assert deep.root() == cur
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest test/test_cursor.py -v`
Expected: FAIL at import (`No module named 'AlgoTree.cursor'`).

- [ ] **Step 3: Create the module**

Create `AlgoTree/cursor.py`:

```python
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
```

- [ ] **Step 4: Export `Cursor` from the package**

In `AlgoTree/__init__.py`, after the `from .tree import Tree` line, add:

```python
from .cursor import Cursor
```

And add `'Cursor',` to the `__all__` list, right after `'Tree',`.

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest test/test_cursor.py -v`
Expected: PASS (8 passed).

- [ ] **Step 6: Commit**

```bash
git add AlgoTree/cursor.py AlgoTree/__init__.py test/test_cursor.py
git commit -m "feat(cursor): add immutable Cursor (zipper) with navigation"
```

---

### Task 2: `Cursor` edits, relatives, and `walk_cursors` (additive)

**Files:**
- Modify: `AlgoTree/cursor.py`
- Modify: `AlgoTree/__init__.py` (export `walk_cursors`)
- Test: `test/test_cursor.py` (append)

**Interfaces:**
- Consumes: `Cursor` (Task 1), `Node.with_attrs`.
- Produces: `Cursor.replace(node)`, `Cursor.set_attr(**attrs)`, `Cursor.ancestors()` (yields parent..root), `Cursor.siblings()` (yields sibling cursors, excludes focus), and module function `walk_cursors(cursor)` (pre-order over focus and descendants).

- [ ] **Step 1: Write the failing test**

Append to `test/test_cursor.py`:

```python
def test_set_attr_rebuilds_only_spine_sharing_siblings():
    root = _tree()
    cur = Cursor(root).down("a")
    edited = cur.set_attr(seen=True)
    new_root = edited.root().node
    # the edited node carries the attr
    assert new_root.children[0].get("seen") is True
    # the untouched sibling 'b' is the very same object (structural sharing)
    assert new_root.children[1] is root.children[1]
    # original tree is unchanged (immutability)
    assert root.children[0].get("seen") is None


def test_replace_swaps_focus_and_shares_siblings():
    root = _tree()
    cur = Cursor(root).down("b")
    new_root = cur.replace(Node("B2")).root().node
    assert new_root.children[1].name == "B2"
    assert new_root.children[0] is root.children[0]   # 'a' subtree shared


def test_ancestors_parent_to_root_order():
    cur = Cursor(_tree()).down("a").down("x")
    names = [c.node.name for c in cur.ancestors()]
    assert names == ["a", "root"]          # parent first, then up to root


def test_siblings_excludes_focus():
    cur = Cursor(_tree()).down("a")
    sib_names = [c.node.name for c in cur.siblings()]
    assert sib_names == ["b"]


def test_walk_cursors_preorder():
    from AlgoTree.cursor import walk_cursors
    names = [c.node.name for c in walk_cursors(Cursor(_tree()))]
    assert names == ["root", "a", "x", "b"]


def test_walk_cursors_depths():
    from AlgoTree.cursor import walk_cursors
    depths = {c.node.name: c.depth for c in walk_cursors(Cursor(_tree()))}
    assert depths == {"root": 0, "a": 1, "x": 2, "b": 1}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest test/test_cursor.py -k "set_attr or replace or ancestors or siblings or walk_cursors" -v`
Expected: FAIL (`AttributeError`/`ImportError` for the not-yet-added members).

- [ ] **Step 3: Add the import for `Iterator`**

In `AlgoTree/cursor.py`, change the typing import line to:

```python
from typing import Any, Dict, Iterator, NamedTuple, Tuple, Union
```

- [ ] **Step 4: Add edits and relatives to `Cursor`**

In `AlgoTree/cursor.py`, insert these methods into class `Cursor`, after `root()` and before `__eq__`:

```python
    # --- edits (rebuild the spine only; untouched subtrees are shared) ---

    def replace(self, node: Node) -> 'Cursor':
        """Return a new cursor with the focus replaced by `node`."""
        return Cursor(node, self._spine)

    def set_attr(self, **attrs: Any) -> 'Cursor':
        """Return a new cursor with attributes merged into the focus node."""
        return Cursor(self._focus.with_attrs(**attrs), self._spine)

    # --- relatives ---

    def ancestors(self) -> Iterator['Cursor']:
        """Yield parent, grandparent, ... up to and including the root."""
        cursor = self
        while cursor._spine:
            cursor = cursor.up()
            yield cursor

    def siblings(self) -> Iterator['Cursor']:
        """Yield a cursor for each sibling of the focus (excludes the focus)."""
        if not self._spine:
            return
        focus_index = len(self._spine[0].left)
        parent = self.up()
        for i in range(len(parent.node.children)):
            if i != focus_index:
                yield parent.down(i)
```

- [ ] **Step 5: Add `walk_cursors` at module scope**

In `AlgoTree/cursor.py`, after the `Cursor` class, add:

```python
def walk_cursors(cursor: Cursor) -> Iterator[Cursor]:
    """Pre-order traversal yielding a Cursor at the focus and every descendant."""
    yield cursor
    for i in range(len(cursor.node.children)):
        yield from walk_cursors(cursor.down(i))
```

- [ ] **Step 6: Export `walk_cursors`**

In `AlgoTree/__init__.py`, change the cursor import to:

```python
from .cursor import Cursor, walk_cursors
```

And add `'walk_cursors',` to `__all__` right after `'Cursor',`.

- [ ] **Step 7: Run tests to verify they pass**

Run: `python -m pytest test/test_cursor.py -v`
Expected: PASS (14 passed).

- [ ] **Step 8: Commit**

```bash
git add AlgoTree/cursor.py AlgoTree/__init__.py test/test_cursor.py
git commit -m "feat(cursor): add edits, ancestors/siblings, and walk_cursors"
```

---

### Task 3: Position-aware selector matching (`matches_at`) and cursor-based selection (additive)

**Files:**
- Modify: `AlgoTree/selectors.py`
- Modify: `AlgoTree/node.py` (`find`, `find_all` route Selectors through cursors)
- Modify: `AlgoTree/tree.py` (`select` routes Selectors through cursors)
- Test: `test/test_selector_cursor.py` (create)

**Interfaces:**
- Consumes: `Cursor`, `walk_cursors` (Task 2); the existing `Selector` classes.
- Produces: `Selector.matches_at(cursor) -> bool` (base default delegates to `self.matches(cursor.node)`); overrides on `AndSelector`/`OrSelector`/`NotSelector`/`XorSelector` and the five positional selectors; `Selector.select` walks cursors and uses `matches_at`; `Node.find`/`Node.find_all`/`Tree.select` route any object with a `matches_at` attribute through the cursor walk.

**Note:** This task is additive. Parent still exists on `Node`, so positional selectors keep their working `matches(node)`; `select` now uses the new `matches_at` path. Existing `test_selectors.py` keeps passing unchanged.

- [ ] **Step 1: Write the failing test**

Create `test/test_selector_cursor.py`:

```python
from AlgoTree import Node, Tree
from AlgoTree.selectors import depth, leaf, name


def _tree():
    return Tree(Node("root",
                     Node("a", Node("x"), Node("y")),
                     Node("b")))


def test_find_all_routes_positional_selector_through_cursor():
    nodes = _tree().find_all(depth(2))
    assert {n.name for n in nodes} == {"x", "y"}


def test_find_returns_first_positional_match():
    assert _tree().find(depth(1)).name == "a"


def test_tree_select_routes_positional_selector():
    nodes = list(_tree().select(depth(1)))
    assert {n.name for n in nodes} == {"a", "b"}


def test_select_value_local_still_works():
    assert {n.name for n in leaf().select(_tree())} == {"x", "y", "b"}


def test_matches_at_default_is_value_local():
    from AlgoTree.cursor import Cursor
    cur = Cursor(Node("hit"))
    assert name("hit").matches_at(cur) is True
    assert name("miss").matches_at(cur) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest test/test_selector_cursor.py -v`
Expected: FAIL (`find_all(depth(2))` currently routes through `make_predicate` -> `DepthSelector.matches` which works via parent, BUT `test_matches_at_default_is_value_local` fails with `AttributeError: 'NameSelector' object has no attribute 'matches_at'`).

- [ ] **Step 3: Add `matches_at` to the base `Selector` and make `select` cursor-based**

In `AlgoTree/selectors.py`, inside class `Selector`, add this method right after `matches` (the abstract method, near the top of the class):

```python
    def matches_at(self, cursor) -> bool:
        """Position-aware match. Default ignores position (value-local)."""
        return self.matches(cursor.node)
```

Then replace the `select` method body with:

```python
    def select(self, tree: Union[Node, Tree]) -> Iterator[Node]:
        """Select all matching nodes from tree (position-aware)."""
        root = tree.root if isinstance(tree, Tree) else tree
        from .cursor import Cursor, walk_cursors
        for cursor in walk_cursors(Cursor(root)):
            if self.matches_at(cursor):
                yield cursor.node
```

- [ ] **Step 4: Add `matches_at` overrides to the logical combinators**

In `AlgoTree/selectors.py`, add a `matches_at` method to each combinator class.

`AndSelector` (after its `matches`):

```python
    def matches_at(self, cursor) -> bool:
        return all(s.matches_at(cursor) for s in self.selectors)
```

`OrSelector`:

```python
    def matches_at(self, cursor) -> bool:
        return any(s.matches_at(cursor) for s in self.selectors)
```

`NotSelector`:

```python
    def matches_at(self, cursor) -> bool:
        return not self.selector.matches_at(cursor)
```

`XorSelector`:

```python
    def matches_at(self, cursor) -> bool:
        return sum(1 for s in self.selectors if s.matches_at(cursor)) == 1
```

- [ ] **Step 5: Add `matches_at` overrides to the positional selectors**

`DepthSelector` (after its `matches`):

```python
    def matches_at(self, cursor) -> bool:
        d = cursor.depth
        if isinstance(self.depth, range):
            return d in self.depth
        return d == self.depth
```

`RootSelector`:

```python
    def matches_at(self, cursor) -> bool:
        return cursor.is_root
```

`ChildOfSelector`:

```python
    def matches_at(self, cursor) -> bool:
        if not self.child_selector.matches_at(cursor):
            return False
        if cursor.is_root:
            return False
        return self.parent_selector.matches_at(cursor.up())
```

`ParentOfSelector`:

```python
    def matches_at(self, cursor) -> bool:
        if not self.parent_selector.matches_at(cursor):
            return False
        return any(
            self.child_selector.matches_at(cursor.down(i))
            for i in range(len(cursor.node.children))
        )
```

`DescendantOfSelector`:

```python
    def matches_at(self, cursor) -> bool:
        if not self.descendant_selector.matches_at(cursor):
            return False
        return any(
            self.ancestor_selector.matches_at(ancestor)
            for ancestor in cursor.ancestors()
        )
```

`AncestorOfSelector`:

```python
    def matches_at(self, cursor) -> bool:
        if not self.ancestor_selector.matches_at(cursor):
            return False
        from .cursor import walk_cursors
        descendants = walk_cursors(cursor)
        next(descendants)  # skip the focus itself
        return any(self.descendant_selector.matches_at(d) for d in descendants)
```

`SiblingOfSelector`:

```python
    def matches_at(self, cursor) -> bool:
        if not self.node_selector.matches_at(cursor):
            return False
        return any(
            self.sibling_selector.matches_at(sib) for sib in cursor.siblings()
        )
```

- [ ] **Step 6: Route `Node.find` / `Node.find_all` through cursors for Selector objects**

In `AlgoTree/node.py`, replace the `find` method body with:

```python
    def find(self, selector: Union[str, Callable[['Node'], bool], 'Selector']) -> Optional['Node']:
        """Find first node matching selector."""
        if hasattr(selector, 'matches_at'):
            from .cursor import Cursor, walk_cursors
            for cursor in walk_cursors(Cursor(self)):
                if selector.matches_at(cursor):
                    return cursor.node
            return None
        predicate = self._make_predicate(selector)
        if predicate(self):
            return self
        for node in self.descendants():
            if predicate(node):
                return node
        return None
```

And replace the `find_all` method body with:

```python
    def find_all(self, selector: Union[str, Callable[['Node'], bool], 'Selector']) -> List['Node']:
        """Find all nodes matching selector."""
        if hasattr(selector, 'matches_at'):
            from .cursor import Cursor, walk_cursors
            return [c.node for c in walk_cursors(Cursor(self)) if selector.matches_at(c)]
        predicate = self._make_predicate(selector)
        return [node for node in self.walk() if predicate(node)]
```

- [ ] **Step 7: Route `Tree.select` through cursors for Selector objects**

In `AlgoTree/tree.py`, replace the `select` method body with:

```python
    def select(self, selector: Union[str, Callable[[Node], bool]]) -> Iterator[Node]:
        """Select nodes matching selector (returns iterator)."""
        if hasattr(selector, 'matches_at'):
            from .cursor import Cursor, walk_cursors
            return (c.node for c in walk_cursors(Cursor(self._root))
                    if selector.matches_at(c))
        predicate = self._make_predicate(selector)
        return (node for node in self._root.walk() if predicate(node))
```

- [ ] **Step 8: Run tests to verify they pass**

Run: `python -m pytest test/test_selector_cursor.py test/test_selectors.py -v`
Expected: PASS (new file plus all existing selector tests, now flowing through the cursor path).

- [ ] **Step 9: Run the full non-shell suite (no regressions)**

Run: `python -m pytest test/ -q --ignore=test/test_shell_core.py --ignore=test/test_shell_commands.py --ignore=test/test_piping_redirection.py`
Expected: all pass (same count as before plus the new tests).

- [ ] **Step 10: Commit**

```bash
git add AlgoTree/selectors.py AlgoTree/node.py AlgoTree/tree.py test/test_selector_cursor.py
git commit -m "feat(selectors): position-aware matches_at; cursor-based select and find"
```

---

### Task 4: `Tree.locate` / `Tree.cursors_at` (additive)

**Files:**
- Modify: `AlgoTree/tree.py`
- Test: `test/test_locate.py` (create)

**Interfaces:**
- Consumes: `Cursor`, `walk_cursors` (Task 2); `matches_at` (Task 3); `_make_predicate_fn` (already imported in `tree.py`).
- Produces: `Tree.locate(selector) -> Optional[Cursor]`, `Tree.cursors_at(selector) -> List[Cursor]`. Both accept a Selector, a name string, or a callable.

- [ ] **Step 1: Write the failing test**

Create `test/test_locate.py`:

```python
from AlgoTree import Node, Tree
from AlgoTree.cursor import Cursor
from AlgoTree.selectors import name, depth


def _tree():
    return Tree(Node("root", Node("a", Node("x")), Node("b")))


def test_locate_returns_cursor_at_match():
    cur = _tree().locate(name("x"))
    assert isinstance(cur, Cursor)
    assert cur.node.name == "x"
    assert cur.path == ("root", "a", "x")


def test_locate_none_when_absent():
    assert _tree().locate(name("zzz")) is None


def test_cursors_at_returns_all():
    curs = _tree().cursors_at(depth(1))
    assert [c.node.name for c in curs] == ["a", "b"]


def test_locate_accepts_string():
    assert _tree().locate("b").node.name == "b"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest test/test_locate.py -v`
Expected: FAIL (`AttributeError: 'Tree' object has no attribute 'locate'`).

- [ ] **Step 3: Add `locate` / `cursors_at` to `Tree`**

In `AlgoTree/tree.py`, add these methods to class `Tree`, right after the `select` method:

```python
    def locate(self, selector: Union[str, Callable[[Node], bool]]) -> Optional['Cursor']:
        """Return a Cursor at the first node matching selector, or None."""
        from .cursor import Cursor, walk_cursors
        for cursor in walk_cursors(Cursor(self._root)):
            if self._cursor_matches(cursor, selector):
                return cursor
        return None

    def cursors_at(self, selector: Union[str, Callable[[Node], bool]]) -> List['Cursor']:
        """Return a Cursor at every node matching selector."""
        from .cursor import Cursor, walk_cursors
        return [c for c in walk_cursors(Cursor(self._root))
                if self._cursor_matches(c, selector)]

    @staticmethod
    def _cursor_matches(cursor: 'Cursor', selector) -> bool:
        if hasattr(selector, 'matches_at'):
            return selector.matches_at(cursor)
        return _make_predicate_fn(selector)(cursor.node)
```

(`Cursor` is referenced only in string type hints, so no top-level import is needed; the method bodies import it locally.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest test/test_locate.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Run the full non-shell suite**

Run: `python -m pytest test/ -q --ignore=test/test_shell_core.py --ignore=test/test_shell_commands.py --ignore=test/test_piping_redirection.py`
Expected: no regressions.

- [ ] **Step 6: Commit**

```bash
git add AlgoTree/tree.py test/test_locate.py
git commit -m "feat(tree): add locate/cursors_at returning Cursors for editing"
```

---

### Task 5: Remove the parent backpointer from `Node` (breaking)

**Files:**
- Modify: `AlgoTree/node.py` (remove parent machinery and positional properties; simplify pickling)
- Modify: `AlgoTree/tree.py` (`paths` rework onto `Cursor.path`)
- Modify: `AlgoTree/selectors.py` (positional selectors' `matches` raise)
- Modify: `test/test_node.py` (remove the four parent/positional spots)
- Test: `test/test_selector_cursor.py` (append the "matches raises" lock)

**Interfaces:**
- Consumes: `Cursor` / `walk_cursors` for `Tree.paths`; `matches_at` for all positional selection (already in place).
- Produces: `Node` with `__slots__ = ('_name', '_attrs', '_children', '_hash')`, constructor `Node(name, *children, attrs=None)` (no `parent`), and NO `parent`/`depth`/`path`/`ancestors`/`siblings`/`is_root` members. Positional selectors' `matches(node)` raise `NotImplementedError`. `Tree.paths` computed via cursor.

**Why this stays green:** by Task 3, all selection flows through `matches_at` (cursor), and by Task 4 editing uses cursors, so nothing depends on `Node.parent` except the items reworked here.

- [ ] **Step 1: Write the failing test (lock the new contract)**

Append to `test/test_selector_cursor.py`:

```python
def test_positional_selector_matches_node_raises():
    import pytest
    from AlgoTree.selectors import depth, root
    with pytest.raises(NotImplementedError):
        depth(1).matches(Node("x"))
    with pytest.raises(NotImplementedError):
        root().matches(Node("x"))


def test_node_has_no_parent_api():
    n = Node("x")
    assert not hasattr(n, "parent")
    assert not hasattr(n, "depth")
    assert not hasattr(n, "is_root")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest test/test_selector_cursor.py -k "raises or no_parent" -v`
Expected: FAIL (positional `matches` currently returns a bool; `Node` still has `parent`/`depth`/`is_root`).

- [ ] **Step 3: Strip parent machinery from `Node.__init__` and `__slots__`**

In `AlgoTree/node.py`:

Remove the line `import weakref`.

Change `__slots__` to:

```python
    __slots__ = ('_name', '_attrs', '_children', '_hash')
```

Replace the `__init__` method with:

```python
    def __init__(
        self,
        name: str,
        *children: 'Node',
        attrs: Optional[Dict[str, Any]] = None
    ):
        """
        Create an immutable, context-free node.

        Args:
            name: Node name/identifier
            *children: Child nodes
            attrs: Node attributes/payload
        """
        self._name = name
        self._attrs = attrs or {}
        self._children = tuple(children)
        self._hash = None  # Cached hash
```

- [ ] **Step 4: Remove the positional members from `Node`**

In `AlgoTree/node.py`, delete these members entirely (they are now properties of a Cursor, not a node value):

- the `parent` property (the `@property def parent(...)` block)
- the `ancestors` method
- the `siblings` method
- the `is_root` property
- the `depth` property
- the `path` property

Keep `is_leaf`, `height`, `size`, `descendants`, `walk`, `leaves`, and everything else.

- [ ] **Step 5: Simplify pickling**

In `AlgoTree/node.py`, replace `__getstate__` and `__setstate__` with:

```python
    def __getstate__(self):
        """Get state for pickling."""
        return {
            'name': self._name,
            'attrs': self._attrs,
            'children': self._children,
        }

    def __setstate__(self, state):
        """Restore state from pickling."""
        object.__setattr__(self, '_name', state['name'])
        object.__setattr__(self, '_attrs', state['attrs'])
        object.__setattr__(self, '_children', state['children'])
        object.__setattr__(self, '_hash', None)
```

- [ ] **Step 6: Make positional selectors' `matches` raise**

In `AlgoTree/selectors.py`, replace the `matches` method body of each of these five classes with a clear error. For `DepthSelector`:

```python
    def matches(self, node: Node) -> bool:
        raise NotImplementedError(
            "DepthSelector is position-dependent; use .select()/.first() "
            "or matches_at(cursor)"
        )
```

Do the same (with the class name in the message) for `RootSelector`, `ChildOfSelector`, `DescendantOfSelector`, and `SiblingOfSelector`. Leave `ParentOfSelector` and `AncestorOfSelector` `matches` as they are (they read children/descendants, not parent).

- [ ] **Step 7: Rework `Tree.paths` onto `Cursor.path`**

In `AlgoTree/tree.py`, replace the `paths` method body with:

```python
    def paths(self, to_leaves_only: bool = True) -> List[str]:
        """
        Get all paths in tree.

        Args:
            to_leaves_only: If True, only return paths to leaves

        Returns:
            List of path strings
        """
        from .cursor import Cursor, walk_cursors
        result = []
        for cursor in walk_cursors(Cursor(self._root)):
            if to_leaves_only and cursor.node.children:
                continue
            result.append('/'.join(cursor.path))
        return result
```

- [ ] **Step 8: Migrate `test/test_node.py` (remove the four parent/positional spots)**

In `test/test_node.py`:

1. In `test_simple_node`, delete the line `self.assertIsNone(n.parent)`.
2. In `test_node_with_children`, delete the comment `# Check parent references` and the two following assertions (`self.assertEqual(parent.children[0].parent, parent)` and `self.assertEqual(parent.children[1].parent, parent)`).
3. Delete the entire `test_is_root` method (positional; covered by `test/test_cursor.py::test_down_by_name_and_index` and `test_focus_and_root_depth`).
4. Delete the entire `test_depth` method (positional; covered by `test/test_cursor.py::test_walk_cursors_depths`).

- [ ] **Step 9: Run the affected suites**

Run: `python -m pytest test/test_node.py test/test_selectors.py test/test_selector_cursor.py test/test_tree.py test/test_transformers.py test/test_serialization.py -v`
Expected: PASS. (`test_tree.py::test_paths`, `test_transformers.py::test_to_paths_shaper`, and the pickle paths in `test_serialization.py` exercise the reworked code.)

- [ ] **Step 10: Run the full non-shell suite**

Run: `python -m pytest test/ -q --ignore=test/test_shell_core.py --ignore=test/test_shell_commands.py --ignore=test/test_piping_redirection.py`
Expected: all pass.

- [ ] **Step 11: Commit**

```bash
git add AlgoTree/node.py AlgoTree/tree.py AlgoTree/selectors.py test/test_node.py test/test_selector_cursor.py
git commit -m "feat(core)!: remove parent from Node; position lives in Cursor

BREAKING: Node no longer has parent/depth/path/ancestors/siblings/is_root.
Use Cursor for position. Fixes the structural-sharing reparenting bug."
```

---

### Task 6: Delete the shell and the dead `jt` CLI (breaking)

**Files:**
- Delete: `AlgoTree/shell/` (whole package), `test/test_shell_core.py`, `test/test_shell_commands.py`, `test/test_piping_redirection.py`, `bin/jt.py`
- Modify: `setup.py` (drop console scripts and `prompt_toolkit`; bump version)
- Modify: `AlgoTree/__init__.py` (bump version)

**Interfaces:**
- Consumes: nothing new.
- Produces: a package with no shell, no console scripts, no `prompt_toolkit` dependency, version `3.0.0.dev0`. The full `python -m pytest test/` now collects cleanly with no missing-dependency errors.

- [ ] **Step 1: Confirm nothing in the library imports the shell**

Run: `grep -rn "AlgoTree.shell\|from .shell\|import shell" AlgoTree/*.py`
Expected: no output (the library core never imports the shell; only `setup.py` console scripts and the deleted tests reference it).

- [ ] **Step 2: Delete the shell, the shell tests, and the dead CLI**

```bash
git rm -r AlgoTree/shell
git rm test/test_shell_core.py test/test_shell_commands.py test/test_piping_redirection.py
git rm bin/jt.py
```

- [ ] **Step 3: Update `setup.py`**

In `setup.py`, replace:

```python
    install_requires=[
        'prompt_toolkit>=3.0.0',
    ],
```

with:

```python
    install_requires=[],
```

Delete the entire `entry_points={...}` block (the three console scripts `jt`, `algotree`, `algotree-shell` are gone: two referenced the deleted shell, one referenced the deleted dead CLI). Also change `packages=find_packages() + ['bin']` to `packages=find_packages()` (the `bin` package no longer ships an entry point). Change `version="2.0.2"` to `version="3.0.0.dev0"`.

- [ ] **Step 4: Bump the package version**

In `AlgoTree/__init__.py`, change `__version__ = "2.0.2"` to `__version__ = "3.0.0.dev0"`.

- [ ] **Step 5: Verify the package imports and the full suite collects cleanly**

Run: `python -c "import AlgoTree; print(AlgoTree.__version__)"`
Expected: prints `3.0.0.dev0` with no import error.

Run: `python -m pytest test/ -q`
Expected: the whole suite collects (no `ModuleNotFoundError: prompt_toolkit`) and passes.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat!: drop the shell and dead jt CLI; remove prompt_toolkit dep

BREAKING: removes AlgoTree.shell, the algotree/algotree-shell/jt console
scripts, and the prompt_toolkit dependency. The Python API plus notebook
reprs are the only interfaces in v3. Version -> 3.0.0.dev0."
```

---

## Definition of Done (Phase 1)

- `AlgoTree/cursor.py` exists: immutable `Cursor` with navigation, edits, `ancestors`/`siblings`, value equality, plus `walk_cursors`. Exported from the package.
- `Node` is a context-free value: no `parent`/`depth`/`path`/`ancestors`/`siblings`/`is_root`, no `weakref`, no `parent=` kwarg. Structural sharing is sound (verified by the sibling-identity test).
- Position-aware selection works through `matches_at`; `select`/`find`/`find_all`/`Tree.select` route Selector objects through the cursor walk; positional selectors' `matches(node)` raise a clear error.
- `Tree.paths` and `to_paths` compute via `Cursor.path`.
- `Tree.locate`/`cursors_at` return Cursors for editing; `find`/`find_all` still return Nodes.
- The shell, the three shell test files, and the dead `jt` CLI are deleted; `prompt_toolkit` is no longer a dependency; version is `3.0.0.dev0`.
- `python -m pytest test/ -q` collects the WHOLE suite cleanly (no skipped-due-to-missing-dependency) and passes.

## Self-Review notes

- **Spec coverage:** implements spec section 8 Phase 1 ("Cursor + remove parent backpointer"), the Cursor design (3.4), the position-aware portion of selectors (3.5) needed to keep matching working after parent removal (the full declared-matching lattice and axis-combinator consolidation remain Phase 4), and the shell-removal cut (section 7, decision D6). The `from_list` bridge and the merge of `Node`/`Tree` are later phases and intentionally out of scope here.
- **Placeholder scan:** none; every step shows complete code or exact shell commands and expected output.
- **Type consistency:** `Cursor` members and `walk_cursors` are named identically across Tasks 1-5; `matches_at(cursor)` has one signature everywhere; `hasattr(selector, 'matches_at')` is the single routing predicate used in `node.py`, `tree.py`, and `Tree._cursor_matches`.
- **Ordering guarantee:** Tasks 1-4 are additive (parent still present), so each leaves the suite green. The single breaking change is isolated to Task 5, which is green on completion only because Tasks 3-4 already moved matching and editing onto cursors. Task 6 (deletion) is independent of Task 5.
- **Known follow-ups (NOT this phase):** `MANIFEST.in`/docs/README may still mention the shell; the `Node`/`Tree` merge, render registry, `Trace`/`diff`, declared selector matching, and `from_list` are Phases 2-5.
