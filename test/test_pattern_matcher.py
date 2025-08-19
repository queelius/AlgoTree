"""
Tests for tree pattern matching functionality.
"""

import unittest
from AlgoTree.node import Node
from AlgoTree.pattern_matcher import (
    Pattern, PatternMatcher, MatchType, pattern_match
)


class TestPattern(unittest.TestCase):
    """Test Pattern class."""
    
    def test_from_string_simple(self):
        """Test parsing simple patterns from strings."""
        # Simple name
        p = Pattern.from_string("root")
        self.assertEqual(p.name, "root")
        self.assertFalse(p.is_wildcard)
        self.assertEqual(len(p.children), 0)
        
        # Wildcard
        p = Pattern.from_string("*")
        self.assertTrue(p.is_wildcard)
        
        # Deep wildcard
        p = Pattern.from_string("**")
        self.assertTrue(p.is_deep_wildcard)
    
    def test_from_string_with_attributes(self):
        """Test parsing patterns with attributes."""
        p = Pattern.from_string("node[type=container,size=10]")
        self.assertEqual(p.name, "node")
        self.assertEqual(p.attributes["type"], "container")
        self.assertEqual(p.attributes["size"], 10)
    
    def test_from_string_with_children(self):
        """Test parsing patterns with children."""
        p = Pattern.from_string("parent(child1, child2, *)")
        self.assertEqual(p.name, "parent")
        self.assertEqual(len(p.children), 3)
        self.assertEqual(p.children[0].name, "child1")
        self.assertEqual(p.children[1].name, "child2")
        self.assertTrue(p.children[2].is_wildcard)
    
    def test_from_dict(self):
        """Test creating pattern from dictionary."""
        pattern_dict = {
            "name": "root",
            "attributes": {"type": "container"},
            "children": [
                {"name": "child1"},
                {"name": "*"}
            ]
        }
        p = Pattern.from_dict(pattern_dict)
        self.assertEqual(p.name, "root")
        self.assertEqual(p.attributes["type"], "container")
        self.assertEqual(len(p.children), 2)


