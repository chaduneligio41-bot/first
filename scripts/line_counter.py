"""Small utility for counting the number of lines in a text file."""

from __future__ import annotations

from pathlib import Path


def count_lines(file_path: str | Path, encoding: str = "utf-8") -> int:
    """Return the number of lines in the file at ``file_path``.

    A "line" is counted per newline-terminated segment. A trailing line
    without a final newline still counts (e.g. ``"a\nb"`` has 2 lines).
    An empty file has 0 lines.

    Args:
        file_path: Path to the file to read.
        encoding: Text encoding used to open the file.

    Returns:
        The number of lines in the file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(file_path)
    with path.open("r", encoding=encoding) as handle:
        return sum(1 for _ in handle)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("usage: python line_counter.py <file>")
        raise SystemExit(2)
    print(count_lines(sys.argv[1]))
