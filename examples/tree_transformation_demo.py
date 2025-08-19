#!/usr/bin/env python3
"""
Example: Tree transformation demonstrations using dotmod family.
"""

from AlgoTree import (
    TreeBuilder, Node,
    dotmod, dotmap, dotmerge, dotannotate,
    dotvalidate, dotnormalize, dotreduce,
    pretty_tree, export_tree
)


def build_sample_tree():
    """Build a sample configuration tree."""
    tree = (TreeBuilder()
        .root("app", version="1.0.0", env="dev")
        .child("config", debug=True, port=8080)
        .sibling("database", host="localhost", port=5432, pool_size=10)
        .sibling("cache", type="memory", ttl=300)
        .sibling("modules")
            .child("auth", enabled=True, provider="local")
            .sibling("api", enabled=True, rate_limit=100)
            .sibling("admin", enabled=False)
        .build())
    return tree


def demonstrate_dotmod():
    """Show dotmod transformation capabilities."""
    print("=" * 60)
    print("DOTMOD: Closed Tree Transformations")
    print("=" * 60)
    
    tree = build_sample_tree()
    print("\nOriginal tree:")
    print(pretty_tree(tree))
    
    # Update multiple nodes
    print("\n1. Update configuration values:")
    tree = dotmod(tree, {
        "app.config": {"debug": False, "port": 9000, "env": "production"},
        "app.database": {"host": "db.prod.example.com", "pool_size": 50}
    })
    
    config = tree.children[0]
    db = tree.children[1]
    print(f"   Config: debug={config.payload['debug']}, port={config.payload['port']}")
    print(f"   Database: host={db.payload['host']}, pool={db.payload['pool_size']}")
    
    # Rename nodes
    print("\n2. Rename cache to redis_cache:")
    tree = dotmod(tree, {"app.cache": "redis_cache"})
    print(f"   Cache renamed to: {tree.children[2].name}")
    
    # Apply functions
    print("\n3. Double all port numbers:")
    tree = dotmod(tree, {
        "app.config": lambda n: {"port": n.payload.get("port", 0) * 2},
        "app.database": lambda n: {"port": n.payload.get("port", 0) * 2}
    })
    print(f"   Config port: {tree.children[0].payload['port']}")
    print(f"   Database port: {tree.children[1].payload['port']}")


def demonstrate_dotmap():
    """Show dotmap functionality."""
    print("\n" + "=" * 60)
    print("DOTMAP: Mapping Transformations")
    print("=" * 60)
    
    tree = build_sample_tree()
    
    # Add timestamps to all nodes
    print("\n1. Add timestamps to all nodes:")
    import time
    tree = dotmap(tree, 
                 lambda n: {"last_modified": int(time.time())},
                 dot_path="**")
    
    print(f"   Root timestamp: {tree.payload.get('last_modified')}")
    print(f"   Config timestamp: {tree.children[0].payload.get('last_modified')}")
    
    # Transform specific fields
    print("\n2. Transform port fields:")
    tree = dotmap(tree, {
        "port": lambda v: f":{v}",  # Format ports as strings with colon
        "enabled": lambda v: "yes" if v else "no"
    }, dot_path="**")
    
    print(f"   Config port: {tree.children[0].payload.get('port')}")
    print(f"   Auth enabled: {tree.children[3].children[0].payload.get('enabled')}")


def demonstrate_dotannotate():
    """Show dotannotate functionality."""
    print("\n" + "=" * 60)
    print("DOTANNOTATE: Adding Metadata")
    print("=" * 60)
    
    tree = build_sample_tree()
    
    # Add computed annotations
    print("\n1. Add structural metadata:")
    tree = dotannotate(tree,
                      lambda n: {
                          "level": n.level,
                          "is_leaf": n.is_leaf,
                          "child_count": len(n.children),
                          "path": ".".join(node.name for node in n.get_path())
                      },
                      annotation_key="_meta")
    
    # Display some annotations
    for node in tree.traverse_preorder():
        if node.level <= 1:
            meta = node.payload.get("_meta", {})
            print(f"   {node.name}: level={meta['level']}, children={meta['child_count']}")


