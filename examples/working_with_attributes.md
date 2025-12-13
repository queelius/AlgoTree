# Working with Node Attributes in AlgoTree Shell

Node attributes allow you to store metadata on each node in your tree. The shell provides several commands for creating and manipulating attributes.

## Creating Nodes with Attributes

### Using mkdir/touch with attributes

You can specify attributes when creating nodes using `key=value` syntax:

```bash
/ $ mktree users
/ $ cd users
/users $ mkdir alice name=Alice age=30 role=Engineer
/users $ mkdir bob name=Bob age=25 role=Designer
/users $ ls
alice
bob

/users $ cat alice
name: alice
attrs:
  name: Alice
  age: 30
  role: Engineer
children: 0
is_leaf: True
```

### Attribute Types

The shell automatically parses attribute values:

```bash
/users $ mkdir product name=Widget price=19.99 stock=100 active=true
/users $ cat product
name: product
attrs:
  name: Widget
  price: 19.99          # float (contains decimal point)
  stock: 100            # int
  active: true          # string (booleans are stored as strings)
```

## Modifying Attributes

### Adding/Updating Attributes with setattr

Use `setattr` to add new attributes or update existing ones:

```bash
/users $ cd alice
/users/alice $ setattr email=alice@example.com department=Engineering
Updated attributes: ['name', 'age', 'role', 'email', 'department']

/users/alice $ cat
name: alice
attrs:
  name: Alice
  age: 30
  role: Engineer
  email: alice@example.com
  department: Engineering
children: 0
is_leaf: True
```

### Updating Existing Attributes

```bash
/users/alice $ setattr age=31 role=SeniorEngineer
Updated attributes: ['name', 'age', 'role', 'email', 'department']

/users/alice $ cat
name: alice
attrs:
  name: Alice
  age: 31               # updated
  role: SeniorEngineer  # updated
  email: alice@example.com
  department: Engineering
children: 0
is_leaf: True
```

## Removing Attributes

### Using rmattr

Remove one or more attributes:

```bash
/users/alice $ rmattr department
Removed attributes: ['department']

/users/alice $ rmattr email role
Removed attributes: ['email', 'role']

/users/alice $ cat
name: alice
attrs:
  name: Alice
  age: 31
children: 0
is_leaf: True
```

## Querying by Attributes

### Using select

Find nodes based on attribute values:

```bash
/users $ cd ..
/users $ select n.get('age', 0) > 28
alice

/users $ select n.get('role', '').endswith('Engineer')
alice

/users $ select n.get('active') == 'true'
product
```

### Using find with attributes

While `find` searches node names, you can use `select` for attribute-based queries:

```bash
# Find nodes with 'name' attribute containing 'A'
/users $ select 'A' in n.get('name', '')
alice

# Find nodes with price > 10
/users $ select n.get('price', 0) > 10
product
```

## Practical Examples

### Example 1: User Directory

```bash
/ $ mktree company
/ $ cd company

/company $ mkdir engineering name=Engineering budget=500000
/company $ mkdir marketing name=Marketing budget=300000
/company $ mkdir sales name=Sales budget=400000

/company $ cd engineering
/company/engineering $ mkdir alice name=Alice salary=120000 level=Senior
/company/engineering $ mkdir bob name=Bob salary=95000 level=Mid
/company/engineering $ mkdir charlie name=Charlie salary=80000 level=Junior

# Find high earners
/company/engineering $ select n.get('salary', 0) > 100000
alice

# Get average salary (using size and descendants)
/company/engineering $ descendants
alice
bob
charlie
```

### Example 2: Product Catalog

```bash
/ $ mktree catalog
/ $ cd catalog

/catalog $ mkdir electronics name=Electronics
/catalog $ mkdir books name=Books
/catalog $ mkdir clothing name=Clothing

/catalog $ cd electronics
/catalog/electronics $ mkdir laptop name=Laptop price=999.99 stock=50 brand=TechCo
/catalog/electronics $ mkdir phone name=Phone price=699.99 stock=100 brand=MobileCo
/catalog/electronics $ mkdir tablet name=Tablet price=399.99 stock=75 brand=TechCo

# Find products under $500
/catalog/electronics $ select n.get('price', 0) < 500
tablet

# Find products by brand
/catalog/electronics $ select n.get('brand') == 'TechCo'
laptop
tablet

# Update stock
/catalog/electronics $ cd laptop
/catalog/electronics/laptop $ setattr stock=45
Updated attributes: ['name', 'price', 'stock', 'brand']

# Add new attributes
/catalog/electronics/laptop $ setattr warranty=2years on_sale=true
```

