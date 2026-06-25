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


def test_positional_selector_matches_node_raises():
    import pytest
    from AlgoTree.selectors import depth, root
    with pytest.raises(NotImplementedError):
        depth(1).matches(Node("x"))
    with pytest.raises(NotImplementedError):
        root().matches(Node("x"))


def test_node_has_no_parent_api():
    n = Node("x")
    assert not hasattr(n, "parent")
    assert not hasattr(n, "depth")
    assert not hasattr(n, "is_root")
