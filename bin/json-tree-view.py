#!/usr/bin/env python3

import argparse
import json
import logging
import sys

from AlgoTree.flattree import FlatTree


def main():
    parser = argparse.ArgumentParser(
        description="Query or render a tree from JSON data",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "file",
        type=argparse.FileType("r"),
        default=sys.stdin,
        nargs="?",
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
        "--schema",
        action="store_true",
        help="Print the specification of the JSON data structure",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")

    args = parser.parse_args()

    try:
        if args.schema:
            FlatTree.schema()
            sys.exit(0)

        # Caution: eval can be risky with untrusted input
        node_name = eval(args.node_name)
        fallback_node_name = (
            eval(args.fallback_node_name) if args.fallback_node_name else None
        )

        if args.file == sys.stdin and sys.stdin.isatty():
            print(
                "No JSON data provided. Please provide a file or pipe data into this program.",
                file=sys.stderr,
            )
            parser.print_usage()
            sys.exit(1)
        tree = DictTree(
            data=json.load(args.file), mapping_key=args.mapping_key
        )
        tree.verify_integrity()

        if args.output:
            tree.save(
                outfile=args.output,
                node_name=node_name,
                fallback_node_name=fallback_node_name,
            )
        else:
            print(
                tree.to_string(
                    node_name=node_name, fallback_node_name=fallback_node_name
                )
            )

    except Exception as e:
        logging.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
