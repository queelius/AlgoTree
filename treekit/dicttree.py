from anytree import Node, RenderTree, PreOrderIter
from anytree.exporter import DotExporter
import anytree, graphviz, os, logging

class DictTree(object):
    """
    A tree class that can be used to render trees from dictionaries
    containing tree data. See the `__init__` method for more details.
    """

    def __init__(self,
                 data,
                 mapping_key='mapping'):
        """
        Initialize a tree from a dictionary.
        The dictionary should have the following structure:
                                    
            {
                # Meta-data (optional key-value pairs)
                ...

                '<mapping_key>': {
                    '<node_key>': {
                        # Key of the parent node
                        'parent': '<parent_node_key>',
                    
                        # List of keys of child nodes
                        "children": ['<child_node_key>', ...],
                    
                        # Additional payload data
                        ... 
                    },
                    
                    # Key-value pairs or other nodes
                    ...
                }
            }

        :param data: Dictionary containing tree data.
        :param mapping_key: Key in the dictionary containing the tree mapping.
        """
        self.metadata = {key: value for key, value in data.items() if key != mapping_key}
        if mapping_key not in data:
            logging.error(f"Mapping key '{mapping_key}' not found in data")
        self.nodes = {}
        self.root_node = None
        self.load_mapping(data.get(mapping_key, {}))

    def load_mapping(self, mapping):
        """
        Load a tree from mapping data.

        Mapping data is a dictionary of key-value pairs, where the key is
        the node ID and the value is a dictionary containing the node's
        parent ID, children IDs, and any other relevant payload data
        extracted using the `payload` function.

        We rerieve the relevant data using the payload function. By default,
        the payload function retrieves the 'message' field from the mapping data,
        which is the default structure of OpenAI's conversation data.

        See the `__init__` method for more details on the expected structure
        of the mapping data.

        This method may be used multiple times to load data from different
        sources into the tree.

        :param mapping: Mapping data.
        :param payload: Function to retrieve payload from mapping data.

        :return: A dictionary of nodes compatible with anyTree library.
        """
        
        for key, value in mapping.items():
            if key in self.nodes:
                logging.warning(f"Ignoring duplicate node ID: {key}")
            else:
                logging.debug(f"Loading node: {key}")
                self.nodes[key] = Node(key, parent=None, children=[],
                                       payload=value)

        for key, value in mapping.items():
            parent_id = value['parent']
            if parent_id:
                self.nodes[key].parent = self.nodes.get(parent_id)
            for child_id in value.get('children', []):
                if child_id in self.nodes.keys():
                    logging.debug(f"Adding node {child_id} as child of node {key}")
                    self.nodes[child_id].parent = self.nodes[key]
                else:
                    logging.warning(f"Child node ID {child_id} not found")

        self.root_node = self.find_root()

    def print_tree(self,
                   node_name = lambda node: node.name,
                   fallback_node_name = None,
                   style = anytree.ContStyle()):
            
        """
        Print the tree to the console.

        :param node_name: Function to generate node names.
        :param fallback_node_name: Function to generate node names if the primary function fails.
        :param style: Style of the tree rendering. See anyTree documentation for more details.

        :return: None
        """

        for pre, _, node in RenderTree(self.root_node, style=style):
            try:
                print("%s%s" % (pre, node_name(node)))
            except Exception as e:
                if fallback_node_name:
                    print("%s%s" % (pre, fallback_node_name(node)))

    def find_root(self):
        """
        Find the root node of the tree.

        :return: The root node of the tree.
        """
        for node in self.nodes.values():
            if node.parent is None:
                return node
        
        logging.error("Root node not found")
        return None

    def verify_integrity(self):
        """
        Verify the integrity of the tree by checking for cycles,
        there is a root node, and all nodes are connected.

        :return: Raises a ValueError if the tree is invalid.
        """

        if not self.root_node:
            raise ValueError("Root node not found")
        
        visited = set()
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

        visited.add(self.root_node)
        __dfs(self.root_node)
        logging.debug("Integrity verified.")

    def __str__(self):
        result = ""
        for pre, _, node in RenderTree(self.root_node):
            result += f"\n{pre}{node.name}"
        return result
    
    def __repr__(self):
        return self.__str__()
    
    def __len__(self):
        return len(self.nodes)
    
    def __getitem__(self, key):
        return self.nodes.get(key)
    
    def __iter__(self):
        return iter(self.nodes.values())

    def save(self,
             outfile,
             node_name = lambda node: node.name,
             fallback_node_name = None):
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

        combined = DictTree.make_combined_node_name(node_name, fallback_node_name)
        DotExporter(node = self.root_node,
                    nodenamefunc = combined).to_dotfile(dot_tmp)
        if ext != "dot":
            graphviz.render('dot',
                            format = ext,
                            filepath = dot_tmp,
                            outfile = outfile)
            os.remove(dot_tmp)
        else:
            os.rename(dot_tmp, outfile)
        logging.info(f"Tree saved as {outfile}")

    def get_node_by_id(self, id):
        return self.nodes.get(id)

    def get_nodes(self):
        return self.nodes
    
    @classmethod
    def make_combined_node_name(cls, node_name, fallback_node_name):
        def combined(node):
            try:
                return node_name(node)
            except Exception as e:
                if fallback_node_name:
                    try:
                        return fallback_node_name(node)
                    except:
                        raise e
                else:
                    raise e
                
        return combined
    
    def flatten(self,
                node_name = lambda node: node.name,
                fallback_node_name = None):

        """
        Flatten the tree into a list of paths from the root to each leaf node.

        :param node_name: Function to generate node names.
        :param fallback_node_name: Function to generate node names if the primary function fails.

        :return: A list of paths from the root to each leaf node.
        """

        combined = DictTree.make_combined_node_name(node_name, fallback_node_name)
        paths = []
        for leaf in [node for node in PreOrderIter(self.root_node) if node.is_leaf]:
            path = []
            cur = leaf
            while cur is not None:
                path.append(combined(cur))
                cur = cur.parent
            paths.append(path[::-1])
        return paths