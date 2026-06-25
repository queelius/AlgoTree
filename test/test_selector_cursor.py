from AlgoTree import Node, Tree
from AlgoTree.selectors import depth, leaf, name


def _tree():
    return Tree(Node("root",
                     Node("a", Node("x"), Node("y")),
                     Node("b")))


def test_find_all_routes_positional_selector_through_cursor():
    nodes = _tree().find_all(depth(2))
    assert {n.name for n in nodes} == {"x", "y"}


def test_find_returns_first_positional_match():
    assert _tree().find(depth(1)).name == "a"


def test_tree_select_routes_positional_selector():
    nodes = list(_tree().select(depth(1)))
    assert {n.name for n in nodes} == {"a", "b"}


def test_select_value_local_still_works():
    assert {n.name for n in leaf().select(_tree())} == {"x", "y", "b"}


def test_matches_at_default_is_value_local():
    from AlgoTree.cursor import Cursor
    cur = Cursor(Node("hit"))
    assert name("hit").matches_at(cur) is True
    assert name("miss").matches_at(cur) is False
