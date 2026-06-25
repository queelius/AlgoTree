from AlgoTree import Node, Tree
from AlgoTree.cursor import Cursor
from AlgoTree.selectors import name, depth


def _tree():
    return Tree(Node("root", Node("a", Node("x")), Node("b")))


def test_locate_returns_cursor_at_match():
    cur = _tree().locate(name("x"))
    assert isinstance(cur, Cursor)
    assert cur.node.name == "x"
    assert cur.path == ("root", "a", "x")


def test_locate_none_when_absent():
    assert _tree().locate(name("zzz")) is None


def test_cursors_at_returns_all():
    curs = _tree().cursors_at(depth(1))
    assert [c.node.name for c in curs] == ["a", "b"]


def test_locate_accepts_string():
    assert _tree().locate("b").node.name == "b"
