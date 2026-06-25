# AlgoTree v3 P2c: Transformer Algebra Cleanup - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`).

**Goal:** Collapse the ~15 delegating `Transformer`/`Shaper` subclasses plus `Pipeline`/`ParallelTransformer`/`DebugTransformer` into ONE function-style `Transformer` wrapper that composes with `>>` (one operator, with a lawful identity). The factory functions (`map_`/`filter_`/`prune`/`graft`/`flatten`/`normalize`/`annotate`/`reduce_`/`fold`/`extract`/`to_dict`/`to_paths`) stay, now returning the unified `Transformer` and operating on the self-sufficient `Node` (duck-typed to also accept `Tree`).

**Architecture:** One `Transformer` holds a `Callable[[Any], Any]` and a label; `__call__` applies it; `__rshift__` composes (`(a >> b)(x) == b(a(x))`); module-level `identity` is the lawful unit; `.repeat(n)` and `.when(cond, else_=None)` stay as methods. Delete the ABC, the `TreeTransformer`/`Shaper` bases, the ~13 op subclasses, `Pipeline`, `ParallelTransformer` (its merge was admittedly unlawful), and `DebugTransformer` (replaced conceptually by the P3 pipeline-provenance/diff). Drop the `|` (duplicate of `>>`) and `&` (parallel) transformer operators - `|`/`&` belong to the Selector lattice only. Factories become thin `Transformer(lambda t: t.<op>(...))` wrappers, duck-typed so a pipeline works on a bare `Node` or a `Tree`. Test migration happens in the same commit; suite stays green.

**Tech Stack:** Python 3.8+, pytest. No new deps.

