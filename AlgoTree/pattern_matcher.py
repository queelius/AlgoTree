"""
Tree pattern matching functionality.

This module provides pattern matching capabilities for tree structures,
allowing users to search for specific structural patterns within trees.
"""

from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import re
from .node import Node


class MatchType(Enum):
    """Types of pattern matching."""
    EXACT = "exact"  # Exact structure match
    PARTIAL = "partial"  # Pattern can match part of a subtree
    WILDCARD = "wildcard"  # Some nodes can be wildcards


@dataclass
class Pattern:
    """
    Represents a tree pattern to match against.
    
    Patterns can include:
    - Exact node matches
    - Wildcards (*) that match any single node
    - Deep wildcards (**) that match any subtree
    - Attribute constraints
    """
    name: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    children: List['Pattern'] = field(default_factory=list)
    is_wildcard: bool = False
    is_deep_wildcard: bool = False
    min_children: Optional[int] = None
    max_children: Optional[int] = None
    predicate: Optional[Callable[[Node], bool]] = None
    
    @staticmethod
    def from_string(pattern_str: str) -> 'Pattern':
        """
        Parse a pattern from string notation.
        
        Examples:
            "root"           # Match node named 'root'
            "*"              # Match any single node
            "**"             # Match any subtree
            "node[type=foo]" # Match node with attribute
            "parent(child1, child2)" # Match parent with specific children
            "root.branch.leaf" # Dot notation path
            "app.*.test"     # Dot notation with wildcard
            "root.**.target" # Dot notation with deep wildcard
        """
        pattern_str = pattern_str.strip()
        
        # Import re at the beginning for consistency
        import re
        
        # Check if this is dot notation
        if '.' in pattern_str and '(' not in pattern_str:
            return Pattern._from_dot_notation(pattern_str)
        
        # Handle wildcards
        if pattern_str == '*':
            return Pattern(is_wildcard=True)
        elif pattern_str == '**':
            return Pattern(is_deep_wildcard=True)
        elif pattern_str.startswith('**['):
            # Deep wildcard with attributes
            attrs_match = re.match(r'^\*\*\[([^\]]+)\]$', pattern_str)
            if attrs_match:
                attrs_str = attrs_match.group(1)
                attributes = {}
                predicate = None
                predicates = []
                
                for attr in attrs_str.split(','):
                    attr = attr.strip()
                    if '=' in attr:
                        key, val = attr.split('=', 1)
                        val = val.strip().strip('"\'')
                        # Try to parse value
                        if val.lower() == 'true':
                            val = True
                        elif val.lower() == 'false':
                            val = False
                        else:
                            try:
                                val = int(val)
                            except ValueError:
                                try:
                                    val = float(val)
                                except ValueError:
                                    pass
                        attributes[key.strip()] = val
                    else:
                        # Just attribute name - check for existence
                        key = attr.strip()
                        predicates.append(lambda n, k=key: k in n.payload)
                
                # Combine predicates if any
                if predicates:
                    if attributes:
                        # Both attribute checks and existence checks
                        def combined_predicate(n):
                            # Check attributes match
                            for k, v in attributes.items():
                                if k not in n.payload or n.payload[k] != v:
                                    return False
                            # Check existence
                            for pred in predicates:
                                if not pred(n):
                                    return False
                            return True
                        predicate = combined_predicate
                    else:
                        # Only existence checks
                        if len(predicates) == 1:
                            predicate = predicates[0]
                        else:
                            def all_exist(n):
                                return all(pred(n) for pred in predicates)
                            predicate = all_exist
                    return Pattern(is_deep_wildcard=True, predicate=predicate)
                else:
                    return Pattern(is_deep_wildcard=True, attributes=attributes)
        
        # Parse node with attributes
        # Match pattern like "name[attr1=val1,attr2=val2](children)"
        match = re.match(r'^([^[\(]+)(?:\[([^\]]+)\])?(?:\(([^)]+)\))?$', pattern_str)
        if not match:
            return Pattern(name=pattern_str)
        
        name = match.group(1).strip()
        attrs_str = match.group(2)
        children_str = match.group(3)
        
        # Parse attributes
        attributes = {}
        if attrs_str:
            for attr in attrs_str.split(','):
                if '=' in attr:
                    key, val = attr.split('=', 1)
                    # Try to parse value as int/float/bool
                    val = val.strip()
                    if val.lower() == 'true':
                        val = True
                    elif val.lower() == 'false':
                        val = False
                    else:
                        try:
                            val = int(val)
                        except ValueError:
                            try:
                                val = float(val)
                            except ValueError:
                                val = val.strip('"\'')
                    attributes[key.strip()] = val
        
        # Parse children
        children = []
        if children_str:
            # Simple split by comma (doesn't handle nested parentheses)
            for child_str in children_str.split(','):
                children.append(Pattern.from_string(child_str.strip()))
        
        return Pattern(name=name, attributes=attributes, children=children)
    
    @staticmethod
    def _from_dot_notation(dot_path: str) -> 'Pattern':
        """
        Parse dot notation path into nested pattern.
        
        Examples:
            "root.branch.leaf" -> root with child branch with child leaf
            "app.*.test" -> app with any child with child test
            "root.**.target" -> root with deep wildcard path to target
            "user[type=admin].permissions" -> user with type=admin and child permissions
            "nodes[?(@.size > 10)].data" -> nodes with size > 10 and child data
            "items[*].value" -> all items' value children
            "src.~test_.*.py" -> src with children matching regex test_ pattern
            "files.doc1\\.txt" -> files with child "doc1.txt" (escaped dot)
        """
        parts = []
        current = ""
        bracket_depth = 0
        escape_next = False
        
        # Parse parts carefully, respecting brackets and escaping
        for i, char in enumerate(dot_path):
            if escape_next:
                current += char
                escape_next = False
            elif char == '\\' and i + 1 < len(dot_path) and dot_path[i + 1] == '.':
                # Escape sequence for literal dot
                escape_next = True
            elif char == '[':
                bracket_depth += 1
                current += char
            elif char == ']':
                bracket_depth -= 1
                current += char
            elif char == '.' and bracket_depth == 0:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char
        if current:
            parts.append(current)
        
        def parse_part(part: str) -> 'Pattern':
            """Parse a single part which may include attributes or filters."""
            # Check for wildcard patterns
            if part == '*' or part == '[*]':
                return Pattern(is_wildcard=True)
            elif part == '**':
                return Pattern(is_deep_wildcard=True)
            elif part.startswith('*') and '.' in part:
                # Pattern like *.txt - match nodes ending with .txt
                suffix = part[1:]  # Remove leading *
                return Pattern(predicate=lambda n: n.name.endswith(suffix))
            
            # Check for regex pattern (starts with ~)
            if part.startswith('~'):
                regex_pattern = part[1:]
                # Support flags after pattern: ~pattern~flags
                flags = 0
                if '~' in regex_pattern:
                    regex_pattern, flag_str = regex_pattern.split('~', 1)
                    if 'i' in flag_str:
                        flags |= re.IGNORECASE
                    if 'm' in flag_str:
                        flags |= re.MULTILINE
                compiled = re.compile(regex_pattern, flags)
                return Pattern(
                    predicate=lambda n: compiled.search(n.name) is not None
                )
            
            # Check for fuzzy matching (starts with %)
            if part.startswith('%'):
                from difflib import SequenceMatcher
                fuzzy_pattern = part[1:]
                threshold = 0.8  # Default threshold
                if ':' in fuzzy_pattern:
                    fuzzy_pattern, thresh_str = fuzzy_pattern.split(':', 1)
                    try:
                        threshold = float(thresh_str)
                    except ValueError:
                        pass
                
                def fuzzy_match(node):
                    ratio = SequenceMatcher(None, node.name, fuzzy_pattern).ratio()
                    return ratio >= threshold
                
                return Pattern(predicate=fuzzy_match)
            
            # Check for filter predicate [?(...)]
            filter_match = re.match(r'^([^[]*)\[\?\((.*?)\)\]$', part)
            if filter_match:
                base_name = filter_match.group(1) if filter_match.group(1) else None
                predicate_str = filter_match.group(2)
                
                # Create a predicate function from the filter expression
                # Support @.property notation
                def create_predicate(expr: str):
                    def predicate(node):
                        # Replace @ with node reference
                        # This is simplified - a full implementation would parse properly
                        try:
                            # Support basic comparisons
                            if '@.size' in expr:
                                expr = expr.replace('@.size', str(node.payload.get('size', 0)))
                            if '@.type' in expr:
                                expr = expr.replace('@.type', repr(node.payload.get('type', '')))
                            if '@.name' in expr:
                                expr = expr.replace('@.name', repr(node.name))
                            if '@.children.length' in expr:
                                expr = expr.replace('@.children.length', str(len(node.children)))
                            # Evaluate the expression (simplified, not production-safe)
                            return eval(expr)
                        except:
                            return False
                    return predicate
                
                return Pattern(
                    name=base_name,
                    predicate=create_predicate(predicate_str)
                )
            
            # Check for attribute filter [key=value]
            if '[' in part and ']' in part:
                # Parse attributes
                bracket_start = part.index('[')
                name_part = part[:bracket_start] if bracket_start > 0 else None
                attrs_part = part[bracket_start+1:part.rindex(']')]
                
                # Check for array index [n] or slice [start:stop:step]
                if ':' in attrs_part:
                    # This is a slice selector [start:stop:step]
                    slice_parts = attrs_part.split(':')
                    try:
                        start = int(slice_parts[0]) if slice_parts[0] else None
                        stop = int(slice_parts[1]) if len(slice_parts) > 1 and slice_parts[1] else None
                        step = int(slice_parts[2]) if len(slice_parts) > 2 and slice_parts[2] else None
                        
                        def slice_predicate(node):
                            if not node.parent:
                                return False
                            try:
                                idx = node.parent.children.index(node)
                                indices = range(*slice(start, stop, step).indices(len(node.parent.children)))
                                return idx in indices
                            except ValueError:
                                return False
                        
                        return Pattern(name=name_part, predicate=slice_predicate)
                    except ValueError:
                        pass
                
                elif attrs_part.isdigit() or (attrs_part.startswith('-') and attrs_part[1:].isdigit()):
                    # This is an array index selector (including negative indices)
                    index = int(attrs_part)
                    
                    def index_predicate(node):
                        if not node.parent:
                            return False
                        try:
                            idx = node.parent.children.index(node)
                            total = len(node.parent.children)
                            # Handle negative indices
                            if index < 0:
                                return idx == total + index
                            return idx == index
                        except ValueError:
                            return False
                    
                    return Pattern(name=name_part, predicate=index_predicate)
                
                # Parse key=value attributes
                attributes = {}
                for attr in attrs_part.split(','):
                    if '=' in attr:
                        key, val = attr.split('=', 1)
                        key = key.strip()
                        val = val.strip().strip('"\'')
                        # Try to parse value
                        if val.lower() == 'true':
                            val = True
                        elif val.lower() == 'false':
                            val = False
                        else:
                            try:
                                val = int(val)
                            except ValueError:
                                try:
                                    val = float(val)
                                except ValueError:
                                    pass
                        attributes[key] = val
                
                return Pattern(name=name_part, attributes=attributes)
            
            # Simple name pattern
            return Pattern(name=part)
        
        # Build pattern from right to left
        if len(parts) == 1:
            return parse_part(parts[0])
        
        # Start from the deepest part
        current = None
        for i in range(len(parts) - 1, -1, -1):
            part_pattern = parse_part(parts[i])
            
            if current is not None:
                # Add current as child of this part
                if part_pattern.is_deep_wildcard:
                    # Deep wildcard: current becomes the target after wildcard
                    part_pattern = Pattern(is_deep_wildcard=True)
                    if i > 0:
                        # Continue building from previous parts
                        current = Pattern(children=[part_pattern, current])
                    else:
                        return Pattern(children=[part_pattern, current])
                else:
                    part_pattern.children = [current]
            
            current = part_pattern
        
        return current
    
    @staticmethod
    def from_dict(pattern_dict: Dict[str, Any]) -> 'Pattern':
        """
        Create a pattern from dictionary representation.
        
        Example:
            {
                "name": "parent",
                "attributes": {"type": "container"},
                "children": [
                    {"name": "child1"},
                    {"name": "*"}  # Wildcard child
                ]
            }
        """
        children = []
        if 'children' in pattern_dict:
            for child_dict in pattern_dict['children']:
                if isinstance(child_dict, dict):
                    children.append(Pattern.from_dict(child_dict))
                elif isinstance(child_dict, str):
                    children.append(Pattern.from_string(child_dict))
        
        return Pattern(
            name=pattern_dict.get('name'),
            attributes=pattern_dict.get('attributes', {}),
            children=children,
            is_wildcard=pattern_dict.get('is_wildcard', False),
            is_deep_wildcard=pattern_dict.get('is_deep_wildcard', False),
            min_children=pattern_dict.get('min_children'),
            max_children=pattern_dict.get('max_children'),
            predicate=pattern_dict.get('predicate')
        )


