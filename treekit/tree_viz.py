import anytree
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
from treekit.tree_converter import TreeConverter
from typing import Callable

class TreeViz:
    @staticmethod
    def text(node,
             style=anytree.ContStyle(),
             node_name: Callable=lambda node: node.name,
             maxlevel=None) -> str:
        """
        Generate a text string representation of the part of the tree rooted at
        `node`. The `style` parameter controls the presentation of the tree.

        Options include:

        - anytree.ContStyle()
        - anytree.DoubleStyle()
        - anytree.AsciiStyle()
        - anytree.AsciiRoundStyle()

        See `RenderTree` in the anytree documentation for more details.

        :param node: the subtree rooted at `node`.
        :param node_name: Function to generate node names. Default is the node's name property.
        :param style: Style of the tree rendering. The default style is `anytree.ContStyle()`.
        :param maxlevel: The maximum depth to render. If None, renders the entire tree.
        :return: str
        """

        if not isinstance(node, Node):
            node = TreeConverter.to_anytree(node)

        result = ""
        for pre, _, n in RenderTree(node=node, style=style, maxlevel=maxlevel):
            result += f"{pre}{node_name(n)}\n"
        return result

    @staticmethod
    def image(node,
              filename: str,
              node_name: Callable=lambda node: node.name,
              maxlevel=None,
              **kwargs) -> None:
        """
        Save the tree to an image or dot file. The outfile should include the
        format extension (e.g., 'tree.png' or 'tree.dot').

        Additional kwargs can be passed to the DotExporter class to
        customize the appearance of the tree. See the anytree documentation
        for more details.

        :param node: The subtree rooted at `node`
        :param filename: Name of the file to output the image to.
        :param node_name: Function to generate node names given a node. Default is the node's name property.
        :param kwargs: Additional parameters to pass to the DotExporter class.
        :return: None
        """

        if not isinstance(node, Node):
            node = TreeConverter.to_anytree(node)

        dotfile = DotExporter(node=node, nodenamefunc=node_name,
                              maxlevel=maxlevel, **kwargs)
        dotfile.to_picture(filename)
