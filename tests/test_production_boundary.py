"""Production archives must not depend on or include the local test adapter."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ('claude', 'openai', 'cursor', 'openclaw')


class ProductionBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        for name in ('package_plugins.py', 'sync_skills.py'):
            shutil.copy2(ROOT / 'scripts' / name, self.root / 'scripts' / name)
        shutil.copytree(ROOT / 'shared', self.root / 'shared')
        for provider in PROVIDERS:
            shutil.copytree(ROOT / 'plugins' / provider, self.root / 'plugins' / provider)

    def run_packager(self):
        return subprocess.run([sys.executable, 'scripts/package_plugins.py'], cwd=self.root,
                              capture_output=True, text=True)

    def test_packager_neither_creates_nor_overwrites_root_archives(self):
        existing = self.root / 'mobilerun-claude.zip'
        existing.write_bytes(b'legacy archive')
        result = self.run_packager()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(existing.read_bytes(), b'legacy archive')
        for provider in PROVIDERS:
            self.assertTrue((self.root / 'zip' / f'mobilerun-{provider}.zip').is_file())
            if provider != 'claude':
                self.assertFalse((self.root / f'mobilerun-{provider}.zip').exists())

    def test_production_only_fixture_packages_without_test_exporter(self):
        for provider in PROVIDERS:
            package = self.root / 'plugins' / provider
            for extra in ('scripts/local-mcp.mjs', 'scripts/setup-local-auth.mjs',
                          'credentials.json', 'node_modules/dependency/index.js'):
                path = package / extra
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('should not be distributed')
        result = self.run_packager()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / 'zip/test-plugin.zip').exists())
        for provider in PROVIDERS:
            with ZipFile(self.root / 'zip' / f'mobilerun-{provider}.zip') as archive:
                names = archive.namelist()
                for forbidden in ('local-mcp.mjs', 'setup-local-auth.mjs', 'credentials', 'node_modules'):
                    self.assertFalse(any(forbidden in name for name in names), names)

    def test_invalid_connectors_leave_existing_archive_untouched(self):
        variants = [
            {'command': 'node', 'args': ['local-mcp.mjs'], 'env': {'TOKEN': 'secret'}},
            {'type': 'http', 'url': 'http://localhost:3000/mcp'},
            {'type': 'http', 'url': 'https://cloud.mobilerun.ai/api/mcp/claude', 'headers': {'Authorization': 'secret'}},
        ]
        for connector in variants:
            with self.subTest(connector=connector):
                config = self.root / 'plugins/claude/.mcp.json'
                config.write_text(json.dumps({'mcpServers': {'mobilerun': connector}}))
                output = self.root / 'zip/mobilerun-claude.zip'
                output.parent.mkdir(exist_ok=True)
                output.write_bytes(b'existing archive')
                result = self.run_packager()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(output.read_bytes(), b'existing archive')


if __name__ == '__main__':
    unittest.main()
