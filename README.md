# DamlForge

DamlForge compiles `.vy` files (Python syntax, Vyper-flavored keywords) into real Daml/Canton `.daml` source. See [`.claude/skills/damlforge-vy-lang/`](.claude/skills/damlforge-vy-lang/SKILL.md) for the full language reference.

## Installing the wheel

Releases are built by CI on every `v*.*.*` tag and attached to the corresponding [GitHub Release](https://github.com/noders-team/damlforge/releases) as `forge-<version>-py3-none-any.whl`.

Download the wheel for the version you want, then install it into your own virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate          # .venv\Scripts\activate on Windows
pip install forge-1.0.0-py3-none-any.whl
```

No source checkout, no dev dependencies, no repo access needed - the wheel is fully self-contained.

## Using it

Installing the wheel puts a `forge` command on your `PATH`. It's a [Click](https://click.palletsprojects.com/) CLI with a subcommand per compile target:

```bash
forge --help          # top-level usage and subcommand list
forge --version       # installed forge version
forge daml --help     # per-subcommand usage (also: forge dar --help, forge json --help)
```

```bash
forge daml path/to/file.vy -o out/          # .vy -> .daml, writes out/<Module>.daml
forge daml path/to/vy_source_dir -o out/    # compiles every top-level .vy in a directory into out/
forge dar path/to/vy_project -o out.dar     # .vy -> .daml -> real .dar (requires `dpm` on PATH)
forge json path/to/file.vy --pretty-json    # .vy -> JSON AST, printed to stdout
```

`forge <path> [options]` (no subcommand) is shorthand for `forge daml <path> [options]`.

Add `--traceback` to any subcommand to get a Python traceback instead of a short error message on compile failure - useful while debugging a new `.vy` file.

## Upgrading

Uninstall the old wheel first if you installed into a long-lived environment, then install the new one:

```bash
pip uninstall forge
pip install forge-<new-version>-py3-none-any.whl
```

Or just point a fresh venv at the new wheel, per above.

## Building the wheel yourself

If you have the source checked out:

```bash
pip install build
python -m build          # or: make build
```

produces `dist/forge-<version>-py3-none-any.whl`, versioned from the nearest git tag (see `Makefile`'s `build`/`release` targets and `.github/workflows/build-wheel.yml`).

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .              # installs forge + runtime deps (click, etc.) in editable mode
pip install --group test      # pytest + friends
pip install --group lint      # black/flake8/isort/mypy
```

`--group` needs `pip>=25.1` (`pip install -U pip` first if needed); otherwise install the pinned packages listed under `[dependency-groups]` in `pyproject.toml` directly.

With an editable install, `forge`/`python -m forge` picks up changes under `forge/` immediately - no reinstall needed:

```bash
forge --help
forge daml examples/basic/simple.vy -o /tmp/out && cat /tmp/out/Simple*.daml
```

Run the test suite and linters:

```bash
pytest -q      # or: make test
make lint      # mypy, black, flake8, isort in sequence
```
