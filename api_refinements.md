# AlgoTree API Refinement Recommendations

## Core Design Principles

1. **Unix Philosophy**: Each component does one thing exceptionally well
2. **Composability**: All operations compose naturally
3. **Immutability by Default**: Operations return new trees unless explicitly marked
4. **Lazy Evaluation**: Use generators and iterators everywhere possible
5. **Type Safety**: Leverage Python's type hints fully

## 1. Node Class Refinements

### Current Issues:
- Missing atomic operations (move, swap, graft)
- Mutating operations mixed with non-mutating
- No clear immutable/mutable separation

### Proposed Improvements:

```python
class Node:
    """Immutable by default, explicit mutation."""

    # Core immutable operations (return new trees)
    def with_name(self, name: str) -> 'Node':
        """Return new tree with node renamed."""

    def with_payload(self, **updates) -> 'Node':
        """Return new tree with payload updated."""

    def with_child(self, child: 'Node', position: int = -1) -> 'Node':
        """Return new tree with child added."""

    def without_child(self, child: Union['Node', str, int]) -> 'Node':
        """Return new tree with child removed."""

    # Explicit mutating operations (suffix with underscore)
    def set_name_(self, name: str) -> None:
        """Mutate: rename this node."""

    def update_payload_(self, **updates) -> None:
        """Mutate: update payload in place."""

    def add_child_(self, child: 'Node', position: int = -1) -> None:
        """Mutate: add child in place."""

    def remove_child_(self, child: Union['Node', str, int]) -> None:
        """Mutate: remove child in place."""

    # Atomic tree operations
    def move_to(self, new_parent: 'Node') -> 'Node':
        """Return new tree with this node moved."""

    def swap_with(self, other: 'Node') -> 'Node':
        """Return new tree with nodes swapped."""

    def graft_onto(self, target: 'Node', children_only: bool = False) -> 'Node':
        """Return new tree with this subtree grafted."""

    # Lazy iteration (all return generators)
    def iter_preorder(self) -> Iterator['Node']:
        """Lazy preorder traversal."""

    def iter_postorder(self) -> Iterator['Node']:
        """Lazy postorder traversal."""

    def iter_levelorder(self) -> Iterator['Node']:
        """Lazy level-order traversal."""

    def iter_leaves(self) -> Iterator['Node']:
        """Iterate over leaf nodes only."""

    def iter_ancestors(self, include_self: bool = False) -> Iterator['Node']:
        """Iterate from this node up to root."""

    # Query operations (composable)
    def select(self, selector: Union[str, Callable, 'Selector']) -> Iterator['Node']:
        """Select nodes matching criteria."""

    def first(self, selector: Union[str, Callable, 'Selector']) -> Optional['Node']:
        """Get first matching node."""

    def exists(self, selector: Union[str, Callable, 'Selector']) -> bool:
        """Check if any node matches."""
```

## 2. Fluent API Refinements

### Current Issues:
- Inconsistent return types (self vs new instance)
- Limited composability
- Missing pipeline operations

### Proposed Improvements:

```python
class Tree:
    """Immutable tree wrapper with fluent API."""

    def __init__(self, root: Node):
        self._root = root

    # All operations return new Tree instances
    def map(self, fn: Callable[[Node], Dict]) -> 'Tree':
        """Map function over all nodes."""

    def filter(self, predicate: Callable[[Node], bool]) -> 'Tree':
        """Filter tree to nodes matching predicate."""

    def reduce(self, fn: Callable[[Any, Node], Any], initial: Any = None) -> Any:
        """Reduce tree to single value."""

    # Composable transformations
    def transform(self, *transformers: 'Transformer') -> 'Tree':
        """Apply series of transformations."""

    def pipe(self, *fns: Callable[['Tree'], Any]) -> Any:
        """Pipe tree through functions."""

    # Pattern-based operations
    def match(self, pattern: str) -> 'TreeSelection':
        """Return selection of matching nodes."""

    def replace(self, pattern: str, replacement: Union[Node, Callable]) -> 'Tree':
        """Replace matching nodes."""

    def modify(self, pattern: str, updates: Dict) -> 'Tree':
        """Modify matching nodes."""

    # Structural operations
    def prune(self, selector: Union[str, Callable]) -> 'Tree':
        """Remove matching subtrees."""

    def graft(self, pattern: str, subtree: Node) -> 'Tree':
        """Graft subtree at matching locations."""

    def flatten(self, levels: int = -1) -> 'Tree':
        """Flatten tree by specified levels."""

    # Export operations (chainable)
    def to(self, format: str, **options) -> Any:
        """Export to format (dict, json, yaml, etc)."""

    def render(self, style: str = 'ascii') -> str:
        """Render tree visually."""
```

