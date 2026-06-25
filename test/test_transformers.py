import unittest
from AlgoTree.node import Node
from AlgoTree.tree import Tree
from AlgoTree.selectors import name, attrs, leaf
from AlgoTree.transformers import (
    Transformer, identity,
    map_, filter_, prune, graft, flatten, normalize, annotate,
    reduce_, fold, extract, to_dict, to_paths
)


class TestMapTransformer(unittest.TestCase):
    """Test map_ factory."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2})
        ))

    def test_map_with_dict(self):
        """Test mapping with dict return."""
        transformer = map_(lambda n: {"doubled": n.get("value", 0) * 2})
        result = transformer(self.tree)

        self.assertEqual(result.root.children[0].get("doubled"), 2)
        self.assertEqual(result.root.children[1].get("doubled"), 4)

    def test_map_with_none(self):
        """Test mapping with None (no change)."""
        transformer = map_(lambda n: None)
        result = transformer(self.tree)

        self.assertEqual(result.root.name, "root")
        self.assertEqual(result.root.children[0].get("value"), 1)


class TestFilterTransformer(unittest.TestCase):
    """Test filter_ factory."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("keep", attrs={"active": True}),
            Node("remove", attrs={"active": False}),
            Node("keep2", attrs={"active": True})
        ))

    def test_filter_with_predicate(self):
        """Test filtering with predicate."""
        transformer = filter_(lambda n: n.get("active", False))
        result = transformer(self.tree)

        self.assertEqual(len(result.root.children), 2)
        names = {c.name for c in result.root.children}
        self.assertEqual(names, {"keep", "keep2"})

    def test_filter_with_selector(self):
        """Test filtering with selector."""
        transformer = filter_(attrs(active=True))
        result = transformer(self.tree)

        self.assertEqual(len(result.root.children), 2)


class TestPruneTransformer(unittest.TestCase):
    """Test prune factory."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("keep"),
            Node("remove", attrs={"delete": True}),
            Node("keep2")
        ))

    def test_prune_with_selector(self):
        """Test pruning with selector."""
        transformer = prune(attrs(delete=True))
        result = transformer(self.tree)

        self.assertEqual(len(result.root.children), 2)
        names = {c.name for c in result.root.children}
        self.assertEqual(names, {"keep", "keep2"})


class TestGraftTransformer(unittest.TestCase):
    """Test graft factory."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("target"),
            Node("other")
        ))

    def test_graft_static_subtree(self):
        """Test grafting static subtree."""
        subtree = Node("grafted")
        transformer = graft(name("target"), subtree)
        result = transformer(self.tree)

        target = result.root.children[0]
        self.assertEqual(len(target.children), 1)
        self.assertEqual(target.children[0].name, "grafted")

    def test_graft_dynamic_subtree(self):
        """Test grafting dynamic subtree."""
        transformer = graft(
            name("target"),
            lambda n: Node(f"{n.name}_child")
        )
        result = transformer(self.tree)

        target = result.root.children[0]
        self.assertEqual(len(target.children), 1)
        self.assertEqual(target.children[0].name, "target_child")


class TestFlattenTransformer(unittest.TestCase):
    """Test flatten factory."""

    def test_flatten_with_depth(self):
        """Test flattening with max depth."""
        tree = Tree(Node("root",
            Node("a",
                Node("b",
                    Node("c")
                )
            )
        ))

        transformer = flatten(max_depth=1)
        result = transformer(tree)

        # After flattening to depth 1, height should be limited
        self.assertLessEqual(result.height, 2)

    def test_flatten_complete(self):
        """Test complete flattening."""
        tree = Tree(Node("root",
            Node("a",
                Node("b")
            )
        ))

        transformer = flatten()
        result = transformer(tree)

        # Complete flatten brings all to root level
        self.assertGreater(len(result.root.children), 0)


