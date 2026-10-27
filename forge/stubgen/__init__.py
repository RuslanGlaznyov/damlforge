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

from pathlib import Path

from forge.stubgen.dar import load_archives
from forge.stubgen.exports import export_items
from forge.stubgen.render import ModuleStub, snake


def _selected(main, archives, modules) -> list:
    if not modules:
        return list(main.package.modules)
    found: dict = {}
    for mod in (m for arc in archives for m in arc.package.modules):
        if str(mod.name) in modules:
            found.setdefault(str(mod.name), mod)
    if missing := set(modules) - set(found):
        raise ValueError(f"modules not found in the DAR: {', '.join(sorted(missing))}")
    return [found[name] for name in sorted(found)]


def _python_names(stub: ModuleStub, name: str) -> set:
    return {n for n in (name, snake(name)) if n in stub.rendered}


def _reexports(stubs: dict, sources: dict) -> None:
    for name, stub in stubs.items():
        reexports: dict = {}
        for kind, item in export_items(sources.get(name, "")) or ():
            if kind == "module":
                if item in stubs and item != name:
                    reexports.setdefault(item, set()).update(stubs[item].rendered)
            elif not _python_names(stub, item):
                owners = ((o, _python_names(s, item)) for o, s in stubs.items() if o != name)
                if owner := next(((o, found) for o, found in owners if found), None):
                    reexports.setdefault(owner[0], set()).update(owner[1])
        stub.reexports = reexports


def generate_stubs(input_path: Path, output_dir: Path, dpm_path=None, modules=()) -> tuple:
    main, archives, sources = load_archives(input_path, dpm_path)

    types: dict = {}
    values: dict = {}
    for mod in (m for arc in archives for m in arc.package.modules):
        name = str(mod.name)
        types.update({(name, str(dt.name)): dt for dt in mod.data_types})
        types.update({("syn", name, ".".join(s.name.segments)): s for s in mod.synonyms})
        values.update({(name, ".".join(v.name_with_type.name)): v for v in mod.values})

    stubs = {str(m.name): ModuleStub(m, types, values) for m in _selected(main, archives, modules)}
    rendered = {name: stub.render() for name, stub in stubs.items()}
    _reexports(stubs, sources)

    written: list = []
    skipped: list = []
    for name, stub in stubs.items():
        source = stub.render() if stub.reexports else rendered[name]
        skipped += stub.skipped
        if source is not None:
            target = output_dir.joinpath(*stub.module.name.segments).with_suffix(".vy")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source)
            written.append(target)
    return written, skipped
