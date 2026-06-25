# AlgoTree v3 P2b: Merge Node and Tree (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`).

**Goal:** Make `Node` the single self-sufficient tree type: every operation `Tree` offers is available directly on `Node`. Reduce `Tree` to a thin forwarder over `Node` (one implementation, no duplicated logic), so consumers can drop the wrap/unwrap tax. Full `DeprecationWarning`/removal of `Tree` is deferred to after the transformer rework (P2c).

**Architecture:** Additive first (add the `Tree`-only operations to `Node`, keeping behavior identical), then refactor `Tree`'s method bodies to delegate to the `Node` equivalents (no behavior change), then point internal consumers (`selectors`, `serialization`, `interop`) at `Node` and broaden tests to the `Node` surface. The suite stays green throughout.

**Tech Stack:** Python 3.8+, pytest. No new deps.

## Global Constraints
- Python `>=3.8`; immutability; tests in `test/`; voice-check hook bans em-dashes in committed `.md`.
- BEHAVIOR PRESERVED: every existing `Tree.*` call must keep returning the same results (the suite must stay green). `Tree` keeps its current public surface; its method bodies just delegate to `Node`.
- `Node` gains the `Tree`-only operations with matching semantics. Where `Tree` returned a `Tree`, the `Node` method returns a `Node` (the analogous structural result).
- ONE lawful `Node.map(f: Node -> Node)` stays as-is (strict). `Tree.map`'s historical `Node | dict | None` runtime sniffing is preserved ONLY inside the `Tree` forwarder (so old callers keep working); it is NOT added to `Node.map`. Provide a named helper `update_attrs(**kw)` on `Node` for the attr-delta convenience.
- The `Node('<empty>')` sentinel is a `Tree`-only legacy detail; `Node.filter` returns `Optional[Node]` (None when nothing matches). `Tree.filter` keeps wrapping None as the empty-tree sentinel for back-compat.
- Source of truth: spec sections 3.2, 7; roadmap P2b.

## Current state (read before implementing)
- `AlgoTree/node.py`: `Node` already has name/attrs/children, with_*/without_*, map_children/filter_children, `map` (strict Node->Node), `filter(predicate|selector)` returning Optional[Node] (NOTE: confirm whether Node.filter already routes selectors via cursor id-membership; if not, add it to match Tree.filter), `find`/`find_all` (cursor-routed for Selectors), `walk`/`descendants`/`leaves`, `to_dict`, `from_dict` (staticmethod, hardcoded 'children'), `is_leaf`/`height`/`size`, `fold`, `render`.
- `AlgoTree/tree.py`: `Tree` wraps a root and adds `from_dict(children_key)`, `from_paths`, `map`(sniffing), `filter`(id-membership + sentinel), `reduce`, `fold`, `prune`, `graft`, `flatten`, `find`/`find_all`/`exists`/`count`, `select`, `locate`, `cursors_at`, `_cursor_matches`, `get_path`, `paths`, `size`/`height`/`leaves`/`is_empty`, `walk`, `nodes`, `to_dict(children_key)`, `to_paths`, `__or__`/`__rshift__`.

---

### Task 1: Add the `Tree`-only operations to `Node` (additive)

**Files:** modify `AlgoTree/node.py`; Test `test/test_node_ops.py` (new).

Add these methods to `Node` (port the logic verbatim from the corresponding `Tree` methods, replacing `self._root` with `self` and returning `Node` instead of `Tree`):
- `from_paths(paths, delimiter='/')` classmethod (returns a `Node`).
- make `from_dict(data, children_key='children')` accept the `children_key` param (keep it a staticmethod/classmethod; do not mutate the input dict - the current `Tree.from_dict` uses `d.pop`, which mutates; use non-mutating reads instead).
- `reduce(fn, initial, order='preorder')`.
- `prune(selector)` (cursor id-membership for Selectors, else predicate; returns Optional[Node] - the pruned tree, or None if everything pruned).
- `graft(selector, subtree)` (subtree may be a `Node`; if a `Tree` is passed, use `.root`).
- `flatten(max_depth=None)`.
- `select(selector)` (iterator of Nodes; cursor-routed for Selectors).
- `locate(selector) -> Optional[Cursor]`, `cursors_at(selector) -> List[Cursor]`, and the `_cursor_matches` static helper (or a module function).
- `exists(selector)`, `count(selector=None)`.
- `get_path(path, delimiter='/')`, `paths(to_leaves_only=True)`, `to_paths(delimiter='/')`.
- `nodes()` (list of all nodes).
- `update_attrs(**kw) -> Node` (alias of `with_attrs`, the named attr-delta helper).
- `__or__`/`__rshift__` pipe operators (apply a callable to self).
- Confirm `Node.filter` accepts a Selector and routes it via cursor id-membership (matching `Tree.filter`); if it currently only takes a callable, extend it.

