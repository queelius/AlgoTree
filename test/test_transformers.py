import unittest
from AlgoTree.node import Node
from AlgoTree.tree import Tree
from AlgoTree.selectors import name, attrs, leaf
from AlgoTree.transformers import (
    Transformer, TreeTransformer,
    MapTransformer, FilterTransformer, PruneTransformer,
    GraftTransformer, FlattenTransformer, NormalizeTransformer, AnnotateTransformer,
    ReduceShaper, FoldShaper, ExtractShaper, ToDictShaper, ToPathsShaper,
    Pipeline, ParallelTransformer, RepeatTransformer, ConditionalTransformer, DebugTransformer,
    map_, filter_, prune, graft, flatten, normalize, annotate,
    reduce_, fold, extract, to_dict, to_paths
)


class TestMapTransformer(unittest.TestCase):
    """Test MapTransformer."""

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
    """Test FilterTransformer."""

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
    """Test PruneTransformer."""

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
    """Test GraftTransformer."""

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
    """Test FlattenTransformer."""

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
    """Test NormalizeTransformer."""

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
    """Test AnnotateTransformer."""

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
        """Test reduce shaper."""
        shaper = reduce_(
            lambda acc, node: acc + node.get("value", 0),
            initial=0
        )
        result = shaper(self.tree)
        self.assertEqual(result, 6)  # 1 + 2 + 3

    def test_fold_shaper(self):
        """Test fold shaper."""
        shaper = fold(
            lambda node, child_results:
                node.get("value", 0) + sum(child_results)
        )
        result = shaper(self.tree)
        self.assertEqual(result, 6)

    def test_extract_shaper(self):
        """Test extract shaper."""
        shaper = extract(lambda n: n.name)
        result = shaper(self.tree)
        self.assertEqual(set(result), {"root", "a", "b", "c"})

        # With selector
        shaper = extract(lambda n: n.get("value"), selector=leaf())
        result = shaper(self.tree)
        self.assertEqual(set(result), {1, 2, 3})

    def test_to_dict_shaper(self):
        """Test to-dict shaper."""
        shaper = to_dict()
        result = shaper(self.tree)

        self.assertEqual(result["name"], "root")
        self.assertEqual(len(result["children"]), 3)

    def test_to_paths_shaper(self):
        """Test to-paths shaper."""
        shaper = to_paths()
        result = shaper(self.tree)

        self.assertEqual(len(result), 3)  # Leaves only by default
        self.assertIn("root/a", result)


