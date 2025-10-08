"""
Showcase of the refined AlgoTree API.

This module demonstrates the elegant, composable API design
that follows Unix philosophy and functional programming principles.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AlgoTree.refined_node import Node, ImmutableNode, MutableNode
from AlgoTree.refined_tree import Tree, TreeSelection
from AlgoTree.refined_transformers import T, Pipeline
from AlgoTree.refined_selectors import S, parse_selector


def example_1_building_trees():
    """Example 1: Building trees with clean API."""
    print("=" * 60)
    print("Example 1: Building Trees")
    print("=" * 60)

    # Immutable tree construction
    root = ImmutableNode(
        "company",
        type="tech",
        revenue="100M"
    )

    # Functional construction
    tree = (root
        .with_child("engineering", size=50)
        .with_child("sales", size=30)
        .with_child("marketing", size=20))

    print("\nImmutable tree structure:")
    print(Tree(tree).render())

    # Mutable tree for in-place operations
    mutable = MutableNode("app", version="1.0")
    config = mutable.add_child_("config", format="json")
    config.add_child_("database", host="localhost", port=5432)
    config.add_child_("cache", type="redis", ttl=3600)

    services = mutable.add_child_("services")
    services.add_child_("auth", provider="oauth2")
    services.add_child_("api", version="v2", rateLimit=1000)

    print("\nMutable tree structure:")
    print(Tree(mutable.to_immutable()).render())


def example_2_fluent_transformations():
    """Example 2: Fluent tree transformations."""
    print("\n" + "=" * 60)
    print("Example 2: Fluent Transformations")
    print("=" * 60)

    # Create sample tree
    root = ImmutableNode("filesystem")
    docs = root.with_child("documents", type="folder")
    docs = docs.with_child("report.pdf", type="file", size=1024)
    docs = docs.with_child("notes.txt", type="file", size=256)

    code = root.with_child("code", type="folder")
    code = code.with_child("main.py", type="file", size=512)
    code = code.with_child("test.py", type="file", size=128, skip=True)

    tree = Tree(root)

    # Fluent transformation chain
    result = (tree
        .filter(lambda n: not n.payload.get("skip", False))  # Skip marked files
        .map(lambda n: {"size_kb": n.payload.get("size", 0) / 1024} if "size" in n.payload else {})
        .modify(S.attr(type="file"), {"processed": True})  # Mark files as processed
        .prune(S.name("test.*"))  # Remove test files
    )

    print("\nOriginal tree:")
    print(tree.render())

    print("\nTransformed tree:")
    print(result.render())

    # Show modified payloads
    print("\nFile nodes after transformation:")
    for node in result.select(S.attr(type="file")):
        print(f"  {node.name}: {node.payload}")


def example_3_composable_pipelines():
    """Example 3: Composable transformation pipelines."""
    print("\n" + "=" * 60)
    print("Example 3: Composable Pipelines")
    print("=" * 60)

    # Create sample data tree
    root = ImmutableNode("data")
    raw = root.with_child("raw", stage="input")
    for i in range(5):
        raw = raw.with_child(f"record_{i}", value=i * 10, active=i % 2 == 0)

    tree = Tree(root)

    # Define reusable pipeline components
    validate = T.filter(lambda n: "value" in n.payload or n.children)
    enrich = T.map(lambda n: {"validated": True, "stage": "processed"})
    cleanup = T.prune(S.attr(active=False))
    sort_by_value = T.sort(key=lambda n: n.payload.get("value", 0), reverse=True)

    # Compose pipeline using >> operator
    pipeline = validate >> enrich >> cleanup >> sort_by_value

    # Apply pipeline
    result = pipeline(tree)

    print("\nOriginal tree:")
    print(tree.render())

    print("\nAfter pipeline:")
    print(result.render())

    # Show the transformation stages
    print("\nPipeline stages:")
    print("1. Validate: Keep nodes with value or children")
    print("2. Enrich: Add metadata")
    print("3. Cleanup: Remove inactive nodes")
    print("4. Sort: Order by value")


def example_4_advanced_selectors():
    """Example 4: Advanced pattern matching with selectors."""
    print("\n" + "=" * 60)
    print("Example 4: Advanced Selectors")
    print("=" * 60)

    # Create a complex tree
    root = ImmutableNode("project")

    src = root.with_child("src", type="directory")
    src = src.with_child("main.py", type="file", lines=100)
    src = src.with_child("utils.py", type="file", lines=50)
    src = src.with_child("config.json", type="config", lines=20)

    tests = root.with_child("tests", type="directory")
    tests = tests.with_child("test_main.py", type="file", lines=80, test=True)
    tests = tests.with_child("test_utils.py", type="file", lines=60, test=True)

    docs = root.with_child("docs", type="directory")
    docs = docs.with_child("README.md", type="doc", lines=200)
    docs = docs.with_child("API.md", type="doc", lines=150)

    tree = Tree(root)

    print("\nProject structure:")
    print(tree.render())

    # Compose complex selectors
    python_files = S.name("*.py")
    large_files = S.attr(lines__gt=75)
    test_files = S.attr(test=True)
    docs_or_configs = S.attr(type="doc") | S.attr(type="config")

    # Combine selectors
    large_python = python_files & large_files
    non_test_python = python_files & ~test_files
    important = (large_files | docs_or_configs) & ~test_files

    print("\nSelector demonstrations:")

    print(f"\nLarge Python files (>75 lines):")
    for node in tree.select(large_python):
        print(f"  - {node.name}: {node.payload['lines']} lines")

    print(f"\nNon-test Python files:")
    for node in tree.select(non_test_python):
        print(f"  - {node.name}")

    print(f"\nImportant files (large or docs/config, not tests):")
    for node in tree.select(important):
        print(f"  - {node.name} ({node.payload.get('type', 'unknown')})")


def example_5_functional_operations():
    """Example 5: Functional operations (map, filter, reduce, fold)."""
    print("\n" + "=" * 60)
    print("Example 5: Functional Operations")
    print("=" * 60)

    # Create a tree with numerical data
    root = ImmutableNode("calculations")

    branch1 = root.with_child("branch1", value=10)
    branch1 = branch1.with_child("leaf1", value=5)
    branch1 = branch1.with_child("leaf2", value=3)

    branch2 = root.with_child("branch2", value=20)
    branch2 = branch2.with_child("leaf3", value=7)
    branch2 = branch2.with_child("leaf4", value=9)

    tree = Tree(root)

    print("\nData tree:")
    print(tree.render())

    # Reduce: sum all values
    total = tree.reduce(
        lambda acc, node: acc + node.payload.get("value", 0),
        initial=0
    )
    print(f"\nSum of all values: {total}")

    # Fold: compute subtree sums bottom-up
    def sum_with_children(node, child_sums):
        node_value = node.payload.get("value", 0)
        return node_value + sum(child_sums)

    subtree_sum = tree.fold(sum_with_children)
    print(f"Root subtree sum (includes all descendants): {subtree_sum}")

    # Map and filter composition
    doubled = tree.map(lambda n: {"value": n.payload.get("value", 0) * 2})
    high_values = doubled.filter(lambda n: n.payload.get("value", 0) > 10)

    print("\nAfter doubling values and filtering > 10:")
    for node in high_values.select(S.all()):
        print(f"  {node.name}: {node.payload.get('value', 0)}")


def example_6_unix_philosophy():
    """Example 6: Unix philosophy - do one thing well, compose beautifully."""
    print("\n" + "=" * 60)
    print("Example 6: Unix Philosophy in Action")
    print("=" * 60)

    # Create a tree
    root = ImmutableNode("system")
    root = root.with_child("process_1", cpu=45, memory=512, priority=1)
    root = root.with_child("process_2", cpu=20, memory=256, priority=2)
    root = root.with_child("process_3", cpu=75, memory=1024, priority=1)
    root = root.with_child("process_4", cpu=10, memory=128, priority=3)

    tree = Tree(root)

    # Each transformer does ONE thing well
    high_cpu = T.filter(lambda n: n.payload.get("cpu", 0) > 30)
    add_alert = T.map(lambda n: {"alert": "high_cpu"} if n.payload.get("cpu", 0) > 50 else {})
    prioritize = T.sort(key=lambda n: n.payload.get("priority", 999))

    # Compose them into meaningful pipelines
    monitor_pipeline = high_cpu >> add_alert >> prioritize

    result = monitor_pipeline(tree)

    print("\nOriginal process tree:")
    for node in tree.select(S.attr(cpu__exists=True)):
        print(f"  {node.name}: CPU={node.payload['cpu']}%, Priority={node.payload['priority']}")

    print("\nAfter monitoring pipeline (high CPU only, with alerts, sorted):")
    for node in result.select(S.attr(cpu__exists=True)):
        alert = node.payload.get("alert", "none")
        print(f"  {node.name}: CPU={node.payload['cpu']}%, Alert={alert}, Priority={node.payload['priority']}")

    # Alternative: Use pipe for open transformations
    summary = tree.pipe(
        lambda t: t.select(S.attr(cpu__gt=30)),  # Get high CPU nodes
        lambda nodes: [n.payload["cpu"] for n in nodes],  # Extract CPU values
        lambda cpus: {"avg": sum(cpus)/len(cpus), "max": max(cpus), "count": len(cpus)}  # Summarize
    )

    print(f"\nHigh CPU summary: {summary}")


def example_7_tree_manipulation():
    """Example 7: Tree manipulation with selection API."""
    print("\n" + "=" * 60)
    print("Example 7: Tree Manipulation with Selections")
    print("=" * 60)

    # Build a tree
    root = ImmutableNode("website")
    pages = root.with_child("pages", type="directory")
    pages = pages.with_child("index.html", type="page", public=True, visits=1000)
    pages = pages.with_child("about.html", type="page", public=True, visits=500)
    pages = pages.with_child("admin.html", type="page", public=False, visits=50)

    api = root.with_child("api", type="directory")
    api = api.with_child("users", type="endpoint", public=False, calls=10000)
    api = api.with_child("products", type="endpoint", public=True, calls=25000)

    tree = Tree(root)

    print("\nWebsite structure:")
    print(tree.render())

    # Use match() for batch operations on selections
    public_pages = tree.match("pages.*").nodes
    print(f"\nFound {len([n for n in public_pages if n.payload.get('public', False)])} public pages")

    # Modify selected nodes
    updated = tree.match("*.html").modify({"last_updated": "2024-01-01"})

    # Complex selection and modification
    high_traffic = (tree
        .match("**")  # All nodes
        .nodes)

    high_traffic_nodes = [n for n in high_traffic
                          if n.payload.get("visits", 0) > 100 or n.payload.get("calls", 0) > 1000]

    print(f"\nHigh traffic nodes:")
    for node in high_traffic_nodes:
        metric = node.payload.get("visits", node.payload.get("calls", 0))
        print(f"  {node.name}: {metric}")


def main():
    """Run all examples."""
    examples = [
        example_1_building_trees,
        example_2_fluent_transformations,
        example_3_composable_pipelines,
        example_4_advanced_selectors,
        example_5_functional_operations,
        example_6_unix_philosophy,
        example_7_tree_manipulation
    ]

    for example in examples:
        example()
        print()

    print("=" * 60)
    print("AlgoTree Refined API Showcase Complete")
    print("=" * 60)
    print("\nKey design principles demonstrated:")
    print("1. Immutability by default with explicit mutation")
    print("2. Composable operations using operators (>>, |, &)")
    print("3. Lazy evaluation with generators")
    print("4. Functional programming (map, filter, reduce, fold)")
    print("5. Unix philosophy: do one thing well")
    print("6. Clean, predictable API that's hard to misuse")
    print("7. Zero external dependencies in core")


if __name__ == "__main__":
    main()