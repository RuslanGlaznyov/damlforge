# DamlForge

DamlForge compiles `.vy` files (Python syntax, Vyper-flavored keywords) into real Daml/Canton `.daml` source. See [`.claude/skills/damlforge-vy-lang/`](.claude/skills/damlforge-vy-lang/SKILL.md) for the full language reference.

## User guide

The guide in [`docs/guide/`](docs/guide) walks through DamlForge from setup to
packaging. Every example in it compiles with `forge dar` and is covered by a
passing Daml Script test.

| # | Page | Covers |
|---|---|---|
| 1 | [Development Environment Setup](docs/guide/01-dev-environment.md) | Installing DPM and DamlForge, creating a project, editor setup, day-to-day commands |
| 2 | [Language Fundamentals](docs/guide/02-language-fundamentals.md) | Types, structs, enums, variants, `Optional`, functions, control flow, dates, imports |
| 3 | [Compiler Errors](docs/guide/03-compiler-errors.md) | Every `DF` error code, with the message, cause, and fix |
| 4 | [Contract Templates](docs/guide/04-contract-templates.md) | Templates, signatories, observers, `ensure`, testing with Daml Script |
| 5 | [Choices](docs/guide/05-choices.md) | Choices as methods and as delegation, updating a contract in place, consuming and non-consuming choices, a simple cash model |
| 6 | [Design Patterns](docs/guide/06-design-patterns.md) | Propose-accept, delegation, authorization, locking, multi-party agreements |
| 7 | [Working with Time](docs/guide/07-working-with-time.md) | `datetime` support, ledger time, deadlines and time windows, `setTime`/`passTime` |
| 8 | [Contract Keys](docs/guide/08-contract-keys.md) | `key` and `maintainer`, by-key lookups, Daml 3.5 requirements |
| 9 | [Interfaces](docs/guide/09-interfaces.md) | Declaring and implementing interfaces, views, converting contract IDs |
| 10 | [Building and Packaging](docs/guide/10-building-packaging.md) | `forge dar`, `daml.yaml` settings, multi-package projects, DAR contents |
| 11 | [Variants](docs/guide/11-variants.md) | Constructor styles, recursive and generic variants, current limitations |

## Installing

DamlForge is published on PyPI as `damlforge`. It installs the `forge` command and the `forge` Python package:

```bash
python -m venv .venv
source .venv/bin/activate          # .venv\Scripts\activate on Windows
pip install damlforge
```

### Using DamlForge in another project

Add DamlForge as a dependency of the project that holds your `.vy` contracts.

With pip, pin it in `requirements.txt`:

```text
damlforge==<version>
```

Use `damlforge[stubgen]==<version>` instead if you also run `forge stubs`. Then install and build:

```bash
pip install -r requirements.txt
forge dar path/to/daml_project -o out.dar
```

With Poetry, add it to a dev group, since it's only needed at build time:

```bash
poetry add --group dev damlforge@<version>
poetry add --group dev 'damlforge[stubgen]@<version>'   # if you also run forge stubs
```

This records it in your `pyproject.toml`:

```toml
[tool.poetry.group.dev.dependencies]
damlforge = { version = "<version>", extras = ["stubgen"] }
```

Leave out `extras` if you don't need `forge stubs`. Run the compiler through Poetry's environment:

```bash
poetry install
poetry run forge dar path/to/daml_project -o out.dar
```

The stubs for the Daml standard library (`DA.*`, `GHC.*`), Splice (`Splice.*`), `forge.models`, and `forge.builtins` ship inside the package. Once it's installed, `.vy` files import them directly, with no extra path setup:

```python
from DA.List import sort
from forge.builtins.daml_lang import create
from forge.models import Party, choice, template
```

