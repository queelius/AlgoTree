"""
Tests for tree transformation functionality.
"""

import unittest
from AlgoTree import (
    Node, TreeBuilder,
    dotmod, dotmap, dotprune, dotmerge,
    dotgraft, dotsplit, dotflatten, dotreduce,
    dotannotate, dotvalidate, dotnormalize
)


class TestDotMod(unittest.TestCase):
    """Test dotmod transformation function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("app", version="1.0")
            .child("config", debug=True)
            .sibling("database", host="localhost", port=5432)
            .sibling("cache", enabled=False)
            .build())
    
    def test_update_payload(self):
        """Test updating node payloads."""
        result = dotmod(self.tree, {
            "app.config": {"debug": False, "env": "production"},
            "app.database": {"host": "db.example.com"}
        })
        
        config = result.children[0]
        self.assertEqual(config.payload["debug"], False)
        self.assertEqual(config.payload["env"], "production")
        
        db = result.children[1]
        self.assertEqual(db.payload["host"], "db.example.com")
        self.assertEqual(db.payload["port"], 5432)  # Unchanged
    
    def test_rename_nodes(self):
        """Test renaming nodes."""
        result = dotmod(self.tree, {
            "app.cache": "redis_cache"
        })
        
        self.assertEqual(result.children[2].name, "redis_cache")
    
    def test_function_transformation(self):
        """Test using functions for transformation."""
        def double_port(node):
            return {"port": node.payload.get("port", 0) * 2}
        
        result = dotmod(self.tree, {
            "app.database": double_port
        })
        
        db = result.children[1]
        self.assertEqual(db.payload["port"], 10864)
    
    def test_clear_payload(self):
        """Test clearing payload with None."""
        result = dotmod(self.tree, {
            "app.cache": None
        })
        
        cache = result.children[2]
        self.assertEqual(len(cache.payload), 0)
    
    def test_in_place_modification(self):
        """Test in-place modification."""
        tree_copy = (TreeBuilder()
            .root("app", version="1.0")
            .child("config", debug=True)
            .build())
        
        result = dotmod(tree_copy, {"app.config": {"debug": False}}, in_place=True)
        
        self.assertIs(result, tree_copy)
        self.assertEqual(tree_copy.children[0].payload["debug"], False)


class TestDotMap(unittest.TestCase):
    """Test dotmap function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("files")
            .child("doc1.txt", size=100)
            .sibling("doc2.txt", size=200)
            .sibling("doc3.txt", size=300)
            .build())
    
    def test_map_all_nodes(self):
        """Test mapping over all nodes."""
        result = dotmap(self.tree, lambda n: {"size_kb": n.payload.get("size", 0) / 1024})
        
        for child in result.children:
            self.assertIn("size_kb", child.payload)
    
    def test_map_specific_pattern(self):
        """Test mapping over specific pattern."""
        result = dotmap(self.tree, 
                       lambda n: {"processed": True},
                       dot_path="files.doc1\\.txt")
        
        self.assertTrue(result.children[0].payload.get("processed"))
        self.assertNotIn("processed", result.children[1].payload)
    
    def test_field_mappers(self):
        """Test using field-specific mappers."""
        result = dotmap(self.tree, {
            "size": lambda v: v * 2,
            "name": lambda v: v.upper()
        })
        
        # Size should be doubled
        self.assertEqual(result.children[0].payload["size"], 200)
        # Name field doesn't exist in payload, so no change


