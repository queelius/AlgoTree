#!/usr/bin/env python3
"""
Comprehensive test suite for the refined AlgoTree API.

This file demonstrates and tests all major features of the new API:
- Immutable nodes with functional operations
- Tree wrapper with consistent API
- Composable selectors
- Composable transformers
- Fluent builders
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from AlgoTree import (
    # Core
    Node, node, Tree,
    # Selectors
    name, attrs, type_, predicate, depth, leaf, root,
    # Transformers
    map_, filter_, prune, graft, flatten, normalize, annotate,
    reduce_, fold, extract, to_dict, to_paths,
    Pipeline,
    # Builders
    TreeBuilder, FluentTree, tree, branch, leaf as leaf_builder
)


def test_node_creation():
    """Test basic node creation and immutability."""
    print("Testing Node Creation...")

    # Create nodes using constructor
    root = Node('root', attrs={'type': 'directory'})
    child1 = Node('child1', attrs={'value': 1})
    child2 = Node('child2', attrs={'value': 2})

    # Immutable operations
    root_with_children = root.with_child(child1).with_child(child2)

    # Original root is unchanged
    assert len(root.children) == 0
    assert len(root_with_children.children) == 2

    # Using convenience function
    tree = node('root',
        node('src',
            'main.py',
            'utils.py'
        ),
        node('docs',
            'README.md'
        )
    )

    assert tree.name == 'root'
    assert len(tree.children) == 2
    assert tree.children[0].name == 'src'
    assert len(tree.children[0].children) == 2

    print("✓ Node creation works correctly")


def test_tree_operations():
    """Test Tree wrapper and functional operations."""
    print("\nTesting Tree Operations...")

    # Create tree
    t = Tree(
        node('root',
            node('a', value=1),
            node('b', value=2),
            node('c',
                node('d', value=3),
                node('e', value=4)
            )
        )
    )

    # Test size and height
    assert t.size == 6
    assert t.height == 2

    # Test map operation
    doubled = t.map(lambda n: {'value': n.get('value', 0) * 2})
    assert doubled.find('a')['value'] == 2
    assert doubled.find('d')['value'] == 6

    # Test filter operation
    filtered = t.filter(lambda n: n.get('value', 0) > 2)
    assert filtered.size == 4  # root, c, d, e kept (root and c as pathways)

    # Test reduce operation
    total = t.reduce(lambda acc, n: acc + n.get('value', 0), 0)
    assert total == 10

    # Test fold operation
    def sum_subtree(node, child_sums):
        node_val = node.get('value', 0)
        return node_val + sum(child_sums)

    subtree_sum = t.fold(sum_subtree)
    assert subtree_sum == 10

    print("✓ Tree operations work correctly")


def test_selectors():
    """Test composable selector system."""
    print("\nTesting Selectors...")

    t = Tree(
        node('root',
            node('file1.txt', **{'type': 'file', 'size': 100}),
            node('file2.py', **{'type': 'file', 'size': 200}),
            node('dir1',
                node('file3.txt', **{'type': 'file', 'size': 150}),
                node('file4.py', **{'type': 'file', 'size': 250}),
                **{'type': 'directory'}
            )
        )
    )

    # Name selector
    txt_files = list(name('*.txt').select(t))
    assert len(txt_files) == 2
    assert all(f.name.endswith('.txt') for f in txt_files)

    # Attribute selector
    files = list(type_('file').select(t))
    assert len(files) == 4

    # Composite selectors
    large_py_files = type_('file') & name('*.py') & attrs(size=lambda s: s > 200)
    matches = list(large_py_files.select(t))
    assert len(matches) == 1
    assert matches[0].name == 'file4.py'

    # Structural selectors
    files_in_dir1 = type_('file').descendant_of(name('dir1'))
    matches = list(files_in_dir1.select(t))
    assert len(matches) == 2
    assert all(m.name in ['file3.txt', 'file4.py'] for m in matches)

    print("✓ Selectors work correctly")


def test_transformers():
    """Test composable transformer system."""
    print("\nTesting Transformers...")

    t = Tree(
        node('root',
            node('src',
                node('main.py', type='file'),
                node('utils.py', type='file')
            ),
            node('test',
                node('test_main.py', type='file')
            ),
            node('README.md', type='file')
        )
    )

    # Single transformer
    annotated = annotate(type_='file', processed=True)(t)
    assert annotated.find('main.py')['processed'] == True

    # Pipeline of transformers
    pipeline = (
        annotate(type_='file', status='pending') >>
        map_(lambda n: {'status': 'processed'} if n.get('type') == 'file' else None) >>
        prune('README.md')
    )

    result = pipeline(t)
    assert result.find('main.py')['status'] == 'processed'
    assert result.find('README.md') is None
    assert result.size == 5  # root, src, test, main.py, utils.py, test_main.py

    # Shaper transformers (tree -> other type)
    paths = to_paths()(t)
    assert 'root/src/main.py' in paths

    file_names = extract(lambda n: n.name, type_('file'))(t)
    assert set(file_names) == {'main.py', 'utils.py', 'test_main.py', 'README.md'}

    print("✓ Transformers work correctly")


def test_builders():
    """Test fluent builder API."""
    print("\nTesting Builders...")

    # TreeBuilder with method chaining
    t1 = (
        TreeBuilder('root')
        .attr(type='directory')
        .child('src')
        .child('docs',
            TreeBuilder('guide.md', type='file'),
            TreeBuilder('api.md', type='file')
        )
        .build()
    )

    assert t1.size == 4
    assert t1.root['type'] == 'directory'
    assert t1.find('guide.md')['type'] == 'file'

    # DSL-style builder
    t2 = tree('app',
        branch('frontend',
            leaf_builder('App.tsx', type='file'),
            leaf_builder('index.tsx', type='file')
        ),
        branch('backend',
            leaf_builder('server.py', type='file')
        )
    ).build()

    assert t2.size == 6
    assert len(t2.root.children) == 2

    # FluentTree for chaining operations
    ft = (
        FluentTree('root')
        .map(lambda n: {'id': n.name})
        .filter(lambda n: n.name != 'excluded')
        .prune('unwanted')
    )

    assert ft.tree.root['id'] == 'root'

    print("✓ Builders work correctly")


def test_immutability():
    """Test that operations preserve immutability."""
    print("\nTesting Immutability...")

    # Create original node
    original = node('root',
        node('child1', value=1),
        node('child2', value=2)
    )

    # Modify operations return new nodes
    modified = original.with_attrs(modified=True)
    assert original.get('modified') is None
    assert modified.get('modified') == True

    # Children operations
    with_new_child = original.with_child('child3')
    assert len(original.children) == 2
    assert len(with_new_child.children) == 3

    # Map operations
    mapped = original.map(lambda n: n.with_attrs(mapped=True))
    assert original.get('mapped') is None
    assert mapped.get('mapped') == True
    assert all(child.get('mapped') == True for child in mapped.children)

    print("✓ Immutability is preserved")


def test_composition():
    """Test that all components compose naturally."""
    print("\nTesting Composition...")

    # Build tree
    t = tree('project',
        branch('src',
            leaf_builder('main.py', type='file', loc=100),
            leaf_builder('utils.py', type='file', loc=50)
        ),
        branch('tests',
            leaf_builder('test_main.py', type='file', loc=75)
        ),
        leaf_builder('README.md', type='file', loc=25)
    ).build()

    # Complex selector
    src_files = type_('file').descendant_of(name('src'))

    # Complex transformer pipeline
    pipeline = (
        annotate(src_files, source=True) >>
        map_(lambda n: {'total_loc': n.get('loc', 0)} if n.is_root else None) >>
        normalize(sort_children=True)
    )

    # Apply pipeline
    result = t | pipeline

    # Verify results
    main_py = result.find('main.py')
    assert main_py['source'] == True
    assert main_py['type'] == 'file'

    readme = result.find('README.md')
    assert readme.get('source') is None

    # Extract metrics
    total_loc = reduce_(lambda acc, n: acc + n.get('loc', 0), 0)(result)
    assert total_loc == 250

    print("✓ Components compose correctly")


def test_tree_traversal():
    """Test tree traversal methods."""
    print("\nTesting Tree Traversal...")

    t = Tree(
        node('A',
            node('B',
                node('D'),
                node('E')
            ),
            node('C',
                node('F')
            )
        )
    )

    # Preorder
    preorder = [n.name for n in t.walk('preorder')]
    assert preorder == ['A', 'B', 'D', 'E', 'C', 'F']

    # Postorder
    postorder = [n.name for n in t.walk('postorder')]
    assert postorder == ['D', 'E', 'B', 'F', 'C', 'A']

    # Level order
    levelorder = [n.name for n in t.walk('levelorder')]
    assert levelorder == ['A', 'B', 'C', 'D', 'E', 'F']

    # Leaves
    leaves = [n.name for n in t.leaves]
    assert set(leaves) == {'D', 'E', 'F'}

    print("✓ Tree traversal works correctly")


def test_practical_example():
    """Test a practical file system example."""
    print("\nTesting Practical Example...")

    # Build a file system tree
    fs = tree('project',
        branch('src',
            branch('components',
                leaf_builder('Button.tsx', type='file', size=1024),
                leaf_builder('Modal.tsx', type='file', size=2048)
            ),
            branch('utils',
                leaf_builder('helpers.ts', type='file', size=512),
                leaf_builder('constants.ts', type='file', size=256)
            )
        ),
        branch('tests',
            leaf_builder('Button.test.tsx', type='file', size=1536)
        ),
        leaf_builder('package.json', type='file', size=384),
        leaf_builder('README.md', type='file', size=2560)
    ).build()

    # Find all TypeScript files
    ts_files = name('*.ts') | name('*.tsx')
    ts_file_list = list(ts_files.select(fs))
    assert len(ts_file_list) == 5

    # Calculate total size of source files
    src_size = fs.reduce(
        lambda acc, n: acc + n.get('size', 0) if n.get('type') == 'file' and 'src' in n.path else acc,
        0
    )
    assert src_size == 3840

    # Transform: add file extensions as type
    def add_extension_type(node):
        if node.get('type') == 'file':
            ext = node.name.split('.')[-1] if '.' in node.name else 'none'
            return {'ext': ext}
        return None

    fs_with_ext = fs.map(add_extension_type)
    assert fs_with_ext.find('Button.tsx')['ext'] == 'tsx'
    assert fs_with_ext.find('README.md')['ext'] == 'md'

    # Export to dictionary
    fs_dict = fs_with_ext.to_dict()
    assert fs_dict['name'] == 'project'
    assert 'children' in fs_dict
    assert len(fs_dict['children']) == 4

    print("✓ Practical example works correctly")


def run_all_tests():
    """Run all test functions."""
    print("=" * 60)
    print("Running Refined AlgoTree API Tests")
    print("=" * 60)

    tests = [
        test_node_creation,
        test_tree_operations,
        test_selectors,
        test_transformers,
        test_builders,
        test_immutability,
        test_composition,
        test_tree_traversal,
        test_practical_example
    ]

    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            return False
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            import traceback
            traceback.print_exc()
            return False

    print("\n" + "=" * 60)
    print("All tests passed successfully!")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)