class PatternMatcher:
    """
    Matches patterns against tree structures.
    """
    
    def __init__(self, match_type: MatchType = MatchType.PARTIAL):
        """
        Initialize pattern matcher.
        
        Args:
            match_type: Type of matching to perform
        """
        self.match_type = match_type
    
    def match(self, node: Node, pattern: Pattern) -> bool:
        """
        Check if a node matches a pattern.
        
        Args:
            node: Node to match against
            pattern: Pattern to match
            
        Returns:
            True if node matches pattern
        """
        # Deep wildcard matches anything, but check attributes and predicate if present
        if pattern.is_deep_wildcard:
            # If deep wildcard has attributes, check them
            if pattern.attributes:
                for key, expected_value in pattern.attributes.items():
                    if key not in node.payload or node.payload[key] != expected_value:
                        return False
            # Check predicate if present
            if pattern.predicate and not pattern.predicate(node):
                return False
            return True
        
        # Regular wildcard matches any single node
        if pattern.is_wildcard:
            return True
        
        # Check custom predicate
        if pattern.predicate and not pattern.predicate(node):
            return False
        
        # Check name
        if pattern.name and node.name != pattern.name:
            return False
        
        # Check attributes
        for key, expected_value in pattern.attributes.items():
            if key not in node.payload or node.payload[key] != expected_value:
                return False
        
        # Check children count constraints
        num_children = len(node.children)
        if pattern.min_children is not None and num_children < pattern.min_children:
            return False
        if pattern.max_children is not None and num_children > pattern.max_children:
            return False
        
        # Check children patterns
        if pattern.children:
            if self.match_type == MatchType.EXACT:
                # Exact match: number and order of children must match
                if len(pattern.children) != len(node.children):
                    return False
                for pattern_child, node_child in zip(pattern.children, node.children):
                    if not self.match(node_child, pattern_child):
                        return False
            else:
                # Partial match: pattern children must be found in node children
                if not self._match_children_partial(node.children, pattern.children):
                    return False
        
        return True
    
    def _match_children_partial(self, node_children: List[Node], 
                               pattern_children: List[Pattern]) -> bool:
        """
        Match pattern children against node children with flexibility.
        Handles wildcards and deep wildcards.
        """
        if not pattern_children:
            return True
        
        if not node_children:
            # Check if all remaining patterns are deep wildcards
            return all(p.is_deep_wildcard for p in pattern_children)
        
        # Try to match pattern children with node children
        return self._match_sequence(node_children, pattern_children, 0, 0)
    
    def _match_sequence(self, nodes: List[Node], patterns: List[Pattern],
                       node_idx: int, pattern_idx: int) -> bool:
        """
        Recursively match a sequence of patterns against nodes.
        """
        # All patterns matched
        if pattern_idx >= len(patterns):
            return True
        
        # No more nodes but patterns remain
        if node_idx >= len(nodes):
            # Check if remaining patterns are all deep wildcards
            return all(p.is_deep_wildcard for p in patterns[pattern_idx:])
        
        pattern = patterns[pattern_idx]
        
        if pattern.is_deep_wildcard:
            # Deep wildcard can match zero or more nodes
            # Try matching 0 nodes
            if self._match_sequence(nodes, patterns, node_idx, pattern_idx + 1):
                return True
            # Try matching 1+ nodes
            for i in range(node_idx, len(nodes)):
                if self._match_sequence(nodes, patterns, i + 1, pattern_idx + 1):
                    return True
            return False
        else:
            # Regular pattern or wildcard - must match exactly one node
            if self.match(nodes[node_idx], pattern):
                return self._match_sequence(nodes, patterns, node_idx + 1, pattern_idx + 1)
            return False
    
    def find_all(self, tree: Node, pattern: Pattern) -> List[Node]:
        """
        Find all nodes in tree that match the pattern.
        
        Args:
            tree: Root node of tree to search
            pattern: Pattern to match
            
        Returns:
            List of nodes that match the pattern
        """
        matches = []
        
        def search(node: Node):
            if self.match(node, pattern):
                matches.append(node)
            for child in node.children:
                search(child)
        
        search(tree)
        return matches
    
    def find_first(self, tree: Node, pattern: Pattern) -> Optional[Node]:
        """
        Find first node that matches the pattern.
        
        Args:
            tree: Root node of tree to search
            pattern: Pattern to match
            
        Returns:
            First matching node or None
        """
        def search(node: Node) -> Optional[Node]:
            if self.match(node, pattern):
                return node
            for child in node.children:
                result = search(child)
                if result:
                    return result
            return None
        
        return search(tree)
    
    def replace(self, tree: Node, pattern: Pattern, 
                replacement: Union[Node, Callable[[Node], Node]]) -> int:
        """
        Replace all nodes matching pattern with replacement.
        
        Args:
            tree: Root node of tree
            pattern: Pattern to match
            replacement: Node or function to generate replacement
            
        Returns:
            Number of replacements made
        """
        count = 0
        
        def replace_recursive(node: Node, parent: Optional[Node] = None) -> Optional[Node]:
            nonlocal count
            
            # Check if current node matches
            if self.match(node, pattern):
                count += 1
                if callable(replacement):
                    new_node = replacement(node)
                else:
                    new_node = replacement
                
                # Update parent's children if needed
                if parent:
                    idx = parent.children.index(node)
                    parent.children[idx] = new_node
                    new_node.parent = parent
                
                return new_node
            
            # Recursively process children
            for i, child in enumerate(list(node.children)):
                new_child = replace_recursive(child, node)
                if new_child and new_child != child:
                    node.children[i] = new_child
            
            return node
        
        replace_recursive(tree)
        return count


