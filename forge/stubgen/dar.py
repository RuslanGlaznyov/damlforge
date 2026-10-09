import re
import subprocess
import tempfile
import zipfile
from pathlib import Path

from forge.cli.forge_dar import _resolve_dpm_path


def _dar_file():
    try:
        from dazl.damlast.pkgfile import DarFile
    except ImportError as e:
        raise RuntimeError(
            "Stub generation needs `dazl` to decode Daml-LF: pip install 'forge[stubgen]'"
        ) from e
    return DarFile


def _main_package_id(dar: Path) -> str:
    with zipfile.ZipFile(dar) as zf:
        raw = zf.read("META-INF/MANIFEST.MF").decode()
    for line in re.sub(r"\r?\n ", "", raw).splitlines():
        if line.startswith("Main-Dalf:"):
            return Path(line.split(":", 1)[1].strip()).stem.rsplit("-", 1)[-1]
    raise ValueError(f"{dar} has no Main-Dalf entry in its manifest")


def _build_dar(project: Path, out_dir: Path, dpm_path) -> Path:
    if not (project / "daml.yaml").is_file():
        raise ValueError(f"{project} is neither a .dar file nor a Daml project (no daml.yaml)")
    dar = out_dir / f"{project.name}.dar"
    res = subprocess.run(
        [_resolve_dpm_path(dpm_path), "build", "-o", str(dar)],
        cwd=project,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        raise RuntimeError(f"dpm build failed (exit {res.returncode}):\n{res.stdout}\n{res.stderr}")
    return dar


def _read_dar(dar: Path):
    main_id = _main_package_id(dar)
    with _dar_file()(dar) as df:
        archives = df.archives()
    main = next((a for a in archives if a.hash == main_id), None)
    if main is None:
        raise ValueError(f"{dar} does not contain its main package {main_id}")
    return main, archives


def load_archives(path: Path, dpm_path=None):
    if path.is_file():
        return _read_dar(path)
    with tempfile.TemporaryDirectory() as tmp:
        return _read_dar(_build_dar(path.resolve(), Path(tmp), dpm_path))
