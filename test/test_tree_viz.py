import pytest
from anytree import Node

def test_to_text():
    root = Node("root")
    child1 = Node("child1", parent=root)
    child2 = Node("child2", parent=root)
    text = to_text(root)
    assert "root" in text
    assert "child1" in text
    assert "child2" in text

def test_to_image(tmp_path):
    root = Node("root")
    child1 = Node("child1", parent=root)
    child2 = Node("child2", parent=root)
    image_path = tmp_path / "tree.png"
    to_image(root, str(image_path))
    assert image_path.exists()
