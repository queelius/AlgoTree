#!/usr/bin/env python3
"""
Example: Pattern matching and dot notation demonstrations.
"""

from AlgoTree import (
    Node, TreeBuilder, 
    dotmatch, dotexists, dotcount, dotfilter, dotpluck,
    pattern_match, Pattern
)


def build_sample_tree():
    """Build a sample application tree."""
    tree = (TreeBuilder()
        .root("app", version="1.0.0")
        .child("src", type="directory")
            .child("models", type="directory")
                .child("user.py", type="file", lines=150, tested=True)
                .sibling("post.py", type="file", lines=200, tested=True)
                .sibling("comment.py", type="file", lines=75, tested=False)
                .up()
            .sibling("views", type="directory")
                .child("index.py", type="file", lines=100, tested=True)
                .sibling("admin.py", type="file", lines=300, tested=False)
                .up()
            .sibling("utils", type="directory")
                .child("helpers.py", type="file", lines=50, tested=True)
                .child("validators.py", type="file", lines=80, tested=True)
                .up(2)
        .sibling("tests", type="directory")
            .child("test_models.py", type="test", lines=200)
            .child("test_views.py", type="test", lines=150)
            .child("test_utils.py", type="test", lines=100)
            .up()
        .sibling("docs", type="directory")
            .child("README.md", type="doc", lines=100)
            .child("API.md", type="doc", lines=200)
        .build())
    
    return tree


def demonstrate_dot_notation(tree):
    """Show dot notation capabilities."""
    print("Dot Notation Examples")
    print("=" * 50)
    
    # Basic path navigation
    print("\n1. Direct path navigation:")
    matches = dotmatch(tree, "app.src.models.user.py")
    print(f"   Found: {[n.name for n in matches]}")
    
    # Wildcards
    print("\n2. Wildcard matching:")
    matches = dotmatch(tree, "app.src.*.*.py")
    print(f"   Python files in src subdirs: {[n.name for n in matches]}")
    
    # Deep wildcards
    print("\n3. Deep wildcard matching:")
    matches = dotmatch(tree, "app.**.test_*")
    print(f"   All test files: {[n.name for n in matches]}")
    
    # Attribute filtering
    print("\n4. Attribute filtering:")
    matches = dotmatch(tree, "app.**[type=file]")
    print(f"   All files: {len(matches)} found")
    
    matches = dotmatch(tree, "app.**[tested=False]")
    print(f"   Untested files: {[n.name for n in matches]}")
    
    # Predicate filtering
    print("\n5. Predicate filtering:")
    matches = dotmatch(tree, "app.**[?(@.lines > 100)]")
    print(f"   Large files (>100 lines): {[n.name for n in matches]}")
    
    # Path existence
    print("\n6. Path existence checks:")
    print(f"   Has models? {dotexists(tree, 'app.src.models')}")
    print(f"   Has backend? {dotexists(tree, 'app.src.backend')}")
    
    # Counting
    print("\n7. Counting matches:")
    print(f"   Total Python files: {dotcount(tree, 'app.**.*.py')}")
    print(f"   Total test files: {dotcount(tree, 'app.tests.*')}")
    
    # Value extraction
    print("\n8. Value extraction with dotpluck:")
    values = dotpluck(tree, "app.version", "app.src.models.user.py")
    print(f"   Extracted values: {values}")


def demonstrate_advanced_filtering(tree):
    """Show advanced filtering capabilities."""
    print("\n" + "=" * 50)
    print("Advanced Filtering")
    print("=" * 50)
    
    # Complex filter expressions
    print("\n1. Complex filter expressions:")
    
    # Find large untested files
    results = dotfilter(tree, "@.lines > 100 and @.tested == False")
    print(f"   Large untested files: {[n.name for n in results]}")
    
    # Find test files with sufficient coverage
    results = dotfilter(tree, "@.type == 'test' and @.lines >= 150")
    print(f"   Well-covered test files: {[n.name for n in results]}")
    
    # Using functions in filters
    results = dotfilter(tree, "contains(@.name, 'test') or contains(@.name, 'spec')")
    print(f"   Test-related files: {[n.name for n in results]}")
    
    # Property checks
    results = dotfilter(tree, "@.is_leaf and @.type == 'file'")
    print(f"   Leaf files: {len(results)}")
    
    results = dotfilter(tree, "not @.is_leaf and @.children.length > 2")
    print(f"   Directories with >2 children: {[n.name for n in results]}")


def demonstrate_pattern_objects(tree):
    """Show Pattern object capabilities."""
    print("\n" + "=" * 50)
    print("Pattern Object Examples")
    print("=" * 50)
    
    # Custom predicate patterns
    print("\n1. Custom predicate patterns:")
    
    # Find nodes with names ending in .py
    py_pattern = Pattern(
        predicate=lambda n: n.name.endswith('.py')
    )
    matches = pattern_match(tree, py_pattern)
    print(f"   Python files: {len(matches)} found")
    
    # Find directories with mixed content
    def has_mixed_content(node):
        if node.is_leaf:
            return False
        types = set(child.payload.get('type') for child in node.children)
        return len(types) > 1
    
    mixed_pattern = Pattern(predicate=has_mixed_content)
    matches = pattern_match(tree, mixed_pattern)
    print(f"   Directories with mixed content: {[n.name for n in matches]}")
    
    # Structural patterns
    print("\n2. Structural patterns:")
    
    # Find nodes with specific child structure
    pattern = Pattern(
        name="src",
        children=[
            Pattern(name="models"),
            Pattern(name="views"),
            Pattern(is_wildcard=True)  # Any third child
        ]
    )
    matches = pattern_match(tree, pattern)
    print(f"   Src with models, views, and more: {len(matches) > 0}")


def analyze_code_quality(tree):
    """Analyze code quality metrics."""
    print("\n" + "=" * 50)
    print("Code Quality Analysis")
    print("=" * 50)
    
    # Get all source files
    src_files = dotmatch(tree, "app.src.**[type=file]")
    test_files = dotmatch(tree, "app.tests.*")
    
    # Calculate metrics
    total_lines = sum(f.payload.get("lines", 0) for f in src_files)
    test_lines = sum(f.payload.get("lines", 0) for f in test_files)
    tested_files = [f for f in src_files if f.payload.get("tested", False)]
    
    print(f"\nCode Metrics:")
    print(f"  Source files: {len(src_files)}")
    print(f"  Test files: {len(test_files)}")
    print(f"  Total source lines: {total_lines}")
    print(f"  Total test lines: {test_lines}")
    print(f"  Test ratio: {test_lines/total_lines:.2%}")
    print(f"  Test coverage: {len(tested_files)}/{len(src_files)} files tested")
    
    # Find files needing attention
    print(f"\nFiles needing attention:")
    
    # Large untested files
    attention = dotfilter(tree, 
        "@.type == 'file' and @.lines > 100 and @.tested == False")
    for f in attention:
        print(f"  - {f.name}: {f.payload['lines']} lines, not tested")
    
    # Small test files (might have insufficient coverage)
    small_tests = dotfilter(tree, "@.type == 'test' and @.lines < 100")
    for t in small_tests:
        print(f"  - {t.name}: Only {t.payload['lines']} lines of tests")


if __name__ == "__main__":
    # Build the sample tree
    tree = build_sample_tree()
    
    # Run demonstrations
    demonstrate_dot_notation(tree)
    demonstrate_advanced_filtering(tree)
    demonstrate_pattern_objects(tree)
    analyze_code_quality(tree)
    
    print("\n" + "=" * 50)
    print("Demo complete!")