#!/usr/bin/env python3

import argparse
import json
import logging
import sys
import textwrap

from treekit.dicttree import DictTree


def show_json_spec():
    print(
        textwrap.dedent(
            """
        The JSON data should have the following structure:

            {
                # Meta-data (optional key-value pairs)
                ...

                'mapping': {
                    'node_key': {
                        'parent': 'parent_node_key',
                        # Additional payload data
                        ...
                    },

                    # More nodes
                    ...
                }
            }
        """
        )
    )


def main():
    parser = argparse.ArgumentParser(
        description="Query or render a tree from JSON data",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--flatten",
        action="store_true",
        help="Flatten the tree into a list of paths and print as JSON",
    )
    parser.add_argument(
        "file",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Path to JSON file (reads from stdin if not provided)",
    )
    parser.add_argument(
        "--log",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    parser.add_argument("--output", help="Output file name to save the tree")
    parser.add_argument(
        "--node-name",
        default="lambda node: node.name",
        type=str,
        metavar="LAMBA_EXPRESSION",
        help="Lambda expression to generate node names from a node, defaults to `lambda node: node.name`",
    )
    parser.add_argument(
        "--fallback-node-name",
        type=str,
        metavar="LAMBA_EXPRESSION",
        help="Fallback lambda expression to generate node names if the node-name LAMBA_EXPRESSION fails",
    )
    parser.add_argument(
        "--json-spec",
        action="store_true",
        help="Print the specification of the JSON data structure",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    parser.add_argument(
        "--mapping-key",
        default="mapping",
        type=str,
        nargs=1,
        metavar="KEY",
        help="The key in the JSON that maps to the structure of the tree",
    )
    parser.add_argument(
        "--size", action="store_true", help="Print the size of the tree"
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
        "--get-node",
        metavar="NODE_KEY",
        help="Get node by key",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--get-root", action="store_true", help="Get the root node"
    )
    parser.add_argument(
        "--get-leaves", action="store_true", help="Get the leaf nodes"
    )
    parser.add_argument(
        "--get-level",
        metavar="LEVEL",
        help="Get nodes at a given level",
        type=int,
        nargs=1,
    )
    parser.add_argument(
        "--get-height", action="store_true", help="Get the height of the tree"
    )
    parser.add_argument(
        "--is-ancesor",
        metavar=("NODE_FROM", "NODE_TO"),
        help="Check if two nodes are connected",
        nargs=2,
        type=str,
    )
    parser.add_argument(
        "--get-ancestors",
        metavar=("START_NODE", "END_NODE"),
        help="Get the path from the start node to the end node",
        nargs=2,
        type=str,
    )
    parser.add_argument(
        "--add-node",
        metavar=("PARENT_NODE", "NODE_KEY", "NODE_DATA"),
        help="Add a new node to the tree",
        nargs=3,
        type=str,
    )
    parser.add_argument(
        "--remove-node",
        metavar="NODE_KEY",
        help="Remove a node from the tree. We connect the children of the node to its parent",
        type=str,
        nargs=1,
    )
    parser.add_argument(
        "--update-node",
        metavar=("NODE_KEY", "NODE_DATA"),
        help="Update the data of a node",
        nargs=2,
        type=str,
    )
    parser.add_argument(
        "--move-node",
        metavar=("NODE_KEY", "NEW_PARENT"),
        help="Move a node to a new parent. If the root node is moved, the tree is re-rooted",
        nargs=2,
        type=str,
    )

    parser.epilog = textwrap.dedent(
        """
            Example usage:
                {prog} ./example.json --flatten  # Flatten the tree and print
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
        if args.json_spec:
            show_json_spec()
            sys.exit(0)

        # Caution: eval can be risky with untrusted input
        NODE_KEY = eval(args.NODE_KEY)
        fallback_NODE_KEY = (
            eval(args.fallback_NODE_KEY) if args.fallback_NODE_KEY else None
        )

        if args.file == sys.stdin and sys.stdin.isatty():
            logging.error(
                "No JSON data provided, please provide a file or pipe data"
            )
            parser.print_usage()
            sys.exit(1)

        tree = DictTree(
            data=json.load(args.file), mapping_key=args.mapping_key
        )
        tree.verify_integrity()

        if args.size:
            print(len(tree))
            sys.exit(0)

        if args.flatten:
            print(
                json.dumps(
                    tree.flatten(
                        NODE_KEY=NODE_KEY, fallback_NODE_KEY=fallback_NODE_KEY
                    ),
                    indent=2,
                )
            )
            sys.exit(1)

        if args.output:
            tree.save(
                outfile=args.output,
                NODE_KEY=NODE_KEY,
                fallback_NODE_KEY=fallback_NODE_KEY,
            )
        else:
            print(
                tree.to_string(
                    NODE_KEY=NODE_KEY, fallback_NODE_KEY=fallback_NODE_KEY
                )
            )

    except Exception as e:
        logging.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
