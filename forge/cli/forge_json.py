#!/usr/bin/env python3

import argparse
import json
import sys
import warnings
from pathlib import Path, PurePath
from typing import Any, Callable, Hashable, Optional
from forge.ast.parse import parse_to_ast

def _parse_cli_args():
    return _parse_args(sys.argv[1:])

def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="DamlForge programming language for .VY - DAML-JSON AST compiler",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "input_file",
        help="JSON file to compile from. If none is given, DamlForge will receive it from stdin.",
        nargs="?",
    )
    parser.add_argument(
        "-o",
        help="Filename to save JSON output to. If the file exists it will be overwritten.",
        default=None,
        dest="output_file",
    )
    parser.add_argument("--pretty-json", help="Output JSON in pretty format.", action="store_true")
    parser.add_argument(
        "--traceback",
        help="Show python traceback on error instead of returning JSON",
        action="store_true",
    )

    args = parser.parse_args(argv)
    if args.input_file:
        with Path(args.input_file).open() as fh:
            input_vy = fh.read()
    else:
        input_vy = "".join(sys.stdin.read()).strip()

    try:
        result = compile_json(input_vy)
    except Exception as exc:
        if args.traceback:
            raise
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(1)

    output_json = json.dumps(
        result,
        indent=2 if args.pretty_json else None,
        sort_keys=True,
        default=str,
    )

    if args.output_file is not None:
        output_path = Path(args.output_file).resolve()
        with output_path.open("w") as fh:
            fh.write(output_json)
        print(f"Results saved to {output_path}")
    else:
        print(output_json)

def compile_json(
    input_vy: str,
) -> dict:
    ast = parse_to_ast(input_vy)
    return ast.to_dict()


if __name__ == "__main__":
    _parse_cli_args()
