"""Tests for ``line_counter.count_lines``.

Run with: ``pytest scripts/test_line_counter.py`` or ``python scripts/test_line_counter.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from line_counter import count_lines  # noqa: E402


def test_empty_file(tmp_path: Path) -> None:
    f = tmp_path / "empty.txt"
    f.write_text("", encoding="utf-8")
    assert count_lines(f) == 0


def test_single_line_no_newline(tmp_path: Path) -> None:
    f = tmp_path / "one.txt"
    f.write_text("hello", encoding="utf-8")
    assert count_lines(f) == 1


def test_multiple_lines(tmp_path: Path) -> None:
    f = tmp_path / "multi.txt"
    f.write_text("a\nb\nc\n", encoding="utf-8")
    assert count_lines(f) == 3


def test_trailing_line_without_newline(tmp_path: Path) -> None:
    f = tmp_path / "trailing.txt"
    f.write_text("a\nb", encoding="utf-8")
    assert count_lines(f) == 2


def test_blank_lines_are_counted(tmp_path: Path) -> None:
    f = tmp_path / "blanks.txt"
    f.write_text("\n\n\n", encoding="utf-8")
    assert count_lines(f) == 3


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        count_lines(tmp_path / "does_not_exist.txt")


def test_accepts_str_path(tmp_path: Path) -> None:
    f = tmp_path / "str.txt"
    f.write_text("x\ny\n", encoding="utf-8")
    assert count_lines(str(f)) == 2


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
