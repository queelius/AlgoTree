from treekit import FlatTree

class MetaTree(dict):
    """
    This class is a wrapper for the treekit.FlatTree and treekit.TreeNode
    classes. Its only purpose is to allow for the creation of a tree from a
    dictionary, where the `MetaTree.MAPPING_KEY` (defaults to "mapping") is
    used to specify the mapping of the tree.

    The other data in this class is treated as metadata. This metadata can be
    accessed as a normal dictionary, but it is not used in the tree creation
    process.
    """

    MAPPING_KEY = "mapping"

    def __init__(self, *args, **kwargs):
        """
        Create a new MetaTree instance.

        :param args: Positional arguments
        :param kwargs: Keyword arguments
        """
        
        # look for the mapping key; we're providing it as a view though
        # so don't modify the original dictionary

        mapping = kwargs.get(self.MAPPING_KEY, None)
        

        super().__init__(*args, **kwargs)