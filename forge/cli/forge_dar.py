#!/usr/bin/env python3

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from loguru import logger

from forge.ast.parse import parse_to_ast
from forge.codegen import daml_module_name, generate_daml
from forge.ir import lower_module
from forge.semantics import analyze_module

_PACKAGE_NAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9]*(-[A-Za-z][A-Za-z0-9]*)*$")
_PACKAGE_VERSION_REGEX = re.compile(r"^(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*$")
_REQUIRED_PACKAGE_CONFIG_FIELDS = ("name", "source", "version", "dependencies")


class ProjectStructureError(ValueError):
    pass


def _parse_cli_args():
    return _parse_args(sys.argv[1:])


def _parse_args(argv):
    parser = argparse.ArgumentParser(
        description="DamlForge programming language for .VY - build a .dar via the DPM manager",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "input_dir",
        help="Path to a Daml project (a directory containing daml.yaml) whose .vy files "
        "should be compiled to Daml and packaged into a .dar.",
    )
    parser.add_argument(
        "-o",
        help="Path to save the built .dar to. Defaults to <input_dir>/<name>-<version>.dar.",
        default=None,
        dest="output_dar",
    )
    parser.add_argument(
        "--dpm",
        help="Path to the dpm executable. Defaults to searching PATH, then ~/.dpm/bin/dpm.",
        default=None,
        dest="dpm_path",
    )
    parser.add_argument(
        "--traceback",
        help="Show python traceback on error instead of a short message.",
        action="store_true",
    )

    args = parser.parse_args(argv)

    try:
        dar_path = build_dar(
            input_dir=Path(args.input_dir),
            output_dar=Path(args.output_dar).resolve() if args.output_dar else None,
            dpm_path=args.dpm_path,
        )
    except Exception as e:
        if args.traceback:
            raise
        logger.error(f"Error building .dar: {e}")
        sys.exit(1)

    logger.info(f"Built .dar: {dar_path}")


def _resolve_dpm_path(dpm_path):
    if dpm_path is not None:
        return dpm_path
    found = shutil.which("dpm")
    if found is not None:
        return found
    fallback = Path.home() / ".dpm" / "bin" / "dpm"
    if fallback.is_file():
        return str(fallback)
    raise RuntimeError(
        "Could not find the `dpm` executable on PATH or at ~/.dpm/bin/dpm. "
        "Install DPM (https://docs.digitalasset.com/build/3.4/dpm/dpm.html) or pass --dpm."
    )


def _load_package_config(daml_yaml: Path) -> dict:
    try:
        config = yaml.safe_load(daml_yaml.read_text())
    except yaml.YAMLError as e:
        raise ProjectStructureError(f"{daml_yaml} is not valid YAML: {e}") from e
    if not isinstance(config, dict):
        raise ProjectStructureError(f"{daml_yaml} must contain a YAML mapping")
    return config


def check_package_config(config: dict, daml_yaml: Path) -> None:
    missing = [field for field in _REQUIRED_PACKAGE_CONFIG_FIELDS if field not in config]
    if missing:
        raise ProjectStructureError(f"{daml_yaml} is missing required field(s): {', '.join(missing)}")

    name = str(config["name"])
    if not _PACKAGE_NAME_REGEX.match(name):
        raise ProjectStructureError(
            f"Invalid package name in {daml_yaml}: {name!r}. Package names should have the "
            f"format {_PACKAGE_NAME_REGEX.pattern}."
        )

    version = str(config["version"])
    if not _PACKAGE_VERSION_REGEX.match(version):
        raise ProjectStructureError(
            f"Invalid package version in {daml_yaml}: {version!r}. Package versions should "
            f"have the format {_PACKAGE_VERSION_REGEX.pattern}."
        )

    if not isinstance(config["dependencies"], list) or not config["dependencies"]:
        raise ProjectStructureError(f"{daml_yaml}: `dependencies` must be a non-empty list")


def check_data_dependencies(config: dict, project_dir: Path, daml_yaml: Path) -> None:
    for dep in config.get("data-dependencies") or []:
        dep_path = project_dir / dep
        if not dep_path.is_file():
            raise ProjectStructureError(
                f"{daml_yaml} declares data-dependency {dep!r}, but no such file exists at {dep_path}"
            )


def check_project_structure(project_dir: Path) -> dict:
    daml_yaml = project_dir / "daml.yaml"
    if not daml_yaml.is_file():
        raise ProjectStructureError(
            f"{project_dir} is not a Daml project: no daml.yaml found. DamlForge compiles "
            "into an existing Daml project - set one up (e.g. via `daml new`, or copy an "
            "existing one) with its daml.yaml/lib checked in alongside the .vy sources."
        )

    config = _load_package_config(daml_yaml)
    check_package_config(config, daml_yaml)
    check_data_dependencies(config, project_dir, daml_yaml)
    return config


def build_dar(
    input_dir: Path,
    output_dar: "Path | None" = None,
    dpm_path: "str | None" = None,
) -> Path:
    input_dir = input_dir.resolve()
    if not input_dir.is_dir():
        raise ValueError(f"Input path is not a directory: {input_dir}")

    config = check_project_structure(input_dir)

    vy_files = sorted(input_dir.glob("*.vy"))
    if not vy_files:
        raise ValueError(f"No .vy files found in: {input_dir}")

    resolved_dpm = _resolve_dpm_path(dpm_path)
    source_dir = (input_dir / str(config["source"])).resolve()
    source_dir.mkdir(parents=True, exist_ok=True)

    package_name = config["name"]
    package_version = config["version"]
    resolved_output = (
        output_dar
        if output_dar is not None
        else input_dir / f"{package_name}-{package_version}.dar"
    )

    for file in vy_files:
        logger.info(f"Compiling: {file}")
        source = file.read_text()
        module = parse_to_ast(source, module_path=file.name, resolved_path=str(file))
        import_graph = analyze_module(module)
        ir = lower_module(module, import_graph=import_graph)
        mod_name = daml_module_name(file.stem)
        daml_source, _ = generate_daml(ir, module_name=mod_name)
        (source_dir / f"{mod_name}.daml").write_text(daml_source)

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Running dpm build (package: {package_name}, version: {package_version})")
    result = subprocess.run(
        [resolved_dpm, "build", "-o", str(resolved_output)],
        cwd=input_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"dpm build failed (exit {result.returncode}):\n{result.stdout}\n{result.stderr}")
    logger.info(result.stdout.strip())

    if not resolved_output.is_file():
        raise RuntimeError(f"dpm build reported success but no .dar was found at: {resolved_output}")

    return resolved_output


if __name__ == "__main__":
    _parse_cli_args()
