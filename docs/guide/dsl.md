# DSL Parsing

AlgoTree supports parsing trees from multiple text formats through its Domain Specific Language (DSL) parser.

## Supported Formats

### Visual Format (Unicode Tree)

The visual format uses Unicode box-drawing characters:

```python
from AlgoTree import parse_tree

tree = parse_tree("""
company
├── engineering
│   ├── frontend
│   └── backend
└── sales
""")
```

With attributes in brackets:

```python
tree = parse_tree("""
company[type:tech]
├── engineering[head:Alice]
│   ├── frontend[size:5]
│   └── backend[size:8]
└── sales[head:Bob]
""")
```

### Indent Format

The indent format uses whitespace for structure:

```python
tree = parse_tree("""
company
  engineering
    frontend
    backend
  sales
""")
```

With attributes (YAML-like):

```python
tree = parse_tree("""
company: {type: tech, revenue: 1M}
  engineering: {head: Alice}
    frontend: {size: 5}
    backend: {size: 8}
  sales: {head: Bob}
""")
```

Or with bracket notation:

```python
tree = parse_tree("""
company[type:tech]
  engineering[head:Alice]
    frontend[size:5]
    backend[size:8]
  sales[head:Bob]
""")
```

### S-Expression Format

The S-expression format uses parentheses:

```python
tree = parse_tree("""
(company
  (engineering
    (frontend)
    (backend))
  (sales))
""")
```

With attributes (Lisp-style keywords):

```python
tree = parse_tree("""
(company :type tech :revenue 1M
  (engineering :head Alice
    (frontend :size 5)
    (backend :size 8))
  (sales :head Bob))
""")
```

## Auto-Detection

The parser auto-detects the format:

```python
from AlgoTree import parse_tree

# Detects visual format (has box characters)
tree = parse_tree("""
root
├── child1
└── child2
""")

# Detects S-expression (starts with parenthesis)
tree = parse_tree("(root (child1) (child2))")

# Detects indent format (default)
tree = parse_tree("""
root
  child1
  child2
""")
```

## Explicit Format

Force a specific format:

```python
tree = parse_tree(text, format='visual')
tree = parse_tree(text, format='indent')
tree = parse_tree(text, format='sexpr')
```

## Using TreeDSL Directly

For more control, use the `TreeDSL` class:

```python
from AlgoTree.dsl import TreeDSL

# Parse with auto-detection
node = TreeDSL.parse(text)

# Parse with specific format
node = TreeDSL.parse(text, format='visual')
```

## Attribute Syntax

### Bracket Notation

```
node[key:value, key2:value2]
```

Values are auto-parsed:

- Numbers: `size:123`, `ratio:3.14`
- Booleans: `active:true`, `hidden:false`
- Strings: `name:"John Doe"`, `type:file`

### Colon Notation (Indent Format)

```
node: {key: value, key2: value2}
```

### Keyword Notation (S-Expression)

```
(node :key value :key2 value2)
```

## Examples

### Parsing File Trees

```python
from AlgoTree import parse_tree

# From `tree` command output
tree = parse_tree("""
project
├── src
│   ├── main.py
│   └── utils.py
├── tests
│   └── test_main.py
└── README.md
""")
```

### Parsing Configuration

```python
tree = parse_tree("""
config
  database
    host: localhost
    port: 5432
  cache
    enabled: true
    ttl: 3600
""")
```

### Parsing Org Charts

```python
tree = parse_tree("""
(CEO :name "Jane Smith"
  (CTO :name "Bob Wilson"
    (Engineering :size 50)
    (DevOps :size 10))
  (CFO :name "Alice Brown"
    (Finance :size 20)
    (HR :size 15)))
""")
```

## Error Handling

```python
from AlgoTree import parse_tree

try:
    tree = parse_tree("invalid (( tree")
except ValueError as e:
    print(f"Parse error: {e}")
```

## Format Comparison

| Format | Best For |
|--------|----------|
| Visual | Output from `tree` command, human-readable docs |
| Indent | Configuration files, YAML-like data |
| S-Expression | Programmatic generation, Lisp users |