### Example 3: Task Management

```bash
/ $ mktree tasks
/ $ cd tasks

/tasks $ mkdir pending name=Pending
/tasks $ mkdir in_progress name=InProgress
/tasks $ mkdir done name=Done

/tasks $ cd pending
/tasks/pending $ mkdir task1 title=ImplementAPI priority=high estimate=8
/tasks/pending $ mkdir task2 title=WriteDocs priority=medium estimate=4
/tasks/pending $ mkdir task3 title=FixBug priority=high estimate=2

# Find high priority tasks
/tasks/pending $ select n.get('priority') == 'high'
task1
task3

# Find quick tasks (< 4 hours)
/tasks/pending $ select n.get('estimate', 0) < 4
task3

# Move a task to in_progress (would need cp/mv commands)
# For now, recreate with updated status
/tasks/pending $ cd ../in_progress
/tasks/in_progress $ mkdir task1 title=ImplementAPI priority=high estimate=8 status=in_progress
```

### Example 4: File System Metadata

```bash
/ $ mktree filesystem
/ $ cd filesystem

/filesystem $ mkdir home
/filesystem $ cd home

/filesystem/home $ mkdir alice size=2048 owner=alice permissions=rwxr-xr-x
/filesystem/home $ cd alice
/filesystem/home/alice $ mkdir documents size=512 modified=2024-01-15
/filesystem/home/alice $ mkdir photos size=1024 modified=2024-01-20
/filesystem/home/alice $ touch readme.txt size=4 modified=2024-01-10

# Find large directories
/filesystem/home/alice $ cd ..
/filesystem/home $ select n.get('size', 0) > 500
alice
documents
photos

# Find recently modified
/filesystem/home $ cd alice
/filesystem/home/alice $ select n.get('modified', '') > '2024-01-12'
photos

# Update metadata
/filesystem/home/alice $ cd photos
/filesystem/home/alice/photos $ setattr size=2048 modified=2024-01-25
```

## Tips and Best Practices

### 1. Consistent Naming

Use consistent attribute names across your tree:

```bash
# Good: consistent naming
mkdir user1 name=Alice role=Engineer age=30
mkdir user2 name=Bob role=Designer age=25

# Avoid: inconsistent naming
mkdir user1 name=Alice job=Engineer years=30
mkdir user2 fullname=Bob role=Designer age=25
```

### 2. Type Awareness

Remember that numbers are automatically parsed:

```bash
# These create numeric attributes
mkdir item price=19.99 quantity=100

# These create string attributes
mkdir item price=19.99USD quantity=100items
```

### 3. Querying Safety

Always provide defaults when querying attributes:

```bash
# Good: provides default
select n.get('age', 0) > 30

# Risky: may fail if attribute doesn't exist
select n.attrs['age'] > 30  # KeyError if no 'age' attribute
```

### 4. Viewing Attributes

Use `cat` to see all attributes:

```bash
/path/to/node $ cat
name: mynode
attrs:
  key1: value1
  key2: value2
children: 0
is_leaf: True
```

Use `stat` for more detailed information:

```bash
/path/to/node $ stat
Name: mynode
Path: /tree/path/to/node
Depth: 3
Height: 0
Is Leaf: True
Is Root: False
Children: 0
Descendants: 0
Attributes: 2

Attributes:
  key1: 'value1'
  key2: 'value2'
```

## Summary of Attribute Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `mkdir name key=val` | Create node with attributes | `mkdir alice name=Alice age=30` |
| `touch name key=val` | Create leaf with attributes | `touch file size=1024 type=txt` |
| `setattr key=val` | Add/update attributes | `setattr email=alice@example.com` |
| `rmattr key` | Remove attributes | `rmattr email age` |
| `cat` | View node attributes | `cat` or `cat nodename` |
| `stat` | Detailed node info | `stat` or `stat nodename` |
| `select expr` | Query by attributes | `select n.get('age') > 30` |

## Next Steps

- Combine attributes with tree operations (`map`, `filter`)
- Export trees with attributes to JSON/YAML
- Use attributes for domain-specific modeling
- Build complex data structures with rich metadata