def pattern_match(tree: Node, pattern: Union[str, Dict, Pattern],
                 match_type: MatchType = MatchType.PARTIAL) -> List[Node]:
    """
    Convenience function to find all matches of a pattern in a tree.
    
    Args:
        tree: Tree to search
        pattern: Pattern as string, dict, or Pattern object
        match_type: Type of matching
        
    Returns:
        List of matching nodes
    """
    if isinstance(pattern, str):
        pattern = Pattern.from_string(pattern)
    elif isinstance(pattern, dict):
        pattern = Pattern.from_dict(pattern)
    
    matcher = PatternMatcher(match_type)
    return matcher.find_all(tree, pattern)


def dotmatch(tree: Node, dot_path: str, return_paths: bool = False) -> Union[List[Node], List[str]]:
    """
    Match nodes using dot notation paths, inspired by dotsuite.
    
    This provides a clean, intuitive way to navigate and match tree paths
    using dot notation similar to JSONPath or object property access.
    
    Args:
        tree: Tree to search
        dot_path: Dot notation path (e.g., "root.branch.*.leaf", "app.**.test")
        return_paths: If True, return dot paths to matches instead of nodes
        
    Returns:
        List of matching nodes or their dot paths
        
    Examples:
        # Find all test files
        dotmatch(tree, "src.**.test_*")
        
        # Find specific path
        dotmatch(tree, "app.models.user")
        
        # Find with wildcards
        dotmatch(tree, "data.*.value")
        
        # Get paths instead of nodes
        paths = dotmatch(tree, "**.config", return_paths=True)
        # Returns: ["app.config", "modules.auth.config", ...]
    """
    # Special case: if path starts with **, search from any point
    if dot_path.startswith('**'):
        # Check if this is ** with attributes (e.g., **[type=file])
        if dot_path.startswith('**[') and ']' in dot_path:
            # Use pattern_match for deep wildcard with attributes
            pattern = Pattern.from_string(dot_path)
            matcher = PatternMatcher(MatchType.PARTIAL)
            matches = matcher.find_all(tree, pattern)
        else:
            # Remove leading ** and optional dot
            remaining_path = dot_path[2:]
            if remaining_path.startswith('.'):
                remaining_path = remaining_path[1:]
            
            if not remaining_path:
                # Just ** - match all nodes
                matches = list(tree.traverse_preorder())
            else:
                # Search for remaining pattern from any node
                matches = []
                seen = set()
                for node in tree.traverse_preorder():
                    sub_matches = dotmatch(node, remaining_path)
                    for match in sub_matches:
                        if match not in seen:
                            matches.append(match)
                            seen.add(match)
    else:
        # Path-based navigation: follow the path from root or any node
        parts = []
        current = ""
        bracket_depth = 0
        escape_next = False
        
        # Parse parts carefully with escaping
        for i, char in enumerate(dot_path):
            if escape_next:
                current += char
                escape_next = False
            elif char == '\\' and i + 1 < len(dot_path) and dot_path[i + 1] == '.':
                # Escape sequence for literal dot
                escape_next = True
            elif char == '[':
                bracket_depth += 1
                current += char
            elif char == ']':
                bracket_depth -= 1
                current += char
            elif char == '.' and bracket_depth == 0:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char
        if current:
            parts.append(current)
        
        # Navigate the path
        matches = []
        
        def navigate_path(node, path_parts, index=0):
            """Recursively navigate the dot path."""
            if index >= len(path_parts):
                # Reached the end of the path
                matches.append(node)
                return
            
            part = path_parts[index]
            
            # Parse the current part
            if part == '*' or part == '[*]':
                # Wildcard - match all children
                for child in node.children:
                    navigate_path(child, path_parts, index + 1)
            elif part == '**':
                # Deep wildcard - match any descendant
                if index == len(path_parts) - 1:
                    # ** at the end matches all descendants
                    for desc in node.traverse_preorder():
                        if desc != node:
                            matches.append(desc)
                else:
                    # ** in the middle - try continuing from any descendant
                    for desc in node.traverse_preorder():
                        navigate_path(desc, path_parts, index + 1)
            else:
                # Check if this is a wildcard pattern with suffix (e.g., *.txt)
                if part.startswith('*') and len(part) > 1:
                    # Pattern like *.txt - match nodes ending with suffix
                    suffix = part[1:]  # Remove leading *
                    part_pattern = Pattern(predicate=lambda n, s=suffix: n.name.endswith(s))
                elif any(char in part for char in ['[', '*', '~', '%', '?']):
                    # Parse part as pattern
                    part_pattern = Pattern.from_string(part)
                else:
                    # Simple name match - don't re-parse to avoid dot splitting
                    part_pattern = Pattern(name=part)
                
                # Find matching children
                for child in node.children:
                    matcher = PatternMatcher(MatchType.PARTIAL)
                    if matcher.match(child, part_pattern):
                        navigate_path(child, path_parts, index + 1)
        
        # Start navigation from root or search all nodes
        if parts and parts[0] == tree.name:
            # Path starts with root name - navigate from root
            navigate_path(tree, parts, 1)
        else:
            # Try to find the path starting from any node
            navigate_path(tree, parts, 0)
    
    if return_paths:
        # Convert matches to dot paths
        paths = []
        for match in matches:
            path_parts = []
            current = match
            while current:
                path_parts.append(current.name)
                current = current.parent
            paths.append('.'.join(reversed(path_parts)))
        return paths
    
    return matches


