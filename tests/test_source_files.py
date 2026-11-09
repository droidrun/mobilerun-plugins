"""Check that publication scanning respects generated/dependency ignores."""
from pathlib import Path
import subprocess
import tempfile
import unittest

from source_files import source_files


class SourceDiscoveryTests(unittest.TestCase):
    def test_ignored_dependencies_are_excluded_but_tracked_files_still_scanned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(['git', 'init', '-q', directory], check=True)
            (root / '.gitignore').write_text('node_modules/\ndist/\n')
            (root / 'node_modules').mkdir()
            (root / 'node_modules' / 'third-party.md').write_text('third party')
            (root / 'node_modules' / 'tracked.md').write_text('must still scan')
            (root / 'README.md').write_text('source')
            subprocess.run(['git', 'add', '-f', 'node_modules/tracked.md'], cwd=root, check=True)
            found = {path.relative_to(root).as_posix() for path in source_files(root)}
            self.assertEqual(found, {'.gitignore', 'README.md', 'node_modules/tracked.md'})
