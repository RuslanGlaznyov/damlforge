"""Map Daml compiler diagnostics back to DamlForge source locations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional


@dataclass(frozen=True)
class DamlRange:
    start_line: int
    start_column: int
    end_line: int
    end_column: int


@dataclass(frozen=True)
class SourceLocation:
    file: str
    start_line: int
    start_column: Optional[int]
    end_line: Optional[int]
    end_column: Optional[int]

    def format(self) -> str:
        start = f"{self.file}:{self.start_line}"
        if self.start_column is not None:
            start += f":{self.start_column}"
        if self.end_line is None or self.end_line == self.start_line:
            return start
        end = str(self.end_line)
        if self.end_column is not None:
            end += f":{self.end_column}"
        return f"{start}-{end}"


@dataclass(frozen=True)
class _Mapping:
    generated_start_line: int
    generated_end_line: int
    source: SourceLocation
    name: str

    @property
    def generated_width(self) -> int:
        return self.generated_end_line - self.generated_start_line


_FILE_RE = re.compile(r"^File:\s*(?P<file>.+?)\s*$")
_RANGE_RE = re.compile(
    r"^Range:\s*(?P<start_line>\d+):(?P<start_column>\d+)"
    r"-(?P<end_line>\d+):(?P<end_column>\d+)\s*$"
)
_ANSI_ESCAPE_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_MESSAGE_CONTEXT_PREFIXES = (
    "in ",
    "probable cause:",
    "expected type:",
    "actual type:",
)


def _as_int(value) -> Optional[int]:
    return value if isinstance(value, int) else None


def _source_location(source: Mapping, source_file: Optional[str]) -> SourceLocation:
    return SourceLocation(
        file=str(source.get("file") or source_file or "<unknown source>"),
        start_line=int(source.get("startLine") or 1),
        start_column=(
            int(source["startColumn"]) + 1
            if _as_int(source.get("startColumn")) is not None
            else None
        ),
        end_line=_as_int(source.get("endLine")),
        end_column=(
            int(source["endColumn"]) + 1
            if _as_int(source.get("endColumn")) is not None
            else None
        ),
    )


def _mappings(source_map: Mapping) -> tuple[_Mapping, ...]:
    source_file = source_map.get("sourceFile")
    result = []
    for raw in source_map.get("mappings", ()):
        generated = raw.get("generated", {})
        source = raw.get("source", {})
        if not generated or not source:
            continue
        try:
            result.append(
                _Mapping(
                    generated_start_line=int(generated["startLine"]),
                    generated_end_line=int(generated["endLine"]),
                    source=_source_location(source, source_file),
                    name=str(raw.get("name") or ""),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return tuple(result)


def _file_matches(diagnostic_file: str, mapped_file: str) -> bool:
    diagnostic = diagnostic_file.replace("\\", "/")
    mapped = mapped_file.replace("\\", "/")
    return diagnostic == mapped or diagnostic.endswith(f"/{mapped}") or mapped.endswith(
        f"/{diagnostic}"
    )


def _symbol_matches(mapping: _Mapping, message: str) -> bool:
    if not mapping.name:
        return False
    haystack = message.casefold()
    parts = [part.casefold() for part in mapping.name.split(".") if part]
    return len(parts) > 1 and all(part in haystack for part in parts)


def map_daml_location(
    diagnostic_file: str,
    diagnostic_range: DamlRange,
    message: str,
    source_maps: Mapping[str, Mapping],
) -> Optional[SourceLocation]:
    """Map one Daml source range to the most specific generated-source range."""

    for mapped_file, source_map in source_maps.items():
        if not _file_matches(diagnostic_file, mapped_file):
            continue
        mappings = _mappings(source_map)
        candidates = [
            mapping
            for mapping in mappings
            if mapping.generated_start_line <= diagnostic_range.start_line <= mapping.generated_end_line
        ]
        if candidates:
            return min(candidates, key=lambda mapping: mapping.generated_width).source

        # Some damlc errors refer to generated desugaring at 1:1.  If the
        # diagnostic mentions a generated choice/template name, use its IR map.
        symbol_candidates = [mapping for mapping in mappings if _symbol_matches(mapping, message)]
        if symbol_candidates:
            return min(symbol_candidates, key=lambda mapping: mapping.generated_width).source
    return None


def _diagnostic_blocks(output: str):
    lines = output.splitlines()
    starts = [index for index, line in enumerate(lines) if _FILE_RE.match(line)]
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(lines)
        block = lines[start:end]
        file_match = _FILE_RE.match(block[0])
        range_match = next(
            (match for line in block[1:] if (match := _RANGE_RE.match(line))), None
        )
        if file_match is None or range_match is None:
            continue
        groups = range_match.groupdict()
        yield (
            file_match.group("file"),
            DamlRange(
                start_line=int(groups["start_line"]),
                start_column=int(groups["start_column"]),
                end_line=int(groups["end_line"]),
                end_column=int(groups["end_column"]),
            ),
            "\n".join(block),
        )


def _diagnostic_explanation(message: str) -> Optional[str]:
    """Extract the first useful explanation from a damlc diagnostic block.

    Daml diagnostics put the actual type/checking error after ``Message:`` and
    commonly format it as a bullet with wrapped continuation lines.  Keep the
    first bullet only: the following bullets usually describe the expression
    context, which is already represented by the mapped source location.
    """

    clean_message = _ANSI_ESCAPE_RE.sub("", message)
    message_lines = clean_message.splitlines()
    try:
        message_start = next(
            index
            for index, line in enumerate(message_lines)
            if line.strip().startswith("Message:")
        )
    except StopIteration:
        return None

    message_header = message_lines[message_start].split("Message:", 1)[1].strip()
    if message_header:
        return message_header

    explanation_lines: list[str] = []
    found_bullet = False
    for line in message_lines[message_start + 1 :]:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("•") or stripped.startswith("-"):
            if found_bullet:
                break
            found_bullet = True
            explanation_lines.append(stripped.lstrip("•-").strip())
            continue
        if not found_bullet:
            continue
        if stripped.casefold().startswith(_MESSAGE_CONTEXT_PREFIXES):
            break
        explanation_lines.append(stripped)

    if not explanation_lines:
        return None
    return " ".join(explanation_lines)


def annotate_daml_output(output: str, source_maps: Mapping[str, Mapping]) -> str:
    """Append DamlForge locations for diagnostics found in DPM/damlc output."""

    annotations = []
    seen = set()
    for diagnostic_file, diagnostic_range, message in _diagnostic_blocks(output):
        source = map_daml_location(diagnostic_file, diagnostic_range, message, source_maps)
        if source is None:
            continue
        explanation = _diagnostic_explanation(message)
        annotation = (
            diagnostic_file,
            diagnostic_range.start_line,
            source.format(),
            explanation,
        )
        if annotation in seen:
            continue
        seen.add(annotation)
        lines = [
            f"  {diagnostic_file}:{diagnostic_range.start_line}:",
            f"    DamlForge source {source.format()}",
        ]
        if explanation:
            lines.append(f"    Daml explanation: {explanation}")
        annotations.append("\n".join(lines))

    if not annotations:
        return output
    return output.rstrip() + "\n\nDamlForge source locations:\n" + "\n".join(annotations) + "\n"


def with_source_file(source_map: Mapping, source_file: Path | str) -> dict:
    """Return a source map tagged with the originating DamlForge file."""

    return {**source_map, "sourceFile": str(source_file)}
