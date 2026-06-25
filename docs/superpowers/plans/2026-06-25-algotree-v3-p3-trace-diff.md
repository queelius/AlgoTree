# AlgoTree v3 P3: Trace + Diff (Visualization Engine) - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`).

**Goal:** Make structural recursion VISIBLE - AlgoTree's defensible niche. Add `Node.fold_traced(fn) -> (result, Trace)` (the one fold, instrumented once), a `Trace` that is itself tree-shaped, a structural `diff(before, after) -> DiffTree`, and renderers that drive the fold step-through and the green/red/yellow diff through the existing Theme machinery.

**Architecture:** Purely additive. `fold_traced` runs the identical recursion as `fold` but records per node: post-order step index, the node, the child results it consumed, and the synthesized value - assembling a parallel `Node` tree (so `Trace`/`DiffTree` render, fold, and diff with the same tools built in P2a). `diff` folds over the position-aligned zip of two trees. New renderers register into the P2a registry.

**Tech Stack:** Python 3.8+, pytest. Uses `render.py` (P2a) for output. No new deps.

## Global Constraints
- Python `>=3.8`; immutability; tests in `test/`; voice-check hook bans em-dashes in committed `.md`.
- Additive only: new `AlgoTree/trace.py` and `AlgoTree/diff.py`, a `fold_traced` method on `Node`, registry entries in `render.py`, and `__init__` exports. Do not change existing fold/render semantics.
- `Trace` and `DiffTree` are `Node`-shaped (wrap a `Node`), so they reuse render/fold/walk.
- Renderers route all text through the P2a escaper (no raw interpolation); colors via the Theme/registry, not ad-hoc.
- Source of truth: spec section 4.2/4.3; roadmap P3.

## Current state (read before implementing)
- `AlgoTree/node.py`: `Node.fold(fn)` is the bottom-up catamorphism `fn(node, child_results)`. `Node` has name/attrs/children, `render(fmt)`, `to_dict`, etc.
- `AlgoTree/render.py` (P2a): `Theme`, `register(fmt, render_fn, ext)`, module `render(node, fmt, **opts)`, `extension_for`, escapers for mermaid/html/dot, deterministic palette. Reuse `register` to add trace/diff backends and reuse the escapers.

---

### Task 1: `Node.fold_traced` + the `Trace` structure

**Files:** modify `AlgoTree/node.py` (add `fold_traced`); create `AlgoTree/trace.py` (`Trace`); Test `test/test_trace.py`.

**Design:**
`Node.fold_traced(self, fn) -> (result, Trace)`: same recursion as `fold`, but build a parallel trace tree. Each trace node is a `Node` with the same `name` and children mirroring structure, carrying attrs: `step` (post-order index, 0-based), `value` (the synthesized `fn` result), and `arity` (len of children). Return `(result, Trace(trace_root))`.

```python
# node.py
def fold_traced(self, fn):
    from .trace import Trace
    counter = [0]
    def go(node):
        child_results, child_traces = [], []
        for c in node.children:
            r, t = go(c)
            child_results.append(r); child_traces.append(t)
        value = fn(node, child_results)
        step = counter[0]; counter[0] += 1
        tnode = Node(node.name, *child_traces,
                     attrs={'step': step, 'value': value, 'arity': len(node.children)})
        return value, tnode
    result, troot = go(self)
    return result, Trace(troot)
```

```python
# trace.py
class Trace:
    __slots__ = ('_root',)
    def __init__(self, root): self._root = root
    @property
    def root(self): return self._root
    def steps(self):
        # nodes in post-order (== ascending 'step')
        return sorted(self._root.walk(), key=lambda n: n['step'])
    def value(self): return self.steps()[-1]['value']  # root is last in post-order
    def at(self, step): return next(n for n in self._root.walk() if n['step'] == step)
    def frontier(self, step):
        # names/steps visited up to and including `step`
        return [n.name for n in self._root.walk() if n['step'] <= step]
    def __len__(self): return self._root.size
    def render(self, fmt='unicode', **o): return self._root.render(fmt, **o)
```

- [ ] Step 1: Write `test/test_trace.py`: for `eval`-style fold on a small arithmetic tree (`Node('add', Node('1'), Node('mul', Node('3'), Node('2')))` with `fn = lambda n,cs: int(n.name) if n.is_leaf else {'add':sum,'mul':lambda xs:xs[0]*xs[1]}[n.name](cs)`), assert `result == 7`, the returned `Trace` has `len == 5`, `steps()` is post-order (leaves before parents; root last), each trace node carries `step`/`value`/`arity`, and `trace.value() == 7`.
- [ ] Step 2: fail. Step 3: implement `fold_traced` + `trace.py`. Step 4: pass. Step 5: full suite green. Step 6: commit `feat(trace): Node.fold_traced + Trace (instrument the one fold)`.

---

### Task 2: Trace rendering - step-through frames + frontier highlight

**Files:** modify `AlgoTree/trace.py`, `AlgoTree/render.py` (a `trace` backend); Test append `test/test_trace.py`.

