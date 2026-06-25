# AlgoTree v3 Phase 0: Promote `fold` to the Primitive (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the catamorphism `Node.fold` as the library's one recursion primitive and re-express `size`, `height`, and `to_dict` as one-line algebras over it, with behavior-identical results and the underlying laws asserted as tests.

**Architecture:** Purely additive and non-breaking. `Node.fold(fn)` does a single bottom-up traversal calling `fn(node, [child_results])`. Three existing members are reimplemented on top of it so their behavior is provably identical while the duplication of hand-rolled recursion shrinks. No public signatures change; no other module is touched.

**Tech Stack:** Python 3.8+, pytest. No new dependencies.

## Global Constraints

- Python floor: `>=3.8` (copied from `setup.py`); do not use 3.9+ only syntax in `AlgoTree/`.
- Immutability: every operation returns a new value and never mutates an existing `Node`.
- No new runtime dependencies in this phase.
- Behavior of `size`, `height`, `to_dict` must remain byte-for-byte identical to v2 output (this phase only changes their *implementation*).
- Tests live under `test/` (singular), run with `python -m pytest`.
- Source of truth: `docs/superpowers/specs/2026-06-24-algotree-v3-fold-cursor-design.md` (sections 3.2, 9).

---

### Task 1: Add `Node.fold` (the catamorphism)

**Files:**
- Modify: `AlgoTree/node.py` (insert a `fold` method in the "Tree-wide transformations" block, after `filter`, ~line 186)
- Test: `test/test_fold.py` (create)

**Interfaces:**
- Consumes: `Node` (existing), its `name`, `attrs`, `children`, `is_leaf`.
- Produces: `Node.fold(self, fn: Callable[[Node, list], T]) -> T` where `fn` receives a node and the list of already-folded child results, in child order. Bottom-up (post-order): all children are folded before their parent.

- [ ] **Step 1: Write the failing test**

Create `test/test_fold.py`:

```python
from AlgoTree import Node


def _sample():
    # root
    #   a (leaf)
    #   b
    #     c (leaf)
    return Node("root",
                Node("a"),
                Node("b", Node("c")))


def test_fold_counts_nodes():
    tree = _sample()
    count = tree.fold(lambda node, child_results: 1 + sum(child_results))
    assert count == 4


def test_fold_is_bottom_up_postorder():
    tree = _sample()
    order = []

    def visit(node, child_results):
        order.append(node.name)
        return None

    tree.fold(visit)
    # children appear before their parent; siblings in order
    assert order == ["a", "c", "b", "root"]


def test_fold_receives_child_results_in_order():
    tree = Node("p", Node("x"), Node("y"), Node("z"))
    names = tree.fold(
        lambda node, child_results: node.name if not child_results else child_results
    )
    assert names == ["x", "y", "z"]


def test_fold_on_leaf_gets_empty_child_results():
    seen = []
    Node("solo").fold(lambda node, child_results: seen.append(child_results))
    assert seen == [[]]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest test/test_fold.py -v`
Expected: FAIL with `AttributeError: 'Node' object has no attribute 'fold'`.

- [ ] **Step 3: Write minimal implementation**

In `AlgoTree/node.py`, add this method immediately after the `filter` method (after line ~185, inside class `Node`, before `find`):

```python
    def fold(self, fn: Callable[['Node', List[T]], T]) -> T:
        """
        Catamorphism: reduce the tree bottom-up.

        Calls fn(node, child_results) for every node, where child_results is
        the list of results already computed for that node's children, in
        order. This is the single recursion primitive: size, height, to_dict,
        rendering, and evaluation are all folds with a different combine step.

        Args:
            fn: Combine step (node, [child_results]) -> result.

        Returns:
            The result of folding the whole subtree rooted at this node.
        """
        child_results = [child.fold(fn) for child in self._children]
        return fn(self, child_results)
```

