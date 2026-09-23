import json
from pathlib import Path

from loguru import logger

from forge.ast.parse import parse_to_ast
from forge.codegen import daml_module_name, generate_daml
from forge.ir import lower_module
from forge.semantics import analyze_module


def _compile_one(file: Path, output_dir: Path, pretty_json: bool) -> None:
    logger.info(f"Processing file: {file}")

    path = file.resolve()
    source = file.read_text()
    module = parse_to_ast(source, module_path=path.name, resolved_path=str(path))
    import_graph = analyze_module(module)
    ir = lower_module(module, import_graph=import_graph)
    module_name = daml_module_name(path.stem)
    daml_source, source_map = generate_daml(ir, module_name=module_name)

    output_file = output_dir / (module_name + ".daml")
    with output_file.open("w") as fh:
        logger.info(f"writing DAML output to: {output_file}")
        fh.write(daml_source)
    output_map_file = output_dir / (module_name + ".map.json")
    with output_map_file.open("w") as fh:
        logger.info(f"writing source map to: {output_map_file}")
        json.dump(source_map, fh, indent=2 if pretty_json else None, sort_keys=True, default=str)


def compile_daml(
    input_path: Path,
    output_dir: Path,
    pretty_json: bool = False,
    ignore_errors: bool = True,
    traceback: bool = False,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    files = [input_path] if input_path.is_file() else sorted(input_path.glob("*.vy"))

    for file in files:
        try:
            _compile_one(file, output_dir, pretty_json)
        except Exception as e:
            if traceback:
                raise
            logger.error(f"Error processing file {file}: {e}")
            if not ignore_errors:
                raise SystemExit(1)
