from AlgoTree import Node, Tree
from AlgoTree.selectors import depth
from AlgoTree.transformers import filter_, prune


def _tree():
    return Tree(Node("root", Node("a", Node("x"), Node("y")), Node("b")))


def test_prune_positional_selector_removes_matches():
    # remove depth-2 nodes (x, y); a survives as a now-leaf, b survives
    pruned = _tree().prune(depth(2))
    assert {n.name for n in pruned.root.walk()} == {"root", "a", "b"}


def test_filter_positional_selector_keeps_matches_and_ancestors():
    # keep depth-2 nodes (x, y) and their ancestors; b has no depth-2 descendant
    filtered = _tree().filter(depth(2))
    assert {n.name for n in filtered.root.walk()} == {"root", "a", "x", "y"}


def test_filter_transformer_routes_positional_selector():
    t = Tree(Node("root", Node("a", Node("x")), Node("b")))
    result = filter_(depth(2))(t)
    assert {n.name for n in result.root.walk()} == {"root", "a", "x"}


def test_prune_transformer_routes_positional_selector():
    t = Tree(Node("root", Node("a", Node("x")), Node("b")))
    result = prune(depth(2))(t)
    assert {n.name for n in result.root.walk()} == {"root", "a", "b"}


def test_value_local_filter_still_works():
    t = Tree(Node("root", Node("keep"), Node("drop")))
    filtered = t.filter(lambda n: n.name != "drop")
    assert {n.name for n in filtered.root.walk()} == {"root", "keep"}
