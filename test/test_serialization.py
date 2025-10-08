import unittest
import tempfile
import os
import json
from AlgoTree.node import Node
from AlgoTree.serialization import save, load, dumps, loads


class TestSerializationBasic(unittest.TestCase):
    """Test basic serialization functions."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Node("root",
            Node("child1", attrs={"value": 1, "type": "leaf"}),
            Node("child2", attrs={"value": 2, "type": "leaf"}),
            Node("parent",
                Node("grandchild", attrs={"value": 3})
            )
        )

    def test_dumps_json(self):
        """Test dumping tree to JSON string."""
        json_str = dumps(self.tree, format="json")
        data = json.loads(json_str)

        self.assertEqual(data["name"], "root")
        self.assertEqual(len(data["children"]), 3)
        self.assertEqual(data["children"][0]["value"], 1)

    def test_dumps_default_format(self):
        """Test dumps with default format (JSON)."""
        json_str = dumps(self.tree)
        data = json.loads(json_str)
        self.assertEqual(data["name"], "root")

    def test_loads_json(self):
        """Test loading tree from JSON string."""
        json_str = dumps(self.tree, format="json")
        loaded = loads(json_str, format="json")

        self.assertEqual(loaded.name, "root")
        self.assertEqual(len(loaded.children), 3)
        self.assertEqual(loaded.children[0].get("value"), 1)

    def test_loads_default_format(self):
        """Test loads with default format (JSON)."""
        json_str = dumps(self.tree)
        loaded = loads(json_str)

        self.assertEqual(loaded.name, "root")
        self.assertEqual(len(loaded.children), 3)

    def test_roundtrip_json(self):
        """Test JSON roundtrip (dump -> load)."""
        json_str = dumps(self.tree, format="json")
        loaded = loads(json_str, format="json")

        # Check structure is preserved
        self.assertEqual(loaded.name, self.tree.name)
        self.assertEqual(len(loaded.children), len(self.tree.children))
        self.assertEqual(loaded.children[0].get("value"), 1)
        self.assertEqual(loaded.children[2].children[0].name, "grandchild")


class TestFileOperations(unittest.TestCase):
    """Test file save/load operations."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2})
        )

    def test_save_json(self):
        """Test saving to JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tree.json")
            save(self.tree, filepath, format="json")

            self.assertTrue(os.path.exists(filepath))

            # Verify content
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.assertEqual(data["name"], "root")

    def test_load_json(self):
        """Test loading from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tree.json")
            save(self.tree, filepath, format="json")

            loaded = load(filepath, format="json")
            self.assertEqual(loaded.name, "root")
            self.assertEqual(len(loaded.children), 2)

    def test_auto_detect_format_json(self):
        """Test auto-detecting JSON format from extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tree.json")
            save(self.tree, filepath)  # No format specified

            loaded = load(filepath)  # No format specified
            self.assertEqual(loaded.name, "root")

    def test_save_yaml(self):
        """Test saving to YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tree.yaml")
            save(self.tree, filepath, format="yaml")

            self.assertTrue(os.path.exists(filepath))

            # Verify it's YAML content
            with open(filepath, 'r') as f:
                content = f.read()
                self.assertIn("name: root", content)

    def test_load_yaml(self):
        """Test loading from YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tree.yaml")
            save(self.tree, filepath, format="yaml")

            loaded = load(filepath, format="yaml")
            self.assertEqual(loaded.name, "root")
            self.assertEqual(len(loaded.children), 2)

    def test_save_xml(self):
        """Test saving to XML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tree.xml")
            save(self.tree, filepath, format="xml")

            self.assertTrue(os.path.exists(filepath))

            with open(filepath, 'r') as f:
                content = f.read()
                self.assertIn('<?xml', content)
                self.assertIn('name="root"', content)

    def test_save_pickle(self):
        """Test saving to pickle file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tree.pkl")
            save(self.tree, filepath, format="pickle")

            self.assertTrue(os.path.exists(filepath))

    def test_load_pickle(self):
        """Test loading from pickle file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tree.pkl")
            save(self.tree, filepath, format="pickle")

            loaded = load(filepath, format="pickle")
            self.assertEqual(loaded.name, "root")
            self.assertEqual(len(loaded.children), 2)

    def test_roundtrip_various_formats(self):
        """Test roundtrip with various formats."""
        formats = ["json", "yaml", "xml", "pickle"]

        for fmt in formats:
            with self.subTest(format=fmt):
                with tempfile.TemporaryDirectory() as tmpdir:
                    filepath = os.path.join(tmpdir, f"tree.{fmt}")
                    save(self.tree, filepath, format=fmt)
                    loaded = load(filepath, format=fmt)

                    self.assertEqual(loaded.name, "root")
                    self.assertEqual(len(loaded.children), 2)


