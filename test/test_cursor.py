import pytest
from AlgoTree import Node
from AlgoTree.cursor import Cursor


def _tree():
    # root
    #   a
    #     x
    #   b
    return Node("root",
                Node("a", Node("x")),
                Node("b"))


def test_focus_and_root_depth():
    cur = Cursor(_tree())
    assert cur.node.name == "root"
    assert cur.depth == 0
    assert cur.is_root
    assert cur.path == ("root",)


def test_down_by_name_and_index():
    cur = Cursor(_tree())
    assert cur.down("a").node.name == "a"
    assert cur.down(1).node.name == "b"
    assert cur.down("a").depth == 1
    assert cur.down("a").path == ("root", "a")
    assert not cur.down("a").is_root


def test_down_missing_child_raises():
    cur = Cursor(_tree())
    with pytest.raises(KeyError):
        cur.down("nope")


def test_up_inverts_down():
    cur = Cursor(_tree())
    assert cur.down("a").up() == cur            # up . down == identity
    assert cur.down("a").down("x").up().up() == cur


def test_up_at_root_raises():
    with pytest.raises(ValueError):
        Cursor(_tree()).up()


def test_left_right_siblings():
    cur = Cursor(_tree())
    a = cur.down("a")
    b = a.right()
    assert b.node.name == "b"
    assert b.left().node.name == "a"


def test_left_at_first_raises():
    with pytest.raises(ValueError):
        Cursor(_tree()).down(0).left()


def test_root_returns_to_top():
    cur = Cursor(_tree())
    deep = cur.down("a").down("x")
    assert deep.depth == 2
    assert deep.root() == cur
