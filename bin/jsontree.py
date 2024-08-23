#!/usr/bin/env python3

import argparse
import json
import sys
import textwrap
import AlgoTree
from pprint import pprint

def main():
    parser = argparse.ArgumentParser(
        description="Query a tree represented in JSON format (FlatForest, TreeNode)",
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
        "--nodes",
        action="store_true",
        help="Get all nodes in the tree"
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
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the tree in JSON format")
    parser.add_argument(
        "--convert",
        help="Convert the tree to a different format",
        nargs=1,
        type=str,
        metavar="TARGET_FORMAT"
    )
    parser.add_argument(
        "--type",
        action="store_true",
        help="Print the type of the tree"
    )
    parser.add_argument(
        "--merge-forest",
        nargs=1,
        type=str,
        metavar="NODE_KEY",
        help="Merge a forest into a single tree under a new node named NODE_KEY")
    parser.add_argument(
        "--set-root",
        nargs=1,
        type=str,
        metavar="NODE_KEY",
        help="Set the root node of the tree to the node with the given key"
    )
    parser.add_argument(
        "--epilog",
        help="Show example usage",
        action="store_true"
    )
    #parser.add_argument(
    #    "--partial",
    #    action="store_true",
    #    help="Depends on the context, but for instance if setting `--partial` with `--set-root stuff` it will match `stuff` as a partial match"
    #)

    parser.epilog = textwrap.dedent(
        """
            Example usage:
                # Check if a node exists
                {prog} ./example.json --has-node nodeName
                # Get specific node details
                {prog} ./example.json --get-node nodeKey
                # Show siblings of a node
                {prog} ./example.json --siblings nodeName
        """
    ).format(prog=parser.prog)

    args = parser.parse_args()

    try:
        if args.file == sys.stdin and sys.stdin.isatty():
            print("No JSON data provided, please provide a file or pipe data")
            parser.print_usage()
            sys.exit(1)

        if args.epilog:
            print(parser.epilog)
            sys.exit(0)

        node_name = lambda node: node.name
        if args.node_name:
            node_name = eval(args.node_name[0])

        data = json.load(args.file)
        tree = None
        if AlgoTree.FlatForest.is_valid(data):
            tree = AlgoTree.FlatForest(data)
        elif AlgoTree.TreeNode.is_valid(data):
            tree = AlgoTree.TreeNode.from_dict(data)
        else:
            print("Unrecognized tree format")
            sys.exit(1)

        if args.merge_forest:
            if type(tree) is AlgoTree.FlatForest:
                tree = tree.as_tree(args.merge_forest[0])

        if args.set_root:
            tree = tree.subtree(args.set_root[0])

        if args.prune:
            AlgoTree.prune(tree, eval(args.prune[0]))

        if args.nodes:
            pprint([node_name(n) for n in tree.nodes()])

        if args.convert:
            target_type = args.convert[0].strip().lower()
            if target_type == "flatforest":
                tree = AlgoTree.TreeConverter.convert(tree, AlgoTree.FlatForestNode)
            elif target_type == "treenode":
                tree = AlgoTree.TreeConverter.convert(tree, AlgoTree.TreeNode)
            else:
                raise ValueError("Invalid target type")
            
        if args.json:
            print(json.dumps(tree.to_dict(), indent=4))

        if args.find_nodes:
            lam = args.find_nodes[0]
            nodes = AlgoTree.find_nodes(tree, eval(args.find_nodes[0]))
            print([node_name(n) for n in nodes])

        if args.root:
            print(node_name(tree.root))

        if args.size:
            print(AlgoTree.size(tree))

        if args.siblings:
            sibs = AlgoTree.siblings(tree.node(args.siblings[0]))
            print([node_name(s) for s in sibs])

        if args.children:
            children = tree.node(args.children[0]).children
            print([node_name(c) for c in children])

        if args.parent:
            node = tree.node(args.parent[0])
            print(node_name(node.parent) if node.parent else None)

        if args.ancestors:
            anc = AlgoTree.ancestors(tree.node(args.ancestors[0]))
            print([node_name(a) for a in anc])

        if args.descendants:
            desc = AlgoTree.descendants(tree.node(args.descendants[0]))
            print([node_name(d) for d in desc])

        if args.has_node:
            print(tree.node(args.has_node[0]) is not None)

        if args.height:
            print(AlgoTree.height(tree))

        if args.leaves:
            print([node_name(l) for l in AlgoTree.leaves(tree)])

        if args.node:
            node = tree.node(args.node[0])
            print(node)
            
        if args.subtree:
            sub = AlgoTree.TreeConverter.convert(tree.subtree(args.subtree[0]), AlgoTree.FlatForestNode)
            print(json.dumps(sub.tree, indent=4))

        if args.depth:
            print(AlgoTree.depth(tree.node(args.depth[0])))

        if args.distance:
            n1, n2 = args.distance
            print(AlgoTree.distance(tree.node(n1), tree.node(n2)))

        if args.lca:
            n1, n2 = args.lca
            print(node_name(AlgoTree.lca(tree.node(n1), tree.node(n2))))

        if args.root_to_leaves:
            paths = [p for p in AlgoTree.node_to_leaf_paths(tree)]
            for p in paths:
                print([node_name(n) for n in p])

        if args.subtree_rooted_at:
            # this does not work, look more closely at this
            node = tree.node(args.subtree_rooted_at[0])
            sub = AlgoTree.subtree_rooted_at(node, 1)
            print(sub.to_dict())

        if args.pretty:
            print(AlgoTree.pretty_tree(tree.root, node_name=node_name, mark=args.mark_nodes or []))

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()