class TestPatternMatcher(unittest.TestCase):
    """Test PatternMatcher class."""
    
    def setUp(self):
        """Set up test tree."""
        # Create a test tree
        self.root = Node("root", type="container")
        self.child1 = self.root.add_child("child1", type="leaf")
        self.child2 = self.root.add_child("child2", type="branch")
        self.grandchild1 = self.child2.add_child("grandchild1", type="leaf")
        self.grandchild2 = self.child2.add_child("grandchild2", type="leaf")
    
    def test_exact_name_match(self):
        """Test matching by exact name."""
        matcher = PatternMatcher()
        pattern = Pattern(name="child1")
        
        self.assertTrue(matcher.match(self.child1, pattern))
        self.assertFalse(matcher.match(self.child2, pattern))
    
    def test_wildcard_match(self):
        """Test wildcard matching."""
        matcher = PatternMatcher()
        pattern = Pattern(is_wildcard=True)
        
        self.assertTrue(matcher.match(self.root, pattern))
        self.assertTrue(matcher.match(self.child1, pattern))
        self.assertTrue(matcher.match(self.grandchild1, pattern))
    
    def test_attribute_match(self):
        """Test matching by attributes."""
        matcher = PatternMatcher()
        pattern = Pattern(attributes={"type": "leaf"})
        
        self.assertTrue(matcher.match(self.child1, pattern))
        self.assertFalse(matcher.match(self.child2, pattern))
        self.assertTrue(matcher.match(self.grandchild1, pattern))
    
    def test_children_exact_match(self):
        """Test exact children matching."""
        matcher = PatternMatcher(MatchType.EXACT)
        
        # Pattern with two children
        pattern = Pattern(
            name="child2",
            children=[
                Pattern(name="grandchild1"),
                Pattern(name="grandchild2")
            ]
        )
        
        self.assertTrue(matcher.match(self.child2, pattern))
        self.assertFalse(matcher.match(self.root, pattern))
    
    def test_children_partial_match(self):
        """Test partial children matching."""
        matcher = PatternMatcher(MatchType.PARTIAL)
        
        # Pattern looking for any node with a child named "grandchild1"
        pattern = Pattern(
            children=[Pattern(name="grandchild1")]
        )
        
        self.assertTrue(matcher.match(self.child2, pattern))
        self.assertFalse(matcher.match(self.root, pattern))
    
    def test_deep_wildcard_match(self):
        """Test deep wildcard matching."""
        matcher = PatternMatcher(MatchType.PARTIAL)
        
        # Pattern: node with deep wildcard followed by specific child
        pattern = Pattern(
            name="child2",
            children=[
                Pattern(is_deep_wildcard=True),
                Pattern(name="grandchild2")
            ]
        )
        
        self.assertTrue(matcher.match(self.child2, pattern))
    
    def test_find_all(self):
        """Test finding all matching nodes."""
        matcher = PatternMatcher()
        pattern = Pattern(attributes={"type": "leaf"})
        
        matches = matcher.find_all(self.root, pattern)
        self.assertEqual(len(matches), 3)
        self.assertIn(self.child1, matches)
        self.assertIn(self.grandchild1, matches)
        self.assertIn(self.grandchild2, matches)
    
    def test_find_first(self):
        """Test finding first matching node."""
        matcher = PatternMatcher()
        pattern = Pattern(attributes={"type": "leaf"})
        
        match = matcher.find_first(self.root, pattern)
        self.assertEqual(match, self.child1)
    
    def test_predicate_match(self):
        """Test matching with custom predicate."""
        matcher = PatternMatcher()
        
        # Pattern matching nodes with names starting with "grand"
        pattern = Pattern(
            predicate=lambda n: n.name.startswith("grand")
        )
        
        self.assertTrue(matcher.match(self.grandchild1, pattern))
        self.assertTrue(matcher.match(self.grandchild2, pattern))
        self.assertFalse(matcher.match(self.child1, pattern))
    
    def test_min_max_children(self):
        """Test min/max children constraints."""
        matcher = PatternMatcher()
        
        # Pattern matching nodes with exactly 2 children
        pattern = Pattern(min_children=2, max_children=2)
        
        self.assertTrue(matcher.match(self.root, pattern))
        self.assertTrue(matcher.match(self.child2, pattern))
        self.assertFalse(matcher.match(self.child1, pattern))
        
        # Pattern matching nodes with at least 1 child
        pattern = Pattern(min_children=1)
        
        self.assertTrue(matcher.match(self.root, pattern))
        self.assertTrue(matcher.match(self.child2, pattern))
        self.assertFalse(matcher.match(self.child1, pattern))
    
    def test_replace(self):
        """Test replacing matching nodes."""
        # Create a fresh tree for replacement test
        root = Node("root")
        old1 = root.add_child("old", value=1)
        old2 = root.add_child("old", value=2)
        keep = root.add_child("keep", value=3)
        
        matcher = PatternMatcher()
        pattern = Pattern(name="old")
        
        # Replace with a fixed node
        def create_new(old_node):
            return Node("new", value=old_node.payload.get("value", 0) * 10)
        
        count = matcher.replace(root, pattern, create_new)
        
        self.assertEqual(count, 2)
        self.assertEqual(len(root.children), 3)
        self.assertEqual(root.children[0].name, "new")
        self.assertEqual(root.children[0].payload["value"], 10)
        self.assertEqual(root.children[1].name, "new")
        self.assertEqual(root.children[1].payload["value"], 20)
        self.assertEqual(root.children[2].name, "keep")


class TestPatternMatchFunction(unittest.TestCase):
    """Test the convenience pattern_match function."""
    
    def setUp(self):
        """Set up test tree."""
        self.root = Node("root")
        self.a = self.root.add_child("a", type="branch")
        self.b = self.root.add_child("b", type="leaf")
        self.c = self.a.add_child("c", type="leaf")
    
    def test_string_pattern(self):
        """Test pattern matching with string pattern."""
        matches = pattern_match(self.root, "a")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], self.a)
    
    def test_dict_pattern(self):
        """Test pattern matching with dict pattern."""
        matches = pattern_match(self.root, {"attributes": {"type": "leaf"}})
        self.assertEqual(len(matches), 2)
        self.assertIn(self.b, matches)
        self.assertIn(self.c, matches)
    
    def test_pattern_object(self):
        """Test pattern matching with Pattern object."""
        pattern = Pattern(name="root")
        matches = pattern_match(self.root, pattern)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], self.root)


if __name__ == "__main__":
    unittest.main()