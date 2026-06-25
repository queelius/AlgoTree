# AlgoTree v3 P4: Selector Lattice with Declared Matching - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`).

**Goal:** Make selection a clean Boolean lattice with DECLARED matching (no inferring structure from string contents): `name` is exact, `glob` and `regex` are explicit constructors; collapse the five `...OfSelector` classes into one `AxisSelector(axis, inner)`; assert the lattice laws behaviorally; bare strings at the find/select boundary mean exact name.

**Architecture:** Breaking but contained. (T1) `name()` becomes exact-only; add `glob()`/`regex()`; `_utils.make_predicate` lifts a bare string to exact name (no wildcard sniffing); the string DSL `parse()` may still map `*`/`?` patterns to `glob()` (sniffing is acceptable inside an explicit string parser, not in the programmatic API). (T2) one `AxisSelector` replaces `ChildOfSelector`/`ParentOfSelector`/`DescendantOfSelector`/`AncestorOfSelector`/`SiblingOfSelector`; the `.child_of()/.parent_of()/.descendant_of()/.ancestor_of()/.sibling_of()` methods now construct `AxisSelector`; `matches_at` dispatches on axis. (T3) lattice laws as behavioral property tests; `any_`/`none_` confirmed as top/bottom. Tests migrate in the same task that changes the behavior, so the suite stays green.

**Tech Stack:** Python 3.8+, pytest. No new deps.

## Global Constraints
- Python `>=3.8`; immutability; tests in `test/`; voice-check hook bans em-dashes in committed `.md`.
- DECLARED matching: `name(p)` matches `node.name == p` exactly - NEVER glob/regex. `glob(p)` uses `fnmatch.fnmatch`; `regex(p)` uses `re.fullmatch`. The programmatic API must not infer match type from string contents.
- Bare-string boundary: `node.find('a+b')` / `select('a+b')` / `prune('a+b')` match the literal name `a+b` exactly (via `make_predicate` lifting to exact name).
- The string DSL `parse('*.txt')` MAY still produce `glob('*.txt')` (a string parser is allowed to interpret wildcard syntax); `parse('name')` -> `name('name')` exact.
- All existing selector behaviors that are still expressible must keep working; tests that used `name('*.txt')`/`name(regex)` migrate to `glob`/`regex` in the same commit.
- Source of truth: spec section 3.5; roadmap P4.

## Current state (read before implementing)
- `AlgoTree/selectors.py`: `Selector` ABC with `matches`/`matches_at`, `& | ~ ^`, axis methods, `where`, `at_depth`. Atoms: `NameSelector` (sniffs glob via `*`/`?`, regex via other regex chars, else exact), `AttrsSelector`, `TypeSelector`, `PredicateSelector`, `DepthSelector`, `LeafSelector`, `RootSelector`. Combinators `And/Or/Not/Xor`. Structural: `ChildOfSelector`, `ParentOfSelector`, `DescendantOfSelector`, `AncestorOfSelector`, `SiblingOfSelector` (each with `matches_at`). Factories: `name/attrs/type_/predicate/depth/leaf/root/any_/none/parse`. `parse()` is a small CSS-like string parser.
- `AlgoTree/_utils.py`: `make_predicate(selector)` - for a bare string, uses glob if `*`/`?` present else exact (this is the sniffing to remove at the API boundary; keep glob handling ONLY for the parse DSL).
- `test/test_selectors.py`: uses `name('*.txt')` (wildcard) and `name(r'file\d+\.py')` (regex), the five axis methods via `.child_of`/etc., `parse('*.txt')`, `parse('parent > child')`, `parse('root child')`, and imports the 5 `...OfSelector` class names.
- `AlgoTree/__init__.py`: exports the selector classes + factories.

---

### Task 1: Declared `name`/`glob`/`regex`; bare-string = exact at the boundary

**Files:** modify `AlgoTree/selectors.py`, `AlgoTree/_utils.py`, `AlgoTree/__init__.py`; migrate `test/test_selectors.py` name tests.

**Design:**
- `NameSelector(pattern)` -> EXACT match only: `node.name == pattern`. Remove the glob/regex sniffing. `repr` -> `NameSelector('x')`.
- Add `GlobSelector(pattern)` (`fnmatch.fnmatch(node.name, pattern)`) and `RegexSelector(pattern)` (`re.fullmatch(pattern, node.name) is not None`), each a `Selector` with `matches`/`repr`. Factories `glob(p)` and `regex(p)`.
- `_utils.make_predicate`: a bare string lifts to EXACT name match (`lambda n: n.name == s`) - remove the `*`/`?` glob branch. (Selectors/callables unchanged.)
- `parse()`: when a bare token contains `*` or `?`, build `glob(token)`; otherwise `name(token)`. (Sniffing stays here only - the string DSL is allowed to interpret wildcard syntax.) `[k=v]` -> `attrs`, `:leaf`/`:root` pseudo, `a > b` child, `a b` descendant - unchanged otherwise.
- Export `GlobSelector`, `RegexSelector`, `glob`, `regex` from `__init__`.
- Migrate `test/test_selectors.py`: `test_name_selector_wildcard` -> use `glob('*.txt')`; `test_name_selector_regex` -> use `regex(r'file\d+\.py')`; keep `test_name_selector_exact` with `name(...)`. Add a test that `name('*.txt')` matches a node literally named `*.txt` (and NOT `a.txt`) - pinning exact semantics. Add a test that `make_predicate('a+b')` matches only the literal `a+b`.