Splice stubs also need the matching Splice DAR in `data-dependencies` in `daml.yaml`. See [Development Environment Setup](docs/guide/01-dev-environment.md#as-a-dependency-of-your-own-project) and [Building and Packaging](docs/guide/10-building-packaging.md#using-other-packages-from-vy).

### Installing from GitHub Releases

Releases are also built by CI on every `v*.*.*` tag and attached to the corresponding [GitHub Release](https://github.com/noders-team/damlforge/releases) as `damlforge-<version>-py3-none-any.whl`, which installs with `pip install damlforge-<version>-py3-none-any.whl`.

### Publishing to PyPI

`.github/workflows/publish-pypi.yml` is started by hand from the Actions tab (**Run workflow**) with the version to publish. It builds the sdist and wheel with that version and uploads them through PyPI trusted publishing, so no API token is stored in the repository.

## Using it

Installing the wheel puts a `forge` command on your `PATH`. It's a [Click](https://click.palletsprojects.com/) CLI with a subcommand per compile target:

```bash
forge --help          # top-level usage and subcommand list
forge --version       # installed forge version
forge daml --help     # per-subcommand usage (also: forge dar, forge json, forge stubs)
```

```bash
forge daml path/to/file.vy -o out/          # .vy -> out/<Module>.daml + out/<Module>.map.json
forge daml path/to/vy_source_dir -o out/    # compiles top-level .vy files in the directory
forge dar path/to/vy_project -o out.dar     # compile the project and build a real .dar
forge json path/to/file.vy --pretty-json    # .vy -> JSON AST, printed to stdout
forge stubs input.dar -o generated/         # .dar -> generated .vy stubs
```

`forge <path> [options]` (no subcommand) is shorthand for `forge daml <path> [options]`.

`forge daml` writes a JSON source map next to each `.daml` file. Directory input is
intentionally non-recursive; `forge dar` recursively compiles every `.vy` below the
project's configured `source` directory. Use `--no-i` with `forge daml` to stop at the
first compile error; the default is to continue with the remaining files. Add
`--traceback` to any subcommand for a Python traceback instead of a short error message.

## Daml projects and DARs

`forge dar` compiles into an existing Daml project. The project must contain a
`daml.yaml` with `name`, `source`, `version`, and a non-empty `dependencies` list.
`data-dependencies` are supported and are checked before invoking DPM. Generated
`.daml` files are written under the configured source directory, then DamlForge runs
`dpm build` to produce the DAR.

By default DPM is searched for on `PATH`, then at `~/.dpm/bin/dpm`; use `--dpm PATH`
when it is installed elsewhere. For example:

```bash
forge dar examples/splice-util-batched-markers \
  -o examples/splice-util-batched-markers/splice-util-batched-markers-current.dar
```

When validating tests that exercise templates from data dependencies, use the Daml
test runner's all-packages mode:

```bash
daml test --all
```

## Generating `.vy` stubs

The optional stub generator reconstructs supported Daml-LF declarations from a DAR.
Install its extra dependency with `pip install 'damlforge[stubgen]'`. It accepts either a
DAR file or a Daml project directory (the latter is built with DPM first):

```bash
forge stubs path/to/package.dar -o generated/
forge stubs path/to/daml_project -o generated/ --dpm /path/to/dpm
forge stubs path/to/package.dar --module Some.Module --module Other.Module
```

The `--module` option may be repeated and selects modules from the main package or
its dependencies. Unsupported declarations are skipped and reported by the command.

## Variants

Use `@variant` on a class to define a Daml variant. Each method declares one
constructor; its parameters are the constructor payload:

```python
from datetime import datetime

from forge.models import Party, variant_record

@variant
class Result:
    def Accepted(value: Party): pass
    def Cancelled(): pass

    @variant_record
    def Deferred(reason: str, retry_at: datetime): pass
```

This generates positional constructors for ordinary methods and a named-field
constructor for the method marked `@variant_record`:

```daml
data Result
  = Accepted Party
  | Cancelled
  | Deferred with
      reason : Text
      retry_at : Time
  deriving (Eq, Show)
```

`@variant` is a DamlForge class marker, like `@template`, and does not need an
import. `@variant_record` is an ordinary method decorator and must be imported.
Use it only when the Daml constructor must use `with` fields; otherwise the
parameter names are not part of the generated Daml API.

Generated derivations follow `daml.yaml`: Daml 3.4 uses inferred serializability;
Daml 3.5 adds `Serializable` only when `--explicit-serializable=yes` is enabled.

See [Variants](docs/guide/11-variants.md) for constructing and comparing values,
recursive and generic variants, and what isn't supported yet.

## Enums

Use Python's `Enum` syntax. Members must be bare names or use `auto()`; explicit
values are rejected. Only member names become Daml constructors:

```python
from enum import Enum, auto

class Status(Enum):
    PENDING = auto()
    COMPLETE = auto()
```

This generates `data Status = PENDING | COMPLETE` in Daml.

## Dates and time

Use Python's standard `datetime` types directly in `.vy` contracts; do not
import `Date`, `Timestamp`, or `RelTime` from `forge.models`:

```python
from datetime import date, datetime, time, timedelta, timezone

def epoch() -> date:
    return date(1970, 1, 1)

def next_week(start: datetime) -> datetime:
    return start + timedelta(days=7)

def midnight(value: date) -> datetime:
    return datetime.combine(value, time())

def from_seconds(seconds: int) -> datetime:
    return datetime.fromtimestamp(seconds, timezone.utc)
```

`date`, `datetime`, and `timedelta` compile to Daml `Date`, `Time`, and
`RelTime`. `datetime.now()` compiles to the Daml update operation `getTime`; DamlForge
infers the enclosing function's `Update` return type automatically.

Only these constructs are translated, not the whole `datetime` module. See
[Working with Time](docs/guide/07-working-with-time.md) for the full list of
supported forms, the `DA.Date` helpers to use instead of the rest, and ledger time.

## Upgrading

Upgrade in place:

```bash
pip install -U damlforge==<new-version>
```

If you installed the old `forge` wheel from GitHub Releases, run `pip uninstall forge` first, since the distribution was renamed to `damlforge`.

## Building the wheel yourself

If you have the source checked out:

```bash
pip install build
python -m build          # or: make build
```

produces `dist/damlforge-<version>-py3-none-any.whl`, versioned from the nearest git tag (see `Makefile`'s `build`/`release` targets and `.github/workflows/build-wheel.yml`).

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

## License

DamlForge is licensed under the [Apache License, Version 2.0](LICENSE).

Copyright 2026 Noders Team. Author: Artem Bogomaz <artembogomaz@gmail.com>.
