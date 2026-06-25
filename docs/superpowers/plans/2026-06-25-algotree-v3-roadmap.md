# AlgoTree v3 Roadmap (Phases 2-5): Execution Meta-Plan

**Date:** 2026-06-25
**Status:** Driving to completion
**Spec:** `docs/superpowers/specs/2026-06-24-algotree-v3-fold-cursor-design.md`
**Done so far (merged to master):** Phase 0 (fold primitive), Phase 1 (Cursor + parent removal + shell deletion). Version `3.0.0.dev0`.

This document decomposes the remaining spec phases into safely-sequenced, individually-shippable sub-phases. Each sub-phase gets its own detailed implementation plan (written just-in-time, with complete code) and is executed subagent-driven (per-task implement + review, final whole-branch review), kept suite-green at every step, then merged. The guiding discipline (proven in Phase 1): additive tasks first, each breaking change isolated and pre-routed so the suite never goes red.

## Current module inventory (post Phase 1)

`node.py` (415, the value + fold), `cursor.py` (149, the zipper), `tree.py` (520, the wrapper to dissolve), `selectors.py` (542), `transformers.py` (508, the ~15-class zoo), `builders.py` (503, the construction zoo), `dsl.py` (372, parsers), `exporters.py` (557, 8 hand-rolled recursions), `pretty_tree.py` (121), `serialization.py` (300), `interop.py` (320), `_utils.py` (49).

## Sub-phase sequence

### P2a - Render registry (additive, low risk) [spec Phase 2, render half]
Collapse `exporters.py` + `pretty_tree.py` + `Tree._simple_tree_str` into one `render.py`: a renderer is a fold algebra parameterized by a `Theme` (charset + palette + escaper), behind a backend registry. `node.render(fmt)` dispatches; `node._repr_html_/_repr_svg_/_repr_mermaid_` for Quarto/Jupyter. Route every backend through one `Escaper` (fixes the HTML-injection hole) and one stable keyed palette (fixes the `hash(name)` nondeterminism). Keep `export_tree`/`save_tree`/`pretty_tree` working as thin delegates. Exporters already take `Node`, so this is independent of the merge.
Tasks: (1) `render.py` core: fold-based ascii/unicode + Theme + registry + `node.render`; (2) structural backends as algebras (mermaid, graphviz) through one escaper; (3) data backends (json, yaml via PyYAML, xml via ElementTree) replacing the fake emitters; (4) html backend with escaping + `_repr_html_`/`_repr_svg_`/`_repr_mermaid_`; (5) re-point `export_tree`/`save_tree`/`pretty_tree`/`Tree.__str__` to the registry; delete the old hand-rolled recursions; migrate `test_exporters.py`/`test_tree_print.py`.

