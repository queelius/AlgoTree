
from treekit import DictTree
import jmespath
import re


def matchers(mat):
    """
    Matchers are functions that take in node data (payload) and output
    True or False if it is a match. The matchers are used to find nodes
    based on a search query.

    The matchers are used in the `find_nodes` and `filter_nodes`
    functions.

    We have provided a few example matchers, but you can also define your
    own:

    - `bool`: A matcher based on Boolean algebra on dictionary keys.
        The query is a JMESPath expression that is evaluated on the
        node's payload. If the expression evaluates to True, the node
        is a match.

        Ex: "field1 == 'value1' && !(field2 == 'value2' ||
                                     field3.subfield == 'value3')"

    - `regex`: A matcher based on regular expressions. The query is a
        regular expression pattern and the pattern is matched against
        the string representation of each node's payload.

        Ex: r".*field1.*value1.*field2.*value2.*field3.subfield.*value3.*"

    - 'pred': A predicate function `node_data -> { True, False }`. The
        query is a function that takes in the node's payload and
        returns True or False. This is useful for more complex
        matching logic.

        Ex: lambda node_data: node_data['field1'] == 'value1' and
                not (node_data['field2']['subfield'] == 'value2' or
                     node_data['field3'] == 'value3')

    :param mat: A matcher.
    :return: A function that takes in a query and node data and returns
        True or False if the node is a match.
    """
    match_dict = {
        'bool': lambda q, node_data: jmespath.compile(q).search(node_data),
        'regex': lambda q, node_data: re.compile(q).search(str(node_data)),
        'pred': lambda q, node_data: q(node_data)}

    return lambda query, node_data: match_dict[mat](query, node_data)


def decorators(decs):
    """
    A decorator is a function that takes a node as input and returns a
    dictionary. The intended purpose is to add additional information to
    a node's payload. This is useful for adding information that may be
    useful for searching or filtering nodes.

    The dictionary will be merged with the node's payload, and will
    overwrite existing keys.

    We have provided several example decorators, but you can also define
    your own.

    :return: A dictionary of key-value pairs where the key is the name of
        the decorator and the value is the decorator function.
    """
    dec_dict = {
        'node_key':
            lambda node: {"node_key": node.name},
        'parent_key':
            lambda node: {"parent_key": node.parent.name if node.parent else None},
        'depth':
            lambda node: {"node_depth": str(node.depth)},
        'is_leaf':
            lambda node: {"is_leaf": str(node.is_leaf)},
        'is_root':
            lambda node: {"is_root": str(node.is_root)},
        'ancestors':
            lambda node: {"ancesors": [a.name for a in node.ancestors]},
        'siblings':
            lambda node: {"siblings": [sib.name for sib in node.siblings]},
        'children':
            lambda node: {"children": [child.name for child in node.children]},
        'descendants':
            lambda node: {"descendants": [d.name for d in node.descendants]},
        'num_children':
            lambda node: {"num_children": str(len(node.children))},
        'num_descendants':
            lambda node: {"num_descendants": str(len(node.descendants))},
        'num_siblings':
            lambda node: {"num_siblings": str(len(node.siblings))},
        'num_ancestors':
            lambda node: {"num_ancestors": str(len(node.ancestors))}
    }

    return [dec_dict[dec] for dec in decs]


def find_nodes(tree,
               query,
               matcher=matchers('pred')):
    """
    Find nodes matching a search query.

    :param query: A search query, whose format depends on the matcher.

    :param matcher: A function that takes in node data (payload) and outputs
    True or False if it is a match. See the `matchers`
    function for examples. The default is the 'pred' matcher, in which the
    query is a function (e.g., lambda express) that takes in the node's payload
    and returns True or False.

    :return: A list of nodes that match the search query.
    """

    return [node_data for node_data in tree.nodes.values()
            if matcher(query, node_data.payload)]

def filter_nodes(tree,
                 query,
                 matcher=matchers('pred')):
    """
    Filter nodes in a tree based on a query and matcher.

    If a node matches the query, it is included in the new tree. If it
    does not match, it is excluded. When a node is removed, its children
    are made the children of the nearest ancestor that is not removed.

    :param tree: The tree to filter.
    :param query: A search query, whose format depends on the matcher.
    :param matcher: The matcher to use. See the `matchers` function for examples.
    """
    node_keys = [n.name for n in find_nodes(tree, query, matcher, decorators)]
    for key in tree.nodes.keys():
        if key not in node_keys:
            tree.remove_node(key)
    return tree


def decorate_nodes(tree, decs):
    """
    Transform nodes in a tree using decorators.

    :param tree: The tree to transform.
    :param decs: A list of decorators. See the `decorators` function for examples.
    :return: A new tree with the nodes transformed by the decorators.
    """
    for node in tree.nodes.values():
        result = {}
        for dec in decs:
            result.update(dec(node))
        node.payload.update(result)

    return tree


def transform_nodes(tree, fn):
    """
    Transform nodes in a tree using function `fn`.

    :param tree: The tree to transform.
    :param fn: A function that takes in a node and returns a new node.
    :return: A new tree with the nodes transformed by the decorators.
    """
    for key, value in tree.nodes.items():
        tree.nodes[key] = fn(value)
    return tree
