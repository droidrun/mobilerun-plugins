"""Enumerate repository source, excluding ignored dependency/build output.

Tracked files remain in scope even if an ignore rule later matches them.
"""
from pathlib import Path
import subprocess


def source_files(root: Path) -> list[Path]:
    output = subprocess.check_output(
        ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
        cwd=root,
    )
    return sorted({root / name.decode('utf-8')
                   for name in output.split(b'\0')
                   if name and (root / name.decode('utf-8')).is_file()})
