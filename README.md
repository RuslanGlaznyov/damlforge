# DamlForge

DamlForge compiles `.vy` files (Python syntax, Vyper-flavored keywords) into real Daml/Canton `.daml` source. See [`.claude/skills/damlforge-vy-lang/`](.claude/skills/damlforge-vy-lang/SKILL.md) for the full language reference.

## Installing the wheel

Releases are built by CI on every `v*.*.*` tag and attached to the corresponding [GitHub Release](https://github.com/noders-team/damlforge/releases) as `forge-<version>-py3-none-any.whl`.

Download the wheel for the version you want, then install it into your own virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate          # .venv\Scripts\activate on Windows
pip install forge-<version>-py3-none-any.whl
```

No source checkout, no dev dependencies, no repo access needed - the wheel is fully self-contained.

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
Install its extra dependency with `pip install 'forge[stubgen]'`. It accepts either a
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
`RelTime`. `datetime.now()` compiles to the ledger effect `getTime`, so use it
only inside a choice or a function marked `@ledger_effect`.

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
