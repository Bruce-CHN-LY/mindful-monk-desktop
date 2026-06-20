from __future__ import annotations

from pathlib import Path


def backup_broken_file(path: Path) -> Path | None:
    if not path.exists():
        return None

    candidate = path.with_suffix(".broken.json")
    index = 2
    while candidate.exists():
        candidate = path.with_suffix(f".broken-{index}.json")
        index += 1

    try:
        path.replace(candidate)
    except OSError:
        return None
    return candidate