## 3. Pattern System Refinements

### Current Issues:
- Pattern compilation not separated from matching
- No pattern composition
- Missing advanced selectors

### Proposed Improvements:

```python
class Selector:
    """Compiled, reusable selector."""

    @classmethod
    def parse(cls, pattern: str) -> 'Selector':
        """Parse pattern string into selector."""

    def __and__(self, other: 'Selector') -> 'Selector':
        """Combine selectors with AND."""

    def __or__(self, other: 'Selector') -> 'Selector':
        """Combine selectors with OR."""

    def __invert__(self) -> 'Selector':
        """Negate selector."""

    def matches(self, node: Node) -> bool:
        """Check if node matches."""

    def select(self, tree: Node) -> Iterator[Node]:
        """Select all matching nodes."""

# Predefined selectors
class S:
    """Selector factory for common patterns."""

    @staticmethod
    def name(pattern: str) -> Selector:
        """Match by name (supports wildcards)."""

    @staticmethod
    def attr(**kwargs) -> Selector:
        """Match by attributes."""

    @staticmethod
    def level(min: int = None, max: int = None) -> Selector:
        """Match by tree level."""

    @staticmethod
    def leaf() -> Selector:
        """Match leaf nodes."""

    @staticmethod
    def root() -> Selector:
        """Match root nodes."""

    @staticmethod
    def has_children(count: Union[int, range] = None) -> Selector:
        """Match by child count."""

    @staticmethod
    def path(pattern: str) -> Selector:
        """Match by path pattern."""
```

## 4. Builder API Refinements

### Current Issues:
- Limited context management
- No validation during building
- Missing batch operations

### Proposed Improvements:

```python
class TreeBuilder:
    """Enhanced builder with validation and context management."""

    def __enter__(self) -> 'TreeBuilder':
        """Support context manager for auto-build."""

    def __exit__(self, *args) -> None:
        """Auto-build on context exit."""

    # Batch operations
    def children(self, *specs: Union[str, Tuple[str, Dict]]) -> 'TreeBuilder':
        """Add multiple children at once."""

    def siblings(self, *specs: Union[str, Tuple[str, Dict]]) -> 'TreeBuilder':
        """Add multiple siblings at once."""

    # Validation
    def validate(self, validator: Callable[[Node], bool]) -> 'TreeBuilder':
        """Add validation rule."""

    def ensure(self, condition: bool, message: str) -> 'TreeBuilder':
        """Ensure condition or raise error."""

    # Templates
    @classmethod
    def from_template(cls, template: Dict) -> 'TreeBuilder':
        """Build from template structure."""

    def apply_template(self, template: Dict) -> 'TreeBuilder':
        """Apply template to current position."""

# Usage example:
with TreeBuilder() as tb:
    tb.root("app", version="1.0")
    tb.children(
        ("config", {"type": "json"}),
        ("database", {"type": "postgres"}),
        ("cache", {"type": "redis"})
    )
    tb.validate(lambda n: n.name != "")
    # Auto-builds on context exit
    tree = tb.tree  # Access built tree
```

## 5. Transformation Pipeline

### Current Issues:
- No clear transformation composition
- Missing reusable transformers
- Poor error handling

### Proposed Improvements:

