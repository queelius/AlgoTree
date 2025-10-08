"""
Tests for tree export functionality.
"""

import unittest
import json
from AlgoTree.node import Node
from AlgoTree.exporters import TreeExporter, export_tree, save_tree
import tempfile
import os


class TestTreeExporter(unittest.TestCase):
    """Test TreeExporter class."""

    def setUp(self):
        """Set up test tree."""
        self.root = Node("root", attrs={"type": "container"})
        child1 = Node("child1", attrs={"value": 10})
        child2 = Node("child2", attrs={"value": 20})
        grandchild = Node("grandchild", attrs={"value": 30})

        # Build tree immutably
        child2 = child2.with_child(grandchild)
        self.root = self.root.with_children(child1, child2)

    def test_to_json(self):
        """Test JSON export."""
        json_str = TreeExporter.to_json(self.root)
        data = json.loads(json_str)

        self.assertEqual(data["name"], "root")
        self.assertEqual(data["type"], "container")
        self.assertEqual(len(data["children"]), 2)
        self.assertEqual(data["children"][0]["name"], "child1")

    def test_to_ascii(self):
        """Test ASCII tree export."""
        ascii_tree = TreeExporter.to_ascii(self.root, style="ascii")

        self.assertIn("root", ascii_tree)
        self.assertIn("+- child1", ascii_tree)
        self.assertIn("\\- child2", ascii_tree)  # child2 is last child
        self.assertIn("    \\- grandchild", ascii_tree)

    def test_to_unicode(self):
        """Test Unicode tree export."""
        unicode_tree = TreeExporter.to_unicode(self.root)

        self.assertIn("root", unicode_tree)
        self.assertIn("├─ child1", unicode_tree)
        self.assertIn("└─ child2", unicode_tree)  # child2 is last child
        self.assertIn("    └─ grandchild", unicode_tree)

    def test_to_graphviz(self):
        """Test GraphViz DOT export."""
        dot = TreeExporter.to_graphviz(self.root, name="TestTree")

        self.assertIn("digraph TestTree {", dot)
        self.assertIn('"root"', dot)
        self.assertIn('"child1"', dot)
        self.assertIn("->", dot)  # Edge indicator

        # Test with custom attributes
        dot = TreeExporter.to_graphviz(
            self.root,
            node_attr=lambda n: {"shape": "box", "color": "blue"}
        )
        self.assertIn("shape=box", dot)
        self.assertIn("color=blue", dot)

    def test_to_mermaid(self):
        """Test Mermaid diagram export."""
        mermaid = TreeExporter.to_mermaid(self.root)

        self.assertIn("graph TD", mermaid)
        self.assertIn("(root)", mermaid)
        self.assertIn("(child1)", mermaid)
        self.assertIn("-->", mermaid)  # Edge indicator

        # Test with different shapes
        mermaid = TreeExporter.to_mermaid(self.root, node_shape="square")
        self.assertIn("[root]", mermaid)

        # Test with custom text
        mermaid = TreeExporter.to_mermaid(
            self.root,
            node_text=lambda n: f"{n.name}: {n.get('value', 'N/A')}"
        )
        self.assertIn("child1: 10", mermaid)

    def test_to_yaml(self):
        """Test YAML export."""
        yaml = TreeExporter.to_yaml(self.root)

        self.assertIn("- name: root", yaml)
        self.assertIn("  type: container", yaml)
        self.assertIn("  children:", yaml)
        self.assertIn("    - name: child1", yaml)
        self.assertIn("      value: 10", yaml)

    def test_to_xml(self):
        """Test XML export."""
        xml = TreeExporter.to_xml(self.root)

        self.assertIn('<?xml version="1.0"', xml)
        self.assertIn('<tree>', xml)
        self.assertIn('<node name="root" type="container">', xml)
        self.assertIn('<node name="child1" value="10" />', xml)
        self.assertIn('</tree>', xml)

    def test_to_html(self):
        """Test HTML export."""
        html = TreeExporter.to_html(self.root, include_styles=True)

        self.assertIn('<div class="tree">', html)
        self.assertIn('root', html)
        self.assertIn('child1', html)
        self.assertIn('<style>', html)

        # Test without styles
        html = TreeExporter.to_html(self.root, include_styles=False)
        self.assertNotIn('<style>', html)

    def test_export_tree_function(self):
        """Test the convenience export_tree function."""
        # Test various formats
        json_output = export_tree(self.root, "json")
        self.assertIsInstance(json.loads(json_output), dict)

        ascii_output = export_tree(self.root, "ascii")
        self.assertIn("root", ascii_output)

        dot_output = export_tree(self.root, "graphviz")
        self.assertIn("digraph", dot_output)

        # Test unknown format
        with self.assertRaises(ValueError):
            export_tree(self.root, "unknown_format")

    def test_save_tree(self):
        """Test saving tree to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test JSON save
            json_path = os.path.join(tmpdir, "tree.json")
            save_tree(self.root, json_path)
            self.assertTrue(os.path.exists(json_path))

            with open(json_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(data["name"], "root")

            # Test auto-format detection
            dot_path = os.path.join(tmpdir, "tree.dot")
            save_tree(self.root, dot_path)

            with open(dot_path, 'r') as f:
                content = f.read()
                self.assertIn("digraph", content)

            # Test explicit format
            txt_path = os.path.join(tmpdir, "tree.txt")
            save_tree(self.root, txt_path, format="unicode")

            with open(txt_path, 'r') as f:
                content = f.read()
                self.assertIn("├─", content)


class TestExportFormats(unittest.TestCase):
    """Test specific format details."""

    def test_graphviz_escaping(self):
        """Test GraphViz handles special characters."""
        root = Node("root \"node\"")
        child = Node("child's node")
        root = root.with_child(child)

        dot = TreeExporter.to_graphviz(root)
        # The label should contain the node name with quotes
        self.assertIn('label="root', dot)
        self.assertIn('node"', dot)
        self.assertIn("child's node", dot)

    def test_mermaid_escaping(self):
        """Test Mermaid handles special characters."""
        root = Node("root <node>")
        child = Node("child & sibling")
        root = root.with_child(child)

        mermaid = TreeExporter.to_mermaid(root)
        self.assertIn("&lt;", mermaid)
        self.assertIn("&gt;", mermaid)

    def test_xml_escaping(self):
        """Test XML handles special characters."""
        root = Node("root & <node>")
        child = Node("child's \"node\"")
        root = root.with_child(child)

        xml = TreeExporter.to_xml(root)
        self.assertIn("&amp;", xml)
        self.assertIn("&lt;", xml)
        self.assertIn("&quot;", xml)

    def test_complex_tree_export(self):
        """Test exporting a more complex tree."""
        # Create a deeper tree
        root = Node("company")
        eng = Node("engineering", attrs={"size": 50})
        sales = Node("sales", attrs={"size": 30})

        frontend = Node("frontend", attrs={"size": 20})
        backend = Node("backend", attrs={"size": 30})

        react = Node("react", attrs={"size": 10})
        vue = Node("vue", attrs={"size": 10})

        # Build tree immutably
        frontend = frontend.with_children(react, vue)
        eng = eng.with_children(frontend, backend)
        root = root.with_children(eng, sales)

        # Test various exports
        json_str = TreeExporter.to_json(root)
        data = json.loads(json_str)
        self.assertEqual(len(data["children"]), 2)

        dot = TreeExporter.to_graphviz(
            root,
            node_attr=lambda n: {
                "label": f"{n.name}\\n({n.get('size', 0)})"
            }
        )
        self.assertIn("engineering\\n(50)", dot)

        mermaid = TreeExporter.to_mermaid(
            root,
            direction="LR",
            node_shape="stadium"
        )
        self.assertIn("graph LR", mermaid)
        self.assertIn("([", mermaid)  # Stadium shape


if __name__ == "__main__":
    unittest.main()
