import anytree
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
from treekit.tree_converter import TreeConverter
from typing import Callable, Optional

class TreeViz:
    @staticmethod
    def text(node,
             style=anytree.ContStyle(),
             node_name: Callable = TreeConverter.default_node_name,
             extract: Callable = TreeConverter.default_extract,
             **kwargs) -> str:
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

        :return: str
        """

        if not isinstance(node, Node):
            node = TreeConverter.to_anytree(node=node)

        result = ""
        for pre, _, n in RenderTree(node=node, style=style, **kwargs):
            result += f"{pre}{node_name(n)}\n"
        return result

    @staticmethod
    def image(node,
              filename: str,
              node_name: Callable=TreeConverter.default_node_name,
              **kwargs) -> None:
        """
        Save the tree to an image or dot file. The outfile should include the
        format extension (e.g., 'tree.png' or 'tree.dot').

        :param node: The subtree rooted at `node`
        :param filename: Name of the file to output the image to.
        :param node_name: Function to generate node names given a node. Default
                          is the node's `name` property.
        :param kwargs: Additional key-word arguments to pass to the DotExporter class.
        :return: None
        """

        if not isinstance(node, Node):
            node = TreeConverter.to_anytree(node=node,
                                            node_name=node_name)

        # Create a dictionary to map each node to a unique identifier
        node_to_id = {n: f"node{idx}" for idx, n in
                      enumerate([node] + list(node.descendants))}

        dot = DotExporter(
            node=node,
            nodenamefunc=lambda node: node_to_id[node],
            nodeattrfunc=lambda node: f'label="{node_name(node)}"',
            **kwargs)

        dot.to_picture(filename)