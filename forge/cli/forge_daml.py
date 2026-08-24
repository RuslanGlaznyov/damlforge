#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path
from forge.semantics import analyze_module
from forge.ast.parse import parse_to_ast
from forge.ir import lower_module
from forge.codegen import generate_daml
from loguru import logger

def _parse_cli_args():
    return _parse_args(sys.argv[1:])

def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="DamlForge programming language for .VY - DAML-JSON Codegen compiler",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "input_dir",
        help=".vy files to compile from. If none is given, DamlForge will receive it from stdin.",
        nargs="?",
    )
    parser.add_argument(
        "-o",
        help="Filename to save DAML output to. If the file exists it will be overwritten.",
        default=None,
        dest="output_dir",
    )
    parser.add_argument("--pretty-json", help="Output JSON in pretty format.", action="store_true")
    parser.add_argument(
        "--traceback",
        help="Show python traceback on error instead of returning JSON",
        action="store_true",
    )
    
    args = parser.parse_args(argv)
    
    if args.input_dir is None:
        logger.error("Error: No input path provided.")
        sys.exit(1)
    
    output_dir = Path(args.input_dir)
    if args.output_dir is not None:
        output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    folder_path = Path(args.input_dir)
    for file in sorted(folder_path.glob("*.vy")):
        logger.info(f"Processing file: {file}")
        path = Path(file).resolve()
        source = Path(file).read_text()
        module = parse_to_ast(source, module_path=path.name, resolved_path=str(path))
        analyze_module(module)
        ir = lower_module(module)
        daml_source, source_map = generate_daml(ir)
        
        output_file = output_dir / (path.stem + ".daml")
        with output_file.open("w") as fh:
             logger.info(f"writing DAML output to: {output_file}")
             fh.write(daml_source)
        output_map_file = output_dir / (path.stem + ".map.json")
        with output_map_file.open("w") as fh:
             logger.info(f"writing source map to: {output_map_file}")
             json.dump(source_map, fh, indent=2 if args.pretty_json else None, sort_keys=True, default=str)


if __name__ == "__main__":
    _parse_cli_args()
