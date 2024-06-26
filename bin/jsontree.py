#!/usr/bin/env python3

import argparse
import json
import logging
import sys
import textwrap

from AlgoTree.dicttree import DictTree


def show_json_spec():
    print(
        textwrap.dedent(
            f"""
        The JSON data should have the following structure:
                                    
            {{
                # Meta-data (optional key-value pairs)
                ...

                '<mapping_key>': {{
                    '<node_key>': {{
                        # Key of the parent node
                        'parent': '<parent_node_key>',
                    
                        # Additional payload data
                        ... 
                    }},
                    
                    # Key-value pairs or other nodes
                    ...
                }}
            }}
        """
        )
    )


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Render a generic tree from JSON data",
            formatter_class=argparse.RawTextHelpFormatter,
        )
        parser.add_argument(
            "--flatten",
            help="Flatten the tree (list of paths)",
            action="store_true",
        )
        parser.add_argument(
            "file",
            nargs="?",
            type=argparse.FileType("r"),
            default=sys.stdin,
            help="Path to JSON file",
        )
        parser.add_argument(
            "--log",
            help="Log level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        )
        parser.add_argument("--output", help="Output file name")
        parser.add_argument(
            "--fallback-node-name",
            type=str,
            help="Fallback function to generate node names",
        )
        parser.add_argument(
            "--node-name",
            help="Lambda expression to generate node names from a node, defaults to `lambda node: node.name`",
            default="lambda node: node.name",
            type=str,
        )
        parser.add_argument(
            "--json-spec",
            action="store_true",
            help="Specification of the JSON data",
        )
        parser.add_argument(
            "--version", action="version", version="%(prog)s 1.0"
        )
        parser.add_argument(
            "--mapping-key",
            default="mapping",
            type=str,
            help="The key that maps to the structure of the tree",
        )
        parser.add_argument(
            "--size", help="Size of the tree", action="store_true"
        )
        parser.add_argument("--siblings", help="Show siblings", type=str)
        parser.add_argument(
            "--children", help="Show children", type=str, nargs=1
        )
        parser.add_argument("--parent", help="Show parent", type=str)
        parser.add_argument("--ancestors", help="Show ancestors", type=str)
        parser.add_argument(
            "--descendants", help="Show descendants", type=str, nargs=1
        )
        parser.add_argument(
            "--has-node", help="Check if node exists", nargs=1, type=str
        )
        parser.add_argument(
            "--get-node", help="Get node by key", type=str, nargs="?"
        )
        parser.add_argument(
            "--has-edge", help="Check if edge exists", type=str, nargs=2
        )
        parser.add_argument(
            "--is-connected",
            help="Check if two nodes are connected",
            type=str,
            nargs=2,
        )
        parser.add_argument(
            "--get-path",
            help="Find the path between two nodes",
            type=str,
            nargs=2,
        )

        epilog = textwrap.dedent(
            f"""Example usage: ./{parser.prog} ./export/conversations.json

                The JSON file should contain a dictionary with a "mapping" key
                containing the tree data. To see the expected structure of the
                JSON data, invoke the --json-spec option."""
        )

        args = parser.parse_args()

        logging.basicConfig(level=args.log)
        logging.debug(f"Reading JSON data from {args.file.name}")

        if args.json_spec:
            show_json_spec()
            sys.exit(0)

        node_name = eval(args.node_name)
        fallback_node_name = (
            eval(args.fallback_node_name) if args.fallback_node_name else None
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
                        node_name=node_name,
                        fallback_node_name=fallback_node_name,
                    ),
                    indent=2,
                )
            )
            sys.exit(1)

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
