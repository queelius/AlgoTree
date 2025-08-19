"""
Tests for the fluent API and new Node class.
"""
import unittest
from AlgoTree.node import Node
from AlgoTree.fluent import TreeBuilder, FluentNode
from AlgoTree.dsl import parse_tree


class TestNode(unittest.TestCase):
    """Test the new Node class."""
    
    def test_node_creation(self):
        """Test basic node creation."""
        node = Node(name="root", value=1, type="test")
        self.assertEqual(node.name, "root")
        self.assertEqual(node.payload["value"], 1)
        self.assertEqual(node.payload["type"], "test")
        self.assertIsNone(node.parent)
        self.assertEqual(len(node.children), 0)
    
    def test_parent_child_relationship(self):
        """Test parent-child relationships."""
        root = Node(name="root")
        child1 = Node(name="child1", parent=root)
        child2 = root.add_child(name="child2")
        
        self.assertEqual(len(root.children), 2)
        self.assertIn(child1, root.children)
        self.assertIn(child2, root.children)
        self.assertEqual(child1.parent, root)
        self.assertEqual(child2.parent, root)
    
    def test_tree_properties(self):
        """Test tree properties like level, is_root, is_leaf."""
        root = Node(name="root")
        child = root.add_child(name="child")
        grandchild = child.add_child(name="grandchild")
        
        self.assertTrue(root.is_root)
        self.assertFalse(root.is_leaf)
        self.assertEqual(root.level, 0)
        
        self.assertFalse(child.is_root)
        self.assertFalse(child.is_leaf)
        self.assertEqual(child.level, 1)
        
        self.assertFalse(grandchild.is_root)
        self.assertTrue(grandchild.is_leaf)
        self.assertEqual(grandchild.level, 2)
    
    def test_traversal(self):
        """Test tree traversal methods."""
        root = Node(name="A")
        b = root.add_child(name="B")
        c = root.add_child(name="C")
        d = b.add_child(name="D")
        e = b.add_child(name="E")
        
        # Preorder: A, B, D, E, C
        preorder = [n.name for n in root.traverse_preorder()]
        self.assertEqual(preorder, ["A", "B", "D", "E", "C"])
        
        # Postorder: D, E, B, C, A
        postorder = [n.name for n in root.traverse_postorder()]
        self.assertEqual(postorder, ["D", "E", "B", "C", "A"])
        
        # Level order: A, B, C, D, E
        levelorder = [n.name for n in root.traverse_levelorder()]
        self.assertEqual(levelorder, ["A", "B", "C", "D", "E"])
    
    def test_find_operations(self):
        """Test find and find_all methods."""
        root = Node(name="root", type="folder")
        file1 = root.add_child(name="file1", type="file")
        folder1 = root.add_child(name="folder1", type="folder")
        file2 = folder1.add_child(name="file2", type="file")
        
        # Find single node
        found = root.find(lambda n: n.name == "file2")
        self.assertEqual(found, file2)
        
        # Find all nodes
        files = root.find_all(lambda n: n.payload.get("type") == "file")
        self.assertEqual(len(files), 2)
        self.assertIn(file1, files)
        self.assertIn(file2, files)
    
    def test_dict_conversion(self):
        """Test conversion to/from dict."""
        root = Node(name="root", value=1)
        child = root.add_child(name="child", value=2)
        
        # To dict
        d = root.to_dict()
        self.assertEqual(d["name"], "root")
        self.assertEqual(d["value"], 1)
        self.assertEqual(len(d["children"]), 1)
        self.assertEqual(d["children"][0]["name"], "child")
        
        # From dict
        new_root = Node.from_dict(d)
        self.assertEqual(new_root.name, "root")
        self.assertEqual(new_root.payload["value"], 1)
        self.assertEqual(len(new_root.children), 1)
        self.assertEqual(new_root.children[0].name, "child")


class TestTreeBuilder(unittest.TestCase):
    """Test the TreeBuilder fluent API."""
    
    def test_simple_tree(self):
        """Test building a simple tree."""
        tree = (TreeBuilder()
            .root("company")
            .child("engineering")
            .sibling("sales")
            .build())
        
        self.assertEqual(tree.name, "company")
        self.assertEqual(len(tree.children), 2)
        self.assertEqual(tree.children[0].name, "engineering")
        self.assertEqual(tree.children[1].name, "sales")
    
    def test_nested_tree(self):
        """Test building a nested tree."""
        tree = (TreeBuilder()
            .root("company", type="tech")
            .child("engineering", head="Alice")
                .child("frontend", size=5)
                .sibling("backend", size=8)
                .up()
            .sibling("sales", head="Bob")
                .child("domestic")
                .sibling("international")
            .build())
        
        self.assertEqual(tree.name, "company")
        self.assertEqual(tree.payload["type"], "tech")
        
        eng = tree.children[0]
        self.assertEqual(eng.name, "engineering")
        self.assertEqual(len(eng.children), 2)
        
        sales = tree.children[1]
        self.assertEqual(sales.name, "sales")
        self.assertEqual(len(sales.children), 2)
    
    def test_navigation(self):
        """Test navigation methods."""
        builder = TreeBuilder().root("root")
        builder.child("a").child("b").child("c")
        
        # Test up navigation
        builder.up(2)
        builder.child("d")
        
        tree = builder.build()
        a = tree.children[0]
        self.assertEqual(len(a.children), 2)  # b and d
        
        # Test to_root navigation
        builder.to_root()
        builder.child("e")
        
        tree = builder.build()
        self.assertEqual(len(tree.children), 2)  # a and e