- [ ] Step 1: write/migrate the tests (RED for the new exact-name and glob/regex factory tests). Step 2: run -> fail. Step 3: implement. Step 4: `pytest test/test_selectors.py -v` -> pass. Step 5: full suite green. Step 6: commit `feat(selectors)!: declared name/glob/regex; bare string is exact name`.

---

### Task 2: One `AxisSelector` replacing the five structural classes

**Files:** modify `AlgoTree/selectors.py`, `AlgoTree/__init__.py`; migrate `test/test_selectors.py` imports.

**Design:**
- Add `AxisSelector(inner, axis, other)` where `axis in {'child_of','parent_of','descendant_of','ancestor_of','sibling_of'}`; `matches_at(cursor)` first checks `inner.matches_at(cursor)`, then evaluates the axis relation against `other` using the cursor (reuse the exact logic from the five existing classes: child_of -> not root and other.matches_at(cursor.up()); parent_of -> any child cursor matches other; descendant_of -> any ancestor cursor matches other; ancestor_of -> any strict descendant cursor matches other; sibling_of -> any sibling cursor matches other). `matches(node)` raises NotImplementedError (positional). `repr` -> `AxisSelector(inner, 'descendant_of', other)` form that mirrors the method spelling.
- Rewrite the `.child_of/.parent_of/.descendant_of/.ancestor_of/.sibling_of` methods on `Selector` to return `AxisSelector(self, '<axis>', other)`.
- DELETE `ChildOfSelector`, `ParentOfSelector`, `DescendantOfSelector`, `AncestorOfSelector`, `SiblingOfSelector`.
- `__init__`: remove the five class names from imports/`__all__`; add `AxisSelector`.
- `test/test_selectors.py`: remove the five class names from the import line (the tests use the `.child_of`/etc. METHODS, not the classes, so the bodies are unchanged). Confirm `test_child_of_selector`/`parent_of`/`descendant_of`/`ancestor_of`/`sibling_of` still pass via `AxisSelector`.

- [ ] Step 1: run `test/test_selectors.py` (capture green baseline for the axis tests). Step 2: implement `AxisSelector`, rewire methods, delete the 5 classes, update `__init__` + test imports. Step 3: `pytest test/test_selectors.py -v` -> pass (axis tests now exercise `AxisSelector`). Step 4: full suite green. Step 5: commit `refactor(selectors)!: one AxisSelector replaces the five structural classes`.

---

### Task 3: Lattice laws + top/bottom; final polish

**Files:** modify `AlgoTree/selectors.py` (ensure `any_`/`none_`), create `test/test_selector_laws.py`; update `__init__` if needed.

**Design:**
- Ensure `any_()` is the lattice top (matches every node) and `none_()` the bottom (matches no node). (Currently `none` is the factory name; keep `none` and also expose `none_` as an alias for symmetry if the spec uses `none_` - check `__init__`/spec and pick one, exporting both as aliases to avoid breakage.)
- Behavioral lattice-law property tests over a representative sample tree (iterate every node via `walk_cursors`): for selectors `x` drawn from `{name(...), glob(...), leaf_(), depth_(1)}`:
  - identity: `(any_() & x)` matches exactly where `x` does; `(none_() | x)` matches exactly where `x` does.
  - annihilator: `(none_() & x)` matches nowhere; `(any_() | x)` matches everywhere.
  - involution: `~~x` matches exactly where `x` does.
  - De Morgan: `~(x & y)` matches exactly where `(~x | ~y)` does; `~(x | y)` == `(~x & ~y)`.
  Assert by comparing the matched-node sets (via `node.select(...)` or `matches_at` over the sample), not by selector identity.

- [ ] Step 1: write `test/test_selector_laws.py` (RED if `none_`/`any_` or any law fails). Step 2: implement any missing `any_`/`none_`/aliases. Step 3: `pytest test/test_selector_laws.py -v` -> pass. Step 4: full suite green. Step 5: commit `test(selectors): behavioral lattice laws (identity/annihilator/De Morgan/involution)`.

## Definition of Done (P4)
- `name` is exact; `glob`/`regex` are explicit; bare strings at the boundary are exact; the programmatic API never sniffs match type from string contents.
- One `AxisSelector` replaces the five structural classes; the axis methods still work; positional `matches(node)` raises.
- Lattice laws hold behaviorally (identity, annihilator, involution, De Morgan); `any_`/`none_` are top/bottom.
- `python -m pytest test/ -q` fully green.
