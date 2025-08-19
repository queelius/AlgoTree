"""
Fluent API for tree construction and manipulation.
"""
from typing import Optional, Any, List, Callable, Union
from .node import Node


class TreeBuilder:
    """
    Fluent API for building trees with method chaining.
    
    Example:
        tree = (TreeBuilder()
            .root("company", type="corporation")
            .child("engineering", head="Alice")
                .child("frontend", team_size=5)
                .sibling("backend", team_size=8)
                .up()
            .sibling("sales", head="Bob")
            .build())
    """
    
    def __init__(self):
        """Initialize a new tree builder."""
        self._root: Optional[Node] = None
        self._current: Optional[Node] = None
        self._stack: List[Node] = []
    
    def root(self, name: str, **payload) -> 'TreeBuilder':
        """
        Create the root node.
        
        Args:
            name: Name for the root node.
            **payload: Data for the root node.
            
        Returns:
            Self for method chaining.
        """
        self._root = Node(name=name, **payload)
        self._current = self._root
        return self
    
    def child(self, name: str, **payload) -> 'TreeBuilder':
        """
        Add a child to the current node and move to it.
        
        Args:
            name: Name for the child node.
            **payload: Data for the child node.
            
        Returns:
            Self for method chaining.
        """
        if self._current is None:
            raise ValueError("No current node. Call root() first.")
        
        self._stack.append(self._current)
        child = self._current.add_child(name=name, **payload)
        self._current = child
        return self
    
    def sibling(self, name: str, **payload) -> 'TreeBuilder':
        """
        Add a sibling to the current node.
        
        Args:
            name: Name for the sibling node.
            **payload: Data for the sibling node.
            
        Returns:
            Self for method chaining.
        """
        if self._current is None:
            raise ValueError("No current node. Call root() first.")
        
        if self._current.parent is None:
            raise ValueError("Cannot add sibling to root node.")
        
        sibling = self._current.parent.add_child(name=name, **payload)
        self._current = sibling
        return self
    
    def up(self, levels: int = 1) -> 'TreeBuilder':
        """
        Move up in the tree by specified levels.
        
        Args:
            levels: Number of levels to move up. Default is 1.
            
        Returns:
            Self for method chaining.
        """
        for _ in range(levels):
            if self._stack:
                self._current = self._stack.pop()
            elif self._current and self._current.parent:
                self._current = self._current.parent
            else:
                break
        return self
    
    def to_root(self) -> 'TreeBuilder':
        """
        Move to the root node.
        
        Returns:
            Self for method chaining.
        """
        self._current = self._root
        self._stack.clear()
        return self
    
    def build(self) -> Node:
        """
        Build and return the tree.
        
        Returns:
            The root node of the constructed tree.
        """
        if self._root is None:
            raise ValueError("No tree to build. Call root() first.")
        return self._root