```python
class Transformer:
    """Base class for composable transformations."""

    def __call__(self, tree: Tree) -> Tree:
        """Apply transformation."""

    def __rshift__(self, other: 'Transformer') -> 'Pipeline':
        """Compose transformers with >>."""

    def __or__(self, other: 'Transformer') -> 'Pipeline':
        """Alternative syntax with |."""

class Pipeline:
    """Composable transformation pipeline."""

    def __init__(self, *transformers: Transformer):
        self.transformers = transformers

    def __call__(self, tree: Tree) -> Tree:
        """Apply all transformations in sequence."""

    def __rshift__(self, other: Transformer) -> 'Pipeline':
        """Add transformer to pipeline."""

    def partial(self, tree: Tree, steps: int) -> Tree:
        """Apply only first N steps."""

    def debug(self, callback: Callable) -> 'Pipeline':
        """Add debug callback between steps."""

# Predefined transformers
class T:
    """Transformer factory."""

    @staticmethod
    def map(fn: Callable) -> Transformer:
        """Map function over nodes."""

    @staticmethod
    def filter(predicate: Callable) -> Transformer:
        """Filter nodes."""

    @staticmethod
    def prune(selector: Selector) -> Transformer:
        """Prune matching nodes."""

    @staticmethod
    def normalize() -> Transformer:
        """Normalize tree structure."""

    @staticmethod
    def sort(key: Callable = None) -> Transformer:
        """Sort children."""

# Usage:
pipeline = T.filter(S.attr(active=True)) >> T.map(add_timestamp) >> T.sort()
result = pipeline(tree)
```

## 6. Simplified Import Structure

```python
# Core imports only
from AlgoTree import Node, Tree, TreeBuilder, S, T

# Everything else is advanced/optional
from AlgoTree.patterns import Pattern, Selector
from AlgoTree.transforms import Transformer, Pipeline
from AlgoTree.export import to_json, to_yaml, to_graphviz
```

## 7. Zero-Dependency Core

The core package should have ZERO external dependencies:
- Use only Python stdlib
- Optional features in extras
- Lazy imports for heavy operations

## 8. Example: Elegant API in Action

```python
from AlgoTree import Tree, TreeBuilder, S, T

# Building trees
tree = (TreeBuilder()
    .root("company")
    .children(
        ("engineering", {"size": 50}),
        ("sales", {"size": 30}),
        ("marketing", {"size": 20})
    )
    .build())

# Fluent transformations
result = (Tree(tree)
    .filter(S.attr(size__gt=25))  # Django-style lookups
    .map(lambda n: {"scaled": n.payload["size"] * 1.1})
    .sort(key=lambda n: n.payload.get("scaled", 0))
    .to("json", indent=2))

# Composable pipelines
process = (
    T.filter(S.leaf() | S.attr(important=True)) >>
    T.map(add_metadata) >>
    T.sort() >>
    T.normalize()
)

processed = process(Tree(tree))

# Pattern-based operations
tree = (Tree(root)
    .match("app.config.*")
    .modify({"validated": True})
    .replace("app.cache", Node("redis", type="cache"))
    .prune(S.attr(deprecated=True)))
```

## 9. Integration Separation

Move these to @integrations:
- Database connectors
- Jupyter widgets
- Pandas/DataFrame operations
- MCP protocol
- LangChain integration
- GraphViz rendering (keep simple ASCII in core)

## 10. Performance Considerations

- All traversals should be lazy (generators)
- Immutable operations should use structural sharing
- Pattern compilation should be cached
- Consider __slots__ for Node class
- Profile and optimize hot paths

## Implementation Priority

1. **Phase 1**: Fix Node class API (immutable/mutable separation)
2. **Phase 2**: Implement Tree wrapper with consistent fluent API
3. **Phase 3**: Refactor pattern system with Selector
4. **Phase 4**: Create Transformer/Pipeline system
5. **Phase 5**: Move integrations out of core
6. **Phase 6**: Performance optimizations

This redesign will make AlgoTree a joy to use while maintaining backward compatibility through deprecation warnings.