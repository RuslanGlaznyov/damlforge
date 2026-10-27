import pytest

from forge.daml_versions import (
    DamlCodegenSettings,
    get_daml_version_policy,
    supports_explicit_serializable,
)


@pytest.mark.parametrize(
    "version,expected",
    [("3.4.8", False), ("3.4.11", False), ("3.5.0", True), ("3.5.0-snapshot.1", True)],
)
def test_daml_version_registry(version, expected):
    assert supports_explicit_serializable(version) is expected
    assert get_daml_version_policy(version).explicit_serializable is expected


def test_unknown_daml_version_is_conservative():
    assert supports_explicit_serializable("3.6.0") is False
    assert supports_explicit_serializable("not-a-version") is False


@pytest.mark.parametrize(
    "version,options,expected",
    [
        ("3.4.8", ("--explicit-serializable=yes",), False),
        ("3.5.0", (), False),
        ("3.5.0", ("--explicit-serializable=no",), False),
        ("3.5.0", ("--explicit-serializable=yes",), True),
        ("3.5.0", ("--explicit-serializable", "yes"), True),
    ],
)
def test_serializable_derivation_requires_sdk_and_build_option(version, options, expected):
    assert DamlCodegenSettings(version, options).derive_serializable is expected


@pytest.mark.parametrize(
    "version,options,supported",
    [
        (None, (), True),
        ("3.5.2", ("--target=2.3",), True),
        ("3.5.2", ("--target=2.dev",), True),
        ("3.5.2", ("--target=2.2",), False),
        ("3.5.2", ("--target=latest",), False),
        ("3.6.0", ("--target=2.3",), False),
    ],
)
def test_contract_keys_require_sdk_and_lf_target(version, options, supported):
    assert (DamlCodegenSettings(version, options).contract_keys_error() is None) is supported
