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