class FluentNode:
    """
    Wrapper for Node that provides fluent API for tree operations.
    
    Example:
        result = (FluentNode(tree)
            .filter(lambda n: n.level <= 2)
            .map(lambda n: n.payload.get('size', 0))
            .where(lambda n: n > 5)
            .to_list())
    """
    
    def __init__(self, node: Union[Node, List[Node]]):
        """
        Initialize fluent wrapper.
        
        Args:
            node: Single node or list of nodes to operate on.
        """
        if isinstance(node, Node):
            self._nodes = [node]
        else:
            self._nodes = list(node)
    
    def filter(self, predicate: Callable[[Node], bool]) -> 'FluentNode':
        """
        Filter nodes by predicate.
        
        Args:
            predicate: Function that returns True for nodes to keep.
            
        Returns:
            New FluentNode with filtered nodes.
        """
        result = []
        for node in self._nodes:
            result.extend(node.find_all(predicate))
        return FluentNode(result)
    
    def where(self, predicate: Callable[[Node], bool]) -> 'FluentNode':
        """
        Filter current nodes by predicate (alias for filter on current set).
        
        Args:
            predicate: Function that returns True for nodes to keep.
            
        Returns:
            New FluentNode with filtered nodes.
        """
        result = [node for node in self._nodes if predicate(node)]
        return FluentNode(result)
    
    def map(self, transform: Callable[[Node], Any]) -> 'FluentNode':
        """
        Transform each node's payload.
        
        Args:
            transform: Function to transform each node.
            
        Returns:
            Self for method chaining.
        """
        for node in self._nodes:
            for n in node.traverse_preorder():
                result = transform(n)
                if isinstance(result, dict):
                    n.payload.update(result)
                elif result is not None:
                    n.payload['_mapped'] = result
        return self
    
    def children(self) -> 'FluentNode':
        """
        Get all children of current nodes.
        
        Returns:
            New FluentNode with all children.
        """
        result = []
        for node in self._nodes:
            result.extend(node.children)
        return FluentNode(result)
    
    def descendants(self) -> 'FluentNode':
        """
        Get all descendants of current nodes.
        
        Returns:
            New FluentNode with all descendants.
        """
        result = []
        for node in self._nodes:
            result.extend(list(node.traverse_preorder())[1:])  # Skip self
        return FluentNode(result)
    
    def leaves(self) -> 'FluentNode':
        """
        Get all leaf nodes from current nodes.
        
        Returns:
            New FluentNode with leaf nodes only.
        """
        result = []
        for node in self._nodes:
            result.extend(n for n in node.traverse_preorder() if n.is_leaf)
        return FluentNode(result)
    
    def sort(self, key: Optional[Callable[[Node], Any]] = None, reverse: bool = False) -> 'FluentNode':
        """
        Sort children of each node.
        
        Args:
            key: Function to extract sort key from each node.
            reverse: Whether to sort in reverse order.
            
        Returns:
            Self for method chaining.
        """
        for node in self._nodes:
            if key:
                node.children.sort(key=key, reverse=reverse)
            else:
                node.children.sort(key=lambda n: n.name, reverse=reverse)
        return self
    
    def prune(self, predicate: Callable[[Node], bool]) -> 'FluentNode':
        """
        Remove nodes matching predicate.
        
        Args:
            predicate: Function that returns True for nodes to remove.
            
        Returns:
            Self for method chaining.
        """
        def prune_recursive(node):
            # Process children first (bottom-up)
            children_to_remove = []
            for child in node.children:
                if predicate(child):
                    children_to_remove.append(child)
                else:
                    prune_recursive(child)
            
            for child in children_to_remove:
                node.remove_child(child)
        
        for node in self._nodes:
            prune_recursive(node)
        
        return self
    
    def each(self, action: Callable[[Node], None]) -> 'FluentNode':
        """
        Execute an action on each node.
        
        Args:
            action: Function to execute on each node.
            
        Returns:
            Self for method chaining.
        """
        for node in self._nodes:
            for n in node.traverse_preorder():
                action(n)
        return self
    
    def to_list(self) -> List[Node]:
        """
        Get list of current nodes.
        
        Returns:
            List of nodes.
        """
        return self._nodes
    
    def to_dict(self) -> Union[dict, List[dict]]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary or list of dictionaries.
        """
        if len(self._nodes) == 1:
            return self._nodes[0].to_dict()
        return [node.to_dict() for node in self._nodes]
    
    def match(self, pattern: Union[str, 'Pattern', dict]) -> 'FluentNode':
        """
        Find nodes matching a pattern.
        
        Args:
            pattern: Pattern to match (string, Pattern object, or dict)
            
        Returns:
            New FluentNode with matching nodes.
        """
        # Import here to avoid circular dependency
        from .pattern_matcher import Pattern, PatternMatcher
        
        if isinstance(pattern, str):
            pattern = Pattern.from_string(pattern)
        elif isinstance(pattern, dict):
            pattern = Pattern.from_dict(pattern)
        
        matcher = PatternMatcher()
        result = []
        for node in self._nodes:
            result.extend(matcher.find_all(node, pattern))
        
        return FluentNode(result)
    
    def replace_matches(self, pattern: Union[str, 'Pattern', dict], 
                       replacement: Union[Node, Callable[[Node], Node]]) -> 'FluentNode':
        """
        Replace nodes matching a pattern.
        
        Args:
            pattern: Pattern to match
            replacement: Node or function to generate replacement
            
        Returns:
            Self for method chaining.
        """
        # Import here to avoid circular dependency
        from .pattern_matcher import Pattern, PatternMatcher
        
        if isinstance(pattern, str):
            pattern = Pattern.from_string(pattern)
        elif isinstance(pattern, dict):
            pattern = Pattern.from_dict(pattern)
        
        matcher = PatternMatcher()
        for node in self._nodes:
            matcher.replace(node, pattern, replacement)
        
        return self
    
    def first(self) -> Optional[Node]:
        """
        Get first node or None.
        
        Returns:
            First node or None if empty.
        """
        return self._nodes[0] if self._nodes else None
    
    def count(self) -> int:
        """
        Get count of current nodes.
        
        Returns:
            Number of nodes.
        """
        return len(self._nodes)