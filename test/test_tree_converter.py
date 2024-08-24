import unittest

from anytree import Node

from AlgoTree.flat_forest_node import FlatForestNode
from AlgoTree.tree_converter import TreeConverter
from AlgoTree.treenode import TreeNode


class TestTreeConverter(unittest.TestCase):
    def setUp(self):
        """
        Create a sample tree for testing

        Here is what the tree looks like::

            root
            ├── child1
            │   └── child1_1
            │       └── child2_1 (child1_1_1 value)
            │   
            └── child2
                ├── child2_1
                └── child2_2

        Notice that child2_1 is not unique in the tree. It appears under both
        child1_1 and child2. This is fine for `TreeNode`, but for `FlatForestNode`
        it will be an issue -- it will have to either rename one of the nodes
        (child_2_1_0, for example) or raise an error, depending on whether
        renaming is set to true or false.
        """
        self.root = TreeNode(name="root", value="root_value")
        self.child1 = TreeNode(
            name="child1", parent=self.root, value="child1_value"
        )
        self.child1_1 = TreeNode(
            name="child1_1", parent=self.child1, value="child1_1_value"
        )
        self.child1_1_1 = TreeNode(
            name="child2_1", parent=self.child1_1, value="child1_1_1_value"
        )

        self.child2 = TreeNode(
            name="child2", parent=self.root, value="child2_value"
        )
        self.child2_1 = TreeNode(
            name="child2_1", parent=self.child2, value="child2_1_value"
        )
        self.child2_2 = TreeNode(
            name="child2_2", parent=self.child2, value="child2_2_value"
        )

    def verify_tree_structure(self, root):
        self.assertEqual(root["name"], "root")
        self.assertEqual(root["payload"], { "value" : "root_value"})
        self.assertEqual(len(root["children"]), 2)
        child1 = root["children"][0]
        child2 = root["children"][1]
        self.assertEqual(child1["name"], "child1")
        self.assertEqual(child1["payload"], { "value" : "child1_value"})
        self.assertEqual(child2["name"], "child2")
        self.assertEqual(child2["payload"], { "value" : "child2_value"})

        self.assertEqual(len(child1["children"]), 1)
        child1_1 = child1["children"][0]
        self.assertEqual(child1_1["name"], "child1_1")
        self.assertEqual(child1_1["payload"], { "value" : "child1_1_value"})

        self.assertEqual(len(child1_1["children"]), 1)
        child1_1_1 = child1_1["children"][0]
        self.assertEqual(child1_1_1["name"], "child2_1")
        self.assertEqual(child1_1_1["payload"], { "value" : "child1_1_1_value"})
        self.assertEqual(len(child1_1_1["children"]), 0)

        self.assertEqual(len(child2["children"]), 2)
        child2_1 = child2["children"][0]
        child2_2 = child2["children"][1]
        self.assertEqual(child2_1["name"], "child2_1")
        self.assertEqual(child2_1["payload"], { "value" : "child2_1_value"})
        self.assertEqual(len(child2_1["children"]), 0)

        self.assertEqual(child2_2["name"], "child2_2")
        self.assertEqual(child2_2["payload"], { "value" : "child2_2_value"})
        self.assertEqual(len(child2_2["children"]), 0)

    def verify_tree_structure_flattree_renamed(self, root):
        self.assertEqual(root["name"], "root")
        self.assertEqual(root["payload"], { "value" : "root_value"})
        self.assertEqual(len(root["children"]), 2)
        child1 = root["children"][0]
        child2 = root["children"][1]
        self.assertEqual(child1["name"], "child1")
        self.assertEqual(child1["payload"], { "value" : "child1_value"})
        self.assertEqual(child2["name"], "child2")
        self.assertEqual(child2["payload"], { "value" : "child2_value"})

        self.assertEqual(len(child1["children"]), 1)
        child1_1 = child1["children"][0]
        self.assertEqual(child1_1["name"], "child1_1")
        self.assertEqual(child1_1["payload"], { "value" : "child1_1_value"})

        self.assertEqual(len(child1_1["children"]), 1)
        child1_1_1 = child1_1["children"][0]
        self.assertTrue(child1_1_1["name"] == "child2_1" or child1_1_1["name"] == "child2_1_0")
        self.assertEqual(child1_1_1["payload"], { "value" : "child1_1_1_value"})
        self.assertEqual(len(child1_1_1["children"]), 0)

        self.assertEqual(len(child2["children"]), 2)
        child2_1 = child2["children"][0]
        child2_2 = child2["children"][1]
        self.assertTrue(child2_1["name"] == "child2_1_0" or child2_1["name"] == "child2_1")
        self.assertEqual(child2_1["payload"], { "value" : "child2_1_value"})
        self.assertEqual(len(child2_1["children"]), 0)

        self.assertEqual(child2_2["name"], "child2_2")
        self.assertEqual(child2_2["payload"], { "value" : "child2_2_value"})
        self.assertEqual(len(child2_2["children"]), 0)


    def test_to_dict(self):
        """
            root
            ├── child1
            │   └── child1_1
            │       └── child2_1 (child1_1_1 value)
            └── child2
                ├── child2_1
                └── child2_2
        """
        
        # Test converting TreeNode to dict
        tree_dict = TreeConverter.to_dict(self.root)
        # logging.debug(json.dumps(tree_dict, indent=2))
        self.verify_tree_structure(tree_dict)

    def test_copy_under(self):
        # Test copying a subtree under another node
        new_root = TreeNode(name="new_root", value="new_root_value")
        TreeConverter.copy_under(self.root, new_root)
        self.assertEqual(len(new_root.children), 1)
        root = new_root.children[0]
        tree_dict = TreeConverter.to_dict(root)
        self.verify_tree_structure(tree_dict)

    def test_convert_to_treenode(self):
        # Test converting TreeNode to TreeNode (identity transformation)
        new_tree = TreeConverter.convert(self.root, TreeNode)

        # logging.debug(json.dumps(new_tree, indent=2))
        self.assertIsInstance(new_tree, TreeNode)
        tree_dict = TreeConverter.to_dict(new_tree)
        self.verify_tree_structure(tree_dict)

    def test_convert_to_flat_forest_node(self):
        # Test converting TreeNode to FlatForestNode
        new_tree = TreeConverter.convert(self.root, FlatForestNode)
        #self.assertIsInstance(new_tree, FlatForestNode)
        #tree_dict = TreeConverter.to_dict(new_tree)
        #self.assertIsInstance(tree_dict, dict)
        #self.verify_tree_structure_flattree_renamed(tree_dict)

    def test_clone_treenode(self):
        root = TreeNode(name="root", value="root value")
        A = TreeNode(name="A", value=1, parent=root)
        B = TreeNode(name="B", value=2, parent=root)
        C = TreeNode(name="C", value=3, parent=root)
        D = TreeNode(name="D", value=4, parent=B)
        E = TreeNode(name="E", value=5, parent=D)
        self.assertEqual(len(root.children), 3)
        new_root = root.clone()
        new_root.add_child(name="F", value=6)
        self.assertEqual(len(new_root.children), 4)
        
        self.assertEqual(new_root.name, "root")
        self.assertEqual(new_root.payload['value'], "root value")
        self.assertEqual(new_root.children[0].name, "A")
        self.assertEqual(new_root.children[0].payload["value"], 1)
        self.assertEqual(new_root.children[1].name, "B")
        self.assertEqual(new_root.children[1].payload["value"], 2)
        self.assertEqual(new_root.children[2].name, "C")
        self.assertEqual(new_root.children[2].payload["value"], 3)
        self.assertEqual(new_root.children[3].name, "F")
        self.assertEqual(new_root.children[3].payload["value"], 6)
        self.assertEqual(new_root.children[1].children[0].name, "D")
        self.assertEqual(new_root.children[1].children[0].payload["value"], 4)
        self.assertEqual(new_root.children[1].children[0].children[0].name, "E")
        self.assertEqual(new_root.children[1].children[0].children[0].payload["value"], 5)
        
    def test_clone_flat_forest(self):
        root = FlatForestNode(name="root", value="root value")
        A = FlatForestNode(name="A", value=1, parent=root)
        B = FlatForestNode(name="B", value=2, parent=root)
        C = FlatForestNode(name="C", value=3, parent=root)
        D = FlatForestNode(name="D", value=4, parent=B)
        E = FlatForestNode(name="E", value=5, parent=D)
        new_root = root.clone(clone_children=True)
        new_root.add_child(name="F", value=6)
        self.assertEqual(len(new_root.children), 4)
        self.assertEqual(len(root.children), 3)
        self.assertEqual(new_root.name, "root")
        self.assertEqual(new_root.payload['value'], "root value")
        self.assertEqual(new_root.children[0].name, "A")
        self.assertEqual(new_root.children[0].payload["value"], 1)
        self.assertEqual(new_root.children[1].name, "B")
        self.assertEqual(new_root.children[1].payload["value"], 2)
        self.assertEqual(new_root.children[2].name, "C")
        self.assertEqual(new_root.children[2].payload["value"], 3)
        self.assertEqual(new_root.children[3].name, "F")
        self.assertEqual(new_root.children[3].payload["value"], 6)
        self.assertEqual(new_root.children[1].children[0].name, "D")
        self.assertEqual(new_root.children[1].children[0].payload["value"], 4)
        self.assertEqual(new_root.children[1].children[0].children[0].name, "E")
        self.assertEqual(new_root.children[1].children[0].children[0].payload["value"], 5)

if __name__ == "__main__":
    unittest.main()
