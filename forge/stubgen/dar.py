# Copyright 2026 Noders Team
# Author: Artem Bogomaz <artembogomaz@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    from forge.stubgen.lf2 import install

    install()
    return DarFile


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
    main_dalf = ""
    with zipfile.ZipFile(dar) as zf:
        raw = zf.read("META-INF/MANIFEST.MF").decode()
    for line in re.sub(r"\r?\n ", "", raw).splitlines():
        if line.startswith("Main-Dalf:"):
            main_dalf = line.split(":", 1)[1].strip()
            break
    if not main_dalf:
        raise ValueError(f"{dar} has no Main-Dalf entry in its manifest")

    main_id = Path(main_dalf).stem.rsplit("-", 1)[-1]
    with _dar_file()(dar) as df:
        archives = df.archives()
    main = next((a for a in archives if a.hash == main_id), None)
    if main is None:
        raise ValueError(f"{dar} does not contain its main package {main_id}")

    sources = {}
    root = main_dalf.split("/", 1)[0]
    with zipfile.ZipFile(dar) as zf:
        for name in zf.namelist():
            if name.startswith(f"{root}/") and name.endswith(".daml"):
                module = name[len(root) + 1 : -len(".daml")].replace("/", ".")
                sources[module] = zf.read(name).decode()

    return main, archives, sources


def load_archives(path: Path, dpm_path=None):
    if path.is_file():
        return _read_dar(path)
    with tempfile.TemporaryDirectory() as tmp:
        return _read_dar(_build_dar(path.resolve(), Path(tmp), dpm_path))
