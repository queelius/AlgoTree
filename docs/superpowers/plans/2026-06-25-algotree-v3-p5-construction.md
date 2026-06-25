# AlgoTree v3 P5: Construction + DSL Cleanup - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`).

**Goal:** One ergonomic construction surface. Add the `Node.from_list`/`to_list` bridge (name-as-operator) that lets the book's list-ASTs become Nodes; unify the DSL parsers behind one stack-assembler; delete the builder zoo. Also fix the deferred `to_paths(delimiter)` no-op footgun.

**Architecture:** (T1) `from_list`/`to_list` with a configurable `parse_scalar`, plus thread `delimiter` through `paths()`/`to_paths()`. (T2) extract the byte-identical `build_tree` assembler shared by the visual/indent DSL parsers into one helper; `parse(text, syntax='auto'|'visual'|'indent'|'sexpr')` keeps working; `parse_tree` stays as an alias. (T3) delete `TreeBuilder`/`FluentTree`/`TreeContext`/`ChildContext`/`QuickBuilder` and the `tree()`/`branch()`/`leaf()` builder functions (the surface is now `node()` + `Node(...)` + `Node.from_dict`/`from_list`/`from_paths` + `parse()`); remove `builders.py` and `test_builders.py`; update `__init__`. Each breaking task migrates tests in the same commit; suite stays green.

**Tech Stack:** Python 3.8+, pytest. No new deps.

## Global Constraints
- Python `>=3.8`; immutability; tests in `test/`; voice-check hook bans em-dashes in committed `.md`.
- `from_list(['add', 1, ['mul', 3, 2]])` -> `Node('add', Node('1'), Node('mul', Node('3'), Node('2')))` (name-as-operator, leaves nullary). `to_list` is the inverse; leaves map back to scalars via `parse_scalar` (default: try int, then float, then str). The round-trip `from_list(to_list(t)) == t` holds for trees built by `from_list` (modulo scalar parsing).
- Construction surface after P5: `node()`, `Node(...)`, `Node.from_dict`/`from_list`/`from_paths`, `parse()`/`parse_tree()`. The builder classes/functions are gone.
- Source of truth: spec section 5 (D7 name-as-operator); roadmap P5; plus the P2b-deferred `to_paths(delimiter)` fix.

## Current state (read before implementing)
- `AlgoTree/node.py`: `node(name, *children, **attrs)` convenience exists; `Node.from_dict`/`from_paths` exist (P2b); `paths(to_leaves_only=True)` joins `cursor.path` with `/` (hardcoded); `to_paths(delimiter='/')` ignores `delimiter` (the footgun). `Node.to_dict` exists.
- `AlgoTree/dsl.py`: `TreeDSL.parse(text, format='auto')`, `_parse_visual`/`_parse_indent` (their inner `build_tree` functions are byte-identical), `_parse_sexpr`, `_parse_node_spec`/`_parse_attrs`/`_parse_value`. `parse_tree(text, format)` convenience.
- `AlgoTree/builders.py`: `TreeBuilder`, `FluentTree`, `TreeContext`, `ChildContext`, `QuickBuilder`, `tree()`, `branch()` (alias of tree), `leaf()`.
- `AlgoTree/__init__.py`: exports `TreeBuilder`, `FluentTree`, `TreeContext`, `QuickBuilder`, `tree`, `branch`, `leaf as leaf_node`, plus `parse_tree`, `TreeDSL`.
- `test/test_builders.py` (tests the zoo), `test/test_dsl.py` (tests the parsers).

---

### Task 1: `Node.from_list`/`to_list` bridge + fix `to_paths(delimiter)`

**Files:** modify `AlgoTree/node.py` (and `AlgoTree/tree.py` for the Tree forwarder); Test `test/test_from_list.py` (new).

**Design:**
```python
# node.py
@staticmethod
def from_list(data, parse_scalar=str):
    """['op', child, ...] -> Node('op', ...). Scalars (non-list) become nullary nodes named str(scalar)."""
    if isinstance(data, list):
        if not data:
            raise ValueError("cannot build a Node from an empty list")
        head, *rest = data
        return Node(str(head), *[Node.from_list(x, parse_scalar) for x in rest])
    return Node(str(data))

def to_list(self, parse_scalar=None):
    """Inverse of from_list. Leaf -> parse_scalar(name) (default: int, then float, then str). Internal -> [name, *child_lists]."""
    ps = parse_scalar or _default_scalar
    if not self.children:
        return ps(self.name)
    return [self.name] + [c.to_list(parse_scalar) for c in self.children]
```
where `_default_scalar(s)` tries `int(s)`, then `float(s)`, else returns `s`. Note: `from_list` builds leaf names via `str(scalar)`; `to_list` of an internal node keeps the name as a string (the operator), and only leaves are scalar-parsed - so `from_list(['add', 1, 2]).to_list()` round-trips to `['add', 1, 2]`.