class TestNormalizeTransformer(unittest.TestCase):
    """Test normalize factory."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("z", attrs={"foo": 1, "bar": 2}),
            Node("a", attrs={"foo": 3, "bar": 4}),
            Node("m", attrs={"foo": 5, "bar": 6})
        ))

    def test_normalize_sort_children(self):
        """Test normalizing with sorted children."""
        transformer = normalize(sort_children=True)
        result = transformer(self.tree)

        names = [c.name for c in result.root.children]
        self.assertEqual(names, ["a", "m", "z"])

    def test_normalize_custom_sort_key(self):
        """Test normalizing with custom sort key."""
        transformer = normalize(
            sort_children=True,
            sort_key=lambda n: -n.get("foo", 0)  # Descending by foo
        )
        result = transformer(self.tree)

        names = [c.name for c in result.root.children]
        self.assertEqual(names, ["m", "a", "z"])

    def test_normalize_clean_attrs(self):
        """Test normalizing with attribute cleaning."""
        transformer = normalize(
            sort_children=False,
            clean_attrs=True,
            allowed_attrs=["foo"]
        )
        result = transformer(self.tree)

        # Only 'foo' attribute should remain
        child = result.root.children[0]
        self.assertIn("foo", child.attrs)
        self.assertNotIn("bar", child.attrs)


class TestAnnotateTransformer(unittest.TestCase):
    """Test annotate factory."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("a"),
            Node("b")
        ))

    def test_annotate_all(self):
        """Test annotating all nodes."""
        transformer = annotate(processed=True, version=2)
        result = transformer(self.tree)

        self.assertTrue(result.root.get("processed"))
        self.assertEqual(result.root.get("version"), 2)

    def test_annotate_selective(self):
        """Test annotating selected nodes."""
        transformer = annotate(name("a"), marked=True)
        result = transformer(self.tree)

        self.assertTrue(result.root.children[0].get("marked"))
        self.assertIsNone(result.root.children[1].get("marked"))

    def test_annotate_with_function(self):
        """Test annotating with computed values."""
        transformer = annotate(label=lambda n: f"Node:{n.name}")
        result = transformer(self.tree)

        self.assertEqual(result.root.get("label"), "Node:root")
        self.assertEqual(result.root.children[0].get("label"), "Node:a")


class TestShapers(unittest.TestCase):
    """Test shaper transformers (Tree -> Any)."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2}),
            Node("c", attrs={"value": 3})
        ))

    def test_reduce_shaper(self):
        """Test reduce_ transformer."""
        shaper = reduce_(
            lambda acc, node: acc + node.get("value", 0),
            initial=0
        )
        result = shaper(self.tree)
        self.assertEqual(result, 6)  # 1 + 2 + 3

    def test_fold_shaper(self):
        """Test fold transformer."""
        shaper = fold(
            lambda node, child_results:
                node.get("value", 0) + sum(child_results)
        )
        result = shaper(self.tree)
        self.assertEqual(result, 6)

    def test_extract_shaper(self):
        """Test extract transformer."""
        shaper = extract(lambda n: n.name)
        result = shaper(self.tree)
        self.assertEqual(set(result), {"root", "a", "b", "c"})

        # With selector
        shaper = extract(lambda n: n.get("value"), selector=leaf())
        result = shaper(self.tree)
        self.assertEqual(set(result), {1, 2, 3})

    def test_to_dict_shaper(self):
        """Test to_dict transformer."""
        shaper = to_dict()
        result = shaper(self.tree)

        self.assertEqual(result["name"], "root")
        self.assertEqual(len(result["children"]), 3)

    def test_to_paths_shaper(self):
        """Test to_paths transformer."""
        shaper = to_paths()
        result = shaper(self.tree)

        self.assertEqual(len(result), 3)  # Leaves only by default
        self.assertIn("root/a", result)

    def test_to_paths_shaper_delimiter(self):
        """Test that to_paths(delimiter='.') returns dot-delimited paths."""
        shaper = to_paths(delimiter='.')
        result = shaper(self.tree)

        self.assertEqual(len(result), 3)  # Leaves only by default
        self.assertIn("root.a", result)
        # No slash-delimited paths should appear
        for path in result:
            self.assertNotIn("/", path)


class TestComposition(unittest.TestCase):
    """Test >> composition operator."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2}),
            Node("c", attrs={"value": 3})
        ))

    def test_pipeline_basic(self):
        """Test basic >> composition."""
        pipeline = map_(lambda n: {"value": n.get("value", 0) * 2}) >> \
                   filter_(lambda n: n.get("value", 0) > 2)

        result = pipeline(self.tree)
        # After doubling: a=2, b=4, c=6
        # After filtering (>2): b=4, c=6
        self.assertEqual(len(result.root.children), 2)

    def test_pipeline_with_shaper(self):
        """Test >> composition ending with shaper."""
        # Note: filter preserves ancestors (root), so extract gets root's value (None) too
        pipeline = filter_(lambda n: n.get("value", 0) > 1) >> \
                   extract(lambda n: n.get("value"))

        result = pipeline(self.tree)
        # Filter out None (from root node which is kept as ancestor)
        values = {v for v in result if v is not None}
        self.assertEqual(values, {2, 3})

    def test_rshift_operator(self):
        """Test >> operator for composition."""
        t1 = map_(lambda n: {"value": n.get("value", 0) * 2})
        t2 = filter_(lambda n: n.get("value", 0) > 2)

        pipeline = t1 >> t2
        result = pipeline(self.tree)

        # setUp has a=1, b=2, c=3; after doubling: a=2, b=4, c=6
        # After filter (>2): b=4 and c=6 both pass -> 2 children
        self.assertEqual(len(result.root.children), 2)

    def test_rshift_is_transformer(self):
        """Test that >> returns a Transformer instance."""
        t1 = map_(lambda n: n)
        t2 = filter_(lambda n: True)
        composed = t1 >> t2
        self.assertIsInstance(composed, Transformer)


