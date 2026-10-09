from pathlib import Path

from forge.stubgen.dar import load_archives
from forge.stubgen.render import ModuleStub


def _indexes(archives):
    types = {}
    values = {}
    for arc in archives:
        for mod in arc.package.modules:
            for dt in mod.data_types:
                types[(str(mod.name), str(dt.name))] = dt
            for val in mod.values:
                values[(str(mod.name), ".".join(val.name_with_type.name))] = val
    return types, values


def generate_stubs(input_path: Path, output_dir: Path, dpm_path=None):
    main, archives = load_archives(input_path, dpm_path)
    types, values = _indexes(archives)
    written = []
    skipped = []
    for mod in main.package.modules:
        stub = ModuleStub(mod, types, values)
        source = stub.render()
        skipped.extend(stub.skipped)
        if source is None:
            continue
        target = output_dir.joinpath(*mod.name.segments).with_suffix(".vy")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source)
        written.append(target)
    return written, skipped