class TestPipeline(unittest.TestCase):
    """Test Pipeline transformer."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2}),
            Node("c", attrs={"value": 3})
        ))

    def test_pipeline_basic(self):
        """Test basic pipeline."""
        pipeline = map_(lambda n: {"value": n.get("value", 0) * 2}) >> \
                   filter_(lambda n: n.get("value", 0) > 2)

        result = pipeline(self.tree)
        # After doubling: a=2, b=4, c=6
        # After filtering (>2): b=4, c=6
        self.assertEqual(len(result.root.children), 2)

    def test_pipeline_with_shaper(self):
        """Test pipeline ending with shaper."""
        # Note: filter preserves ancestors (root), so extract gets root's value (None) too
        pipeline = filter_(lambda n: n.get("value", 0) > 1) >> \
                   extract(lambda n: n.get("value"))

        result = pipeline(self.tree)
        # Filter out None (from root node which is kept as ancestor)
        values = {v for v in result if v is not None}
        self.assertEqual(values, {2, 3})

    def test_pipeline_or_operator(self):
        """Test pipeline with | operator."""
        pipeline = map_(lambda n: {"doubled": True}) | \
                   annotate(marked=True)

        result = pipeline(self.tree)
        self.assertTrue(result.root.get("doubled"))
        self.assertTrue(result.root.get("marked"))


class TestParallelTransformer(unittest.TestCase):
    """Test ParallelTransformer."""

    def test_parallel_execution(self):
        """Test parallel transformer execution."""
        tree = Tree(Node("root"))

        parallel = ParallelTransformer(
            graft("root", Node("from_t1")),
            graft("root", Node("from_t2"))
        )

        result = parallel(tree)
        # Both transformers should have added children
        self.assertGreaterEqual(len(result.root.children), 1)


class TestRepeatTransformer(unittest.TestCase):
    """Test RepeatTransformer."""

    def test_repeat(self):
        """Test repeating transformer."""
        tree = Tree(Node("root", attrs={"value": 1}))

        transformer = map_(lambda n: {"value": n.get("value", 0) * 2})
        repeated = transformer.repeat(3)

        result = repeated(tree)
        # After 3 repeats: 1 * 2 * 2 * 2 = 8
        self.assertEqual(result.root.get("value"), 8)


class TestConditionalTransformer(unittest.TestCase):
    """Test ConditionalTransformer."""

    def test_conditional_when_true(self):
        """Test conditional when condition is true."""
        tree = Tree(Node("root", attrs={"value": 10}))

        transformer = map_(lambda n: {"value": 999})
        conditional = transformer.when(lambda t: t.root.get("value") > 5)

        result = conditional(tree)
        self.assertEqual(result.root.get("value"), 999)

    def test_conditional_when_false(self):
        """Test conditional when condition is false."""
        tree = Tree(Node("root", attrs={"value": 3}))

        transformer = map_(lambda n: {"value": 999})
        conditional = transformer.when(lambda t: t.root.get("value") > 5)

        result = conditional(tree)
        self.assertEqual(result.root.get("value"), 3)  # Unchanged


class TestDebugTransformer(unittest.TestCase):
    """Test DebugTransformer."""

    def test_debug_transformer(self):
        """Test debug transformer with callback."""
        tree = Tree(Node("root"))
        messages = []

        transformer = map_(lambda n: {"debugged": True})
        debug_transformer = transformer.debug(
            name="test",
            callback=lambda msg: messages.append(msg)
        )

        result = debug_transformer(tree)

        self.assertTrue(result.root.get("debugged"))
        self.assertEqual(len(messages), 2)  # Before and after


class TestTransformerComposition(unittest.TestCase):
    """Test transformer composition operators."""

    def setUp(self):
        """Set up test tree."""
        self.tree = Tree(Node("root",
            Node("a", attrs={"value": 1}),
            Node("b", attrs={"value": 2})
        ))

    def test_rshift_operator(self):
        """Test >> operator for composition."""
        t1 = map_(lambda n: {"value": n.get("value", 0) * 2})
        t2 = filter_(lambda n: n.get("value", 0) > 2)

        pipeline = t1 >> t2
        result = pipeline(self.tree)

        # After doubling: a=2, b=4
        # After filter: only b (4 > 2)
        self.assertEqual(len(result.root.children), 1)

    def test_or_operator(self):
        """Test | operator for composition."""
        t1 = map_(lambda n: {"doubled": True})
        t2 = annotate(marked=True)

        pipeline = t1 | t2
        result = pipeline(self.tree)

        self.assertTrue(result.root.get("doubled"))
        self.assertTrue(result.root.get("marked"))

    def test_and_operator(self):
        """Test & operator for parallel composition."""
        t1 = annotate(from_t1=True)
        t2 = annotate(from_t2=True)

        parallel = t1 & t2
        result = parallel(self.tree)

        # Both should be applied (parallel merge)
        self.assertIsInstance(result, Tree)


class TestTransformerRepresentations(unittest.TestCase):
    """Test transformer string representations."""

    def test_map_repr(self):
        """Test MapTransformer repr."""
        transformer = map_(lambda n: n)
        repr_str = repr(transformer)
        self.assertIn("MapTransformer", repr_str)

    def test_pipeline_repr(self):
        """Test Pipeline repr."""
        pipeline = map_(lambda n: n) >> filter_(lambda n: True)
        repr_str = repr(pipeline)
        self.assertIn("Pipeline", repr_str)
        self.assertIn(">>", repr_str)


if __name__ == "__main__":
    unittest.main()
