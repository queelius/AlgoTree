from anytree import Node, RenderTree, PreOrderIter
from anytree.exporter import DotExporter
import anytree
import graphviz
import os
import logging
import json
import copy


class DictTree(object):
    """
    A tree class that can be used to render trees from dictionaries
    containing tree data. See the `__init__` method for more details.
    """

    @classmethod
    def spec(cls):
        with open('SPEC.md', 'r') as file:
            return file.read()

    def __init__(self, metadata=None):
        """
        Initialize a tree.

        :param metadata: Optional meta-data
        """
        self.metadata = copy.deepcopy(metadata)
        self.nodes = {}
        self.root_node = None

    @classmethod
    def from_anytree(cls, node):
        """
        Construct a DictTree from an AnyTree node. `node` will be the new
        root of the new tree. Note that we use deepcopy to avoid modifying
        the original tree.

        :param node: An AnyTree node.

        :return: A DictTree object.
        """
        tree = DictTree()
        for n in PreOrderIter(node):
            tree.nodes[n.name] = Node(n.name, parent=None, children=[],
                                      payload=copy.deepcopy(n.payload)) 
            
        for n in PreOrderIter(node):
            tree.nodes[n.name].children = [tree.nodes[child.name] for child in n.children]

        tree.root_node = DictTree.find_root(tree)
        return tree 
            
    @classmethod
    def from_dict(cls, data, mapping_key='mapping'):
        """
        Construct a tree from a dictionary. See `spec` for more details
        on the expected structure of the dictionary.

        :param data: Dictionary containing tree data.
        :param mapping_key: Key in the dictionary containing the tree mapping.

        :return: A DictTree object.
        """

        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")
        if mapping_key not in data:
            raise ValueError(f"Mapping key '{mapping_key}' not found in data")

        tree = DictTree(metadata = {
            key: value for key, value in data.items() if key != mapping_key})
        
        tree.load_mapping(data.get(mapping_key, {}))
        return tree

    def load_mapping(self, mapping, ignore_duplicates=False):
        """
        Load mapping data from `mapping` dict.

        Mapping data is a dictionary of key-value pairs, where the key is
        the node ID and the value is a dictionary containing the node's
        parent ID, children IDs, and any other relevant payload data
        extracted using the `payload` function.

        We rerieve the relevant data using the payload function. By default,
        the payload function retrieves the 'message' field from the mapping data,
        which is the default structure of OpenAI's conversation data.

        See the `spec` method for more details on the expected structure
        of the mapping data.

        (This method may be used multiple times to load mapping data from
        different sources into the tree.)

        :param mapping: Mapping data.
        :param ignore_duplicates: Ignore duplicate node IDs.

        :return: The root node of the tree.
        """

        if not isinstance(mapping, dict):
            raise ValueError("Mapping data must be a dictionary")

        for key, value in mapping.items():
            if key in self.nodes:
                if ignore_duplicates:
                    logging.warning(f"Ignoring duplicate node ID: {key}")
                else:
                    raise ValueError(f"Duplicate node ID: {key}")
            else:
                logging.debug(f"Loading node: {key}")
                self.nodes[key] = Node(key, parent=None, children=[],
                                       payload=copy.deepcopy(value))

        for key, value in mapping.items():
            parent_id = value.get('parent', None)
            if parent_id:
                self.nodes[key].parent = self.nodes.get(parent_id)

        for key, value in mapping.items():
            children = value.get('children', [])
            for child_id in children:
                self.nodes[key].children += (self.nodes.get(child_id),)

        self.root_node = DictTree.find_root(self)
        return self.root_node

    def add_node(self, key, parent_key=None, payload=None):
        """
        Add a node to the tree.

        :param key: The key of the node.
        :param parent_key: The key of the parent node.
        :param payload: Additional data for the node.

        :return: The node that was added.
        """

        if key in self.nodes:
            raise ValueError(f"Node {key} already exists")
        
        if parent_key and parent_key not in self.nodes:
            raise ValueError(f"Parent node {parent_key} not found")

        node = Node(
            key,
            parent=self.nodes.get(parent_key),
            children=[],
            payload=copy.deepcopy(payload))
        self.nodes[key] = node
        return node
    
    def merge_under(self, key, tree):
        """
        Merge another tree under a node in the current tree.

        :param key: The key of the node to merge `tree` under.
        :param tree: The tree to merge.

        :return: The node under which the tree was merged.
        """

        node = self.nodes.get(key)
        if not node:
            raise ValueError(f"Node {key} not found")

        tree = copy.deepcopy(tree)
        for child in tree.nodes.values():
            if child.name in self.nodes:
                raise ValueError(f"Node {child.name} already exists")
            self.nodes[child.name] = child
        
        tree.root_node.parent = node
        return node

    def edit_node(self, key, new_key=None, parent_key=None, payload=None, children=None):
        """
        Edit a node in the tree.

        :param key: The key of the node.
        :param new_key: The new key of the node.
        :param parent_key: The key of the parent node.
        :param payload: Additional data for the node.
        :param children: List of children IDs.

        :return: The node that was edited.
        """

        node = self.nodes.get(key)
        if not node:
            raise ValueError(f"Node {key} not found")

        if new_key:
            if new_key in self.nodes:
                raise ValueError(f"Node {new_key} already exists")
            self.nodes.pop(key)
            node.name = new_key
            self.nodes[new_key] = node
        if parent_key:
            node.parent = self.nodes.get(parent_key)
        if children:
            node.children = [self.nodes.get(child) for child in children]
        if payload:
            node.payload = payload
        return node

    def remove_node(self, key):
        """
        Remove a node from the tree, and any of its children. Return the
        subtree that was removed (the root of the node, i.e., the node
        named by `key`).

        :param key: The key of the node to remove.

        :return: The node that was removed (all its children are removed as well)
        """

        node = self.nodes.pop(key, None)
        if not node:
            raise ValueError(f"Node {key} not found")
                
        node.parent = None
        for child in node.children:
            self.nodes.pop(child.name)

        return node

    def get_node(self, key):
        """
        Get a node by key.

        Once you have a node, you can access its parent, children, and siblings.
        and so on. See the documentation for anytree for more details.

        :param key: The key of the node.

        :return: The node with the given key. None if the node was not found.
        """

        return self.nodes.get(key, None)

    def height(self):
        """
        Return the height of the tree.

        :return: The height of the tree.
        """
        return self.root_node.height

    def leaves(self):
        """
        Return the leaf nodes of the tree.

        :return: The leaf nodes of the tree.
        """
        return [node for node in PreOrderIter(self.root_node) if node.is_leaf]

    def to_dict(self):
        """
        Convert the tree to a dictionary.

        :return: A dictionary representation of the tree.
        """
        return {**self.metadata,
                'mapping': {node.name: node.payload for node in self.nodes.values()}}

    def __repr__(self):
        """
        Return a JSON representation of the tree.

        :return: str
        """
        return json.dumps(self.to_dict(), indent=2)

    def to_string(self,
                  node_name=lambda node: node.name,
                  fallback_node_name=None,
                  style=anytree.ContStyle()):
        """
        Generate a string representation of the tree.

        :param node_name: Function to generate node names.
        :param fallback_node_name: Function to generate node names if the primary function fails.
        :param style: Style of the tree rendering. See anyTree documentation for more details.

        :return: str
        """
        result = ""
        for pre, _, node in RenderTree(self.root_node, style=style):
            try:
                result += f"{pre}{node_name(node)}\n"
            except Exception as e:
                if fallback_node_name:
                    result += f"{pre}{fallback_node_name(node)}\n"
        return result.strip()

    def __str__(self):
        return self.to_string(style=anytree.AsciiStyle())

    @classmethod
    def find_root(cls, tree):
        """
        Find the root node of the tree.

        :return: The root node of the tree.
        """
        for node in tree.nodes.values():
            if node.is_root:
                return node

        raise ValueError("No root node")

    def is_connected(self):
        """
        Check if the tree is connected.

        :return: True if the tree is connected, False otherwise.
        """

        return len(
            [node for node in PreOrderIter(self.root_node)]) == len(
            self.nodes)

    def verify_integrity(self):
        """
        Verify the integrity of the tree by checking for cycles,
        there is a root node, and all nodes are connected.

        :return: Raises a ValueError if the tree is invalid.
        """

        if not self.root_node:
            raise ValueError("No root node")

        visited = {self.root_node}
        path = set()
        def __dfs(node):
            if node in path:
                raise ValueError(f"Cycle detected involving node {node.name}")
            path.add(node)
            for child in node.children:
                if child not in visited:
                    visited.add(child)
                    __dfs(child)
            path.remove(node)

        __dfs(self.root_node)

        if not self.is_connected():
            logging.debug("Not fully connected")

    def __len__(self):
        return self.root_node.size

    def __getitem__(self, key):
        return self.get_node(key)

    def __iter__(self):
        return iter(self.nodes.items())

    def __contains__(self, key):
        return key in self.nodes.keys()

    def save(self,
             outfile,
             node_name=lambda node: node.name,
             fallback_node_name=None):
        """
        Save the tree to an image or dot file. The outfile should
        include the format extension (e.g., 'tree.png' or 'tree.dot').

        :param node_name: Function to generate node names given a node.
        :param outfile Name of the output file.

        :return: None
        """
        ext = outfile.split('.')[-1]

        # generate a random dot filename, hidden, using a hash
        dot_tmp = f".{hash(outfile)}.dot"

        combined = DictTree.make_combined_node_name(
            node_name, fallback_node_name)
        DotExporter(node=self.root_node,
                    nodenamefunc=combined).to_dotfile(dot_tmp)
        if ext != "dot":
            graphviz.render('dot',
                            format=ext,
                            filepath=dot_tmp,
                            outfile=outfile)
            os.remove(dot_tmp)
        else:
            os.rename(dot_tmp, outfile)
        logging.info(f"Tree saved as {outfile}")

    def get_nodes(self):
        return self.nodes.values()

    @classmethod
    def make_combined_node_name(cls, node_name, fallback_node_name):
        def combined(node):
            try:
                return node_name(node)
            except Exception as e:
                if fallback_node_name:
                    try:
                        return fallback_node_name(node)
                    except BaseException:
                        raise e
                else:
                    raise e

        return combined

    def flatten(self,
                node_name=lambda node: node,
                fallback_node_name=None):
        """
        Flatten the tree into a list of paths from the root to each leaf node.

        :param node_name: Function to generate node names.
        :param fallback_node_name: Function to generate node names if the primary function fails.

        :return: A list of paths from the root to each leaf node.
        """

        combined = DictTree.make_combined_node_name(
            node_name, fallback_node_name)
        paths = []
        for leaf in [node for node in PreOrderIter(
                self.root_node) if node.is_leaf]:
            path = []
            cur = leaf
            while cur is not None:
                path.append(combined(cur))
                cur = cur.parent
            paths.append(path[::-1])
        return paths
