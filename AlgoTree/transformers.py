"""
Composable transformation system for trees.

This module provides a clean, functional approach to tree transformations
that can be composed using operators like >> and |.
"""

from typing import Any, Callable, Optional, Union, List, Dict, TypeVar, Generic
from abc import ABC, abstractmethod
from .tree import Tree
from .node import Node
from .selectors import Selector

T = TypeVar('T')
S = TypeVar('S')


class Transformer(ABC, Generic[T, S]):
    """
    Base class for composable tree transformations.

    Transformers can be composed using operators:
    - >> or | for sequential composition (pipeline)
    - & for parallel composition (apply both, merge results)
    """

    @abstractmethod
    def __call__(self, tree: T) -> S:
        """Apply transformation to tree."""
        pass

    def __rshift__(self, other: 'Transformer[S, Any]') -> 'Pipeline':
        """Compose transformers with >> operator."""
        return Pipeline(self, other)

    def __or__(self, other: 'Transformer[S, Any]') -> 'Pipeline':
        """Alternative composition syntax with | operator."""
        return Pipeline(self, other)

    def __and__(self, other: 'Transformer[T, S]') -> 'ParallelTransformer[T, S]':
        """Parallel composition - apply both and merge."""
        return ParallelTransformer(self, other)

    def repeat(self, times: int) -> 'RepeatTransformer[T]':
        """Apply transformer N times."""
        return RepeatTransformer(self, times)

    def when(self, condition: Callable[[T], bool]) -> 'ConditionalTransformer[T, S]':
        """Apply transformer only if condition is met."""
        return ConditionalTransformer(self, condition)

    def debug(self, name: str = "", callback: Optional[Callable[[Any], None]] = None) -> 'DebugTransformer':
        """Add debugging to transformer."""
        return DebugTransformer(self, name, callback)


# Tree -> Tree transformers (closed transformations)

class TreeTransformer(Transformer[Tree, Tree]):
    """Base class for tree-to-tree transformations."""
    pass


class MapTransformer(TreeTransformer):
    """Map function over all nodes."""

    def __init__(self, fn: Callable[[Node], Union[Node, Dict[str, Any], None]]):
        self.fn = fn

    def __call__(self, tree: Tree) -> Tree:
        return tree.map(self.fn)

    def __repr__(self) -> str:
        return f"MapTransformer({self.fn})"


class FilterTransformer(TreeTransformer):
    """Filter nodes by predicate."""

    def __init__(self, predicate: Union[Selector, Callable[[Node], bool]]):
        if isinstance(predicate, Selector):
            self.predicate = predicate.matches
        else:
            self.predicate = predicate

    def __call__(self, tree: Tree) -> Tree:
        return tree.filter(self.predicate)

    def __repr__(self) -> str:
        return f"FilterTransformer({self.predicate})"


class PruneTransformer(TreeTransformer):
    """Remove nodes matching selector."""

    def __init__(self, selector: Union[Selector, str, Callable[[Node], bool]]):
        self.selector = selector

    def __call__(self, tree: Tree) -> Tree:
        return tree.prune(self.selector)

    def __repr__(self) -> str:
        return f"PruneTransformer({self.selector})"


class GraftTransformer(TreeTransformer):
    """Add subtree to nodes matching selector."""

    def __init__(
        self,
        selector: Union[Selector, str, Callable[[Node], bool]],
        subtree: Union[Node, Tree, Callable[[Node], Node]]
    ):
        self.selector = selector
        self.subtree = subtree

    def __call__(self, tree: Tree) -> Tree:
        if callable(self.subtree):
            # Dynamic subtree based on matched node
            def add_dynamic(node: Node) -> Node:
                if tree._matches(node, self.selector):
                    new_subtree = self.subtree(node)
                    return node.with_child(new_subtree)
                return node
            return Tree(tree.root.map(add_dynamic))
        else:
            return tree.graft(self.selector, self.subtree)

    def __repr__(self) -> str:
        return f"GraftTransformer({self.selector}, {self.subtree})"


class FlattenTransformer(TreeTransformer):
    """Flatten tree to specified depth."""

    def __init__(self, max_depth: Optional[int] = None):
        self.max_depth = max_depth

    def __call__(self, tree: Tree) -> Tree:
        return tree.flatten(self.max_depth)

    def __repr__(self) -> str:
        return f"FlattenTransformer(max_depth={self.max_depth})"