(`T` and `List` are already imported at the top of `node.py`.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest test/test_fold.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Run the full suite to confirm nothing else moved**

Run: `python -m pytest test/ -q`
Expected: all previously-passing tests still pass (no regressions; this step only added a method).

- [ ] **Step 6: Commit**

```bash
git add AlgoTree/node.py test/test_fold.py
git commit -m "feat(core): add Node.fold catamorphism (the one recursion primitive)"
```

---

### Task 2: Re-express `size` and `height` as fold algebras

**Files:**
- Modify: `AlgoTree/node.py` (`size` property ~line 329-332, `height` property ~line 322-327)
- Test: `test/test_fold.py` (append)

**Interfaces:**
- Consumes: `Node.fold` (from Task 1).
- Produces: no signature change. `Node.size -> int` and `Node.height -> int` keep identical results; only their bodies change to use `fold`.

- [ ] **Step 1: Write the failing test (the laws that pin behavior)**

Append to `test/test_fold.py`:

```python
def test_size_equals_walk_count():
    tree = _sample()
    assert tree.size == len(list(tree.walk()))      # size is node count


def test_size_is_fold():
    tree = _sample()
    assert tree.size == tree.fold(lambda n, cs: 1 + sum(cs))


def test_height_of_leaf_is_zero():
    assert Node("leaf").height == 0


def test_height_is_one_plus_max_child_height():
    tree = _sample()                                # root -> b -> c is the deepest path
    assert tree.height == 2
    assert tree.height == tree.fold(lambda n, cs: 0 if not cs else 1 + max(cs))
```

- [ ] **Step 2: Run test to verify the law tests pass against the CURRENT implementation first**

Run: `python -m pytest test/test_fold.py -k "size or height" -v`
Expected: PASS. (These laws hold for the v2 implementation too; they are the contract we must preserve. If any fails now, stop: the law is wrong, not the code.)

- [ ] **Step 3: Reimplement `size` and `height` on `fold`**

In `AlgoTree/node.py`, replace the existing `size` property body:

```python
    @property
    def size(self) -> int:
        """Get total number of nodes in subtree."""
        return self.fold(lambda _node, child_results: 1 + sum(child_results))
```

And replace the existing `height` property body:

```python
    @property
    def height(self) -> int:
        """Get height of subtree rooted at this node."""
        return self.fold(
            lambda _node, child_results: 0 if not child_results else 1 + max(child_results)
        )
```

- [ ] **Step 4: Run tests to verify they still pass after the rewrite**

Run: `python -m pytest test/test_fold.py test/test_node.py -v`
Expected: PASS (the law tests plus all existing node tests).

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest test/ -q`
Expected: no regressions.

- [ ] **Step 6: Commit**

```bash
git add AlgoTree/node.py test/test_fold.py
git commit -m "refactor(core): derive Node.size and Node.height from fold"
```

---

### Task 3: Re-express `to_dict` as a fold algebra, with the round-trip law

**Files:**
- Modify: `AlgoTree/node.py` (`to_dict` method ~line 262-275)
- Test: `test/test_fold.py` (append)

**Interfaces:**
- Consumes: `Node.fold` (Task 1), `Node.from_dict` (existing static method).
- Produces: no signature change. `Node.to_dict(self) -> Dict[str, Any]` keeps identical output; its body becomes a single fold.

- [ ] **Step 1: Write the failing test (identical output + round-trip law)**

Append to `test/test_fold.py`. Note the `Node` constructor takes `attrs=` (a dict), not `**kwargs`, so attribute nodes are written `Node("a", attrs={"value": 1})`:

```python
def test_to_dict_shape_unchanged():
    tree = Node("root",
                Node("a", attrs={"value": 1}),
                Node("b", Node("c", attrs={"value": 3}), attrs={"value": 2}))
    assert tree.to_dict() == {
        "name": "root",
        "children": [
            {"name": "a", "value": 1},
            {"name": "b", "value": 2, "children": [{"name": "c", "value": 3}]},
        ],
    }


def test_from_dict_to_dict_round_trip():
    tree = Node("root",
                Node("a", attrs={"value": 1}),
                Node("b", Node("c", attrs={"value": 3}), attrs={"value": 2}))
    assert Node.from_dict(tree.to_dict()) == tree        # from_dict . to_dict == id


def test_to_dict_is_fold():
    tree = Node("root", Node("a", attrs={"value": 1}))
    via_fold = tree.fold(
        lambda n, cs: {"name": n.name, **n.attrs, **({"children": cs} if cs else {})}
    )
    assert tree.to_dict() == via_fold
```

- [ ] **Step 2: Run test to verify behavior holds against the CURRENT implementation**

Run: `python -m pytest test/test_fold.py -k "to_dict or round_trip" -v`
Expected: PASS against v2 `to_dict` (these are the contract). If a test fails now, the test is wrong, fix the test, not the code.

- [ ] **Step 3: Reimplement `to_dict` on `fold`**

In `AlgoTree/node.py`, replace the existing `to_dict` method body:

```python
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tree to nested dictionary.

        Returns:
            Dictionary with 'name', attributes, and 'children' list.
        """
        return self.fold(
            lambda node, child_results: {
                'name': node.name,
                **node.attrs,
                **({'children': child_results} if child_results else {}),
            }
        )
```

- [ ] **Step 4: Run tests to verify they still pass after the rewrite**

Run: `python -m pytest test/test_fold.py test/test_node.py test/test_serialization.py -v`
Expected: PASS (round-trip law, shape test, and all existing serialization/node tests that exercise `to_dict`).

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest test/ -q`
Expected: no regressions.

- [ ] **Step 6: Commit**

```bash
git add AlgoTree/node.py test/test_fold.py
git commit -m "refactor(core): derive Node.to_dict from fold; assert from_dict.to_dict == id"
```

---

## Definition of Done (Phase 0)

- `Node.fold` exists, is documented, and is covered by tests for counting, post-order, child-result ordering, and the leaf base case.
- `Node.size`, `Node.height`, `Node.to_dict` are each one fold over an algebra, with byte-identical output verified against their v2 behavior.
- `from_dict . to_dict == id` is asserted as a test.
- `python -m pytest test/ -q` is fully green with no regressions and no new dependencies.
- Nothing outside `AlgoTree/node.py` and `test/test_fold.py` changed (purely additive phase).

## Self-Review notes

- **Spec coverage:** implements the Phase 0 row of spec section 8 ("Promote `fold` to public primitive; rewrite `size`/`height`/`to_dict` ... as algebras") and the relevant laws from section 9 (`from_dict . to_dict == id`, `size == len(list(walk))`). `leaves`/`walk` are intentionally left on their existing generator implementations this phase to preserve laziness and stay non-breaking; converting them is deferred (they are not value-returning algebras and changing them risks the byte-identical constraint).
- **Placeholder scan:** none; every step shows complete code and exact commands.
- **Type consistency:** `fold(fn: Callable[[Node, List[T]], T]) -> T` is used identically in Tasks 1, 2, 3; the algebra signature `(node, child_results)` matches everywhere.
- **Constructor gotcha called out for the implementer:** the v2 `Node` constructor takes `attrs=` (a dict), not `**attrs`. All test code in this plan uses `Node("a", attrs={"value": 1})` accordingly; the `**attrs` ergonomic change is a later phase.
