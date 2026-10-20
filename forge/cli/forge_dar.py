import re
import shutil
import subprocess
from pathlib import Path

import yaml
from loguru import logger

from forge.ast.parse import parse_to_ast
from forge.codegen import daml_module_name, generate_daml
from forge.codegen.source_map import annotate_daml_output, with_source_file
from forge.daml_versions import DamlCodegenSettings
from forge.exceptions import tag_exceptions
from forge.ir import lower_module
from forge.semantics import analyze_module

_PACKAGE_NAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9]*(-[A-Za-z][A-Za-z0-9]*)*$")
_PACKAGE_VERSION_REGEX = re.compile(r"^(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*$")
_REQUIRED_PACKAGE_CONFIG_FIELDS = ("name", "source", "version", "dependencies")


class ProjectStructureError(ValueError):
    pass


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
        raise ProjectStructureError(
            f"{daml_yaml} is missing required field(s): {', '.join(missing)}"
        )

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
                f"{daml_yaml} declares data-dependency {dep!r}, but no such file "
                f"exists at {dep_path}"
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
    input_dir: Path, output_dar: "Path | None" = None, dpm_path: "str | None" = None
) -> Path:
    input_dir = input_dir.resolve()
    if not input_dir.is_dir():
        raise ValueError(f"Input path is not a directory: {input_dir}")

    if output_dar is not None:
        if output_dar.is_dir():
            raise ValueError(
                f"-o must be a path to the .dar FILE to write, not a directory: {output_dar}"
            )
        if output_dar.suffix != ".dar":
            raise ValueError(f"-o must end in `.dar`: {output_dar}")

    config = check_project_structure(input_dir)
    codegen_settings = DamlCodegenSettings.from_config(config)

    source_dir = (input_dir / str(config["source"])).resolve()
    source_dir.mkdir(parents=True, exist_ok=True)

    vy_files = sorted(source_dir.rglob("*.vy"))
    if not vy_files:
        raise ValueError(f"No .vy files found under: {source_dir}")

    resolved_dpm = _resolve_dpm_path(dpm_path)

    package_name = config["name"]
    package_version = config["version"]
    resolved_output = (
        output_dar
        if output_dar is not None
        else input_dir / f"{package_name}-{package_version}.dar"
    )

    source_maps = {}
    for file in vy_files:
        logger.info(f"Compiling: {file}")
        source = file.read_text()
        rel = file.relative_to(source_dir)
        module = parse_to_ast(source, module_path=str(rel), resolved_path=str(file))
        with tag_exceptions(module):
            import_graph = analyze_module(module)
            ir = lower_module(module, import_graph=import_graph)
            mod_stem = daml_module_name(rel.stem)
            mod_name = ".".join((*rel.parent.parts, mod_stem))
            daml_source, source_map = generate_daml(
                ir, module_name=mod_name, settings=codegen_settings
            )
        out_dir = source_dir / rel.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        daml_file = out_dir / f"{mod_stem}.daml"
        source_maps[str(daml_file.relative_to(input_dir))] = with_source_file(source_map, file)
        daml_file.write_text(daml_source)

    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Running dpm build (package: {package_name}, version: {package_version})")
    result = subprocess.run(
        [resolved_dpm, "build", "-o", str(resolved_output)],
        cwd=input_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        dpm_output = annotate_daml_output(
            f"{result.stdout}\n{result.stderr}", source_maps
        )
        raise RuntimeError(
            f"dpm build failed (exit {result.returncode}):\n{dpm_output}"
        )
    logger.info(result.stdout.strip())

    if not resolved_output.is_file():
        raise RuntimeError(
            f"dpm build reported success but no .dar was found at: {resolved_output}"
        )

    return resolved_output
