# P4 Final Review: Fix Report

**Date:** 2026-06-25  
**Branch:** `algotree-v3-roadmap`  
**Suite result:** 641 passed, 15 skipped (was 638 passed, 15 skipped before this patch; 3 new tests added)

---

## Fix 1: `Node.graft()` positional/AxisSelector guard

**File:** `AlgoTree/node.py`  
**What changed:** `graft()` previously called `_make_predicate_fn(selector)` unconditionally.
Positional selectors (AxisSelector / DepthSelector / RootSelector) expose `matches_at(cursor)` but raise `NotImplementedError` from `matches(node)`, so `_make_predicate_fn` would blow up at call time.

The fix mirrors the pattern already used in `prune()`, `filter()`, `select()`, and `find_all()`:

```python
if hasattr(selector, 'matches_at'):
    from .cursor import Cursor, walk_cursors
    matched = {id(c.node) for c in walk_cursors(Cursor(self))
               if selector.matches_at(c)}
    predicate = lambda n: id(n) in matched
else:
    predicate = _make_predicate_fn(selector)
```

The existing `add_subtree` inner function then uses `predicate` unchanged. No other logic altered.

**File:** `AlgoTree/tree.py`  
`Tree.graft` type hint updated from `Union[str, Callable[[Node], bool]]` to `Union[str, Callable[[Node], bool], 'Selector']` (matching `Node.graft`).

---

## Fix 2: Stale docstrings

**File:** `AlgoTree/node.py`, five `selector:` param lines updated in:
- `prune()` (line 482)
- `graft()` (line 506)
- `select()` (line 578)
- `locate()` (line 598)
- `cursors_at()` (line 617)

Changed `"predicate, name pattern, or Selector"` to `"predicate, exact name (str), or Selector"` everywhere (bulk replace-all, no manual spots missed).

---

## Fix 3: Vacuous `test_none_alias_matches_none`

**File:** `test/test_selector_laws.py`

Old test compared `none_()` and `none()` matched-id sets. That comparison is vacuous: both always return `frozenset()`, proving nothing beyond the two being equal to each other.

New test explicitly checks:
- `none_()` matches **no** nodes over `self.cursors` (result is `frozenset()`)
- `any_()` matches **all** nodes (result is `_all_ids(self.cursors)`)

---

## New tests added

**File:** `test/test_node_ops.py`, class `TestGraftWithPositionalSelector` (3 tests):

1. `test_graft_depth_selector_no_raise`: calls `node.graft(depth(1), tag)` and asserts no exception.
2. `test_graft_depth_selector_correct_nodes_receive_child`: asserts the depth-1 nodes ("a", "b", "c") each gain a "tag" child, and that `root` itself does not gain one.
3. `test_graft_depth_selector_via_tree`: same check through `Tree.graft`.

---

## Concerns

None. All behaviorally equivalent paths for string/callable selectors are unchanged; only the `hasattr(selector, 'matches_at')` branch is new, and it is exercised by the new tests.