**Design:** add `Trace.to_mermaid(highlight=None)` and `Trace.to_html()` that render the trace tree with each node labeled `name = value` and, if `highlight` (a set/list of node steps or names) is given, mark those nodes (e.g. a mermaid `class`/style or an HTML class). Add `Trace.frames()` yielding, for steps 0..len-1, a rendered snapshot (mermaid string) with the frontier up to that step highlighted - this is the "watch 1+3*2 evaluate" filmstrip. Route label text through the P2a mermaid/html escaper. Register a `trace` render backend if helpful, or implement directly on `Trace` reusing `render.py` escapers.

- [ ] Step 1: Test that `trace.to_mermaid()` contains each `name = value` label (escaped), that `to_mermaid(highlight=[trace.at(0).name])` marks the highlighted node, and that `len(list(trace.frames())) == len(trace)` and each frame is a non-empty mermaid string.
- [ ] Step 2-6; commit `feat(trace): step-through frames + frontier-highlighted mermaid/html`.

---

### Task 3: structural `diff` -> `DiffTree`

**Files:** create `AlgoTree/diff.py` (`diff`, `DiffTree`); Test `test/test_diff.py`.

**Design:** `diff(before, after) -> DiffTree`. Align children by index (position). Status per node in `{'unchanged','added','removed','changed'}`: `added` when before is None, `removed` when after is None, `changed` when names differ or attrs differ, else `unchanged`. Carry `attr_delta` (dict of changed/added/removed attr keys) for changed nodes. Build a `DiffTree` wrapping a `Node` whose attrs include `diff_status` and `attr_delta`; node name is the after-name (or before-name when removed).

```python
def diff(before, after):
    def go(b, a):
        if b is None:
            name, status, delta = a.name, 'added', {}
        elif a is None:
            name, status, delta = b.name, 'removed', {}
        else:
            name = a.name
            delta = _attr_delta(b.attrs, a.attrs)
            status = 'changed' if (b.name != a.name or delta) else 'unchanged'
        bc = b.children if b is not None else ()
        ac = a.children if a is not None else ()
        m = max(len(bc), len(ac))
        kids = [go(bc[i] if i < len(bc) else None, ac[i] if i < len(ac) else None) for i in range(m)]
        return Node(name, *kids, attrs={'diff_status': status, 'attr_delta': delta})
    return DiffTree(go(before, after))
```
`DiffTree`: `.root`, `.summary()` -> `{'added':n,'removed':n,'changed':n,'unchanged':n}` (fold counting `diff_status`), `.render`/`.to_mermaid`/`.to_html` (Task 4).

- [ ] Step 1: `test/test_diff.py`: `diff(t, t).summary()` is all-unchanged; removing a leaf yields one `removed`; changing an attr yields one `changed` with the right `attr_delta`; adding a child yields one `added`. Counts match a brute-force oracle.
- [ ] Step 2-6; commit `feat(diff): structural diff -> DiffTree + summary`.

---

### Task 4: diff rendering through the Theme (green/red/yellow)

**Files:** modify `AlgoTree/diff.py`, `AlgoTree/render.py`; Test append `test/test_diff.py`.

**Design:** `DiffTree.to_mermaid()` colors nodes by `diff_status` (added=green, removed=red, changed=yellow, unchanged=default) using mermaid `classDef`/`class` directives; `DiffTree.to_html()` adds a CSS class per status. All text escaped via the P2a escapers. Optionally register a `diff` backend. Add `DiffTree.changed_nodes()` returning the nodes whose status != unchanged.

- [ ] Step 1: Test `to_mermaid()` contains a green/added style applied to the added node and a red/removed style to the removed node (assert the classDef + the class assignment lines exist for the right node ids); `to_html()` contains the status CSS classes; escaping holds for a node named `<x>`.
- [ ] Step 2-6; commit `feat(diff): themed mermaid/html rendering (added/removed/changed)`.

---

### Task 5: exports + a worked example

**Files:** modify `AlgoTree/__init__.py`; create `examples/visualize_fold_and_diff.py` (a small runnable script, not a test); Test: `test/test_trace.py`/`test/test_diff.py` already cover behavior; add an import-surface test.

**Design:** export `Trace`, `diff`, `DiffTree` (and `fold_traced` is a Node method). The example script: builds an arithmetic AST, evaluates it via `fold_traced`, prints the step-through, applies a one-rule rewrite (e.g. `x*1 -> x` done manually via `node.map`), and prints `diff(before, after).to_mermaid()` - demonstrating the book's "watch it evaluate" and "watch it shrink" figures.

- [ ] Step 1: Add `test/test_viz_exports.py` asserting `from AlgoTree import Trace, diff, DiffTree` works and `Node(...).fold_traced(...)` is callable. Run the example script end-to-end (it must exit 0).
- [ ] Step 2: implement exports + example. Step 3: full suite green; `python examples/visualize_fold_and_diff.py` exits 0. Step 4: commit `feat(viz): export Trace/diff/DiffTree + worked example`.

## Definition of Done (P3)
- `Node.fold_traced` returns `(result, Trace)`; `Trace` is tree-shaped with per-node step/value/arity, `steps()`/`frames()`/`frontier()`.
- `diff(before, after) -> DiffTree` with `summary()`, `changed_nodes()`, themed mermaid/html (green/red/yellow), all escaped.
- `Trace`/`diff`/`DiffTree` exported; a runnable example demonstrates the fold step-through and the diff view.
- `python -m pytest test/ -q` fully green.
