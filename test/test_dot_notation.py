"""
Tests for enhanced dot notation pattern matching.
"""

import unittest
from AlgoTree.node import Node
from AlgoTree.pattern_matcher import Pattern, dotmatch, dotpluck


class TestDotNotation(unittest.TestCase):
    """Test dot notation pattern matching."""
    
    def setUp(self):
        """Set up test tree structure."""
        # Create a more complex tree for testing
        self.root = Node("app")
        
        # Models branch
        models = self.root.add_child("models", type="directory")
        user_model = models.add_child("user", type="model", size=150)
        user_model.add_child("id", type="field")
        user_model.add_child("name", type="field")
        post_model = models.add_child("post", type="model", size=200)
        post_model.add_child("id", type="field")
        post_model.add_child("content", type="field")
        
        # Views branch
        views = self.root.add_child("views", type="directory")
        index = views.add_child("index", type="view", size=50)
        admin = views.add_child("admin", type="view", size=100)
        admin.add_child("dashboard", type="component")
        admin.add_child("settings", type="component")
        
        # Tests branch
        tests = self.root.add_child("tests", type="directory")
        test_models = tests.add_child("test_models", type="test", size=80)
        test_views = tests.add_child("test_views", type="test", size=60)
        test_views.add_child("test_index", type="test_case")
    
    def test_simple_dot_path(self):
        """Test simple dot notation paths."""
        # Direct path
        matches = dotmatch(self.root, "app.models.user")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].name, "user")
        
        # Nested path
        matches = dotmatch(self.root, "app.views.admin.dashboard")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].name, "dashboard")
    
    def test_wildcard_dot_path(self):
        """Test wildcard in dot notation."""
        # Single wildcard
        matches = dotmatch(self.root, "app.*.user")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].name, "user")
        
        # Multiple wildcards
        matches = dotmatch(self.root, "app.*.test_*")
        self.assertEqual(len(matches), 2)
        names = {m.name for m in matches}
        self.assertIn("test_models", names)
        self.assertIn("test_views", names)
    
    def test_deep_wildcard_dot_path(self):
        """Test deep wildcard in dot notation."""
        # Find all test-related nodes
        matches = dotmatch(self.root, "app.**.test_*")
        self.assertEqual(len(matches), 3)
        names = {m.name for m in matches}
        self.assertIn("test_models", names)
        self.assertIn("test_views", names)
        self.assertIn("test_index", names)
        
        # Find all fields
        matches = dotmatch(self.root, "app.**.id")
        self.assertEqual(len(matches), 2)
        for match in matches:
            self.assertEqual(match.name, "id")
            self.assertEqual(match.payload["type"], "field")
    
    def test_attribute_filter_dot_path(self):
        """Test attribute filtering in dot notation."""
        # Filter by type
        matches = dotmatch(self.root, "app.*[type=directory].*")
        self.assertGreater(len(matches), 0)
        
        # Filter by size
        matches = dotmatch(self.root, "app.**[size=100]")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].name, "admin")
        
        # Multiple attributes
        matches = dotmatch(self.root, "app.**[type=model,size=150]")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].name, "user")
    
    def test_predicate_filter_dot_path(self):
        """Test predicate filtering with @. notation."""
        # Filter by size comparison
        matches = dotmatch(self.root, "app.**[?(@.size > 100)]")
        self.assertEqual(len(matches), 2)
        names = {m.name for m in matches}
        self.assertIn("user", names)
        self.assertIn("post", names)
        
        # Filter by type
        matches = dotmatch(self.root, "app.**[?(@.type == 'test')]")
        self.assertEqual(len(matches), 2)
        
        # Filter by children count
        matches = dotmatch(self.root, "app.*[?(@.children.length > 1)]")
        names = {m.name for m in matches}
        self.assertIn("models", names)
        self.assertIn("views", names)
    
    def test_regex_pattern_dot_path(self):
        """Test regex patterns in dot notation."""
        # Regex pattern for test files
        matches = dotmatch(self.root, "app.**.~test_.*")
        self.assertGreater(len(matches), 0)
        for match in matches:
            self.assertTrue(match.name.startswith("test_"))
    
    def test_return_paths(self):
        """Test returning dot paths instead of nodes."""
        # Get paths to all test nodes
        paths = dotmatch(self.root, "app.**.test_*", return_paths=True)
        self.assertIn("app.tests.test_models", paths)
        self.assertIn("app.tests.test_views", paths)
        self.assertIn("app.tests.test_views.test_index", paths)
        
        # Get path to specific node
        paths = dotmatch(self.root, "app.views.admin.dashboard", return_paths=True)
        self.assertEqual(paths, ["app.views.admin.dashboard"])
    
    def test_dotpluck(self):
        """Test dotpluck for extracting values."""
        # Extract single values
        values = dotpluck(self.root, "app.models.user", "app.models.post")
        self.assertEqual(len(values), 2)
        self.assertEqual(values[0]["type"], "model")
        self.assertEqual(values[0]["size"], 150)
        self.assertEqual(values[1]["type"], "model")
        self.assertEqual(values[1]["size"], 200)
        
        # Extract with wildcards (multiple matches)
        values = dotpluck(self.root, "app.models.*")
        self.assertEqual(len(values), 1)
        self.assertIsInstance(values[0], list)
        self.assertEqual(len(values[0]), 2)
        
        # Extract missing path
        values = dotpluck(self.root, "app.models.user", "app.nonexistent")
        self.assertEqual(len(values), 2)
        self.assertIsNotNone(values[0])
        self.assertIsNone(values[1])
    
    def test_complex_dot_path(self):
        """Test complex combinations in dot notation."""
        # Combine deep wildcard with attribute filter
        matches = dotmatch(self.root, "app.**[type=view].*")
        names = {m.name for m in matches}
        self.assertIn("dashboard", names)
        self.assertIn("settings", names)
        
        # Multiple filters in path
        matches = dotmatch(self.root, "app.*[type=directory].**[type=field]")
        self.assertEqual(len(matches), 4)  # 2 fields in user, 2 in post
        for match in matches:
            self.assertEqual(match.payload["type"], "field")


class TestDotNotationParsing(unittest.TestCase):
    """Test dot notation parsing edge cases."""
    
    def test_parse_with_brackets(self):
        """Test parsing paths with brackets."""
        # Attributes with special characters
        pattern = Pattern.from_string("node[name=test-node].child")
        self.assertIsNotNone(pattern)
        
        # Multiple attributes
        pattern = Pattern.from_string("node[a=1,b=2,c=true].child")
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.attributes["a"], 1)
        self.assertEqual(pattern.attributes["b"], 2)
        self.assertEqual(pattern.attributes["c"], True)
    
    def test_parse_wildcards(self):
        """Test parsing different wildcard formats."""
        # Simple wildcard
        pattern = Pattern.from_string("root.*.leaf")
        self.assertIsNotNone(pattern)
        
        # Bracket wildcard
        pattern = Pattern.from_string("root.[*].leaf")
        self.assertIsNotNone(pattern)
        
        # Deep wildcard
        pattern = Pattern.from_string("root.**.leaf")
        self.assertIsNotNone(pattern)
    
    def test_parse_empty_path(self):
        """Test parsing edge cases."""
        # Single node
        pattern = Pattern.from_string("node")
        self.assertIsNotNone(pattern)
        self.assertEqual(pattern.name, "node")
        
        # Just wildcard
        pattern = Pattern.from_string("*")
        self.assertIsNotNone(pattern)
        self.assertTrue(pattern.is_wildcard)


if __name__ == "__main__":
    unittest.main()