class TestRepeat(unittest.TestCase):
    """Test .repeat() method."""

    def test_repeat(self):
        """Test repeating transformer."""
        tree = Tree(Node("root", attrs={"value": 1}))

        transformer = map_(lambda n: {"value": n.get("value", 0) * 2})
        repeated = transformer.repeat(3)

        result = repeated(tree)
        # After 3 repeats: 1 * 2 * 2 * 2 = 8
        self.assertEqual(result.root.get("value"), 8)

    def test_repeat_returns_transformer(self):
        """Test that .repeat() returns a Transformer."""
        t = map_(lambda n: n)
        self.assertIsInstance(t.repeat(2), Transformer)


class TestWhen(unittest.TestCase):
    """Test .when() method."""

    def test_when_true(self):
        """Test when condition is true."""
        tree = Tree(Node("root", attrs={"value": 10}))

        transformer = map_(lambda n: {"value": 999})
        conditional = transformer.when(lambda t: t.root.get("value") > 5)

        result = conditional(tree)
        self.assertEqual(result.root.get("value"), 999)

    def test_when_false(self):
        """Test when condition is false."""
        tree = Tree(Node("root", attrs={"value": 3}))

        transformer = map_(lambda n: {"value": 999})
        conditional = transformer.when(lambda t: t.root.get("value") > 5)

        result = conditional(tree)
        self.assertEqual(result.root.get("value"), 3)  # Unchanged

    def test_when_returns_transformer(self):
        """Test that .when() returns a Transformer."""
        t = map_(lambda n: n)
        self.assertIsInstance(t.when(lambda _: True), Transformer)


class TestIdentity(unittest.TestCase):
    """Test the identity transformer."""

    def setUp(self):
        self.tree = Tree(Node("root",
            Node("a", attrs={"value": 1}),
        ))

    def test_identity_is_noop(self):
        """identity(tree) == tree."""
        result = identity(self.tree)
        self.assertIs(result, self.tree)

    def test_identity_left_unit(self):
        """(identity >> t)(x) behaves as t(x)."""
        t = map_(lambda n: {"value": n.get("value", 0) * 2})
        composed = identity >> t
        self.assertEqual(composed(self.tree).root.children[0].get("value"),
                         t(self.tree).root.children[0].get("value"))

    def test_identity_right_unit(self):
        """(t >> identity)(x) behaves as t(x)."""
        t = map_(lambda n: {"value": n.get("value", 0) * 2})
        composed = t >> identity
        self.assertEqual(composed(self.tree).root.children[0].get("value"),
                         t(self.tree).root.children[0].get("value"))


class TestTransformerRepr(unittest.TestCase):
    """Test transformer string representations."""

    def test_transformer_repr(self):
        """Test that Transformer repr includes label."""
        t = map_(lambda n: n)
        self.assertIn("Transformer", repr(t))

    def test_composed_repr(self):
        """Test that >> repr includes >>."""
        composed = map_(lambda n: n) >> filter_(lambda n: True)
        self.assertIn(">>", repr(composed))


