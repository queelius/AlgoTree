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


def test_set_attr_rebuilds_only_spine_sharing_siblings():
    root = _tree()
    cur = Cursor(root).down("a")
    edited = cur.set_attr(seen=True)
    new_root = edited.root().node
    # the edited node carries the attr
    assert new_root.children[0].get("seen") is True
    # the untouched sibling 'b' is the very same object (structural sharing)
    assert new_root.children[1] is root.children[1]
    # original tree is unchanged (immutability)
    assert root.children[0].get("seen") is None


def test_replace_swaps_focus_and_shares_siblings():
    root = _tree()
    cur = Cursor(root).down("b")
    new_root = cur.replace(Node("B2")).root().node
    assert new_root.children[1].name == "B2"
    assert new_root.children[0] is root.children[0]   # 'a' subtree shared


def test_ancestors_parent_to_root_order():
    cur = Cursor(_tree()).down("a").down("x")
    names = [c.node.name for c in cur.ancestors()]
    assert names == ["a", "root"]          # parent first, then up to root


def test_siblings_excludes_focus():
    cur = Cursor(_tree()).down("a")
    sib_names = [c.node.name for c in cur.siblings()]
    assert sib_names == ["b"]


def test_walk_cursors_preorder():
    from AlgoTree.cursor import walk_cursors
    names = [c.node.name for c in walk_cursors(Cursor(_tree()))]
    assert names == ["root", "a", "x", "b"]


def test_walk_cursors_depths():
    from AlgoTree.cursor import walk_cursors
    depths = {c.node.name: c.depth for c in walk_cursors(Cursor(_tree()))}
    assert depths == {"root": 0, "a": 1, "x": 2, "b": 1}
