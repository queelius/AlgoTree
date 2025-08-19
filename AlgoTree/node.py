"""
Modern node implementation using proper classes instead of dict inheritance.
"""
from typing import Any, Optional, List, Dict, Iterator, Callable
from uuid import uuid4


class Node:
    """
    A tree node with proper attributes instead of dict inheritance.
    
    This class represents a single node in a tree structure with:
    - A unique name/identifier
    - Optional parent reference
    - List of children
    - Arbitrary payload data
    """
    
    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional['Node'] = None,
        **payload
    ):
        """
        Initialize a node.
        
        Args:
            name: Unique identifier for the node. If None, generates a UUID.
            parent: Parent node reference. If provided, adds this node to parent's children.
            **payload: Arbitrary key-value pairs to store as node data.
        """
        self.name = name if name is not None else str(uuid4())
        self._parent: Optional[Node] = None
        self.children: List[Node] = []
        self.payload: Dict[str, Any] = payload
        
        # Set parent (which also updates parent's children list)
        if parent is not None:
            self.parent = parent
    
    @property
    def parent(self) -> Optional['Node']:
        """Get the parent node."""
        return self._parent
    
    @parent.setter
    def parent(self, new_parent: Optional['Node']):
        """
        Set the parent node, updating both old and new parent's children lists.
        """
        # Remove from old parent's children
        if self._parent is not None:
            self._parent.children.remove(self)
        
        # Set new parent
        self._parent = new_parent
        
        # Add to new parent's children
        if new_parent is not None:
            if self not in new_parent.children:
                new_parent.children.append(self)
    
    @property
    def root(self) -> 'Node':
        """Get the root node of the tree."""
        node = self
        while node.parent is not None:
            node = node.parent
        return node
    
    @property
    def level(self) -> int:
        """Get the level (depth) of this node in the tree."""
        level = 0
        node = self.parent
        while node is not None:
            level += 1
            node = node.parent
        return level
    
    @property
    def is_root(self) -> bool:
        """Check if this is a root node."""
        return self.parent is None
    
    @property
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return len(self.children) == 0
    
    @property
    def siblings(self) -> List['Node']:
        """Get list of sibling nodes."""
        if self.parent is None:
            return []
        return [child for child in self.parent.children if child != self]
    
    def add_child(self, name: Optional[str] = None, **payload) -> 'Node':
        """
        Add a child node.
        
        Args:
            name: Name for the child node.
            **payload: Data for the child node.
            
        Returns:
            The newly created child node.
        """
        return Node(name=name, parent=self, **payload)
    
    def remove_child(self, child: 'Node') -> None:
        """Remove a child node."""
        if child in self.children:
            child._parent = None
            self.children.remove(child)
    
    def traverse_preorder(self) -> Iterator['Node']:
        """Traverse tree in preorder (parent before children)."""
        yield self
        for child in self.children:
            yield from child.traverse_preorder()
    
    def traverse_postorder(self) -> Iterator['Node']:
        """Traverse tree in postorder (children before parent)."""
        for child in self.children:
            yield from child.traverse_postorder()
        yield self
    
    def traverse_levelorder(self) -> Iterator['Node']:
        """Traverse tree in level order (breadth-first)."""
        queue = [self]
        while queue:
            node = queue.pop(0)
            yield node
            queue.extend(node.children)
    
    def find(self, predicate: Callable[['Node'], bool]) -> Optional['Node']:
        """
        Find first node matching predicate.
        
        Args:
            predicate: Function that returns True for matching nodes.
            
        Returns:
            First matching node or None.
        """
        for node in self.traverse_preorder():
            if predicate(node):
                return node
        return None
    
    def find_all(self, predicate: Callable[['Node'], bool]) -> List['Node']:
        """
        Find all nodes matching predicate.
        
        Args:
            predicate: Function that returns True for matching nodes.
            
        Returns:
            List of matching nodes.
        """
        return [node for node in self.traverse_preorder() if predicate(node)]
    
    def get_path(self) -> List['Node']:
        """Get path from root to this node."""
        path = []
        node = self
        while node is not None:
            path.append(node)
            node = node.parent
        return list(reversed(path))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tree to nested dictionary representation.
        
        Returns:
            Dictionary with node data and nested children.
        """
        result = {
            'name': self.name,
            **self.payload
        }
        if self.children:
            result['children'] = [child.to_dict() for child in self.children]
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], parent: Optional['Node'] = None) -> 'Node':
        """
        Create tree from nested dictionary representation.
        
        Args:
            data: Dictionary with node data and optional 'children' key.
            parent: Parent node for the created tree.
            
        Returns:
            Root node of created tree.
        """
        children_data = data.pop('children', [])
        name = data.pop('name', None)
        
        node = cls(name=name, parent=parent, **data)
        
        for child_data in children_data:
            cls.from_dict(child_data, parent=node)
        
        return node
    
    def clone(self) -> 'Node':
        """Create a deep copy of this node and its subtree."""
        return self.from_dict(self.to_dict())
    
    def __repr__(self) -> str:
        return f"Node(name={self.name!r}, payload={self.payload!r}, children={len(self.children)})"
    
    def __str__(self) -> str:
        """Return a simple string representation."""
        return self.name