## Global Constraints
- Python `>=3.8`; immutability; tests in `test/`; voice-check hook bans em-dashes in committed `.md`.
- `>>` is the ONE composition operator on transformers, with a lawful identity (`identity >> t` and `t >> identity` behave as `t`). No `|`/`&` on transformers.
- Factory function NAMES and call signatures are preserved (`map_`, `filter_`, `prune`, `graft`, `flatten`, `normalize`, `annotate`, `reduce_`, `fold`, `extract`, `to_dict`, `to_paths`); they now return the unified `Transformer`. Existing behavior of each (including `graft`'s dynamic-subtree callable form, `normalize`'s sort/clean, `annotate`'s selector+computed values) is preserved.
- A transformer must work applied to either a `Node` or a `Tree` (both expose `map`/`filter`/`prune`/`graft`/`flatten`/`reduce`/`fold`/`to_dict`/`paths`/`find_all`/`nodes`). Return type follows the input type for tree->tree ops.
- DELETE: the ABC `Transformer` base's abstractness, `TreeTransformer`, `Shaper`, `MapTransformer`, `FilterTransformer`, `PruneTransformer`, `GraftTransformer`, `FlattenTransformer`, `NormalizeTransformer`, `AnnotateTransformer`, `ReduceShaper`, `FoldShaper`, `ExtractShaper`, `ToDictShaper`, `ToPathsShaper`, `Pipeline`, `ParallelTransformer`, `DebugTransformer`, `ConditionalTransformer`, `RepeatTransformer`. (`repeat`/`when` survive as `Transformer` METHODS, implemented inline, not as separate classes.)
- Source of truth: spec section 6; roadmap P2c.

## Current state (read before implementing)
- `AlgoTree/transformers.py`: ABC `Transformer` with `>>`/`|`/`&`/`repeat`/`when`/`debug`; `TreeTransformer` + 7 tree->tree subclasses; `Shaper` + 5 shaper subclasses; `Pipeline`/`ParallelTransformer`/`RepeatTransformer`/`ConditionalTransformer`/`DebugTransformer`; factory functions returning the subclasses. All operate on `Tree` (via `tree.map`/etc., which also exist on `Node`).
- `AlgoTree/__init__.py`: exports `Transformer`, `TreeTransformer`, all the subclass names, `Pipeline`, `ParallelTransformer`, `RepeatTransformer`, `ConditionalTransformer`, `DebugTransformer`, `Shaper`, the shaper names, and the factory functions.
- `test/test_transformers.py`: read it fully to see which symbols it uses (factory funcs, `>>`, possibly `&`/`.debug`/`Pipeline`/class names).

---

### Task 1: Rewrite `transformers.py` to one function-style `Transformer`; migrate tests

**Files:** rewrite `AlgoTree/transformers.py`; modify `AlgoTree/__init__.py`; migrate `test/test_transformers.py` (same commit).

**Design:**
```python
class Transformer:
    """A composable tree operation: callable, composes with >>."""
    __slots__ = ('_fn', '_label')
    def __init__(self, fn, label='transformer'):
        self._fn = fn; self._label = label
    def __call__(self, tree):
        return self._fn(tree)
    def __rshift__(self, other):
        nxt = other if isinstance(other, Transformer) else Transformer(other, getattr(other, '__name__', 'fn'))
        return Transformer(lambda t: nxt(self(t)), f'{self._label} >> {nxt._label}')
    def repeat(self, times):
        def run(t):
            for _ in range(times): t = self(t)
            return t
        return Transformer(run, f'{self._label}.repeat({times})')
    def when(self, condition, else_=None):
        def run(t):
            if condition(t): return self(t)
            return else_(t) if else_ is not None else t
        return Transformer(run, f'{self._label}.when(...)')
    def __repr__(self): return f'Transformer({self._label})'

identity = Transformer(lambda t: t, 'identity')
```
Factory functions (preserve behavior; duck-typed on Node/Tree):
- `map_(fn) = Transformer(lambda t: t.map(fn), ...)`
- `filter_(pred) = Transformer(lambda t: t.filter(pred), ...)`
- `prune(sel) = Transformer(lambda t: t.prune(sel), ...)`
- `graft(sel, subtree)`: preserve the dynamic-subtree (callable) form. If `callable(subtree)` and not a Node/Tree: `Transformer(lambda t: t.map(lambda n: n.with_child(subtree(n)) if _pred(sel)(n) else n))` using a cursor-aware predicate consistent with `Node.graft`'s guard; else `Transformer(lambda t: t.graft(sel, subtree))`.
- `flatten(max_depth=None) = Transformer(lambda t: t.flatten(max_depth))`
- `normalize(**kw) = Transformer(lambda t: t.map(_normalize_node_factory(**kw)))` (port `NormalizeTransformer.normalize_node`).
- `annotate(sel=None, **ann) = Transformer(lambda t: t.map(_annotate_node_factory(sel, ann)))` (port `AnnotateTransformer.annotate_node`).
- `reduce_(fn, initial, order='preorder') = Transformer(lambda t: t.reduce(fn, initial, order))`
- `fold(fn) = Transformer(lambda t: t.fold(fn))`
- `extract(extractor, sel=None) = Transformer(lambda t: [extractor(n) for n in (t.find_all(sel) if sel else t.nodes())])`
- `to_dict(children_key='children') = Transformer(lambda t: t.to_dict(children_key))`
- `to_paths(delimiter='/', to_leaves_only=True) = Transformer(lambda t: t.paths(to_leaves_only=to_leaves_only, delimiter=delimiter))`

`__init__.py`: export `Transformer`, `identity`, and all the factory functions. REMOVE the deleted class names from imports and `__all__`.

Test migration (`test/test_transformers.py`): keep/adjust tests for the factory functions and `>>` composition and `.repeat`/`.when`. DELETE tests that exercise removed features: `&`/`ParallelTransformer`, `.debug()`/`DebugTransformer`, direct use of `Pipeline`/the subclass names. Where a test imported a subclass name, rewrite it to use the factory function. Keep `to_dict`/`to_paths`/`fold`/`reduce_`/`extract` shaper-as-transformer tests (they still return values).

- [ ] Step 1: read `test/test_transformers.py` fully; identify the symbols used. Step 2: rewrite `transformers.py`, update `__init__`, migrate the tests (remove Parallel/Debug/Pipeline-class/subclass-name tests; keep the rest working via factories + `>>`). Step 3: `python -m pytest test/test_transformers.py -v` -> green. Step 4: full suite `python -m pytest test/ -q` -> green. Step 5: commit `refactor(transformers)!: one function-style Transformer; delete the subclass zoo`.

---

### Task 2: Transformer-algebra law tests + final polish

**Files:** create `test/test_transformer_laws.py`; verify `__init__` surface.

**Design:** behavioral law tests on a sample tree:
- identity unit: `(identity >> t)(x) == t(x)` and `(t >> identity)(x) == t(x)` for `t in {map_(...), prune(...)}`.
- composition order: `(a >> b)(x) == b(a(x))`.
- associativity: `((a >> b) >> c)(x) == (a >> (b >> c))(x)`.
- works on a bare `Node` AND on a `Tree` (same logical result).
- `.repeat(n)` applies n times; `.when(cond)` applies conditionally.

- [ ] Step 1: write `test/test_transformer_laws.py` (RED if identity/compose/associativity fail). Step 2: fix anything needed (should already hold). Step 3: `pytest test/test_transformer_laws.py -v` -> green. Step 4: full suite green. Step 5: commit `test(transformers): identity/composition/associativity laws; Node and Tree inputs`.

## Definition of Done (P2c)
- One `Transformer` (callable + `>>` + `identity` + `repeat`/`when`); the subclass zoo, `Pipeline`, `ParallelTransformer`, `DebugTransformer` are gone; no `|`/`&` on transformers.
- All factory functions preserved and working on both `Node` and `Tree`; existing transformer behavior preserved (graft dynamic form, normalize, annotate).
- Algebra laws (identity, composition, associativity) tested behaviorally.
- `__init__` exports updated; no dangling imports.
- `python -m pytest test/ -q` fully green.
