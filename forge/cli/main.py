import json
import sys
from pathlib import Path

import click
from loguru import logger

from forge import __version__
from forge.cli.forge_dar import build_dar
from forge.cli.forge_daml import compile_daml
from forge.cli.forge_json import compile_json

_TRACEBACK_OPTION = click.option(
    "--traceback", is_flag=True, help="Show a Python traceback on error instead of a short message."
)
_PRETTY_JSON_OPTION = click.option(
    "--pretty-json", is_flag=True, help="Output JSON in pretty (indented) format."
)


class _DefaultCommandGroup(click.Group):
    def resolve_command(self, ctx, args):
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            args = ["daml", *args]
        return super().resolve_command(ctx, args)


@click.group(cls=_DefaultCommandGroup, invoke_without_command=True)
@click.version_option(__version__, "--version", "-V", prog_name="forge")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """DamlForge: compile .vy sources (Python/Vyper-flavored syntax) into Daml/Canton."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command("daml")
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "output_dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory to write DAML output to. Defaults next to INPUT_PATH.",
)
@_PRETTY_JSON_OPTION
@click.option(
    "--i/--no-i",
    "ignore_errors",
    default=True,
    help="Keep compiling remaining files after one fails (default: enabled).",
)
@_TRACEBACK_OPTION
def daml_cmd(
    input_path: Path,
    output_dir: "Path | None",
    pretty_json: bool,
    ignore_errors: bool,
    traceback: bool,
) -> None:
    """Compile .vy source(s) at INPUT_PATH (a file or a directory) into .daml."""
    resolved_output = (
        output_dir.resolve()
        if output_dir is not None
        else (input_path if input_path.is_dir() else input_path.parent)
    )
    try:
        compile_daml(
            input_path=input_path,
            output_dir=resolved_output,
            pretty_json=pretty_json,
            ignore_errors=ignore_errors,
            traceback=traceback,
        )
    except SystemExit as e:
        sys.exit(e.code)


@cli.command("dar")
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "-o",
    "output_dar",
    type=click.Path(path_type=Path),
    default=None,
    help="Path to save the built .dar to. Defaults to <input_dir>/<name>-<version>.dar.",
)
@click.option(
    "--dpm",
    "dpm_path",
    default=None,
    help="Path to the dpm executable. Defaults to searching PATH, then ~/.dpm/bin/dpm.",
)
@_TRACEBACK_OPTION
def dar_cmd(input_dir: Path, output_dar: "Path | None", dpm_path: str, traceback: bool) -> None:
    """Compile the .vy sources of a Daml project at INPUT_DIR and package them into a .dar."""
    try:
        dar_path = build_dar(
            input_dir=input_dir,
            output_dar=output_dar.resolve() if output_dar else None,
            dpm_path=dpm_path,
        )
    except Exception as e:
        if traceback:
            raise
        logger.error(f"Error building .dar: {e}")
        sys.exit(1)

    logger.info(f"Built .dar: {dar_path}")


@cli.command("json")
@click.argument(
    "input_file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=False
)
@click.option(
    "-o",
    "output_file",
    type=click.Path(path_type=Path),
    default=None,
    help="Filename to save JSON output to. If omitted, prints to stdout.",
)
@_PRETTY_JSON_OPTION
@_TRACEBACK_OPTION
def json_cmd(
    input_file: "Path | None", output_file: "Path | None", pretty_json: bool, traceback: bool
) -> None:
    """Compile a single .vy file (or stdin, if INPUT_FILE is omitted) to its JSON AST."""
    input_vy = input_file.read_text() if input_file is not None else sys.stdin.read().strip()

    try:
        result = compile_json(input_vy)
    except Exception as exc:
        if traceback:
            raise
        click.echo(json.dumps({"error": str(exc)}), err=True)
        sys.exit(1)

    output_json = json.dumps(result, indent=2 if pretty_json else None, sort_keys=True, default=str)

    if output_file is not None:
        resolved_output = output_file.resolve()
        resolved_output.write_text(output_json)
        click.echo(f"Results saved to {resolved_output}")
    else:
        click.echo(output_json)


if __name__ == "__main__":
    cli()