### P2b - Merge Node and Tree (breaking) [spec Phase 2, merge half]
A rose tree IS its root. Move `Tree`-only members onto `Node`: factories `from_dict`/`from_paths` (classmethods), and `reduce`/`prune`/`graft`/`flatten`/`select`/`locate`/`cursors_at`/`exists`/`count`/`get_path`/`paths`/`to_paths`/`nodes`/pipe operators. Reconcile the dual `map` to ONE lawful `Node.map` (drop `Tree.map`'s `dict|None` runtime sniffing; provide named `update_attrs` helper). Replace the `Node('<empty>')` sentinel with `Optional[Node]`. `Tree` becomes a thin deprecated veneer in `compat.py` (keeps `.root`, delegates, emits `DeprecationWarning`). Update `selectors.py` (`select` accepts a `Node`), `transformers.py`, `serialization.py`, `interop.py`, and all tests to the single type.
Tasks: (1) add factories + non-conflicting query/structure ops to `Node` (additive); (2) reconcile `map` + add `update_attrs`; replace empty sentinel with Optional; (3) move pipe operators + `reduce`/`select`/`locate`/`cursors_at`/`paths`/`get_path` to `Node`; (4) update `selectors.py`/`transformers.py`/`serialization.py`/`interop.py` to use `Node` directly; (5) move `Tree` to `compat.py` as a deprecated veneer; update `__init__`; migrate `test_tree.py`.

### P2c - Transformer algebra cleanup (breaking) [spec Phase 6 / section 6]
Collapse the ~15 delegating `Transformer`/`Shaper` subclasses to plain `Node -> Node` functions (fold algebras) with `>>` composition carrying a lawful identity; drop the `>>`/`|` duplication (reserve `|`/`&` for selectors only); delete `ParallelTransformer`'s unlawful merge and `DebugTransformer`. Keep `map_`/`filter_`/`prune`/`annotate`/`fold`/`reduce_`/`extract`/`to_dict`/`to_paths` as functions.
Tasks: (1) define the `Transformer` function-composition core (`>>` + identity); (2) re-express the tree->tree ops as functions; (3) re-express the shapers; (4) delete the dead subclasses + update `__init__`; migrate `test_transformers.py`.

### P3 - Trace + diff + the visualization engine (additive) [spec Phase 3]
`Node.fold_traced(fn) -> (result, Trace)`; `Trace` is itself a `Node` (renders/folds/diffs with the same tools). `diff(before, after) -> DiffTree` (a `Node`) via a fold over the position/name-aligned zip; renders through the Theme (green/red/yellow). Step-through frames for the fold animation; pipeline provenance.
Tasks: (1) `fold_traced` + `Trace` structure + `steps()`; (2) `Trace` render (mermaid/html, frontier highlight); (3) `diff` -> `DiffTree` + `summary()`; (4) diff render through Theme; (5) tests + a docs/example notebook stub.

### P4 - Selector lattice with declared matching (breaking) [spec Phase 4]
Declared `name`/`glob`/`regex` constructors (no string sniffing; bare string in find/select stays exact via the boundary lift); collapse the five `...OfSelector` classes into one `AxisSelector(axis, inner)`; assert lattice laws (`any_ & x == x`, De Morgan, `~~x == x`); target `parse(repr(s)) == s`. Fully unify positional selectors (the id-membership shim from Phase 1 is replaced by the cursor-native lattice).
Tasks: (1) declared atoms `name/glob/regex/attr/leaf_/root_/depth_/any_/none_/predicate`; (2) one `AxisSelector` replacing the 5 classes; (3) lattice law property tests; (4) update `parse`/`make_predicate` boundary (bare string = exact) + `__init__`; migrate `test_selectors.py`.

### P5 - Construction + DSL cleanup (breaking) [spec Phase 5]
`Node.from_list(['add',1,['mul',3,2]])` (name-as-operator) + `to_list` inverse with configurable `parse_scalar`; unify the DSL parsers behind one stack-assembler fed per-syntax coalgebras (`parse(text, syntax='indent'|'visual'|'sexpr')`), one declared attribute grammar; delete `TreeBuilder`/`FluentTree`/`TreeContext`/`QuickBuilder`/`branch`/`leaf` alias and the byte-identical `_parse_visual`/`_parse_indent`. Rebuild `serialize.py`/`interop.py` on the canonical fold if not already.
Tasks: (1) `from_list`/`to_list` + round-trip law; (2) unified `parse(text, syntax)` stack-assembler + declared attr grammar; (3) delete the builder zoo + update `__init__`/`bin`; migrate `test_builders.py`/`test_dsl.py`.

## Cross-cutting rules
- Suite green after every task (`python -m pytest test/`); the markdown voice-check hook bans em-dashes in committed files.
- Each breaking sub-phase: land additive pieces first, pre-route consumers, then flip.
- `compat.py` accumulates deprecated veneers (v2 `Tree`, old transformer/builder names) with `DeprecationWarning` + a migration note; deprecated-on-arrival.
- Convert example tests to law/property tests where natural (functor, round-trip, lattice, diff-correctness, structural-sharing).
- Merge each sub-phase to master after its final whole-branch review.

## Status ledger (updated as we go)
- [ ] P2a render registry
- [ ] P2b merge Node/Tree
- [ ] P2c transformer cleanup
- [ ] P3 trace + diff
- [ ] P4 selector lattice
- [ ] P5 construction + DSL