Also FIX the footgun: give `paths(to_leaves_only=True, delimiter='/')` a `delimiter` param and join `cursor.path` with it; `to_paths(delimiter='/')` passes it through. Apply the same to the `Tree` forwarder.

- [ ] Step 1: `test/test_from_list.py`: `from_list(['add', 1, ['mul', 3, 2]])` builds the right tree (names 'add'/'1'/'mul'/'3'/'2', right structure); `to_list()` returns `['add', 1, ['mul', 3, 2]]`; round-trip `from_list(x).to_list() == x` for several `x`; leaves with non-numeric names round-trip as strings; `to_paths(delimiter='.')` now joins with '.'.
- [ ] Step 2: fail. Step 3: implement (node.py + tree.py forwarder). Step 4: pass. Step 5: full suite green. Step 6: commit `feat(core): Node.from_list/to_list bridge; fix to_paths delimiter`.

---

### Task 2: Unify the DSL parsers behind one stack-assembler

**Files:** modify `AlgoTree/dsl.py`; Test: `test/test_dsl.py` stays green (extend if needed).

**Design:** Extract the duplicated inner `build_tree(lines, start_idx, parent_indent)` from `_parse_visual` and `_parse_indent` into ONE module-level helper `_assemble(parsed_lines)` that takes a list of `(indent, name, attrs)` and returns the root `Node` (it is the same stack/recursion in both today). `_parse_visual` and `_parse_indent` keep their own line-parsing (glyph-strip vs whitespace) but both call `_assemble(...)`. Keep `_parse_sexpr` as-is. Keep `parse(text, format='auto'|'visual'|'indent'|'sexpr')` and `parse_tree` working unchanged. Optionally accept `syntax=` as an alias kwarg for `format=` (the spec names it `syntax`); keep `format=` for back-compat.

- [ ] Step 1: run `test/test_dsl.py` (baseline). Step 2: extract `_assemble`; route both parsers through it; remove the duplicated inner functions. Step 3: `pytest test/test_dsl.py -v` -> pass (identical outputs); add a test that visual and indent forms of the same tree produce equal Nodes. Step 4: full suite green. Step 5: commit `refactor(dsl): one shared stack-assembler for visual/indent parsers`.

---

### Task 3: Delete the builder zoo

**Files:** delete `AlgoTree/builders.py`, `test/test_builders.py`; modify `AlgoTree/__init__.py`; check `examples/` and other consumers.

**Design:** Remove `TreeBuilder`, `FluentTree`, `TreeContext`, `ChildContext`, `QuickBuilder`, and the `tree()`/`branch()`/`leaf()` builder functions. The construction surface is now `node()` (node.py), `Node(...)`, `Node.from_dict`/`from_list`/`from_paths`, and `parse()`. Update `AlgoTree/__init__.py` to drop the builder imports/`__all__` entries (remove `TreeBuilder`, `FluentTree`, `TreeContext`, `QuickBuilder`, `tree`, `branch`, `leaf_node`). Delete `test/test_builders.py` (it tested the removed zoo; construction is covered by `test_node.py` (node()), `test_node_ops.py`/`test_node_primary.py` (from_dict/from_paths), and `test_from_list.py`). Grep the repo for any remaining import of the deleted names (examples, docs code) and update or remove them.

- [ ] Step 1: grep `grep -rn "TreeBuilder\|FluentTree\|TreeContext\|QuickBuilder\|from AlgoTree import.*\btree\b\|builders" AlgoTree examples test` to find all consumers. Step 2: delete `builders.py` + `test_builders.py`; update `__init__`; fix/remove any other consumer (e.g. examples). Step 3: `python -c "import AlgoTree"` works; `python -m pytest test/ -q` collects cleanly and is green. Step 4: commit `feat(core)!: delete the builder zoo; node()/from_*/parse() are the construction surface`.

## Definition of Done (P5)
- `Node.from_list`/`to_list` round-trip (name-as-operator); `to_paths(delimiter)` honored.
- One shared DSL stack-assembler; `parse`/`parse_tree` unchanged in behavior.
- Builder zoo gone; construction surface is `node()`/`Node(...)`/`from_dict`/`from_list`/`from_paths`/`parse()`; `__init__` updated; no dangling imports.
- `python -m pytest test/ -q` fully green.
