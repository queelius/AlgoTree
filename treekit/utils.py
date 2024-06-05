from collections import deque
from typing import Any, Callable, Deque, List, Tuple, Type


def visit(
    node: Any, func: Callable[[Any], bool], order: str = "post", **kwargs
) -> bool:
    """
    Visit the nodes in the tree rooted at `node` in a pre-order or post-order
    traversal. The procedure `proc` should have a side-effect you want to
    achieve, such as printing the node or mutating the node in some way.

    If `func` returns True, the traversal will stop and the traversal will
    return True immediately. Otherwise, it will return False after traversing
    all nodes.

    Requirement:

    - This function requires that the node has a `children` property that is
      iterable.

    :param node: The root node to start the traversal.
    :param func: The function to call on each node. The function should take a
                 single argument, the node. It should have some side-effect
                 you want to achieve. See `map` if you want to return a new
                 node to rewrite the sub-tree rooted at `node`.
    :param order: The order of traversal (`pre`, `post`, or `level`).
    :param kwargs: Additional keyword arguments to pass to `func`.
    :raises ValueError: If the order is not valid.
    :raises TypeError: If func is not callable.
    :raises AttributeError: If the node does not have a 'children'.
    """

    if not callable(func):
        raise TypeError("func must be callable")

    if order not in ("pre", "post", "level"):
        raise ValueError(f"Invalid order: {order}")

    if not hasattr(node, "children"):
        raise AttributeError("node must have a 'children' property")

    if order == "level":
        return breadth_first(node, func, **kwargs)

    s = deque([node])
    while s:
        node = s.pop()
        if order == "pre":
            if func(node, **kwargs):
                return True

        s.extend(reversed(node.children))
        if order == "post":
            if func(node, **kwargs):
                return True

    # if order == 'pre':
    #     if func(node, **kwargs):
    #         return True

    # # Traverse children and apply `func` recursively
    # for child in node.children:
    #     if visit(child, func, order, **kwargs):
    #         return True

    # if order == 'post':
    #     if func(node, **kwargs):
    #         return True

    return False


def map(node: Any, func: Callable[[Any], Any], order: str = "post", **kwargs) -> Any:
    """
    Map a function over the nodes in the tree rooted at `node`. It is a map
    operation over trees. In particular, the function `func`, of type

        func : Node -> Node,

    is called on each node in pre or post order traversal. The function should
    return a new node. The tree rooted at `node` will be replaced with the tree
    rooted at the new node. The order of traversal can be specified as 'pre' or
    'post'.

    Requirement:

    - This function requires that the node has a `children` property that is
      iterable and assignable, e.g., `node.children = [child1, child2, ...]`.

    :param node: The root node to start the traversal.
    :param func: The function to call on each node. The function should take a
                 single argument, the node, and return a new node (or
                 have some other side effect you want to achieve).
    :param order: The order of traversal (pre or post).
    :param kwargs: Additional keyword arguments to pass to `func`.
    :raises ValueError: If the order is not 'pre' or 'post'.
    :raises TypeError: If func is not callable.
    :raises AttributeError: If the node does not have a 'children'.
    :return: The modified node. If `func` returns a new node, the tree rooted
             at `node` will be replaced with the tree rooted at the new node.
    """

    if not callable(func):
        raise TypeError("func must be callable")

    if order not in ("pre", "post"):
        raise ValueError(f"Invalid order: {order}")

    if not hasattr(node, "children"):
        raise AttributeError("node must have a 'children' property")

    if order == "pre":
        node = func(node, **kwargs)

    # Traverse children and apply `func` recursively
    node.children = [map(c, func, order, **kwargs) for c in node.children]

    if order == "post":
        node = func(node, **kwargs)

    return node


def descendants(node) -> List:
    """
    Get the descendants of a node.

    :param node: The root node.
    :return: List of descendant nodes.
    """
    results = []
    visit(node, lambda n: results.append(n) or False, order="pre")
    return results


def ancestors(node) -> List:
    """
    Get the ancestors of a node.

    :param node: The root node.
    :return: List of ancestor nodes.
    """

    def _ancestors(n):
        nonlocal anc
        if not is_root(n):
            anc.append(n.parent)
            _ancestors(n.parent)

    anc = []
    _ancestors(node)
    return anc


def siblings(node) -> List:
    """
    Get the siblings of a node.

    :param node: The root node.
    :return: List of sibling nodes.
    """
    return [] if is_root(node) else [c for c in node.parent.children if c != node]


def leaves(node) -> List:
    """
    Get the leaves of a node.

    :param node: The root node.
    :return: List of leaf nodes.
    """
    results = []
    visit(
        node,
        lambda n: results.append(n) or False if not n.children else False,
        order="post",
    )
    return results