def dotpluck(tree: Node, *dot_paths: str) -> List[Any]:
    """
    Extract values from tree using dot notation paths.
    
    Inspired by dotsuite's dotpluck, this extracts payload values from
    nodes at specified paths.
    
    Args:
        tree: Tree to extract from
        *dot_paths: Variable number of dot notation paths
        
    Returns:
        List of values (payload or None for missing paths)
        
    Examples:
        # Extract multiple values
        values = dotpluck(tree, "user.name", "user.age", "user.email")
        
        # Extract with wildcards (returns all matching values)
        values = dotpluck(tree, "users.*.name")
    """
    results = []
    
    for path in dot_paths:
        matches = dotmatch(tree, path)
        if not matches:
            results.append(None)
        elif len(matches) == 1:
            results.append(matches[0].payload)
        else:
            # Multiple matches - return list of payloads
            results.append([m.payload for m in matches])
    
    return results


def dotexists(tree: Node, dot_path: str) -> bool:
    """
    Check if a path exists in the tree.
    
    Inspired by dotsuite's dotexists from the Truth pillar.
    
    Args:
        tree: Tree to check
        dot_path: Dot notation path
        
    Returns:
        True if path exists, False otherwise
    """
    matches = dotmatch(tree, dot_path)
    return len(matches) > 0


