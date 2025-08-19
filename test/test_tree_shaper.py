"""
Tests for tree shaping (open transformation) functionality.
"""

import unittest
from AlgoTree import (
    Node, TreeBuilder,
    dotpipe, to_dict, to_list, to_paths,
    to_adjacency_list, to_edge_list, to_nested_lists,
    to_table, dotextract, dotcollect, dotgroup,
    dotpartition, dotproject
)


class TestDotPipe(unittest.TestCase):
    """Test dotpipe function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("app")
            .child("config", type="settings", size=100)
            .sibling("data", type="storage", size=500)
            .sibling("modules")
                .child("auth", type="module", enabled=True)
                .sibling("api", type="module", enabled=False)
            .build())
    
    def test_simple_pipe(self):
        """Test simple pipeline."""
        # Extract all names
        names = dotpipe(self.tree,
                       lambda t: [n.name for n in t.traverse_preorder()])
        
        self.assertIn("app", names)
        self.assertIn("config", names)
        self.assertIn("auth", names)
    
    def test_multi_stage_pipe(self):
        """Test multi-stage pipeline."""
        # Get enabled modules and extract their names
        result = dotpipe(self.tree,
                        ("app.modules.*", lambda n: n if n.payload.get("enabled") else None),
                        lambda nodes: [n.name for n in nodes if n],
                        sorted)
        
        self.assertEqual(result, ["auth"])
    
    def test_extract_and_transform(self):
        """Test extracting specific data and transforming."""
        # Extract sizes and sum them
        total = dotpipe(self.tree,
                       ("**[size]", lambda n: n.payload["size"]),
                       sum)
        
        self.assertEqual(total, 600)


class TestConversionFunctions(unittest.TestCase):
    """Test tree conversion functions."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("root")
            .child("child1", value=1)
            .sibling("child2", value=2)
                .child("grandchild", value=3)
            .build())
    
    def test_to_dict(self):
        """Test converting to dict."""
        result = to_dict(self.tree)
        
        self.assertEqual(result["name"], "root")
        self.assertIn("children", result)
        self.assertEqual(len(result["children"]), 2)
        self.assertEqual(result["children"][0]["name"], "child1")
        self.assertEqual(result["children"][0]["value"], 1)
    
    def test_to_dict_without_children(self):
        """Test converting to dict without children."""
        result = to_dict(self.tree, include_children=False)
        
        self.assertEqual(result["name"], "root")
        self.assertNotIn("children", result)
    
    def test_to_list(self):
        """Test converting to list."""
        # Just names
        names = to_list(self.tree, include_data=False)
        self.assertEqual(names, ["root", "child1", "child2", "grandchild"])
        
        # With data
        data = to_list(self.tree, include_data=True)
        self.assertEqual(len(data), 4)
        self.assertEqual(data[0]["name"], "root")
        self.assertIn("value", data[1])
    
    def test_to_paths(self):
        """Test converting to paths."""
        paths = to_paths(self.tree)
        
        self.assertIn("root", paths)
        self.assertIn("root.child1", paths)
        self.assertIn("root.child2", paths)
        self.assertIn("root.child2.grandchild", paths)
        
        # With custom separator
        paths = to_paths(self.tree, path_separator="/")
        self.assertIn("root/child2/grandchild", paths)
    
    def test_to_paths_with_payload(self):
        """Test paths with payload data."""
        path_data = to_paths(self.tree, include_payload=True)
        
        self.assertIsInstance(path_data, dict)
        self.assertIn("root.child1", path_data)
        self.assertEqual(path_data["root.child1"]["value"], 1)
    
    def test_to_adjacency_list(self):
        """Test adjacency list conversion."""
        adj = to_adjacency_list(self.tree)
        
        self.assertEqual(adj["root"], ["child1", "child2"])
        self.assertEqual(adj["child2"], ["grandchild"])
        self.assertEqual(adj["grandchild"], [])
    
    def test_to_edge_list(self):
        """Test edge list conversion."""
        edges = to_edge_list(self.tree)
        
        self.assertIn(("root", "child1"), edges)
        self.assertIn(("root", "child2"), edges)
        self.assertIn(("child2", "grandchild"), edges)
        self.assertEqual(len(edges), 3)
    
    def test_to_nested_lists(self):
        """Test nested list conversion."""
        nested = to_nested_lists(self.tree)
        
        self.assertEqual(nested[0], "root")
        self.assertEqual(nested[1], ["child1"])
        self.assertEqual(nested[2][0], "child2")
        self.assertEqual(nested[2][1], ["grandchild"])
    
    def test_to_table(self):
        """Test table conversion."""
        rows = to_table(self.tree)
        
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["name"], "root")
        self.assertEqual(rows[0]["level"], 0)
        self.assertEqual(rows[1]["name"], "child1")
        self.assertEqual(rows[1]["value"], 1)
        
        # With specific columns
        rows = to_table(self.tree, columns=["value"])
        self.assertIn("value", rows[1])
        self.assertEqual(rows[1]["value"], 1)