def height(node) -> int:
    """
    Get the height of a node.

    :param node: The root node.
    :return: The height of the node.
    """
    return 0 if is_leaf(node) else 1 + max(height(c) for c in node.children)


def depth(node) -> int:
    """
    Get the depth of a node.

    :param node: The root node.
    :return: The depth of the node.
    """
    return 0 if is_root(node) else 1 + depth(node.parent)


def is_root(node) -> bool:
    """
    Check if a node is a root node.

    :param node: The node to check.
    :return: True if the node is a root node, False otherwise.
    """
    return node.parent is None


def is_leaf(node) -> bool:
    """
    Check if a node is a leaf node.

    :param node: The node to check.
    :return: True if the node is a leaf node, False otherwise.
    """
    return not is_internal(node)


def is_internal(node) -> bool:
    """
    Check if a node is an internal node.

    :param node: The node to check.
    :return: True if the node is an internal node, False otherwise.
    """
    return len(node.children) > 0


def is_ancestor(node, other) -> bool:
    """
    Check if a node is an ancestor of another node.

    :param node: The node to check.
    :param other: The other node.
    :return: True if the node is an ancestor of the other node, False otherwise.
    """
    return other in descendants(node)


def is_descendant(node, other) -> bool:
    """
    Check if a node is a descendant of another node.

    :param node: The node to check.
    :param other: The other node.
    :return: True if the node is a descendant of the other node, False otherwise.
    """
    return node in descendants(other)


def is_sibling(node, other) -> bool:
    """
    Check if a node is a sibling of another node.

    :param node: The node to check.
    :param other: The other node.
    :return: True if the node is a sibling of the other node, False otherwise.
    """
    return node in siblings(other)


def breadth_first(node: Any, func: Callable[[Any], bool], **kwargs) -> bool:
    """
    Traverse the tree in breadth-first order. The function `func` is called on
    each node and level. The function should have a side-effect you want to
    achieve, and if it returns True, the traversal will stop. The keyword
    arguments are passed to `func`.

    If `func` returns True, the traversal will stop and the traversal will
    return True immediately. Otherwise, it will return False after traversing
    all nodes. This is useful if you want to find a node that satisfies a
    condition, and you want to stop the traversal as soon as you find it.

    Requirement:

    - This function requires that the node has a `children` property that is
      iterable.

    - The function `func` should have the signature:

        `func(node: Any, **kwargs) -> bool`

    :param node: The root node.
    :param func: The function to call on each node and any additional keyword
                 arguments. We augment kwargs with a level key, too, which
                 specifies the level of the node in the tree.
    :param kwargs: Additional keyword arguments to pass to `func`.
    :raises TypeError: If func is not callable.
    :raises AttributeError: If the node does not have a 'children'.
    :return: None
    """
    if not callable(func):
        raise TypeError("func must be callable")

    if not hasattr(node, "children"):
        raise AttributeError("node must have a 'children' property")

    q: Deque[Tuple[Any, int]] = deque([(node, 0)])
    while q:
        cur, lvl = q.popleft()
        kwargs["level"] = lvl
        if func(cur, **kwargs):
            return True
        q.extend((child, lvl + 1) for child in cur.children)
    return False


def find_nodes(node: Any, pred: Callable[[Any], bool], **kwargs) -> List[Any]:
    """
    Find nodes that satisfy a predicate.

    :param pred: The predicate function.
    :param kwargs: Additional keyword arguments to pass to `pred`.
    :return: List of nodes that satisfy the predicate.
    """
    nodes: List[Any] = []
    visit(
        node,
        lambda n, **kwargs: nodes.append(n) or False if pred(n, **kwargs) else False,
        order="pre",
    )
    return nodes


def find_node(node: Any, pred: Callable[[Any], bool], **kwargs) -> Any:
    """
    Find closest node that satisfies a predicate. The predicate function should
    return True if the node satisfies the condition. It can also accept
    any additional keyword arguments, which are passed to the predicate. Note
    that we also augment the keyword arguments with a level key, which specifies
    the level of the node in the tree, so you can use this information in your
    predicate function.

    :param pred: The predicate function which returns True if the node satisfies
                 the condition.
    :param kwargs: Additional keyword arguments to pass to `pred`.
    :return: The node that satisfies the predicate.
    """
    result = None

    def _pred(n, **kwargs):
        nonlocal result
        if pred(n, **kwargs):
            result = n
            return True
        else:
            return False

    breadth_first(node, _pred, **kwargs)
    return result