def demonstrate_dotreduce():
    """Show dotreduce functionality."""
    print("\n" + "=" * 60)
    print("DOTREDUCE: Aggregating Tree Data")
    print("=" * 60)
    
    tree = build_sample_tree()
    
    # Count enabled modules
    enabled_count = dotreduce(tree,
                             lambda acc, n: acc + (1 if n.payload.get("enabled") else 0),
                             initial=0,
                             traverse_pattern="app.modules.*")
    print(f"\n1. Enabled modules: {enabled_count}")
    
    # Collect all ports
    ports = dotreduce(tree,
                     lambda acc, n: acc + [n.payload["port"]] if "port" in n.payload else acc,
                     initial=[])
    print(f"\n2. All ports in configuration: {ports}")
    
    # Find maximum tree depth
    max_depth = dotreduce(tree,
                         lambda acc, n: max(acc, n.level),
                         initial=0)
    print(f"\n3. Maximum tree depth: {max_depth}")


def demonstrate_dotmerge():
    """Show dotmerge functionality."""
    print("\n" + "=" * 60)
    print("DOTMERGE: Merging Trees")
    print("=" * 60)
    
    # Create two configuration trees
    tree1 = (TreeBuilder()
        .root("config")
        .child("app", port=8080, debug=True)
        .sibling("database", host="localhost")
        .build())
    
    tree2 = (TreeBuilder()
        .root("config")
        .child("app", port=9000, env="production")
        .sibling("cache", type="redis")
        .build())
    
    print("\n1. Overlay merge (tree2 overrides tree1):")
    merged = dotmerge(tree1, tree2, "overlay")
    app = merged.children[0]
    print(f"   App port: {app.payload['port']} (from tree2)")
    print(f"   App debug: {app.payload.get('debug', 'not set')} (from tree1)")
    print(f"   App env: {app.payload.get('env', 'not set')} (from tree2)")
    
    # Check for new nodes
    cache_nodes = [n for n in merged.children if n.name == "cache"]
    if cache_nodes:
        print(f"   Cache added: type={cache_nodes[0].payload['type']}")


def demonstrate_dotvalidate():
    """Show dotvalidate functionality."""
    print("\n" + "=" * 60)
    print("DOTVALIDATE: Validating Tree Constraints")
    print("=" * 60)
    
    tree = build_sample_tree()
    
    # Validate all modules have required fields
    print("\n1. Validating module configuration:")
    try:
        dotvalidate(tree,
                   lambda n: "enabled" in n.payload,
                   dot_path="app.modules.*")
        print("   ✓ All modules have 'enabled' field")
    except ValueError as e:
        print(f"   ✗ Validation failed: {e}")
    
    # Check for invalid configurations
    print("\n2. Finding invalid nodes:")
    invalid = dotvalidate(tree,
                         lambda n: n.payload.get("port", 0) < 65536,
                         dot_path="**",
                         raise_on_invalid=False)
    if invalid:
        print(f"   Found {len(invalid)} nodes with invalid ports")
    else:
        print("   ✓ All port numbers are valid")


def demonstrate_dotnormalize():
    """Show dotnormalize functionality."""
    print("\n" + "=" * 60)
    print("DOTNORMALIZE: Normalizing Names")
    print("=" * 60)
    
    # Create tree with inconsistent naming
    tree = (TreeBuilder()
        .root("My-App")
        .child("User Config", type="config")
        .sibling("DATABASE_SETTINGS", type="config")
        .sibling("cache-config", type="config")
        .build())
    
    print("\n1. Before normalization:")
    print(pretty_tree(tree))
    
    print("\n2. After normalization:")
    normalized = dotnormalize(tree)
    print(pretty_tree(normalized))


if __name__ == "__main__":
    print("\nAlgoTree Transformation Demonstrations")
    print("======================================\n")
    
    # Run all demonstrations
    demonstrate_dotmod()
    demonstrate_dotmap()
    demonstrate_dotannotate()
    demonstrate_dotreduce()
    demonstrate_dotmerge()
    demonstrate_dotvalidate()
    demonstrate_dotnormalize()
    
    print("\n" + "=" * 60)
    print("Demonstrations complete!")
    print("=" * 60)