- [ ] Step 1: Write `test/test_node_ops.py` asserting each new `Node` op matches the corresponding `Tree` op on the same tree (build a `Tree(root)` and a bare `root`, assert `root.prune(...).to_dict() == tree.prune(...).root.to_dict()`, etc. for prune/graft/flatten/reduce/select/find_all/paths/get_path/from_paths/from_dict/count/exists/locate). Use a representative tree with attrs + depth 3.
- [ ] Step 2: run -> fails (methods missing). Step 3: implement. Step 4: `pytest test/test_node_ops.py -v` -> pass. Step 5: full suite green. Step 6: commit `feat(core): Node gains Tree's full operation set (additive)`.

---

### Task 2: Reduce `Tree` to a thin forwarder over `Node`

**Files:** modify `AlgoTree/tree.py`; Test: existing `test/test_tree.py` must stay green unchanged.

Rewrite each `Tree` method body to delegate to the `Node` equivalent, wrapping `Node` results back into `Tree` where the method historically returned a `Tree`:
- `Tree.from_dict`/`from_paths` -> `cls(Node.from_dict(...))` / `cls(Node.from_paths(...))`.
- `prune`/`graft`/`flatten`/`filter` -> `Tree(self._root.<op>(...) or Node('<empty>'))` (preserve the empty sentinel for filter/prune).
- `map` -> keep the `Node | dict | None` sniffing in the forwarder (build a `Node->Node` transform, call `self._root.map(transform)`), so old callers are unchanged.
- `reduce`/`fold`/`find`/`find_all`/`exists`/`count`/`select`/`locate`/`cursors_at`/`get_path`/`paths`/`to_paths`/`to_dict`/`walk`/`nodes`/`size`/`height`/`leaves`/`is_empty` -> delegate to `self._root`.
- Keep `__or__`/`__rshift__`, `__repr__`, `__str__` (str -> `render(self._root,'unicode')`).
- Delete the now-duplicated logic bodies (the forwarder must not re-implement traversal). `tree.py` should shrink substantially.

- [ ] Step 1: Run `test/test_tree.py` first to capture current behavior. Step 2: rewrite bodies as delegates. Step 3: `pytest test/test_tree.py test/test_transformers.py -v` -> green (transformers use Tree; they must keep working). Step 4: full suite green. Step 5: commit `refactor(core): Tree becomes a thin forwarder over Node`.

---

### Task 3: Point internal consumers at `Node`; broaden tests

**Files:** modify `AlgoTree/selectors.py` (`select` already handles Node via `isinstance(tree, Tree)` fallback - confirm and keep), `AlgoTree/serialization.py`, `AlgoTree/interop.py` (accept/return `Node` primarily; keep `Tree` acceptance where present), `AlgoTree/__init__.py` (docstring/comment that `Node` is the primary type); Test: extend coverage.

- Ensure `serialization.save/load/dumps/loads` work given a `Node` (not only `Tree`). If they currently require `Tree`, make them accept `Node` (and keep `Tree` via `.root`).
- Ensure `interop` functions accept a `Node`.
- Add `test/test_node_primary.py` asserting the full pipeline works with bare `Node`: build with `Node`/`from_dict`, transform (`prune`/`map`/`filter`), query (`find_all`/`select`/`locate`), render (`node.render('unicode')`), serialize round-trip (`dumps`/`loads`), to_dict round-trip - all without ever constructing a `Tree`.

- [ ] Step 1: write `test/test_node_primary.py` (Node-only pipeline). Step 2: run -> identify any consumer that rejects a bare Node; fix it. Step 3: full suite green. Step 4: commit `feat(core): Node is the primary type across serialization/interop; Node-only pipeline tested`.

## Definition of Done (P2b)
- A bare `Node` can do everything `Tree` could (construct, transform, query, navigate, render, serialize) with no `Tree` involved.
- `Tree` is a thin forwarder (no duplicated traversal logic) and every existing `Tree` test still passes.
- `update_attrs` exists; `Node.map` stays strict; the empty sentinel is confined to the `Tree` forwarder.
- `python -m pytest test/ -q` fully green.
- (Deferred to P2c/P5: emit `DeprecationWarning` from `Tree` and migrate `transformers` to `Node->Node`, after which `Tree` can move to `compat.py`.)
