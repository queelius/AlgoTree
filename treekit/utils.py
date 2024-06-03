from typing import Callable, Any    

def visit(node,
          func: Callable,
          order: str = 'post',
          **kwargs) -> None:
    """
    Visit the nodes in the tree rooted at `node` in a pre-order or post-order
    traversal. The procedure `proc` should have a side-effect you want to
    achieve, such as printing the node or mutating the node in some way. (See
    `map` if you want to return a new node to rewrite the sub-tree rooted at
    `node`.) The order of traversal can be specified as 'pre' or
    'post'. Pre-order traversal is a top-down traversal where the procedure
    has a side-effect on the parent before the children. Post-order traversal
    is a bottom-up traversal where the procedure has a side-effect on the
    children before the parent. Both have their uses, e.g., pre-order
    traversal is useful for printing the tree in a human-readable format.

    Requirement:

    - This function requires that the node has a `children` property that is
      iterable.

    :param node: The root node to start the traversal.
    :param func: The function to call on each node. The function should take a
                 single argument, the node. It should have some side-effect
                 you want to achieve. See `map` if you want to return a new
                 node to rewrite the sub-tree rooted at `node`.
    :param order: The order of traversal (pre or post).
    :param kwargs: Additional keyword arguments to pass to `func`.
    :raises ValueError: If the order is not 'pre' or 'post'.
    :raises TypeError: If func is not callable.
    """

    if not callable(func):
        raise TypeError("func must be callable")

    if order not in ('pre', 'post'):
        raise ValueError(f"Invalid order: {order}")

    if not hasattr(node, 'children'):
        raise AttributeError("node must have a 'children' property")

    if order == 'pre':
        func(node, **kwargs)

    # Traverse children and apply `func` recursively
    for child in node.children:
        visit(child, func, order, **kwargs)

    if order == 'post':
        func(node, **kwargs)

def map(node,
        func: Callable,
        order: str = 'post',
        **kwargs) -> Any:
    """
    Map a function over the nodes in the tree rooted at `node`. It is a map
    operation over trees. In particular, the function `func`, of type
    
        func : Node -> Node,

    is called on each node in pre or post order traversal. Post-order traversal
    is a bottom-up traversal where the function is called on the children before
    the parent. Pre-order traversal is a top-down traversal where the function is
    called on the parent before the children. Both have their uses. A canonical
    example of post-order traversal is the evaluation of an expression tree. A
    canonical example of pre-order traversal is printing the tree in a human-
    readable format.
    
    While this function can be used to do tasks like tree rewiting systems
    (e.g., rewriting expression trees representing algebraic expressions to
    different but equivalent forms), it is most useful when you want to
    transform the tree in a relatively simple way.

    :param node: The root node to start the traversal.
    :param func: The function to call on each node. The function should take a
                 single argument, the node, and return a new node (or
                 have some other side effect you want to achieve).
    :param order: The order of traversal (pre or post).
    :param kwargs: Additional keyword arguments to pass to `func`.
    :raises ValueError: If the order is not 'pre' or 'post'.
    :raises TypeError: If func is not callable.
    :raises AttributeError: If the node does not have a 'children' property or
                            a 'set_children' method.
    :return: The modified node. If `func` returns a new node, the tree rooted
             at `node` will be replaced with the tree rooted at the new node.
    """

    if not callable(func):
        raise TypeError("func must be callable")

    if order not in ('pre', 'post'):
        raise ValueError(f"Invalid order: {order}")

    if not hasattr(node, 'children'):
        raise AttributeError("node must have a 'children' property")

    if not hasattr(node, 'set_children'):
        raise AttributeError("node must have a 'set_children' method")

    if order == 'pre':
        node = func(node, **kwargs)

    # Traverse children and apply `func` recursively
    node.set_children([map(c, func, order, **kwargs) for c in node.children])

    if order == 'post':
        node = func(node, **kwargs)

    return node