class TestDotExtract(unittest.TestCase):
    """Test dotextract function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("files")
            .child("doc1.txt", type="file", size=100)
            .sibling("doc2.txt", type="file", size=200)
            .sibling("folder", type="dir")
                .child("doc3.txt", type="file", size=150)
            .build())
    
    def test_extract_simple(self):
        """Test simple extraction."""
        sizes = dotextract(self.tree,
                          lambda n: n.payload.get("size"),
                          dot_path="**[type=file]")
        
        self.assertEqual(sorted(sizes), [100, 150, 200])
    
    def test_extract_complex(self):
        """Test complex extraction."""
        file_info = dotextract(self.tree,
                              lambda n: {"name": n.name, "size": n.payload["size"]},
                              dot_path="**[type=file]")
        
        self.assertEqual(len(file_info), 3)
        names = [f["name"] for f in file_info]
        self.assertIn("doc1.txt", names)
    
    def test_extract_structured(self):
        """Test structured extraction."""
        structured = dotextract(self.tree,
                              lambda n: n.payload.get("size", 0),
                              flatten=False)
        
        self.assertIsInstance(structured, dict)
        self.assertIn("files.doc1.txt", structured)


class TestDotCollect(unittest.TestCase):
    """Test dotcollect function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("app")
            .child("module1", type="module", lines=100)
            .sibling("module2", type="module", lines=200)
            .sibling("config", type="settings", lines=50)
            .build())
    
    def test_collect_statistics(self):
        """Test collecting statistics."""
        stats = dotcollect(self.tree,
                          lambda n, acc: {
                              "count": acc["count"] + 1,
                              "total_lines": acc["total_lines"] + n.payload.get("lines", 0)
                          },
                          initial={"count": 0, "total_lines": 0})
        
        self.assertEqual(stats["count"], 4)  # root + 3 children
        self.assertEqual(stats["total_lines"], 350)
    
    def test_collect_by_type(self):
        """Test collecting into groups."""
        by_type = dotcollect(self.tree,
                           lambda n, acc: {
                               **acc,
                               n.payload.get("type", "unknown"): 
                                   acc.get(n.payload.get("type", "unknown"), []) + [n.name]
                           },
                           initial={})
        
        self.assertEqual(len(by_type["module"]), 2)
        self.assertIn("module1", by_type["module"])


class TestDotGroup(unittest.TestCase):
    """Test dotgroup function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("project")
            .child("src")
                .child("main.py", type="file", lang="python")
                .sibling("utils.py", type="file", lang="python")
                .sibling("config.json", type="file", lang="json")
                .up()
            .sibling("tests")
                .child("test_main.py", type="file", lang="python")
            .build())
    
    def test_group_by_attribute(self):
        """Test grouping by attribute."""
        by_lang = dotgroup(self.tree, "lang", dot_path="**[type=file]")
        
        self.assertIn("python", by_lang)
        self.assertIn("json", by_lang)
        self.assertEqual(len(by_lang["python"]), 3)
        self.assertEqual(len(by_lang["json"]), 1)
    
    def test_group_by_function(self):
        """Test grouping by function."""
        by_level = dotgroup(self.tree, lambda n: n.level)
        
        self.assertIn(0, by_level)
        self.assertIn(1, by_level)
        self.assertIn(2, by_level)
        self.assertEqual(len(by_level[2]), 4)  # 4 files at level 2


class TestDotPartition(unittest.TestCase):
    """Test dotpartition function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("files")
            .child("small1.txt", size=100)
            .sibling("large1.txt", size=2000)
            .sibling("small2.txt", size=200)
            .sibling("large2.txt", size=3000)
            .build())
    
    def test_partition_by_size(self):
        """Test partitioning by size."""
        large, small = dotpartition(self.tree,
                                   lambda n: n.payload.get("size", 0) > 1000)
        
        self.assertEqual(len(large), 2)
        self.assertEqual(len(small), 3)  # Including root which has no size
        
        large_names = [n.name for n in large]
        self.assertIn("large1.txt", large_names)
        self.assertIn("large2.txt", large_names)


class TestDotProject(unittest.TestCase):
    """Test dotproject function."""
    
    def setUp(self):
        """Set up test tree."""
        self.tree = (TreeBuilder()
            .root("db")
            .child("users", type="table", rows=1000, indexed=True)
            .sibling("posts", type="table", rows=5000, indexed=False)
            .sibling("config", type="settings")
            .build())
    
    def test_project_fields(self):
        """Test projecting specific fields."""
        data = dotproject(self.tree, ["name", "type", "rows"])
        
        self.assertEqual(len(data), 4)
        self.assertIn("name", data[0])
        self.assertIn("type", data[0])
        self.assertEqual(data[1]["name"], "users")
        self.assertEqual(data[1]["rows"], 1000)
    
    def test_project_with_aliases(self):
        """Test projecting with aliases."""
        data = dotproject(self.tree,
                         {"name": "table_name", "rows": "row_count"},
                         dot_path="**[type=table]")
        
        self.assertEqual(len(data), 2)
        self.assertIn("table_name", data[0])
        self.assertIn("row_count", data[0])
        self.assertEqual(data[0]["table_name"], "users")


if __name__ == "__main__":
    unittest.main()