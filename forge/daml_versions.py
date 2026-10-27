"""Daml SDK version policies used by code generation."""

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from packaging.version import InvalidVersion, Version


@dataclass(frozen=True)
class DamlVersionPolicy:
    """Code-generation capabilities for one Daml major/minor line."""

    explicit_serializable: bool = False
    contract_keys: bool = False


# Keep this registry explicit. Unknown SDK lines use the conservative default
# until their compiler capabilities are verified and added here.
DAML_VERSION_REGISTRY: Mapping[tuple[int, int], DamlVersionPolicy] = {
    (3, 4): DamlVersionPolicy(explicit_serializable=False),
    (3, 5): DamlVersionPolicy(explicit_serializable=True, contract_keys=True),
}
_UNKNOWN_VERSION_POLICY = DamlVersionPolicy()
_DAML_VERSION_PREFIX = re.compile(r"^(?P<major>[0-9]+)\.(?P<minor>[0-9]+)")


@dataclass(frozen=True)
class DamlCodegenSettings:
    """Daml project settings that affect generated source syntax."""

    sdk_version: str | None = None
    build_options: tuple[str, ...] = ()

    @property
    def derive_serializable(self) -> bool:
        """Whether generated data types should derive ``Serializable``."""
        return supports_explicit_serializable(self.sdk_version) and _has_option(
            self.build_options, "--explicit-serializable", "yes"
        )

    def contract_keys_error(self) -> str | None:
        if not self.sdk_version:
            return None
        if not get_daml_version_policy(self.sdk_version).contract_keys:
            return f"Daml SDK {self.sdk_version} does not support them; use SDK 3.5 or later"
        prefix = "--target="
        target = next((o[len(prefix) :] for o in self.build_options if o.startswith(prefix)), "")
        major, _, minor = target.partition(".")
        if minor == "dev" or (
            major.isdigit() and minor.isdigit() and (int(major), int(minor)) >= (2, 3)
        ):
            return None
        return (
            f"they need `--target=2.3` or later in `build-options`, not {target or 'the default'}"
        )

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "DamlCodegenSettings":
        options = config.get("build-options") or ()
        if isinstance(options, str):
            options = (options,)
        return cls(
            sdk_version=str(config["sdk-version"]) if config.get("sdk-version") else None,
            build_options=tuple(str(option) for option in options),
        )


def get_daml_version_policy(sdk_version: str | None) -> DamlVersionPolicy:
    """Return the registered policy for an SDK version."""
    if not sdk_version:
        return _UNKNOWN_VERSION_POLICY
    try:
        version = Version(sdk_version)
        version_key = (version.major, version.minor)
    except InvalidVersion:
        match = _DAML_VERSION_PREFIX.match(sdk_version)
        if match is None:
            return _UNKNOWN_VERSION_POLICY
        version_key = (int(match["major"]), int(match["minor"]))
    return DAML_VERSION_REGISTRY.get(version_key, _UNKNOWN_VERSION_POLICY)


def supports_explicit_serializable(sdk_version: str | None) -> bool:
    """Return whether the SDK line supports explicit serializability."""
    return get_daml_version_policy(sdk_version).explicit_serializable


def _has_option(options: Sequence[str], name: str, value: str) -> bool:
    expected = f"{name}={value}"
    for index, option in enumerate(options):
        if option == expected:
            return True
        if option == name and index + 1 < len(options) and options[index + 1] == value:
            return True
    return False