def dotcount(tree: Node, dot_path: str) -> int:
    """
    Count nodes matching a path pattern.
    
    Args:
        tree: Tree to count in
        dot_path: Dot notation path pattern
        
    Returns:
        Number of matching nodes
    """
    matches = dotmatch(tree, dot_path)
    return len(matches)


def dotfilter(tree: Node, filter_expr: str) -> List[Node]:
    """
    Filter tree nodes using advanced expressions.
    
    Supports:
    - Comparison operators: >, <, >=, <=, ==, !=
    - Logical operators: and, or, not
    - Path expressions: @.property
    - Functions: contains(), startswith(), endswith()
    
    Args:
        tree: Tree to filter
        filter_expr: Filter expression
        
    Returns:
        List of matching nodes
        
    Examples:
        # Size greater than 100
        dotfilter(tree, "@.size > 100")
        
        # Name contains "test" and has children
        dotfilter(tree, "contains(@.name, 'test') and @.children.length > 0")
    """
    # Create a predicate from the filter expression
    def create_filter_predicate(expr: str):
        def predicate(node):
            # Build evaluation context
            context = {
                '@': node,
                'contains': lambda s, sub: sub in s if isinstance(s, str) else False,
                'startswith': lambda s, pre: s.startswith(pre) if isinstance(s, str) else False,
                'endswith': lambda s, suf: s.endswith(suf) if isinstance(s, str) else False,
                'len': len,
                'type': type,
                'isinstance': isinstance,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
            }
            
            # Replace @.property references
            import re
            expr_eval = expr
            
            # Replace @.name
            expr_eval = re.sub(r'@\.name\b', repr(node.name), expr_eval)
            
            # Replace @.children.length
            expr_eval = re.sub(r'@\.children\.length\b', str(len(node.children)), expr_eval)
            
            # Replace @.parent
            expr_eval = re.sub(r'@\.parent\b', str(node.parent is not None), expr_eval)
            
            # Replace @.is_leaf
            expr_eval = re.sub(r'@\.is_leaf\b', str(node.is_leaf), expr_eval)
            
            # Replace @.is_root
            expr_eval = re.sub(r'@\.is_root\b', str(node.is_root), expr_eval)
            
            # Replace @.level
            expr_eval = re.sub(r'@\.level\b', str(node.level), expr_eval)
            
            # Replace @.payload.property references
            for match in re.finditer(r'@\.payload\.(\w+)\b', expr_eval):
                prop = match.group(1)
                value = node.payload.get(prop, None)
                if isinstance(value, str):
                    value = repr(value)
                elif value is None:
                    value = 'None'
                else:
                    value = str(value)
                expr_eval = expr_eval.replace(match.group(0), value)
            
            # Replace generic @.property
            for match in re.finditer(r'@\.(\w+)\b', expr_eval):
                prop = match.group(1)
                if hasattr(node, prop):
                    value = getattr(node, prop)
                    if callable(value):
                        value = value()
                    if isinstance(value, str):
                        value = repr(value)
                    else:
                        value = str(value)
                elif prop in node.payload:
                    value = node.payload[prop]
                    if isinstance(value, str):
                        value = repr(value)
                    else:
                        value = str(value)
                else:
                    value = 'None'
                expr_eval = expr_eval.replace(match.group(0), value)
            
            try:
                return eval(expr_eval, {"__builtins__": {}}, context)
            except:
                return False
        
        return predicate
    
    # Find all nodes and filter them
    all_nodes = list(tree.traverse_preorder())
    predicate = create_filter_predicate(filter_expr)
    return [node for node in all_nodes if predicate(node)]