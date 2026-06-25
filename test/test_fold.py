from AlgoTree import Node


def _sample():
    # root
    #   a (leaf)
    #   b
    #     c (leaf)
    return Node("root",
                Node("a"),
                Node("b", Node("c")))


def test_fold_counts_nodes():
    tree = _sample()
    count = tree.fold(lambda node, child_results: 1 + sum(child_results))
    assert count == 4


def test_fold_is_bottom_up_postorder():
    tree = _sample()
    order = []

    def visit(node, child_results):
        order.append(node.name)
        return None

    tree.fold(visit)
    # children appear before their parent; siblings in order
    assert order == ["a", "c", "b", "root"]


def test_fold_receives_child_results_in_order():
    tree = Node("p", Node("x"), Node("y"), Node("z"))
    names = tree.fold(
        lambda node, child_results: node.name if not child_results else child_results
    )
    assert names == ["x", "y", "z"]


def test_fold_on_leaf_gets_empty_child_results():
    seen = []
    Node("solo").fold(lambda node, child_results: seen.append(child_results))
    assert seen == [[]]


def test_size_equals_walk_count():
    tree = _sample()
    assert tree.size == len(list(tree.walk()))      # size is node count


def test_size_is_fold():
    tree = _sample()
    assert tree.size == tree.fold(lambda n, cs: 1 + sum(cs))


def test_height_of_leaf_is_zero():
    assert Node("leaf").height == 0


def test_height_is_one_plus_max_child_height():
    tree = _sample()                                # root -> b -> c is the deepest path
    assert tree.height == 2
    assert tree.height == tree.fold(lambda n, cs: 0 if not cs else 1 + max(cs))