class NormalizeTransformer(TreeTransformer):
    """Normalize tree structure (sort children, clean attributes)."""

    def __init__(
        self,
        sort_children: bool = True,
        sort_key: Optional[Callable[[Node], Any]] = None,
        clean_attrs: bool = False,
        allowed_attrs: Optional[List[str]] = None
    ):
        self.sort_children = sort_children
        self.sort_key = sort_key or (lambda n: n.name)
        self.clean_attrs = clean_attrs
        self.allowed_attrs = allowed_attrs

    def __call__(self, tree: Tree) -> Tree:
        def normalize_node(node: Node) -> Node:
            # Clean attributes if needed
            if self.clean_attrs:
                if self.allowed_attrs:
                    # Keep only allowed attributes
                    new_attrs = {k: v for k, v in node.attrs.items() if k in self.allowed_attrs}
                    node = Node(node.name, *node.children, attrs=new_attrs)
                else:
                    # Remove all attributes
                    node = Node(node.name, *node.children)

            # Sort children if needed
            if self.sort_children and node.children:
                sorted_children = sorted(node.children, key=self.sort_key)
                node = node.with_children(*sorted_children)

            return node

        return Tree(tree.root.map(normalize_node))

    def __repr__(self) -> str:
        return f"NormalizeTransformer(sort={self.sort_children}, clean_attrs={self.clean_attrs})"


class AnnotateTransformer(TreeTransformer):
    """Add annotations to nodes."""

    def __init__(
        self,
        selector: Optional[Union[Selector, str, Callable[[Node], bool]]] = None,
        **annotations
    ):
        self.selector = selector
        self.annotations = annotations

    def __call__(self, tree: Tree) -> Tree:
        def annotate_node(node: Node) -> Node:
            if self.selector is None or tree._matches(node, self.selector):
                # Add annotations
                computed_annotations = {}
                for key, value in self.annotations.items():
                    if callable(value):
                        computed_annotations[key] = value(node)
                    else:
                        computed_annotations[key] = value
                return node.with_attrs(**computed_annotations)
            return node

        return Tree(tree.root.map(annotate_node))

    def __repr__(self) -> str:
        return f"AnnotateTransformer({self.selector}, {self.annotations})"


# Tree -> Any transformers (open transformations)

class Shaper(Transformer[Tree, T], Generic[T]):
    """Base class for tree-to-any transformations."""
    pass


class ReduceShaper(Shaper[T]):
    """Reduce tree to single value."""

    def __init__(
        self,
        fn: Callable[[T, Node], T],
        initial: T,
        order: str = 'preorder'
    ):
        self.fn = fn
        self.initial = initial
        self.order = order

    def __call__(self, tree: Tree) -> T:
        return tree.reduce(self.fn, self.initial, self.order)

    def __repr__(self) -> str:
        return f"ReduceShaper({self.fn}, initial={self.initial})"


class FoldShaper(Shaper[T]):
    """Fold tree bottom-up."""

    def __init__(self, fn: Callable[[Node, List[T]], T]):
        self.fn = fn

    def __call__(self, tree: Tree) -> T:
        return tree.fold(self.fn)

    def __repr__(self) -> str:
        return f"FoldShaper({self.fn})"


class ExtractShaper(Shaper[List[T]]):
    """Extract values from nodes."""

    def __init__(
        self,
        extractor: Callable[[Node], T],
        selector: Optional[Union[Selector, str, Callable[[Node], bool]]] = None
    ):
        self.extractor = extractor
        self.selector = selector

    def __call__(self, tree: Tree) -> List[T]:
        if self.selector:
            nodes = tree.find_all(self.selector)
        else:
            nodes = tree.nodes()

        return [self.extractor(node) for node in nodes]

    def __repr__(self) -> str:
        return f"ExtractShaper({self.extractor}, {self.selector})"


class ToDictShaper(Shaper[Dict[str, Any]]):
    """Convert tree to dictionary."""

    def __init__(self, children_key: str = 'children'):
        self.children_key = children_key

    def __call__(self, tree: Tree) -> Dict[str, Any]:
        return tree.to_dict(self.children_key)

    def __repr__(self) -> str:
        return f"ToDictShaper(children_key={self.children_key!r})"


class ToPathsShaper(Shaper[List[str]]):
    """Convert tree to list of paths."""

    def __init__(self, delimiter: str = '/', to_leaves_only: bool = True):
        self.delimiter = delimiter
        self.to_leaves_only = to_leaves_only

    def __call__(self, tree: Tree) -> List[str]:
        return tree.paths(to_leaves_only=self.to_leaves_only)

    def __repr__(self) -> str:
        return f"ToPathsShaper(delimiter={self.delimiter!r})"


# Composite transformers

class Pipeline(Transformer[Any, Any]):
    """Sequential composition of transformers."""

    def __init__(self, *transformers: Transformer):
        self.transformers = []
        for t in transformers:
            if isinstance(t, Pipeline):
                # Flatten nested pipelines
                self.transformers.extend(t.transformers)
            else:
                self.transformers.append(t)

    def __call__(self, tree: Any) -> Any:
        """Apply all transformations in sequence."""
        result = tree
        for transformer in self.transformers:
            result = transformer(result)
        return result

    def __rshift__(self, other: Transformer) -> 'Pipeline':
        """Add transformer to pipeline."""
        return Pipeline(*self.transformers, other)

    def __or__(self, other: Transformer) -> 'Pipeline':
        """Add transformer to pipeline (alternative syntax)."""
        return Pipeline(*self.transformers, other)

    def partial(self, tree: Any, steps: int) -> Any:
        """Apply only first N steps of pipeline."""
        result = tree
        for transformer in self.transformers[:steps]:
            result = transformer(result)
        return result

    def __repr__(self) -> str:
        return f"Pipeline({' >> '.join(repr(t) for t in self.transformers)})"


