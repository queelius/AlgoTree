# Transformers

Transformers provide composable, reusable tree operations that can be chained together using operators.

## Tree Transformers

These transform a tree into another tree.

### Map Transformer

Apply a function to all nodes:

```python
from AlgoTree import map_

# Add attribute to all nodes
transformer = map_(lambda n: n.with_attrs(processed=True))

# Double all values
transformer = map_(lambda n: n.with_attrs(
    value=n.get("value", 0) * 2
))

result = transformer(tree)
```

### Filter Transformer

Keep nodes matching a predicate:

```python
from AlgoTree import filter_
from AlgoTree import leaf, name

# Keep only leaves
transformer = filter_(leaf())

# Keep Python files
transformer = filter_(name("*.py"))

# Keep nodes with size > 100
transformer = filter_(lambda n: n.get("size", 0) > 100)
```

### Prune Transformer

Remove nodes matching a selector:

```python
from AlgoTree import prune

# Remove temp directories
transformer = prune("temp*")

# Remove hidden files
transformer = prune(lambda n: n.name.startswith("."))
```

### Graft Transformer

Add subtrees to matching nodes:

```python
from AlgoTree import graft, Node

# Add utils to src directory
transformer = graft("src", Node("utils"))

# Dynamic graft based on node
transformer = graft(
    "src",
    lambda n: Node(f"{n.name}_backup")
)
```

### Flatten Transformer

Flatten tree to specified depth:

```python
from AlgoTree import flatten

# Flatten to depth 2
transformer = flatten(max_depth=2)
```

### Normalize Transformer

Sort children and clean attributes:

```python
from AlgoTree import normalize

# Sort children by name
transformer = normalize(sort_children=True)

# Sort with custom key
transformer = normalize(
    sort_children=True,
    sort_key=lambda n: n.get("priority", 0)
)

# Clean attributes
transformer = normalize(
    clean_attrs=True,
    allowed_attrs=["name", "type"]
)
```

### Annotate Transformer

Add annotations to nodes:

```python
from AlgoTree import annotate

# Add to all nodes
transformer = annotate(visited=True)

# Add to selected nodes
transformer = annotate(
    "*.py",
    file_type="python",
    size=lambda n: len(n.name)
)
```

## Shapers (Tree to Value)

These transform a tree into a different type.

### Reduce Shaper

Reduce tree to single value:

```python
from AlgoTree import reduce_

# Count total size
transformer = reduce_(
    lambda acc, n: acc + n.get("size", 0),
    initial=0
)

# Collect all names
transformer = reduce_(
    lambda acc, n: acc + [n.name],
    initial=[],
    order="postorder"
)
```

### Fold Shaper

Bottom-up fold:

```python
from AlgoTree import fold

# Calculate subtree sizes
transformer = fold(
    lambda node, child_results: 1 + sum(child_results)
)

# Calculate max depth
transformer = fold(
    lambda node, child_results: (
        1 + max(child_results) if child_results else 0
    )
)
```

### Extract Shaper

Extract values from nodes:

```python
from AlgoTree import extract

# Extract all names
transformer = extract(lambda n: n.name)

# Extract from selected nodes
transformer = extract(
    lambda n: n.get("size"),
    selector="*.py"
)
```

### To Dict Shaper

Convert to dictionary:

```python
from AlgoTree import to_dict

transformer = to_dict(children_key="children")
result = transformer(tree)
```

### To Paths Shaper

Convert to list of paths:

```python
from AlgoTree import to_paths

transformer = to_paths(delimiter="/", to_leaves_only=True)
paths = transformer(tree)
```

## Composing Transformers

### Pipeline (`>>` or `|`)

Chain transformers sequentially:

```python
from AlgoTree import map_, filter_, prune

# Using >> operator
pipeline = (
    prune("temp*")
    >> filter_(lambda n: n.get("size", 0) > 0)
    >> map_(lambda n: n.with_attrs(processed=True))
)

# Using | operator
pipeline = (
    prune("temp*")
    | filter_(lambda n: n.get("size", 0) > 0)
    | map_(lambda n: n.with_attrs(processed=True))
)

result = pipeline(tree)
```

### Parallel (`&`)

Apply multiple transformers and merge:

```python
from AlgoTree import map_

# Apply both transformers
transformer = (
    map_(lambda n: n.with_attrs(a=1))
    & map_(lambda n: n.with_attrs(b=2))
)
```

### Repeat

Apply a transformer multiple times:

```python
from AlgoTree import prune

# Prune 3 times
transformer = prune("empty*").repeat(3)
```

### Conditional

Apply transformer only when condition is met:

```python
from AlgoTree import map_

transformer = map_(
    lambda n: n.with_attrs(large=True)
).when(lambda t: t.size > 100)
```

### Debug

Add debugging to see intermediate results:

```python
from AlgoTree import map_, filter_

pipeline = (
    filter_(lambda n: n.depth > 0).debug("after_filter")
    >> map_(lambda n: n.with_attrs(done=True)).debug("after_map")
)
```

## Using with Trees

### Direct Application

```python
from AlgoTree import Tree, Node, map_

tree = Tree(Node("root", Node("a"), Node("b")))
transformer = map_(lambda n: n.with_attrs(visited=True))

result = transformer(tree)
```

### Pipe Operator

```python
from AlgoTree import Tree, map_, filter_

result = tree | map_(lambda n: {...})
result = tree >> map_(...) >> filter_(...)
```

## Transformer Reference

### Tree Transformers

| Transformer | Description |
|-------------|-------------|
| `map_(fn)` | Map function over nodes |
| `filter_(pred)` | Keep matching nodes |
| `prune(sel)` | Remove matching nodes |
| `graft(sel, subtree)` | Add subtree to matches |
| `flatten(depth)` | Flatten to max depth |
| `normalize(**opts)` | Sort/clean tree |
| `annotate(sel, **attrs)` | Add annotations |

### Shapers

| Shaper | Description |
|--------|-------------|
| `reduce_(fn, init)` | Reduce to value |
| `fold(fn)` | Bottom-up fold |
| `extract(fn, sel)` | Extract from nodes |
| `to_dict(key)` | Convert to dict |
| `to_paths(delim)` | Convert to paths |
