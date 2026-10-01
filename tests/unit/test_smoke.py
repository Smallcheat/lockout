"""Smoke test: the package imports and exposes a version string."""

import lockout


def test_package_exposes_version() -> None:
    assert isinstance(lockout.__version__, str)
    assert lockout.__version__
