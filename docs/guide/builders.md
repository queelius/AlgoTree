# Builders

AlgoTree provides multiple builder patterns for constructing trees fluently.

## TreeBuilder

The primary fluent builder for constructing trees:

```python
from AlgoTree import TreeBuilder

tree = (
    TreeBuilder('root')
    .attr(type='directory')
    .child('src',
        TreeBuilder('main.py', type='file', size=1024),
        TreeBuilder('utils.py', type='file', size=512)
    )
    .child('docs',
        TreeBuilder('README.md', type='file')
    )
    .build()
)
```

### Methods

```python
builder = TreeBuilder('name')

# Add attributes
builder.attr(key=value)
builder.attrs({'key': 'value'})

# Add children
builder.child('name')
builder.child('name', TreeBuilder(...), TreeBuilder(...))
builder.children('a', 'b', TreeBuilder('c'))

# Navigation
builder.up()    # Move to parent
builder.root()  # Move to root

# Build
tree = builder.build()       # Returns Tree
node = builder.build_node()  # Returns Node
```

### Operator Syntax

```python
# Add child with <<
builder = TreeBuilder('root') << 'child1' << 'child2'

# Add attributes with ()
builder = TreeBuilder('root')(type='file', size=1024)
```

## DSL Functions

Quick tree construction with `tree()`, `branch()`, and `leaf()`:

```python
from AlgoTree import tree, branch, leaf

my_tree = tree('root',
    branch('src',
        leaf('main.py', type='file'),
        leaf('utils.py', type='file')
    ),
    branch('docs',
        leaf('README.md', type='file')
    ),
    type='directory'
).build()
```

## FluentTree

Chainable wrapper for Tree operations:

```python
from AlgoTree import FluentTree, Node

fluent = FluentTree(Node('root', Node('a'), Node('b')))

# Chain operations
result = (
    fluent
    .map(lambda n: n.with_attrs(visited=True))
    .filter(lambda n: n.depth > 0)
    .prune('temp*')
    .tree  # Get underlying Tree
)

# Pipe operators
from AlgoTree import map_, filter_

result = fluent | map_(lambda n: {...})
result = fluent >> filter_(...) >> to_dict()
```

### Methods

```python
# Chainable (return FluentTree)
fluent.map(fn)
fluent.filter(pred)
fluent.prune(selector)
fluent.graft(selector, subtree)
fluent.flatten(max_depth)
fluent.transform(fn)

# Terminal (return values)
fluent.find(selector)
fluent.find_all(selector)
fluent.reduce(fn, initial)
fluent.fold(fn)
fluent.to_dict()
fluent.to_paths()
```

## TreeContext

Context manager for building trees with Python's `with` statement:

```python
from AlgoTree import TreeContext

with TreeContext('root') as ctx:
    with ctx.child('src') as src:
        with src.child('main.py', type='file'):
            pass
        with src.child('utils.py', type='file'):
            pass
    with ctx.child('docs') as docs:
        with docs.child('README.md', type='file'):
            pass

tree = ctx.build()
```

### Adding Children Without Context

```python
with TreeContext('root') as ctx:
    with ctx.child('src') as src:
        # Quick add without nesting
        src.add_child('file1.py', type='file')
        src.add_child('file2.py', type='file')
```

## QuickBuilder

Path-based builder for simple tree structures:

```python
from AlgoTree import QuickBuilder

tree = (
    QuickBuilder()
    .root('app')
    .add('src/main.py', type='file')
    .add('src/utils.py', type='file')
    .add('docs/README.md', type='file')
    .add('tests/test_main.py', type='file')
    .build()
)
```

### With Custom Delimiter

```python
tree = (
    QuickBuilder()
    .root('app')
    .add('src.main', type='module')
    .add('src.utils', type='module')
    .build(delimiter='.')
)
```

## Choosing a Builder

| Builder | Best For |
|---------|----------|
| `TreeBuilder` | Full control, complex trees |
| `tree()/branch()/leaf()` | Quick DSL-style construction |
| `FluentTree` | Chaining transformations |
| `TreeContext` | Visually nested structure |
| `QuickBuilder` | Path-based construction |

## Examples

### Complex Tree with TreeBuilder

```python
from AlgoTree import TreeBuilder

project = (
    TreeBuilder('project', type='directory')
    .child('src',
        TreeBuilder('core',
            TreeBuilder('engine.py', type='file', lines=500),
            TreeBuilder('utils.py', type='file', lines=200)
        ),
        TreeBuilder('api',
            TreeBuilder('handlers.py', type='file', lines=300),
            TreeBuilder('routes.py', type='file', lines=150)
        )
    )
    .child('tests',
        TreeBuilder('test_core.py', type='file', lines=400),
        TreeBuilder('test_api.py', type='file', lines=250)
    )
    .child('docs',
        TreeBuilder('README.md', type='file'),
        TreeBuilder('API.md', type='file')
    )
    .build()
)
```

### From Paths with QuickBuilder

```python
from AlgoTree import QuickBuilder

# Build tree from file listing
files = [
    'src/main.py',
    'src/utils/helpers.py',
    'src/utils/validators.py',
    'tests/test_main.py',
    'README.md'
]

builder = QuickBuilder().root('project')
for path in files:
    builder.add(path, type='file')
tree = builder.build()
```

### FluentTree Pipeline

```python
from AlgoTree import FluentTree, Node, map_, filter_

tree = Node('root',
    Node('a', attrs={'value': 10}),
    Node('b', attrs={'value': 5}),
    Node('c', attrs={'value': 15})
)

# Chain operations
result = (
    FluentTree(tree)
    .filter(lambda n: n.get('value', 0) > 7)
    .map(lambda n: n.with_attrs(
        value=n.get('value', 0) * 2
    ))
    .to_dict()
)
```
