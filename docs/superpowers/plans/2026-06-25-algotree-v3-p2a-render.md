# AlgoTree v3 P2a: Render Registry (Implementation Plan)

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development. Steps use checkbox (`- [ ]`).

**Goal:** Collapse `exporters.py` + `pretty_tree.py` + `Tree._simple_tree_str` into one `render.py` where rendering is a fold-driven, registry-backed operation parameterized by a `Theme` (charset + palette + escaper), with notebook-native reprs.

**Architecture:** One `render(node, fmt, **opts) -> str` dispatches through a backend registry. The text-tree backend (ascii/unicode) is implemented as a fold that returns a function of inherited context (the "synthesized-vs-inherited attributes" lesson). Structural (mermaid/graphviz) and data (json/yaml/xml/html) backends are registry entries that all route text through one `Escaper`, fixing the HTML-injection hole and the nondeterministic `hash(name)` palette. Old public names (`export_tree`, `save_tree`, `pretty_tree`, `TreeExporter`) survive as thin delegates so nothing downstream breaks.

**Tech Stack:** Python 3.8+, pytest. Optional `PyYAML` for yaml backend (degrade gracefully if absent). No required new runtime deps.

## Global Constraints
- Python `>=3.8`; immutability; tests in `test/`; voice-check hook bans em-dashes in committed `.md`.
- `node.render('ascii')` must reproduce the current `TreeExporter.to_ascii` output for the default style (characterization), and `render('unicode')` the unicode style.
- Every backend that emits text into a structured format MUST escape via the Theme's escaper (no raw f-string interpolation of `node.name`/attrs into html/xml/mermaid).
- The emoji/marker palette must be deterministic across runs (no `hash()` of names).
- Existing public API names keep working: `export_tree(node, fmt, **kw)`, `save_tree(node, path, fmt=None, **kw)`, `pretty_tree(node, ...)`, `TreeExporter` (delegating shim).
- Source of truth: spec sections 4.1, 7; roadmap P2a.

---

### Task 1: `render.py` core - Theme, registry, dispatch, and the text-tree fold

**Files:** Create `AlgoTree/render.py`; modify `AlgoTree/node.py` (add `render` method + reprs hook is Task 4); Test `test/test_render.py`.

**Design (write this):**

```python
# render.py
from typing import Any, Callable, Dict, List, NamedTuple, Optional
from .node import Node

class Theme(NamedTuple):
    # charset for the text tree
    vertical: str
    horizontal: str
    branch: str
    last: str
    # escaper: text -> safe text for the target format
    escape: Callable[[str], str]

IDENTITY_ESCAPE = lambda s: s

ASCII_THEME = Theme("|", "-", "+", "\\", IDENTITY_ESCAPE)
UNICODE_THEME = Theme("│", "─", "├", "└", IDENTITY_ESCAPE)

# A backend: (render_fn(node, **opts) -> str, file_extension)
class _Backend(NamedTuple):
    render: Callable[..., str]
    ext: str

_REGISTRY: Dict[str, _Backend] = {}

def register(fmt: str, render: Callable[..., str], ext: str) -> None:
    _REGISTRY[fmt] = _Backend(render, ext)

def render(node: Node, fmt: str = "unicode", **opts) -> str:
    backend = _REGISTRY.get(fmt)
    if backend is None:
        raise ValueError(f"unknown render format: {fmt!r} (have {sorted(_REGISTRY)})")
    return backend.render(node, **opts)

def extension_for(fmt: str) -> str:
    b = _REGISTRY.get(fmt)
    return b.ext if b else ".txt"

# --- the text tree as a fold returning a function of inherited context ---
# algebra: each node folds to render(prefix, is_last, is_root) -> List[str]
def _text_tree(node: Node, theme: Theme) -> str:
    def alg(n: Node, child_fns: List[Callable[[str, bool, bool], List[str]]]):
        def emit(prefix: str, is_last: bool, is_root: bool) -> List[str]:
            if is_root:
                lines = [n.name]
            else:
                connector = theme.last if is_last else theme.branch
                lines = [f"{prefix}{connector}{theme.horizontal} {n.name}"]
            for i, cf in enumerate(child_fns):
                last = i == len(child_fns) - 1
                if is_root:
                    child_prefix = ""
                else:
                    ext = "    " if is_last else f"{theme.vertical}   "
                    child_prefix = prefix + ext
                lines.extend(cf(child_prefix, last, False))
            return lines
        return emit
    return "\n".join(node.fold(alg)("", True, True))

register("ascii", lambda node, **o: _text_tree(node, ASCII_THEME), ".txt")
register("unicode", lambda node, **o: _text_tree(node, UNICODE_THEME), ".txt")
```

Add to `Node` (node.py): `def render(self, fmt: str = "unicode", **opts) -> str: from .render import render as _r; return _r(self, fmt, **opts)`.

- [ ] Step 1: Write `test/test_render.py` asserting `node.render('ascii')` equals the known ASCII layout (root line, `+- child` / `\- last` connectors) and `render('unicode')` uses box chars, for a 3-level tree. Also `render('bogus')` raises ValueError.
- [ ] Step 2: Run -> fails (no module).
- [ ] Step 3: Create `render.py` per design; add `Node.render`.
- [ ] Step 4: Run `test/test_render.py` -> pass.
- [ ] Step 5: Full non-shell-free suite `python -m pytest test/ -q` -> green.
- [ ] Step 6: Commit `feat(render): render.py core - Theme, registry, fold-based text tree`.

---

### Task 2: Structural backends (mermaid, graphviz) through one escaper

**Files:** modify `render.py`; Test append `test/test_render.py`.

