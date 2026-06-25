"""
Composable transformation system for trees.

One function-style Transformer that composes with >>.  Factory functions
return Transformer instances; they work on Node or Tree (duck-typed).
"""

from typing import Any, Callable, Optional, Union, List, Dict, TypeVar

from ._utils import make_predicate as _make_predicate_fn

T = TypeVar('T')


class Transformer:
    """A composable tree operation: callable, composes with >>."""

    __slots__ = ('_fn', '_label')

    def __init__(self, fn: Callable[[Any], Any], label: str = 'transformer'):
        self._fn = fn
        self._label = label

    def __call__(self, tree: Any) -> Any:
        return self._fn(tree)

    def __rshift__(self, other: 'Transformer') -> 'Transformer':
        """Sequential composition: (a >> b)(x) == b(a(x))."""
        nxt = other if isinstance(other, Transformer) else Transformer(
            other, getattr(other, '__name__', 'fn')
        )
        label = f'{self._label} >> {nxt._label}'
        # Capture self and nxt by value to avoid late-binding issues
        _self = self
        _nxt = nxt

        def _composed(t):
            return _nxt(_self(t))

        return Transformer(_composed, label)

    def repeat(self, times: int) -> 'Transformer':
        """Apply this transformer N times."""
        _self = self

        def _run(t):
            for _ in range(times):
                t = _self(t)
            return t

        return Transformer(_run, f'{self._label}.repeat({times})')

    def when(
        self,
        condition: Callable[[Any], bool],
        else_: Optional[Callable[[Any], Any]] = None
    ) -> 'Transformer':
        """Apply this transformer only when condition(tree) is true."""
        _self = self

        def _run(t):
            if condition(t):
                return _self(t)
            return else_(t) if else_ is not None else t

        return Transformer(_run, f'{self._label}.when(...)')

    def __repr__(self) -> str:
        return f'Transformer({self._label!r})'


# Lawful identity element for >>
identity = Transformer(lambda t: t, 'identity')


# ---------------------------------------------------------------------------
# Internal helpers for normalize / annotate
# ---------------------------------------------------------------------------

def _normalize_node_factory(
    sort_children: bool = True,
    sort_key: Optional[Callable] = None,
    clean_attrs: bool = False,
    allowed_attrs: Optional[List[str]] = None
) -> Callable:
    from .node import Node

    _sort_key = sort_key if sort_key is not None else (lambda n: n.name)

    def normalize_node(node: Node) -> Node:
        # Clean attributes if needed
        if clean_attrs:
            if allowed_attrs:
                new_attrs = {k: v for k, v in node.attrs.items() if k in allowed_attrs}
                node = Node(node.name, *node.children, attrs=new_attrs)
            else:
                node = Node(node.name, *node.children)

        # Sort children if needed
        if sort_children and node.children:
            sorted_children = sorted(node.children, key=_sort_key)
            node = node.with_children(*sorted_children)

        return node

    return normalize_node


def _annotate_node_factory(
    selector: Optional[Any],
    annotations: Dict[str, Any]
) -> Callable:
    predicate = _make_predicate_fn(selector) if selector is not None else None

    def annotate_node(node):
        if predicate is None or predicate(node):
            computed = {
                key: value(node) if callable(value) else value
                for key, value in annotations.items()
            }
            return node.with_attrs(**computed)
        return node

    return annotate_node


# ---------------------------------------------------------------------------
# Factory functions (return Transformer; duck-typed on Node or Tree)
# ---------------------------------------------------------------------------

def _adapt_map_fn(fn: Callable) -> Callable:
    """
    Wrap *fn* so it is safe for strict Node.map (Node -> Node only).

    Tree.map already handles dict/None returns; Node.map is strict.  By
    adapting fn here, map_() works uniformly for both callers:

    - None return  -> keep node unchanged
    - dict return  -> merge attrs onto the node (same as Tree.map behaviour)
    - Node return  -> use as-is

    This makes the dict-shorthand pattern work with bare Node callers too.
    """
    from .node import Node as _Node

    def _adapted(node: _Node) -> _Node:
        result = fn(node)
        if result is None:
            return node
        if isinstance(result, dict):
            return node.with_attrs(**result)
        return result  # assumed Node

    return _adapted


def map_(fn: Callable) -> Transformer:
    """
    Create a transformer that maps fn over all nodes.

    fn may return a Node, a dict of attribute updates, or None (keep
    unchanged).  The transformer works identically on bare Node and Tree
    inputs (duck-typed).
    """
    _fn = _adapt_map_fn(fn)
    return Transformer(lambda t: t.map(_fn), f'map_({getattr(fn, "__name__", "fn")})')


