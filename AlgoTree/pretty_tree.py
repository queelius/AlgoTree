from typing import Callable, Optional, Dict, Any, List

#from AlgoTree.treenode_api import TreeNodeApi

class PrettyTree:
    """
    A class to print a tree in a more readable way.
    """

    default_style = {
        "vertical": "│",
        "horizontal": "─",
        "last_child_connector": "└",
        "markers": ["🔵", "🔴", "🟢", "🟣", "🟠", "🟡", "🟤", "⚫", "⚪", "⭕", "🔘"],
        "spacer": " ",
        "child_connector": "├",
        "payload_connector": "◄"
    }

    def __init__(self,
                 style: Optional[Dict[str, str]] = None,
                 node_name: Callable[[Any], str] = lambda node: node.name,
                 indent: int = 7,
                 mark: Optional[List[str]] = None,
                 node_details: Optional[Callable[[Any], Any]] = None):
        """
        Initialize the PrettyTree object. If a node name is not provided, the default
        node name is the `name` property of the node. If a node detail is not provided,
        no additional node details are displayed. If a style is not provided, the default
        style is used. Any missing style keys are filled in with the default style.

        :param style: A style to use for printing. See `default_style` for the default style.
        :param node_name: A function that returns the name of a node. Defaults to returning the node's `name` property.
        :param mark: A list of node names. The marker will be a function of the hash of the node's name,
        which indexes into the markers.
        :param node_details: A function to map a node to a string to be displayed next to the node name. Default is None.
        :param indent: The number of spaces to indent each level of the tree.
        """
        self.style = self.default_style.copy()
        if style:
            self.style.update(style)

        self.node_name = node_name
        self.node_details = node_details
        self.marked_nodes = mark if mark is not None else []
        self.indent = indent

    @staticmethod
    def mark(name: str, markers: List[str]) -> str:
        """
        Get the marker for a node based on the hash of the node name.

        :param name: The name of the node.
        :return: The marker for the node.
        """
        return markers[hash(name) % len(markers)]

    def __call__(self, node, **kwargs) -> str:
        """
        Print the tree.

        :param node: The root node of the tree.
        :param kwargs: Additional style parameters to override the default style.
        :return: A pretty string representation of the tree.
        """
        # TreeNodeApi.check(node)
        style = self.style.copy()
        style.update(kwargs.get("style", {}))

        marked_nodes = self.marked_nodes + kwargs.get("mark", [])
        node_name = kwargs.get("node_name", self.node_name)
        node_details = kwargs.get("node_details", self.node_details)
        indent = kwargs.get("indent", self.indent)
        markers = kwargs.get("markers", style['markers'])

        def _build(cur, ind, bar_levels, is_last):
            s = ""
            if ind > 0:
                for i in range(ind - 1):
                    if i in bar_levels:
                        s += style["vertical"]
                    else:
                        s += style["spacer"]
                    s += style["spacer"] * (indent - 1)
                if is_last:
                    s += style["last_child_connector"]
                else:
                    s += style["child_connector"]
                s += style["horizontal"] * (indent - 2)
                s += style["spacer"] 

            s += str(node_name(cur))
            if node_details is not None:
                s += style["spacer"]
                s += style["payload_connector"]
                s += style["spacer"]
                s += str(node_details(cur))
            if cur.name in marked_nodes:
                s += style["spacer"]
                s += PrettyTree.mark(str(node_name(cur)), markers)
            s += "\n"

            for i, child in enumerate(cur.children):
                new_bar_levels = bar_levels.copy()
                if i < len(cur.children) - 1:
                    new_bar_levels.add(ind)
                s += _build(child, ind + 1, new_bar_levels, i == len(cur.children) - 1)

            return s

        return _build(node, 0, set(), True)


def pretty_tree(node, **kwargs) -> str:
    """
    Converts a tree to a pretty string representation.

    :param kwargs: Key-word arguments. See `PrettyTree` for more details.
    :return: A pretty string representation of the tree.
    """
    return PrettyTree()(node, **kwargs)