class TestFluentNode(unittest.TestCase):
    """Test the FluentNode wrapper for method chaining."""
    
    def setUp(self):
        """Create a test tree."""
        self.tree = Node(name="root", value=10)
        self.tree.add_child(name="a", value=5)
        self.tree.add_child(name="b", value=15)
        b = self.tree.children[1]
        b.add_child(name="c", value=20)
        b.add_child(name="d", value=25)
    
    def test_filter(self):
        """Test filtering nodes."""
        result = (FluentNode(self.tree)
            .filter(lambda n: n.payload.get("value", 0) > 10)
            .to_list())
        
        self.assertEqual(len(result), 3)
        names = [n.name for n in result]
        self.assertIn("b", names)
        self.assertIn("c", names)
        self.assertIn("d", names)
    
    def test_map(self):
        """Test mapping transformation."""
        FluentNode(self.tree).map(lambda n: {"doubled": n.payload.get("value", 0) * 2})
        
        self.assertEqual(self.tree.payload["doubled"], 20)
        self.assertEqual(self.tree.children[0].payload["doubled"], 10)
    
    def test_children_descendants(self):
        """Test children and descendants methods."""
        children = FluentNode(self.tree).children().to_list()
        self.assertEqual(len(children), 2)
        
        descendants = FluentNode(self.tree).descendants().to_list()
        self.assertEqual(len(descendants), 4)  # a, b, c, d
    
    def test_prune(self):
        """Test pruning nodes."""
        FluentNode(self.tree).prune(lambda n: n.name in ["c", "d"])
        
        self.assertEqual(len(self.tree.children), 2)
        b = self.tree.children[1]
        self.assertEqual(len(b.children), 0)  # c and d removed
    
    def test_chaining(self):
        """Test method chaining."""
        result = (FluentNode(self.tree)
            .descendants()
            .where(lambda n: n.payload.get("value", 0) > 10)
            .map(lambda n: {"category": "high"})
            .to_list())
        
        self.assertEqual(len(result), 3)
        for node in result:
            self.assertEqual(node.payload["category"], "high")


class TestTreeDSL(unittest.TestCase):
    """Test the tree DSL parser."""
    
    def test_visual_format(self):
        """Test parsing visual tree format."""
        text = """company[type:tech]
├── engineering[head:Alice]
│   ├── frontend[size:5]
│   └── backend[size:8]
└── sales[head:Bob]"""
        
        tree = parse_tree(text)
        self.assertEqual(tree.name, "company")
        self.assertEqual(tree.payload["type"], "tech")
        self.assertEqual(len(tree.children), 2)
        
        eng = tree.children[0]
        self.assertEqual(eng.name, "engineering")
        self.assertEqual(eng.payload["head"], "Alice")
        self.assertEqual(len(eng.children), 2)
    
    def test_indent_format(self):
        """Test parsing indent-based format."""
        text = """company: {type: tech}
  engineering: {head: Alice}
    frontend: {size: 5}
    backend: {size: 8}
  sales: {head: Bob}"""
        
        tree = parse_tree(text, format='indent')
        self.assertEqual(tree.name, "company")
        self.assertEqual(tree.payload["type"], "tech")
        
        eng = tree.children[0]
        self.assertEqual(eng.name, "engineering")
        self.assertEqual(len(eng.children), 2)
    
    def test_sexpr_format(self):
        """Test parsing S-expression format."""
        text = """(company :type tech
  (engineering :head Alice
    (frontend :size 5)
    (backend :size 8))
  (sales :head Bob))"""
        
        tree = parse_tree(text)
        self.assertEqual(tree.name, "company")
        self.assertEqual(tree.payload["type"], "tech")
        
        eng = tree.children[0]
        self.assertEqual(eng.name, "engineering")
        self.assertEqual(eng.payload["head"], "Alice")
    
    def test_auto_format_detection(self):
        """Test automatic format detection."""
        # Visual format
        visual = "root\n├── child"
        tree = parse_tree(visual)
        self.assertEqual(tree.name, "root")
        
        # S-expression
        sexpr = "(root (child))"
        tree = parse_tree(sexpr)
        self.assertEqual(tree.name, "root")
        
        # Indent (default)
        indent = "root\n  child"
        tree = parse_tree(indent)
        self.assertEqual(tree.name, "root")


if __name__ == "__main__":
    unittest.main()