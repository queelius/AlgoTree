import anytree
from anytree import Node, RenderTree
from anytree.exporter import DotExporter

def to_text(root: Node, node_name=lambda node: node.name, style=anytree.ContStyle()) -> str:
    """
    Generate a string representation of any anytree rooted at the given node.

    :param root: Root anytree node.
    :param node_name: Function to generate node names.
    :param style: Style of the tree rendering. See anyTree documentation for more details.
    :return: str
    """
    result = ""
    for pre, _, node in RenderTree(root, style=style):
        result += f"{pre}{node_name(node)}\n"
    return result

def to_image(root: Node, out: str, node_name=lambda node: node.name) -> None:
    """
    Save the tree to an image or dot file. The outfile should include the format extension (e.g., 'tree.png' or 'tree.dot').

    :param root: Root node.
    :param node_name: Function to generate node names given a node.
    :param out: Name of the output file.
    :return: None
    """
    ext = out.split('.')[-1]
    dotfile = DotExporter(node=root, nodenamefunc=node_name)
    dotfile.to_picture(out)