class TestComplexTrees(unittest.TestCase):
    """Test serialization of complex trees."""

    def test_deep_nesting(self):
        """Test deeply nested tree."""
        tree = Node("root",
            Node("a",
                Node("b",
                    Node("c",
                        Node("d")
                    )
                )
            )
        )

        json_str = dumps(tree, format="json")
        loaded = loads(json_str, format="json")

        # Navigate to deepest node
        d = loaded.children[0].children[0].children[0].children[0]
        self.assertEqual(d.name, "d")

    def test_many_children(self):
        """Test tree with many children."""
        children = [Node(f"child{i}", attrs={"index": i}) for i in range(100)]
        tree = Node("root", *children)

        json_str = dumps(tree, format="json")
        loaded = loads(json_str, format="json")

        self.assertEqual(len(loaded.children), 100)
        self.assertEqual(loaded.children[50].get("index"), 50)

    def test_complex_attributes(self):
        """Test tree with complex attributes."""
        tree = Node("root", attrs={
            "string": "value",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "none": None,
            "list": [1, 2, 3],
            "dict": {"nested": "data"}
        })

        json_str = dumps(tree, format="json")
        loaded = loads(json_str, format="json")

        self.assertEqual(loaded.get("string"), "value")
        self.assertEqual(loaded.get("number"), 42)
        self.assertEqual(loaded.get("float"), 3.14)
        self.assertTrue(loaded.get("bool"))
        self.assertIsNone(loaded.get("none"))
        self.assertEqual(loaded.get("list"), [1, 2, 3])
        self.assertEqual(loaded.get("dict"), {"nested": "data"})


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_empty_tree(self):
        """Test serializing tree with no children."""
        tree = Node("lonely")

        json_str = dumps(tree, format="json")
        loaded = loads(json_str, format="json")

        self.assertEqual(loaded.name, "lonely")
        self.assertEqual(len(loaded.children), 0)

    def test_special_characters_in_names(self):
        """Test nodes with special characters."""
        tree = Node("root",
            Node("node with spaces"),
            Node("node/with/slashes"),
            Node("node\"with\"quotes")
        )

        json_str = dumps(tree, format="json")
        loaded = loads(json_str, format="json")

        self.assertEqual(loaded.children[0].name, "node with spaces")
        self.assertEqual(loaded.children[1].name, "node/with/slashes")
        self.assertEqual(loaded.children[2].name, "node\"with\"quotes")

    def test_unicode_names(self):
        """Test nodes with Unicode characters."""
        tree = Node("root",
            Node("中文节点"),
            Node("العربية"),
            Node("🌳")
        )

        json_str = dumps(tree, format="json")
        loaded = loads(json_str, format="json")

        self.assertEqual(loaded.children[0].name, "中文节点")
        self.assertEqual(loaded.children[1].name, "العربية")
        self.assertEqual(loaded.children[2].name, "🌳")

    def test_invalid_format(self):
        """Test error on invalid format."""
        tree = Node("root")

        with self.assertRaises(ValueError):
            dumps(tree, format="invalid")

        with self.assertRaises(ValueError):
            loads("{}", format="invalid")

    def test_file_not_found(self):
        """Test error when loading non-existent file."""
        with self.assertRaises(FileNotFoundError):
            load("/nonexistent/path/tree.json")


class TestFormatDetection(unittest.TestCase):
    """Test format auto-detection."""

    def test_detect_json_extension(self):
        """Test detecting JSON from .json extension."""
        tree = Node("root")

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tree.json")
            save(tree, filepath)  # Auto-detect from extension

            with open(filepath, 'r') as f:
                content = f.read()
                # Should be JSON
                data = json.loads(content)
                self.assertEqual(data["name"], "root")

    def test_detect_yaml_extension(self):
        """Test detecting YAML from .yaml/.yml extension."""
        tree = Node("root")

        for ext in [".yaml", ".yml"]:
            with self.subTest(extension=ext):
                with tempfile.TemporaryDirectory() as tmpdir:
                    filepath = os.path.join(tmpdir, f"tree{ext}")
                    save(tree, filepath)

                    with open(filepath, 'r') as f:
                        content = f.read()
                        self.assertIn("name:", content)

    def test_detect_xml_extension(self):
        """Test detecting XML from .xml extension."""
        tree = Node("root")

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tree.xml")
            save(tree, filepath)

            with open(filepath, 'r') as f:
                content = f.read()
                self.assertIn("<?xml", content)

    def test_detect_pickle_extension(self):
        """Test detecting pickle from .pkl extension."""
        tree = Node("root")

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "tree.pkl")
            save(tree, filepath)

            loaded = load(filepath)
            self.assertEqual(loaded.name, "root")


if __name__ == "__main__":
    unittest.main()