class ParallelTransformer(Transformer[T, S], Generic[T, S]):
    """Apply transformers in parallel and merge results."""

    def __init__(self, *transformers: Transformer[T, Tree]):
        self.transformers = transformers

    def __call__(self, tree: T) -> Tree:
        """Apply all transformers and merge results."""
        results = [t(tree) for t in self.transformers]

        # Merge trees (simplified - could be more sophisticated)
        if all(isinstance(r, Tree) for r in results):
            # Merge by combining children
            merged_root = results[0].root
            for result in results[1:]:
                for child in result.root.children:
                    merged_root = merged_root.with_child(child)
            return Tree(merged_root)

        # Return first result if not all trees
        return results[0]

    def __repr__(self) -> str:
        return f"Parallel({' & '.join(repr(t) for t in self.transformers)})"


class RepeatTransformer(Transformer[T, T], Generic[T]):
    """Apply transformer multiple times."""

    def __init__(self, transformer: Transformer[T, T], times: int):
        self.transformer = transformer
        self.times = times

    def __call__(self, tree: T) -> T:
        result = tree
        for _ in range(self.times):
            result = self.transformer(result)
        return result

    def __repr__(self) -> str:
        return f"Repeat({repr(self.transformer)}, times={self.times})"


class ConditionalTransformer(Transformer[T, Union[T, S]], Generic[T, S]):
    """Apply transformer conditionally."""

    def __init__(
        self,
        transformer: Transformer[T, S],
        condition: Callable[[T], bool],
        else_transformer: Optional[Transformer[T, S]] = None
    ):
        self.transformer = transformer
        self.condition = condition
        self.else_transformer = else_transformer

    def __call__(self, tree: T) -> Union[T, S]:
        if self.condition(tree):
            return self.transformer(tree)
        elif self.else_transformer:
            return self.else_transformer(tree)
        else:
            return tree

    def __repr__(self) -> str:
        return f"Conditional({repr(self.transformer)}, if={self.condition})"


class DebugTransformer(Transformer):
    """Transformer wrapper for debugging."""

    def __init__(
        self,
        transformer: Transformer,
        name: str = "",
        callback: Optional[Callable[[Any], None]] = None
    ):
        self.transformer = transformer
        self.name = name
        self.callback = callback or print

    def __call__(self, tree: Any) -> Any:
        if self.name:
            self.callback(f"[{self.name}] Before: {tree}")

        result = self.transformer(tree)

        if self.name:
            self.callback(f"[{self.name}] After: {result}")

        return result

    def __repr__(self) -> str:
        return f"Debug({repr(self.transformer)}, name={self.name!r})"


# Factory functions for common transformers

def map_(fn: Callable[[Node], Union[Node, Dict[str, Any], None]]) -> MapTransformer:
    """Create map transformer."""
    return MapTransformer(fn)


def filter_(predicate: Union[Selector, Callable[[Node], bool]]) -> FilterTransformer:
    """Create filter transformer."""
    return FilterTransformer(predicate)


def prune(selector: Union[Selector, str, Callable[[Node], bool]]) -> PruneTransformer:
    """Create prune transformer."""
    return PruneTransformer(selector)


def graft(
    selector: Union[Selector, str, Callable[[Node], bool]],
    subtree: Union[Node, Tree, Callable[[Node], Node]]
) -> GraftTransformer:
    """Create graft transformer."""
    return GraftTransformer(selector, subtree)


def flatten(max_depth: Optional[int] = None) -> FlattenTransformer:
    """Create flatten transformer."""
    return FlattenTransformer(max_depth)


def normalize(**kwargs) -> NormalizeTransformer:
    """Create normalize transformer."""
    return NormalizeTransformer(**kwargs)


def annotate(
    selector: Optional[Union[Selector, str, Callable[[Node], bool]]] = None,
    **annotations
) -> AnnotateTransformer:
    """Create annotate transformer."""
    return AnnotateTransformer(selector, **annotations)


def reduce_(fn: Callable[[T, Node], T], initial: T, order: str = 'preorder') -> ReduceShaper[T]:
    """Create reduce shaper."""
    return ReduceShaper(fn, initial, order)


def fold(fn: Callable[[Node, List[T]], T]) -> FoldShaper[T]:
    """Create fold shaper."""
    return FoldShaper(fn)


def extract(
    extractor: Callable[[Node], T],
    selector: Optional[Union[Selector, str, Callable[[Node], bool]]] = None
) -> ExtractShaper[T]:
    """Create extract shaper."""
    return ExtractShaper(extractor, selector)


def to_dict(children_key: str = 'children') -> ToDictShaper:
    """Create to-dict shaper."""
    return ToDictShaper(children_key)


def to_paths(delimiter: str = '/', to_leaves_only: bool = True) -> ToPathsShaper:
    """Create to-paths shaper."""
    return ToPathsShaper(delimiter, to_leaves_only)