class TestDotPrune(unittest.TestCase):
    """Test dotprune function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("project")
            .child("src")
                .child("main.py", type="file")
                .sibling("test_main.py", type="test")
                .up()
            .sibling("tests")
                .child("test_unit.py", type="test")
                .child("test_integration.py", type="test")
            .build())
    
    def test_prune_by_pattern(self):
        """Test pruning by dot pattern."""
        result = dotprune(self.tree, "**.test_*\\.py")
        
        # test_main.py should be removed
        src = result.children[0]
        self.assertEqual(len(src.children), 1)
        self.assertEqual(src.children[0].name, "main.py")
        
        # test files in tests dir should be removed
        tests = result.children[1]
        self.assertEqual(len(tests.children), 0)
    
    def test_prune_by_predicate(self):
        """Test pruning by predicate function."""
        result = dotprune(self.tree, 
                         lambda n: n.payload.get("type") == "test")
        
        src = result.children[0]
        self.assertEqual(len(src.children), 1)
    
    def test_keep_structure(self):
        """Test keeping structure when pruning."""
        result = dotprune(self.tree, "**.test_*\\.py", keep_structure=True)
        
        # Nodes should exist but be empty
        src = result.children[0]
        test_node = src.children[1]
        self.assertEqual(test_node.name, "test_main.py")
        self.assertEqual(len(test_node.payload), 0)
        self.assertEqual(len(test_node.children), 0)


class TestDotMerge(unittest.TestCase):
    """Test dotmerge function."""
    
    def setUp(self):
        """Set up test trees."""
        self.tree1 = (TreeBuilder()
            .root("config")
            .child("app", port=8080, debug=True)
            .sibling("database", host="localhost")
            .build())
        
        self.tree2 = (TreeBuilder()
            .root("config")
            .child("app", port=9000, env="production")
            .sibling("cache", type="redis")
            .build())
    
    def test_overlay_merge(self):
        """Test overlay merge strategy."""
        result = dotmerge(self.tree1, self.tree2, "overlay")
        
        app = result.children[0]
        self.assertEqual(app.payload["port"], 9000)  # Overridden
        self.assertEqual(app.payload["debug"], True)  # Kept from tree1
        self.assertEqual(app.payload["env"], "production")  # Added from tree2
        
        # New node from tree2
        self.assertEqual(len(result.children), 3)
        cache = result.children[2]
        self.assertEqual(cache.name, "cache")
    
    def test_underlay_merge(self):
        """Test underlay merge strategy."""
        result = dotmerge(self.tree1, self.tree2, "underlay")
        
        app = result.children[0]
        self.assertEqual(app.payload["port"], 8080)  # Kept from tree1
        self.assertEqual(app.payload["env"], "production")  # Added from tree2
    
    def test_combine_merge(self):
        """Test combine merge strategy."""
        tree1 = Node("root", tags=["important"])
        tree2 = Node("root", tags=["urgent"])
        
        result = dotmerge(tree1, tree2, "combine")
        self.assertEqual(result.payload["tags"], ["important", "urgent"])


class TestDotGraft(unittest.TestCase):
    """Test dotgraft function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("app")
            .child("modules")
            .build())
        
        self.subtree = (TreeBuilder()
            .root("auth")
            .child("login.py")
            .sibling("logout.py")
            .build())
    
    def test_graft_append(self):
        """Test grafting with append."""
        result = dotgraft(self.tree, "app.modules", self.subtree)
        
        modules = result.children[0]
        self.assertEqual(len(modules.children), 1)
        self.assertEqual(modules.children[0].name, "auth")
    
    def test_graft_prepend(self):
        """Test grafting with prepend."""
        # Add existing child first
        modules = self.tree.children[0]
        modules.add_child("existing")
        
        result = dotgraft(self.tree, "app.modules", self.subtree, position="prepend")
        
        modules = result.children[0]
        self.assertEqual(modules.children[0].name, "auth")
        self.assertEqual(modules.children[1].name, "existing")
    
    def test_graft_replace(self):
        """Test grafting with replace."""
        modules = self.tree.children[0]
        modules.add_child("old_module")
        
        result = dotgraft(self.tree, "app.modules", self.subtree, position="replace")
        
        modules = result.children[0]
        self.assertEqual(len(modules.children), 1)
        self.assertEqual(modules.children[0].name, "auth")


class TestDotSplit(unittest.TestCase):
    """Test dotsplit function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("app")
            .child("core")
                .child("main.py")
                .up()
            .sibling("deprecated")
                .child("old1.py")
                .child("old2.py")
                .up()
            .sibling("utils")
                .child("helper.py")
            .build())
    
    def test_split_include_point(self):
        """Test splitting with including split point."""
        result, extracted = dotsplit(self.tree, "app.deprecated")
        
        # Deprecated should be removed from result
        self.assertEqual(len(result.children), 2)
        self.assertEqual(result.children[0].name, "core")
        self.assertEqual(result.children[1].name, "utils")
        
        # Extracted should contain deprecated node
        self.assertEqual(len(extracted), 1)
        self.assertEqual(extracted[0].name, "deprecated")
        self.assertEqual(len(extracted[0].children), 2)
    
    def test_split_exclude_point(self):
        """Test splitting without including split point."""
        result, extracted = dotsplit(self.tree, "app.deprecated", include_point=False)
        
        # Deprecated node should remain but be empty
        self.assertEqual(len(result.children), 3)
        deprecated = result.children[1]
        self.assertEqual(deprecated.name, "deprecated")
        self.assertEqual(len(deprecated.children), 0)
        
        # Extracted should contain children only
        self.assertEqual(len(extracted), 2)
        self.assertEqual(extracted[0].name, "old1.py")


class TestDotReduce(unittest.TestCase):
    """Test dotreduce function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("files")
            .child("doc1.txt", size=100)
            .sibling("doc2.txt", size=200)
            .sibling("folder")
                .child("doc3.txt", size=150)
            .build())
    
    def test_reduce_sum(self):
        """Test reducing with sum."""
        total = dotreduce(self.tree,
                         lambda acc, n: acc + n.payload.get("size", 0),
                         initial=0)
        
        self.assertEqual(total, 450)
    
    def test_reduce_collect(self):
        """Test reducing to collect values."""
        names = dotreduce(self.tree,
                         lambda acc, n: acc + [n.name],
                         initial=[])
        
        self.assertIn("files", names)
        self.assertIn("doc1.txt", names)
        self.assertIn("folder", names)
    
    def test_reduce_with_pattern(self):
        """Test reducing with pattern."""
        txt_files = dotreduce(self.tree,
                             lambda acc, n: acc + 1,
                             initial=0,
                             traverse_pattern="**.*\\.txt")
        
        self.assertEqual(txt_files, 3)


