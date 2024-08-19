#!/usr/bin/env python3

import argparse
import json
import sys
import textwrap
from AlgoTree.flattree import FlatTree

def main():
    parser = argparse.ArgumentParser(
        description="Query a FlatTree tree represented in JSON format",
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Path to JSON file (reads from stdin if not provided)",
    )
    parser.add_argument(
        "--node-name",
        type=str,
        nargs=1,
        metavar="LAMBA_EXPRESSION",
        help="Lambda expression to generate node names from a node, defaults to `lambda node: node.name`",
    )
    parser.add_argument(
        "--spec",
        action="store_true",
        help="Print the specification of the FlatTree JSON data structure",
    )
    parser.add_argument(
        "--lca",
        metavar=("NODE_KEY1", "NODE_KEY2"),
        help="Get the lowest common ancestor of two nodes",
        type=str,
        nargs=2,
    )
    parser.add_argument(
        "--depth",
        metavar="NODE_KEY",
        help="Get the depth of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--mark-nodes",
        metavar="NODE_KEY",
        help="Mark nodes in the tree",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "--distance",
        metavar=("NODE_KEY1", "NODE_KEY2"),
        help="Get the distance between two nodes",
        type=str,
        nargs=2,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0"
    )
    parser.add_argument(
        "--size",
        action="store_true",
        help="Print the size of the tree"
    )
    parser.add_argument(
        "--siblings",
        metavar="NODE_KEY",
        help="Show siblings of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--children",
        metavar="NODE_KEY",
        help="Show children of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--parent",
        metavar="NODE_KEY",
        help="Show parent of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--ancestors",
        metavar="NODE_KEY",
        help="Show ancestors of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--descendants",
        metavar="NODE_KEY",
        help="Show descendants of a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--has-node",
        metavar="NODE_KEY",
        help="Check if a node exists",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--subtree",
        metavar="NODE_KEY",
        help="Get the subtree rooted at a given node",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--node",
        metavar="NODE_KEY",
        help="Get node by key",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--root",
        action="store_true",
        help="Get the root node"
    )
    parser.add_argument(
        "--root-to-leaves",
        action="store_true",
        help="Get a list of paths from the root to the leaves")
    parser.add_argument(
        "--leaves",
        action="store_true",
        help="Get the leaf nodes"
    )
    parser.add_argument(
        "--height",
        action="store_true",
        help="Get the height of the tree"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print the tree in a pretty format",
    )
    parser.add_argument(
        "--prune",
        metavar="LAMBDA_EXPRESSION",
        help="Prune the tree by predicate function",
        type=str,
        nargs=1)
    parser.add_argument(
        "--subtree-rooted-at",
        metavar="NODE_KEY",
        help="Get the subtree rooted at a given node",
        type=str,
        nargs=1)
    parser.add_argument(
        "--find-nodes",
        nargs=1,
        type=str,
        metavar="LAMBDA_EXPRESSION",
        help="Find nodes by predicate function")

    parser.epilog = textwrap.dedent(
        """
            Example usage:
                # Check if a node exists
                {prog} ./example.json --has-node nodeName
                # Get specific node details
                {prog} ./example.json --get-node nodeKey
                # Show siblings of a node
                {prog} ./example.json --siblings nodeName

            To see the expected structure of the JSON data, invoke the --json-spec option.
        """
    ).format(prog=parser.prog)

    args = parser.parse_args()

    try:
        if args.file == sys.stdin and sys.stdin.isatty():
            print("No JSON data provided, please provide a file or pipe data")
            parser.print_usage()
            sys.exit(1)

        if args.spec:
            print(FlatTree.spec.__doc__)

        node_name = lambda node: node.name
        if args.node_name:
            node_name = eval(args.node_name[0])

        tree = FlatTree(json.load(args.file))

        result = {}
        if args.prune:
            from AlgoTree.utils import prune
            prune(tree.root, eval(args.prune[0]))

        if args.find_nodes:
            from AlgoTree.utils import find_nodes
            nodes = find_nodes(tree, eval(args.find_nodes[0]))
            print([node_name(n) for n in nodes])

        if args.root:
            print(node_name(tree.root))

        if args.size:
            from AlgoTree.utils import size
            print(size(tree))

        if args.siblings:
            from AlgoTree.utils import siblings
            sibs = siblings(tree.node(args.siblings[0]))
            print([node_name(s) for s in sibs])

        if args.children:
            children = tree.node(args.children[0]).children
            print([node_name(c) for c in children])

        if args.parent:
            node = tree.node(args.parent[0])
            print(node_name(node.parent) if node.parent else None)

        if args.ancestors:
            from AlgoTree.utils import ancestors
            anc = ancestors(tree.node(args.ancestors[0]))
            print([node_name(a) for a in anc])

        if args.descendants:
            from AlgoTree.utils import descendants
            desc = descendants(tree.node(args.descendants[0]))
            print([node_name(d) for d in desc])

        if args.has_node:
            print(tree.node(args.has_node[0]) is not None)

        if args.height:
            from AlgoTree.utils import height
            print(height(tree))

        if args.leaves:
            from AlgoTree.utils import leaves
            print([node_name(l) for l in leaves(tree)])

        if args.node:
            node = tree.node(args.node[0])
            print(node)
            
        if args.subtree:
            from AlgoTree.tree_converter import TreeConverter
            from AlgoTree.flattree_node import FlatTreeNode
            sub = TreeConverter.convert(tree.subtree(args.subtree[0]), FlatTreeNode)
            print(json.dumps(sub.tree, indent=4))

        if args.depth:
            from AlgoTree.utils import depth
            print(depth(tree.node(args.depth[0])))

        if args.distance:
            from AlgoTree.utils import distance
            n1, n2 = args.distance
            print(distance(tree.node(n1), tree.node(n2)))

        if args.lca:
            from AlgoTree.utils import lca
            n1, n2 = args.lca
            print(node_name(lca(tree.node(n1), tree.node(n2))))

        if args.root_to_leaves:
            from AlgoTree.utils import node_to_leaf_paths
            paths = [p for p in node_to_leaf_paths(tree)]
            for p in paths:
                print([node_name(n) for n in p])

        if args.subtree_rooted_at:
            # this does not work, look more closely at this
            from AlgoTree.utils import subtree_rooted_at
            from AlgoTree.pretty_tree import pretty_tree
            node = tree.node(args.subtree_rooted_at[0])
            sub = subtree_rooted_at(node, 1)
            print(sub.tree)

        if args.pretty:
            from AlgoTree.pretty_tree import pretty_tree
            print(pretty_tree(tree.root, node_name=node_name, mark=args.mark_nodes or []))

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()



        # return {
        #     "type": "object",
        #     "patternProperties": {
        #         ".*": {
        #             "type": "object",
        #             "properties": {
        #                 "parent": {"type": ["string", "null"]},
        #             },
        #             "additionalProperties": True,
        #         }
        #     },
        #     "additionalProperties": False
        # }