**Design:** add `MERMAID_ESCAPE` and `DOT_ESCAPE` functions; implement `to_mermaid(node, direction="TD", node_shape="round")` and `to_graphviz(node, name="Tree")` as registry backends. Reuse the existing logic from `exporters.py` `to_mermaid`/`to_graphviz` (node-id assignment via a counter is fine; it is not a pure fold and that is acceptable), BUT route all node text through the escaper (no raw interpolation). Use stable node ids (`N0`, `N1`, ... in pre-order). `register('mermaid', ..., '.mmd')`, `register('graphviz', ..., '.dot')`, alias `register('dot', ...)`.

- [ ] Step 1: Test that `render('mermaid')` contains `graph TD`, one `N0(...)` per node, `-->` edges; and that a node named `a<b>"c` is escaped (`&lt;`, `&gt;`, `'`), not raw. Test `render('graphviz')` contains `digraph` and `->` edges and escapes quotes.
- [ ] Step 2: fail. Step 3: implement. Step 4: pass. Step 5: full suite green. Step 6: commit `feat(render): mermaid + graphviz backends with escaping`.

---

### Task 3: Data backends (json, yaml, xml) - real emitters

**Files:** modify `render.py`; Test append.

**Design:** `to_json(node, indent=2)` via `json.dumps(node.to_dict(), indent=...)`. `to_yaml(node)` via `import yaml; yaml.safe_dump(node.to_dict(), sort_keys=False)` if PyYAML available, else raise a clear ImportError with install hint (do NOT hand-roll YAML). `to_xml(node, root_tag="tree")` via `xml.etree.ElementTree` (build an Element tree from nodes, attrs as element attributes with str() values, children nested; `ElementTree.tostring`), pretty-print with `minidom` or `ElementTree.indent` (3.9+: guard, fall back to compact on 3.8). Register json/.json, yaml/.yaml, xml/.xml.

- [ ] Step 1: Test `json.loads(render('json'))` round-trips name/attrs/children; `render('xml')` parses via `ElementTree.fromstring` and has the root tag + node elements; if PyYAML present, `yaml.safe_load(render('yaml'))` equals `node.to_dict()` (skip yaml assertion with importorskip if not installed).
- [ ] Step 2-6 as above; commit `feat(render): json/yaml/xml backends via stdlib + PyYAML`.

---

### Task 4: HTML backend (escaped) + notebook reprs + stable palette

**Files:** modify `render.py`, `node.py` (add `_repr_html_`, `_repr_mermaid_`); Test append.

**Design:** `to_html(node, include_styles=True, collapsible=True)` reusing the existing CSS/JS but routing ALL `node.name` and attr text through an HTML escaper (`html.escape`) - this fixes the injection hole. Provide a deterministic marker palette keyed by a stable function (e.g. sorted index of distinct names, or `zlib.crc32(name.encode())` - deterministic across runs, NOT builtin `hash`). On `Node`: `_repr_html_(self)` -> `render('html')`; `_repr_mermaid_(self)` -> `render('mermaid')`. (`_repr_svg_` deferred to P3.)

- [ ] Step 1: Test `render('html')` escapes a node named `<script>` to `&lt;script&gt;` (assert raw `<script>` NOT present); `Node(...)._repr_html_()` returns the same as `render('html')`; the palette/marker for a given name is identical across two calls in separate processes is approximated by asserting two calls in-process are equal AND that it does not use builtin `hash` (assert determinism by value).
- [ ] Step 2-6; commit `feat(render): escaped html backend + _repr_html_/_repr_mermaid_; stable palette`.

---

### Task 5: Re-point public API to the registry; delete old internals; migrate tests

**Files:** rewrite `AlgoTree/exporters.py` (thin delegates), `AlgoTree/pretty_tree.py` (thin delegate), `AlgoTree/tree.py` (`__str__`/`_simple_tree_str` -> `render`), `AlgoTree/__init__.py`; migrate `test/test_exporters.py`, `test/test_tree_print.py`.

**Design:** `export_tree(node, fmt, **kw)` -> `render(node, fmt, **kw)` (keep the `flat`/`graph` aliases by registering a `flat` backend that delegates to interop's flat-dict, or keep `to_flat` in exporters as a delegate to interop). `save_tree` -> write `render(...)` with extension auto-detect via `extension_for`/a format map. `pretty_tree(node, ...)` -> `render(node, 'unicode')` (preserve its current signature/behavior as closely as tests require). `TreeExporter` becomes a class of staticmethods delegating to `render(node, fmt)`. `Tree.__str__` -> `render(self._root, 'unicode')`. Update `test_exporters.py`/`test_tree_print.py` to the new outputs where the format changed (keep assertions behavior-focused: structure present, escaping correct), not brittle whitespace.

- [ ] Step 1: Run existing `test_exporters.py`/`test_tree_print.py` to capture current expectations; adjust only where the registry output legitimately differs (document each change in the report).
- [ ] Step 2: Rewrite the delegates; update `__init__` exports (add `render`, `Theme`, `register`; keep `export_tree`/`save_tree`/`pretty_tree`/`TreeExporter`).
- [ ] Step 3: Run `python -m pytest test/ -q` -> green (whole suite).
- [ ] Step 4: Commit `refactor(render): route export_tree/pretty_tree/Tree.__str__ through registry; drop hand-rolled recursions`.

## Definition of Done (P2a)
- One `render.py` owns all rendering; `node.render(fmt)` works for ascii/unicode/mermaid/graphviz/json/yaml/xml/html.
- HTML-injection hole closed (escaper); palette deterministic.
- `_repr_html_`/`_repr_mermaid_` on Node for Quarto/Jupyter.
- Old public names delegate; `exporters.py`/`pretty_tree.py` are thin; the 8 hand-rolled recursions + fake YAML + string-concatenated XML are gone.
- `python -m pytest test/ -q` fully green.