def filter_(predicate: Callable) -> Transformer:
    """Create a transformer that filters nodes by predicate or Selector."""
    return Transformer(
        lambda t: t.filter(predicate),
        f'filter_({getattr(predicate, "__name__", "pred")})'
    )


def prune(selector: Any) -> Transformer:
    """Create a transformer that removes nodes matching selector."""
    return Transformer(
        lambda t: t.prune(selector),
        f'prune({getattr(selector, "__name__", repr(selector))})'
    )


def graft(
    selector: Any,
    subtree: Any
) -> Transformer:
    """
    Create a transformer that grafts subtree onto nodes matching selector.

    If subtree is callable (and not a Node/Tree), it is treated as a
    dynamic-subtree factory: each matching node receives a child produced
    by subtree(node).
    """
    from .node import Node

    if callable(subtree) and not isinstance(subtree, Node) and not hasattr(subtree, 'root'):
        _pred = _make_predicate_fn(selector)
        _make_subtree = subtree

        def _dynamic_graft(t):
            def add_dynamic(node):
                if _pred(node):
                    return node.with_child(_make_subtree(node))
                return node

            # For Tree, map via the Tree wrapper; for Node, map directly.
            if hasattr(t, 'root'):
                from .tree import Tree
                return Tree(t.root.map(add_dynamic))
            else:
                return t.map(add_dynamic)

        return Transformer(_dynamic_graft, f'graft(..., dynamic)')
    else:
        return Transformer(
            lambda t: t.graft(selector, subtree),
            f'graft(..., {getattr(subtree, "name", repr(subtree))})'
        )


def flatten(max_depth: Optional[int] = None) -> Transformer:
    """Create a transformer that flattens the tree to max_depth."""
    return Transformer(
        lambda t: t.flatten(max_depth),
        f'flatten(max_depth={max_depth!r})'
    )


def normalize(
    sort_children: bool = True,
    sort_key: Optional[Callable] = None,
    clean_attrs: bool = False,
    allowed_attrs: Optional[List[str]] = None
) -> Transformer:
    """
    Create a transformer that normalizes tree structure.

    Options:
        sort_children: Sort children alphabetically by name (default True).
        sort_key: Custom sort key callable (default: lambda n: n.name).
        clean_attrs: Remove attributes not in allowed_attrs (default False).
        allowed_attrs: Attribute names to keep when clean_attrs=True.
    """
    _fn = _normalize_node_factory(
        sort_children=sort_children,
        sort_key=sort_key,
        clean_attrs=clean_attrs,
        allowed_attrs=allowed_attrs,
    )
    return Transformer(lambda t: t.map(_fn), f'normalize(sort={sort_children}, clean={clean_attrs})')


def annotate(
    selector: Optional[Any] = None,
    **annotations: Any
) -> Transformer:
    """
    Create a transformer that adds annotations to nodes.

    Args:
        selector: If provided, only annotate matching nodes.
        **annotations: Key-value pairs; values may be callables node -> val.
    """
    _fn = _annotate_node_factory(selector, annotations)
    return Transformer(lambda t: t.map(_fn), 'annotate')


def reduce_(fn: Callable, initial: Any, order: str = 'preorder') -> Transformer:
    """Create a transformer that reduces the tree to a single value."""
    return Transformer(
        lambda t: t.reduce(fn, initial, order),
        f'reduce_({getattr(fn, "__name__", "fn")}, order={order!r})'
    )


def fold(fn: Callable) -> Transformer:
    """Create a transformer that folds the tree bottom-up."""
    return Transformer(
        lambda t: t.fold(fn),
        f'fold({getattr(fn, "__name__", "fn")})'
    )


def extract(
    extractor: Callable,
    selector: Optional[Any] = None
) -> Transformer:
    """
    Create a transformer that extracts values from nodes.

    Returns a list of extractor(node) for each matching node.
    """
    if selector is not None:
        return Transformer(
            lambda t: [extractor(n) for n in t.find_all(selector)],
            f'extract({getattr(extractor, "__name__", "fn")}, sel)'
        )
    else:
        return Transformer(
            lambda t: [extractor(n) for n in t.nodes()],
            f'extract({getattr(extractor, "__name__", "fn")})'
        )


def to_dict(children_key: str = 'children') -> Transformer:
    """Create a transformer that converts the tree to a nested dict."""
    return Transformer(
        lambda t: t.to_dict(children_key),
        f'to_dict(children_key={children_key!r})'
    )


def to_paths(delimiter: str = '/', to_leaves_only: bool = True) -> Transformer:
    """Create a transformer that returns all paths in the tree."""
    return Transformer(
        lambda t: t.paths(to_leaves_only=to_leaves_only, delimiter=delimiter),
        f'to_paths(delimiter={delimiter!r})'
    )
