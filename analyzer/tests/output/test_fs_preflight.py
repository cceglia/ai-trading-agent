"""Tests for the analysis CLI data-root preflight (AC-014 / NFR §18)."""

from __future__ import annotations

from pathlib import Path

from src.output.fs_preflight import verify_data_root_writable


def test_writable_root_roundtrip_ok(tmp_path: Path):
    ok, message = verify_data_root_writable(tmp_path / "data")
    assert ok is True
    assert message == "writable"
    assert (tmp_path / "data").is_dir()
    # Probe file is cleaned up after the roundtrip.
    assert not list((tmp_path / "data").glob(".analysis-write-probe"))


def test_creates_missing_root(tmp_path: Path):
    target = tmp_path / "deep" / "nested" / "data"
    ok, _ = verify_data_root_writable(target)
    assert ok is True
    assert target.is_dir()


def test_unwritable_root_fails_safely(tmp_path: Path):
    """A root whose parent is a file fails preflight without claiming a signal."""
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("x")
    ok, message = verify_data_root_writable(blocker / "sub")
    assert ok is False
    assert "unwritable" in message


def test_readonly_root_fails_safely(tmp_path: Path):
    """chmod 0o500 makes writes fail for the non-root probe (best effort).

    When the suite runs as root (container build) mode bits are ignored, so
    the test only asserts the safe-failure contract when the probe really
    cannot write; otherwise it asserts the roundtrip still succeeds.
    """
    root = tmp_path / "ro"
    root.mkdir()
    root.chmod(0o500)
    try:
        ok, message = verify_data_root_writable(root)
        if ok:
            assert message == "writable"
        else:
            assert "unwritable" in message
    finally:
        root.chmod(0o755)
