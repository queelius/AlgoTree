import unittest

from AlgoTree.flat_forest import FlatForest

class TestFlatTree(unittest.TestCase):
    def setUp(self):
        self.tree_data = {
            "a": {"parent": None},
            "b": {"parent": "a"},
            "c": {"parent": "a"},
            "d": {"parent": "b"},
            "e": {"parent": "b"},
            "f": {"parent": "c"},
        }
        self.flat_tree = FlatForest(self.tree_data)

    def test_initialization(self):
        self.assertEqual(self.flat_tree["a"]["parent"], None)
        self.assertEqual(self.flat_tree["b"]["parent"], "a")
        self.assertEqual(self.flat_tree["c"]["parent"], "a")

    def test_node_names(self):
        keys = self.flat_tree.node_names()
        expected_keys = [
            "__DETACHED__",
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
        ]
        self.assertCountEqual(keys, expected_keys)

    def test_child_names(self):
        self.assertEqual(self.flat_tree.child_names("a"), ["b", "c"])
        self.assertEqual(self.flat_tree.child_names("b"), ["d", "e"])
        self.assertEqual(self.flat_tree.child_names("c"), ["f"])

    def test_detach(self):
        detached_node = self.flat_tree.detach("b")
        self.assertEqual(self.flat_tree["b"]["parent"], FlatForest.DETACHED_KEY)
        self.assertEqual(detached_node._key, "b")

    def test_purge(self):
        self.flat_tree.detach("b")
        self.flat_tree.purge()
        # order doesn't matter, so use this instead:
        self.assertNotIn("b", self.flat_tree)
        self.assertNotIn("d", self.flat_tree)
        self.assertNotIn("e", self.flat_tree)

    def test_check_valid(self):
        # Valid tree
        FlatForest.check_valid(self.flat_tree)

        # Invalid tree (cycle)
        self.flat_tree["a"]["parent"] = "f"
        with self.assertRaises(ValueError):
            FlatForest.check_valid(self.flat_tree)

        # Invalid tree (non-dict node value)
        self.flat_tree["a"] = "invalid"
        with self.assertRaises(ValueError):
            FlatForest.check_valid(self.flat_tree)

        # Invalid tree (non-existing parent)
        self.flat_tree["a"] = {"parent": "non_existing"}
        with self.assertRaises(KeyError):
            FlatForest.check_valid(self.flat_tree)

    def test_node(self):
        node_b = self.flat_tree.node("b")
        self.assertEqual(node_b._key, "b")

        with self.assertRaises(KeyError):
            self.flat_tree.node("non_existing")

    def test_root(self):
        root_node = self.flat_tree.root
        self.assertEqual(root_node._key, "a")

    def test_detached(self):
        detached_node = self.flat_tree.detached
        self.assertEqual(detached_node._key, FlatForest.DETACHED_KEY)


if __name__ == "__main__":
    unittest.main()
