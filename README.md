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

Installing the wheel puts a `forge` command on your `PATH`:

```bash
forge --help
```

```bash
forge path/to/file.vy -o out/              # .vy -> .daml, writes out/<Module>.daml
forge path/to/vy_source_dir -o out/        # compiles every .vy under a directory, mirroring its structure
forge --dar path/to/vy_source_dir -o out/  # .vy -> .daml -> real .dar (requires `dpm` on PATH)
forge --json path/to/file.vy               # .vy -> JSON AST, printed to stdout
```

Add `--traceback` to any of the above to get a Python traceback instead of a JSON error on compile failure - useful while debugging a new `.vy` file.

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