class TestTransformersOnBareNode(unittest.TestCase):
    """T1: every factory must work on a bare Node (duck-typing claim)."""

    def setUp(self):
        self.node = Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2})
        )

    def test_map_node_returning_fn_on_bare_node(self):
        """map_(Node-returning fn) on bare Node returns a Node."""
        result = map_(lambda n: n.with_attrs(x=1))(self.node)
        self.assertIsInstance(result, Node)
        self.assertEqual(result.get("x"), 1)

    def test_map_dict_fn_on_bare_node(self):
        """map_(dict-shorthand fn) on bare Node works like on Tree."""
        result = map_(lambda n: {"doubled": n.get("value", 0) * 2})(self.node)
        self.assertIsInstance(result, Node)
        self.assertEqual(result.children[0].get("doubled"), 2)
        self.assertEqual(result.children[1].get("doubled"), 4)

    def test_map_none_fn_on_bare_node(self):
        """map_(None-returning fn) on bare Node keeps nodes unchanged."""
        result = map_(lambda n: None)(self.node)
        self.assertIsInstance(result, Node)
        self.assertEqual(result.children[0].get("value"), 1)

    def test_filter_on_bare_node(self):
        """filter_ on bare Node returns a Node."""
        result = filter_(lambda n: n.get("value", 0) > 1)(self.node)
        # filter returns None if nothing matches at root; root is kept as ancestor
        self.assertIsInstance(result, Node)

    def test_prune_on_bare_node(self):
        """prune on bare Node returns a Node."""
        result = prune("a")(self.node)
        self.assertIsInstance(result, Node)
        self.assertEqual(len(result.children), 1)
        self.assertEqual(result.children[0].name, "b")

    def test_graft_on_bare_node(self):
        """graft on bare Node returns a Node."""
        result = graft("a", Node("child_of_a"))(self.node)
        self.assertIsInstance(result, Node)
        a_node = next(c for c in result.children if c.name == "a")
        self.assertEqual(len(a_node.children), 1)
        self.assertEqual(a_node.children[0].name, "child_of_a")

    def test_normalize_on_bare_node(self):
        """normalize on bare Node returns a Node."""
        unordered = Node("root", Node("z"), Node("a"), Node("m"))
        result = normalize()(unordered)
        self.assertIsInstance(result, Node)
        self.assertEqual([c.name for c in result.children], ["a", "m", "z"])

    def test_annotate_on_bare_node(self):
        """annotate on bare Node returns a Node."""
        result = annotate(tagged=True)(self.node)
        self.assertIsInstance(result, Node)
        self.assertTrue(result.get("tagged"))

    def test_flatten_on_bare_node(self):
        """flatten on bare Node returns a Node."""
        deep = Node("root", Node("a", Node("b", Node("c"))))
        result = flatten(max_depth=1)(deep)
        self.assertIsInstance(result, Node)


class TestCompositionAssociativity(unittest.TestCase):
    """T2: >> is associative: ((a >> b) >> c)(x) == (a >> (b >> c))(x)."""

    def setUp(self):
        self.tree = Tree(Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2}),
            Node("c", attrs={"value": 3}),
        ))

    def test_associativity_on_tree(self):
        """((a >> b) >> c)(tree) == (a >> (b >> c))(tree)."""
        a = map_(lambda n: {"value": n.get("value", 0) * 2})
        b = filter_(lambda n: n.get("value", 0) > 2)
        c = annotate(processed=True)

        lhs = (a >> b) >> c
        rhs = a >> (b >> c)

        lhs_result = lhs(self.tree)
        rhs_result = rhs(self.tree)

        # Both compositions must produce identical trees
        self.assertEqual(lhs_result.root, rhs_result.root)

    def test_associativity_on_bare_node(self):
        """((a >> b) >> c)(node) == (a >> (b >> c))(node) for bare Node."""
        node = Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2}),
        )
        a = map_(lambda n: {"value": n.get("value", 0) + 10})
        b = annotate(step1=True)
        c = annotate(step2=True)

        lhs = (a >> b) >> c
        rhs = a >> (b >> c)

        lhs_result = lhs(node)
        rhs_result = rhs(node)

        self.assertIsInstance(lhs_result, Node)
        self.assertEqual(lhs_result, rhs_result)


if __name__ == "__main__":
    unittest.main()