class TestDotAnnotate(unittest.TestCase):
    """Test dotannotate function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("app")
            .child("module1")
            .sibling("module2")
            .build())
    
    def test_annotate_with_function(self):
        """Test annotating with function."""
        result = dotannotate(self.tree,
                           lambda n: {
                               "level": n.level,
                               "has_children": len(n.children) > 0
                           })
        
        self.assertEqual(result.payload["_annotation"]["level"], 0)
        self.assertTrue(result.payload["_annotation"]["has_children"])
        
        module1 = result.children[0]
        self.assertEqual(module1.payload["_annotation"]["level"], 1)
        self.assertFalse(module1.payload["_annotation"]["has_children"])
    
    def test_annotate_with_static(self):
        """Test annotating with static dict."""
        result = dotannotate(self.tree,
                           {"reviewed": True, "version": "1.0"},
                           dot_path="app.module1")
        
        module1 = result.children[0]
        self.assertTrue(module1.payload["_annotation"]["reviewed"])
        
        # Others shouldn't have annotation
        self.assertNotIn("_annotation", result.children[1].payload)


class TestDotValidate(unittest.TestCase):
    """Test dotvalidate function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("files")
            .child("doc1.txt", size=100, validated=True)
            .sibling("doc2.txt", size=2000000, validated=False)
            .sibling("doc3.txt", size=500, validated=True)
            .build())
    
    def test_validate_with_function(self):
        """Test validation with function."""
        # Should pass
        result = dotvalidate(self.tree,
                           lambda n: n.payload.get("size", 0) < 3000000)
        self.assertTrue(result)
        
        # Should fail
        with self.assertRaises(ValueError):
            dotvalidate(self.tree,
                       lambda n: n.payload.get("size", 0) < 1000000)
    
    def test_validate_with_dict(self):
        """Test validation with required attributes."""
        with self.assertRaises(ValueError):
            dotvalidate(self.tree,
                       {"validated": True},
                       dot_path="**.*\\.txt")
    
    def test_validate_no_raise(self):
        """Test validation without raising."""
        invalid = dotvalidate(self.tree,
                            lambda n: n.payload.get("validated", False),
                            dot_path="**.*\\.txt",
                            raise_on_invalid=False)
        
        self.assertEqual(len(invalid), 1)
        self.assertEqual(invalid[0].name, "doc2.txt")


class TestDotNormalize(unittest.TestCase):
    """Test dotnormalize function."""
    
    def test_normalize_names(self):
        """Test normalizing node names."""
        tree = (TreeBuilder()
            .root("My App")
            .child("User-Module")
            .sibling("DATABASE CONFIG")
            .build())
        
        result = dotnormalize(tree)
        
        self.assertEqual(result.name, "my_app")
        self.assertEqual(result.children[0].name, "user_module")
        self.assertEqual(result.children[1].name, "database_config")
    
    def test_normalize_payload(self):
        """Test normalizing payload keys."""
        tree = Node("root", **{"User-Name": "Alice", "Last-Login": "2024-01-01"})
        
        result = dotnormalize(tree, normalize_payload=True)
        
        self.assertIn("user_name", result.payload)
        self.assertIn("last_login", result.payload)
        self.assertEqual(result.payload["user_name"], "Alice")
    
    def test_custom_normalizer(self):
        """Test with custom normalizer."""
        tree = Node("MyNode")
        
        result = dotnormalize(tree,
                            normalizer=lambda s: s.upper())
        
        self.assertEqual(result.name, "MYNODE")


class TestDotFlatten(unittest.TestCase):
    """Test dotflatten function."""
    
    def test_flatten_all(self):
        """Test flattening entire tree."""
        tree = (TreeBuilder()
            .root("app")
            .child("module1")
                .child("submodule1")
                .up()
            .sibling("module2")
            .build())
        
        flat = dotflatten(tree)
        
        self.assertEqual(len(flat), 4)
        names = [n.name for n in flat]
        self.assertIn("app", names)
        self.assertIn("submodule1", names)
    
    def test_flatten_with_depth(self):
        """Test flattening with max depth."""
        tree = (TreeBuilder()
            .root("app")
            .child("module1")
                .child("submodule1")
                    .child("deep")
            .build())
        
        flat = dotflatten(tree, max_depth=2)
        
        # Should include app (0), module1 (1), submodule1 (2)
        # but not deep (3)
        self.assertEqual(len(flat), 3)
        names = [n.name for n in flat]
        self.assertNotIn("deep", names)


if __name__ == "__main__":
    unittest.main()