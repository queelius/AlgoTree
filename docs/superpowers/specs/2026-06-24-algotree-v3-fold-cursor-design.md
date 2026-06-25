# AlgoTree v3: Design Spec for the Fold / Cursor / Trace Substrate

**Date:** 2026-06-24
**Status:** Approved for planning
**Author:** Alexander Towell (with Claude Code)
**Consumer of record:** `~/github/literature/drafts/interpret-this` ("Interpret This: DSLs for the Neural Age")

---

## 1. Charter

AlgoTree v3 is a clean, breaking rewrite whose purpose is to be the minimal, beautiful embodiment of the book's own thesis: that a tree is an AST, a fold is an interpreter, a zipper is a navigation context, and a selector is a pattern. It stops being a general "tree utility library" and becomes the one live AST that threads the book from Chapter 1 onward, with the distinguishing capability of making structural recursion *visible*.

### Decisions locked in brainstorming (do not relitigate without cause)

| # | Decision | Choice |
|---|----------|--------|
| D1 | Mandate | **Clean v3, book-first.** Break v2. Ship a thin, deprecated-on-arrival `compat` shim plus migration guide so existing PyPI users are not stranded. |
| D2 | Role / scope | **Substrate**: AlgoTree owns `fold`, `Cursor`, `Trace`, `diff`, and rendering. Term rewriting is deferred to `rerum` (the book's sibling library). No rewrite engine in core. |
| D3 | Theory on surface | **Plain words public** (`fold`, `build`, `cursor`). Greek (`catamorphism`, `anamorphism`, `zipper`) is named precisely once per concept in book sidebars, never required to use the API. |
| D4 | Pattern matching | Lean on **Python-native `match`/`case`** via `__match_args__` on `Node`. AlgoTree's `Selector` lattice is the *query* surface; native `match` is the *destructuring* surface. |
| D5 | Selector string policy | **Bare string means exact name match.** Globs and regex require explicit `glob(...)` / `regex(...)`. No inferring structure from string contents. |
| D6 | Shell | **Dropped entirely.** The Python API plus notebook rich reprs are the only interfaces. `AlgoTree/shell/` and its tests are removed; the `algotree` / `algotree-shell` console scripts are removed. |
| D7 | `from_list` AST encoding | **Name is the operator/literal.** `['add', 1, ['mul', 3, 2]]` becomes `Node('add', Node('1'), Node('mul', Node('3'), Node('2')))`. Leaves are nullary. |

### Non-goals

- No term-rewriting / pattern-DSL engine (rerum's job; AlgoTree shows a ~15-line *interlude* built on `Cursor` and `diff` in the book, not in the package).
- No interactive shell or REPL.
- No backward source compatibility beyond the deprecated `compat` shim.
- No category-theory vocabulary forced onto the public API surface.

---

## 2. Motivation: what is wrong with v2

Grounded in a full read of the current source (~4.3k lib, ~3.7k shell, ~5k tests):

1. **A latent referential-transparency bug.** `Node.__init__` stores parent via `weakref.ref(self)` and *mutates every child's* `_parent_ref` (`node.py:57-58`). Because every immutable op (`with_attrs`, `map`, `_rebuild`) constructs a new `Node(name, *children)`, shared children get re-pointed at the newest parent (last-build-wins). So `depth`, `path`, `ancestors`, `is_root`, `siblings`, and every structural selector are fragile under the structural sharing the docstring promises, while `__eq__` / `__hash__` ignore parent. Equality and position contradict.
2. **The one good idea is buried.** `Tree.fold` (`tree.py:205-222`) is the catamorphism, and is used by *nothing*. Meanwhile there are eight hand-rolled recursions in `exporters.py`, plus `PrettyTree._build`, `Tree._simple_tree_str`, and three separate dict/tree converters.
3. **Node vs Tree is duplicated surface.** `map`, `filter`, `find`, `find_all`, `walk`, `leaves`, `size`, `height`, `to_dict` exist on both, with subtly different contracts (`Node.map` is strict `Node->Node`; `Tree.map` type-sniffs `Node | dict | None` at runtime). Consumers pay a constant wrap/unwrap tax (`Tree(...)`, `.root`).
4. **Stringly-typed selectors.** `NameSelector` sniffs regex-vs-glob-vs-exact from pattern contents; `make_predicate` uses a *different* glob/exact policy, so `tree.find('a+b')` and `name('a+b')` match differently today. This is the user's own stated anti-pattern.
5. **Construction sprawl.** Eight front-ends (`Node`, `node`, `TreeBuilder`, `tree` / `branch` / `leaf`, `TreeContext`, `QuickBuilder`, `from_dict`, `from_paths`) plus DSL parsers. `branch` is a verbatim alias of `tree`; `QuickBuilder` reimplements `from_paths`; `_parse_visual` and `_parse_indent` are byte-identical.
6. **The shell is a 3.7k-line reimplementation** of navigation (`cd` / `ls` / `pwd` is a zipper) and queries (`eval()`-based predicates, nine copies of `_replace_node_in_tree`) outside the core.
7. **Real defects en route:** an HTML-injection hole in the HTML exporter; a nondeterministic `hash(name)`-based emoji picker in `PrettyTree`; a fake hand-rolled YAML emitter and string-concatenated XML; `Tree.from_dict` mutates its input via `d.pop(...)` inside a "functional" library; a `Node('<empty>')` magic-string sentinel.

---

## 3. Architecture: one type, one recursion, position-as-value

### 3.1 Module DAG (rooted at `core`)

Every module depends only on `core` (`Node` plus `fold`), never sideways:

```
core.py    : Node (frozen value) + fold + fold_traced + __match_args__
  - cursor.py    : Cursor (zipper); position, navigation, local edits
  - select.py    : Selector Boolean lattice; declared name/glob/regex; axis combinator
  - render.py    : render-as-fold + Theme + backend registry + _repr_*_
  -   diff.py    : diff(before, after) -> DiffTree (a Node); renders via render
  - trace.py     : Trace (a Node); fold_traced frames; step-through
  - build.py     : node(), from_dict, from_list, from_paths, parse(text, syntax)
  - pipe.py      : Node->Node transformer algebra (>> with identity), map/filter/prune/annotate
  - serialize.py : save/load/dumps/loads over canonical to_dict/from_dict
  - interop.py   : AlgoGraph / flat-dict / edge-list as derived folds (lower priority)
  - compat.py    : deprecated v2 Tree + transformer shim (DeprecationWarning)
```

**Isolation contract:** each module answers "what does it do, how do you use it, what does it depend on" without reading internals; each is unit-testable against `core` alone.

### 3.2 `core.Node`: a context-free frozen value

```python
class Node:
    __slots__ = ('_name', '_attrs', '_children', '_hash')
    __match_args__ = ('name', 'children')          # D4: native match/case

    def __init__(self, name: str, *children: 'Node', **attrs): ...
    # properties: name, attrs (read-only view), children (tuple)
    # immutable edits: with_name, with_attrs, without_attrs,
    #                  with_child, with_children, without_child, map_children
    # VALUE-LOCAL queries only (no parent!): is_leaf, arity
    # the one recursion:
    def fold(self, f: Callable[['Node', list], T]) -> T: ...
    def fold_traced(self, f) -> tuple[T, 'Trace']: ...
    # derived as one-line algebras (in core or as free fns):
    #   size, height, walk(order), leaves, to_dict
```

**Removed from `Node`** (now properties of a *position*, see Cursor): `parent`, `depth`, `path`, `ancestors`, `siblings`, `is_root`. Removed entirely: `_parent_ref`, `weakref`, the `object.__setattr__` reparenting, the `parent=` kwarg, the `__getstate__` / `__setstate__` parent-rebuild dance.

**`fold` is the primitive.** Bottom-up, `f(node, child_results)`. Everything derives:

```python
size     = lambda n: n.fold(lambda nd, cs: 1 + sum(cs))
height   = lambda n: n.fold(lambda nd, cs: 0 if not cs else 1 + max(cs))
to_dict  = lambda n: n.fold(lambda nd, cs: {'name': nd.name, **nd.attrs,
                                            **({'children': cs} if cs else {})})
evaluate = lambda n: n.fold(lambda nd, cs: scalar(nd.name) if nd.is_leaf
                                           else OPS[nd.name](*cs))     # same shape
```

**`map` and `filter` are folds, with one lawful contract each** (no runtime type-sniffing):
- `map(f: Node->Node)` rebuilds bottom-up; obeys `map(f) . map(g) == map(f . g)`.
- attr-delta and no-op conveniences become *named* helpers (`update_attrs(**kw)`, `identity`), not `isinstance` dispatch.
- `filter(pred)` keeps a node iff it or a descendant matches (structure-preserving); returns `Optional[Node]` (no `<empty>` sentinel).

### 3.3 The synthesized-vs-inherited tension (explicit design choice)

`fold` is bottom-up (synthesized attributes). Renderers need *inherited* context (prefix, `is_last`). Resolution: the render algebra returns a function of context, so `fold` produces `lambda ctx -> str`, threading inherited state downward through one fold. No second primitive. This is surfaced in the book as the named "synthesized vs. inherited attributes" lesson, not hidden as a wart.

### 3.4 `cursor.Cursor`: position is a value

```python
class Cursor:
    # immutable: (focus: Node, spine: tuple[Frame, ...])
    # Frame captures parent name+attrs, left siblings, right siblings.
    def down(self, name_or_index) -> 'Cursor': ...
    def up(self) -> 'Cursor': ...
    def left(self) -> 'Cursor': ...
    def right(self) -> 'Cursor': ...
    def root(self) -> 'Cursor': ...
    @property
    def node(self) -> Node: ...
    @property
    def depth(self) -> int: ...        # read from spine, no tree walk
    @property
    def path(self) -> tuple[str, ...]: ...
    def replace(self, node: Node) -> 'Cursor': ...   # rebuild spine only, O(depth)
    def set_attr(self, **kw) -> 'Cursor': ...
```

Edits rebuild only the spine to the focus (O(depth)); all untouched subtrees are shared. This is the principled cure for section 2.1 and the natural carrier for local edits. The shell's `current_path` plus nine `_replace_node_in_tree` copies were exactly `cursor.replace(...)`, but the shell is dropped (D6), so this is purely a library primitive now.

**Query/position split (no overloading):** `find` / `find_all` return **Nodes** (values); `locate(selector)` / `cursors_at(selector)` return **Cursors** when you intend to edit.

### 3.5 `select.Selector`: one Boolean lattice, declared matching

```python
# atoms (declared, never sniffed):
name('add')          # exact
glob('tmp*')         # fnmatch
regex(r'val_\d+')    # re.fullmatch
attr(trained=True)   # attribute equality / existence / predicate
leaf_(); root_(); depth_(2); any_; none_; predicate(fn)
# combinators: & | ~ ^  (a real lattice: any_ & x == x, De Morgan, absorption)
# axis (ONE class, replacing 5 ...OfSelector classes):
name('x').descendant_of(name('let'))   # axis in {child, parent, descendant, ancestor, sibling}
```

A `Selector` is one composable `Node -> bool`. At API boundaries, a bare `str` lifts to `name(str)` (exact, D5); a bare callable lifts to `predicate`. One `to_selector` at the edge; structured selectors internally. `parse(repr(sel)) == sel` is a target property.

---

## 4. The visualization engine (AlgoTree's defensible niche)

Because there is exactly one recursion, it is instrumented once, and every operation animates for free. No companion library in the book (rerum, JSL, JAF, dotsuite) offers tree-diff or fold-tracing. This is AlgoTree's non-redundant reason to exist.

### 4.1 `render.py`: render is a fold algebra plus a Theme

```python
node.render('mermaid')                 # one dispatch, registry-backed
register('dot', algebra=dot_algebra, ext='.dot', escaper=dot_escape)  # new backend is 1 algebra
node._repr_html_(); node._repr_svg_(); node._repr_mermaid_()          # Quarto/Jupyter auto-render
```

- One `Theme` is charset plus palette plus `Escaper`. Backends (ascii, unicode, mermaid, graphviz, svg, html, json, yaml, xml) are the same fold with different algebras.
- Routing every backend through one `Escaper` fixes the HTML-injection hole; one stable keyed palette fixes the nondeterministic `hash(name)` emoji picker.
- Delete the fake hand-rolled YAML and string-concatenated XML; keep real PyYAML / ElementTree algebras.
- Collapses `exporters.py`, `pretty_tree.py`, and `Tree._simple_tree_str` into `render.py`. The three drifting `extension -> format` maps become one table.

### 4.2 `trace.py`: the reified fold run

```python
result, trace = expr.fold_traced(eval_algebra)
trace.steps()                 # frames in post-order: node visited, child results, value
for frame in trace.steps():
    display(frame.render(highlight=frame.frontier))
```

`Trace` *is* a `Node` (tree-shaped), so it folds, renders, and diffs with the same machinery. Drives:
- **Step-through fold animation**, the book's signature figure ("watch `1+3*2` evaluate"). Uniform across `size` / `eval` / `pretty` because it is Trace-driven, not op-specific.
- **Banana-split inspector**, N algebras overlaid per node in one pass (the fusion law, visible).
- **Pipeline provenance filmstrip**, each `>>` stage annotated by its `diff` (the honest replacement for the decorative `DebugTransformer`, which is deleted).

### 4.3 `diff.py`: structural diff

```python
d = diff(before, after)       # DiffTree (a Node): each node tagged added/removed/changed/unchanged
d.summary()                   # {added: 1, removed: 2, changed: 1}
d.to_mermaid()                # green=new, red=gone, yellow=changed; shared subtrees identical
```

Built as a fold over the position/name-aligned zip of two trees; renders through the same `Theme` machinery. Powers the equivalence/rewriting/optimization chapters ("these ASTs differ ONLY here") and shows structural sharing as a picture.

---

## 5. Construction (`build.py`): one ergonomic surface

- **`node(name, *children, **attrs)`** literal (mixed `str` / `Node`), the everyday surface.
- **`from_dict` / `from_paths` / `from_list`** factories. `from_list` per D7: `from_list(['add', 1, ['mul', 3, 2]])` becomes `Node('add', Node('1'), Node('mul', Node('3'), Node('2')))`; `to_list` is the inverse (leaves to scalar via a configurable `parse_scalar`, default `int` then `float` then `str`). The list-AST bridge is the single change that gets AlgoTree off the appendix shelf into Chapter 1.
- **`parse(text, syntax='indent' | 'visual' | 'sexpr')`**, one stack-assembler fed per-syntax coalgebras; one *declared* attribute grammar (no glyph-replace-then-count-spaces depth detection).
- `from_dict` and `to_dict` are provably inverse, giving a round-trip property test.

**Deleted:** `TreeBuilder`, `FluentTree`, `TreeContext`, `QuickBuilder`, `branch` (alias of `tree`), `leaf` (name collision with `selectors.leaf`), the byte-identical `_parse_visual` / `_parse_indent`, the regex attribute mini-language.

---

## 6. Transformers (`pipe.py`): keep the algebra, lose the zoo

A transformer is just `Node -> Node`. Compose with **`>>`** (one meaning, pipe, with a lawful identity element). `map` / `filter` / `prune` / `annotate` are plain functions (fold algebras):

```python
result = expr >> prune(glob('tmp*')) >> annotate(seen=True)
```

**Deleted:** the ~15 delegating `Transformer` / `Shaper` subclasses; the `>>` / `|` duplication (reserve `|` and `&` for the *selector* lattice only, one operator one meaning across modules); `ParallelTransformer`'s unlawful "simplified" merge; `DebugTransformer` (replaced by the provenance filmstrip).

Term rewriting is **not** a library feature (D2). The book demonstrates it as a ~15-line interlude over `Cursor` and `diff` ("watch rules fire"), explicitly deferring pattern-DSL depth to rerum.

---

## 7. Cuts, migration, removed defects

### 7.1 The cut list (elegance is subtraction)

- **The entire `AlgoTree/shell/` package, its tests, and console scripts** (D6).
- The parent-weakref machinery and everything it drags in (section 2.1).
- The `Node` / `Tree` split: merge to one type; factories and pipes become classmethods / free functions. `Tree` survives only as a deprecated alias in `compat`.
- Both incompatible `map` contracts, replaced by one lawful `map`.
- The ~15 transformer subclasses; the 8 exporter recursions; `pretty_tree.py`; `Tree._simple_tree_str`.
- The `Node('<empty>')` sentinel, replaced by `Optional[Node]`.
- The 8 construction front-ends (see section 5).
- Selector string-sniffing, replaced by declared constructors; 5 axis classes collapsed to 1.
- Fake YAML, string-concatenated XML, the HTML-injection hole, the `hash(name)` emoji nondeterminism.
- Interop's flat-dict shape-guessing becomes a derived fold over canonical `to_dict` (keep the cycle-fix `try` / `finally` as a book sidebar on DFS path-set restoration).

### 7.2 Migration (`compat.py`)

A thin, deprecated-on-arrival shim: a v2-shaped `Tree` wrapper plus the old factory and transformer names, each emitting `DeprecationWarning` and pointing to `docs/migration-v2-to-v3.md`. Present only so existing PyPI installs do not hard-break; it carries none of the v2 warts into the teachable surface. Major version bump to **3.0.0**.

---

## 8. Phasing (each independently shippable, low-risk first)

| Phase | Scope | Breaking? |
|---|---|---|
| **0** | Promote `fold` to public primitive; rewrite `size`, `height`, `to_dict`, `leaves`, `walk` as algebras | No (additive), de-risks everything |
| **1** | `Cursor` plus **remove parent backpointer** from `Node` | **Yes** (keystone correctness fix) |
| **2** | Merge `Node` / `Tree`; `render.py` registry plus `Theme`; delete `exporters.py` / `pretty_tree.py` | **Yes** |
| **3** | `Trace` plus `diff` plus `_repr_*_` (the differentiator) | No (additive) |
| **4** | `select.py` lattice plus declared matching plus axis combinator | **Yes** |
| **5** | `build.py`: `node()` / `from_dict` / `from_list` / `from_paths` plus unified `parse`; delete builder zoo; rebuild `serialize.py` / `interop.py` on canonical fold | **Yes** |
| (cross) | `compat.py` shim plus migration guide authored alongside Phases 1-5 as breaks land | n/a |

Shell removal (D6) happens with Phase 1 (it reads `node.parent` / `.depth` everywhere and cannot survive the parent removal anyway).

---

## 9. Testing strategy: specification-driven (a book lesson in itself)

Convert the example-driven suite to law/property tests (Hypothesis):

- **Immutability and structural sharing:** every op returns a new value; untouched subtrees are `is`-identical; `Cursor.set_attr` rebuilds only the spine.
- **Functor law:** `map(f) . map(g) == map(f . g)`; `map(identity) == identity`.
- **Round-trips:** `from_dict . to_dict == id`; `from_list . to_list == id` (modulo `parse_scalar`); `parse . render == id` per syntax where defined.
- **Selector lattice:** `any_ & x == x`, `none_ | x == x`, De Morgan, `~~x == x`; `to_selector(repr(s))` matches `s`.
- **Diff correctness:** `diff(t, t)` is all-unchanged; `diff` add/remove/change counts match a brute-force oracle.
- **Cursor:** `up . down == identity` at any valid focus; `depth == len(path) - 1`.

Coverage target maintained at the current level or better on the surviving (smaller) surface.

---

## 10. Pedagogical mapping (why each piece earns its place in the book)

| Book chapter | AlgoTree piece |
|---|---|
| Ch.1 Why Interpretation | `Node` as the canonical rose tree; `size` / `height` built live as folds and **animated** |
| Ch.2 Anatomy of a DSL | `from_list` bridge (list-AST to `Node`); `to_dict` / `from_dict` as mirror fold/unfold; render-fold is unparsing |
| Ch.3 Pattern Matching | native `match` / `case` via `__match_args__`; `Selector` lattice as the embedded query DSL with stated laws |
| Ch.4-5 Rewriting / Equivalence | `diff` makes "watch the tree shrink to fixpoint" and "these ASTs differ ONLY here" into *pictures*; rewriting itself deferred to rerum, shown as a Cursor-plus-diff interlude |
| Ch.6 Navigation | motivate the `path: list` re-walk plus the reparenting bug, then **derive `Cursor`** as the fix (Huet's zipper meets a filesystem cursor) |
| Ch.7 Evaluation strategies | `evaluate` is the *same fold* as `size` with the algebra swapped; `Trace` makes bottom-up synthesis watchable; serialize/round-trip for the propose-verify loop |

---

## 11. Open questions / risks

- **`attrs` immutability:** store as a plain `dict` treated as immutable (copy-on-read) versus a frozen mapping. Lean: plain dict plus a read-only property view; revisit if hashing cost matters. (Resolve in Phase 0.)
- **`parse_scalar` ambiguity:** the `from_list` / `to_list` round-trip is exact only modulo scalar parsing (`'1'` versus `1`). Documented edge; default `int` then `float` then `str`, overridable. (Resolve in Phase 5.)
- **Effort:** this is a large breaking rewrite touching every module plus the test suite; the shell removal alone deletes ~5k lines (lib plus tests). Phasing keeps each step shippable and reviewable.
- **`interop.py` priority:** the AlgoGraph bridge is secondary to the book; rebuild it on the canonical fold in Phase 5, or stub it behind `compat` if time-constrained.
