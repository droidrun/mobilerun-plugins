"""Contracts for Test Plugin's local OpenAI-profile connection (no device calls)."""
import json
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'plugins' / 'test-plugin'


class TestPluginTests(unittest.TestCase):
    def test_identity_and_version(self):
        self.assertTrue((PACKAGE / 'plugin.json').is_file(), 'Missing Test Plugin manifest')
        manifest = json.loads((PACKAGE / 'plugin.json').read_text())
        self.assertEqual(manifest['name'], 'test-plugin')
        self.assertEqual(manifest['version'], '0.3.0')
        extension = manifest['extensions']['com.openai']
        self.assertEqual(extension['interface']['displayName'], 'Test Plugin')
        self.assertEqual(extension['onboardingSkill'], './skills/onboarding/SKILL.md')
        self.assertTrue((PACKAGE / extension['onboardingSkill']).is_file())
        self.assertIn('Node.js 20.3 or later', extension['interface']['longDescription'])
        self.assertIn('Node.js 22 is recommended', extension['interface']['longDescription'])
        self.assertIn('does not connect regular cloud ChatGPT chats', extension['interface']['longDescription'])
        hosted = json.loads((ROOT / 'plugins/openai/mcp.json').read_text())
        self.assertTrue(all('url' in server for server in hosted['mcpServers'].values()))

    def test_local_openai_profile_has_no_embedded_credentials(self):
        self.assertTrue((PACKAGE / 'mcp.json').is_file(), 'Missing public MCP configuration')
        config = json.loads((PACKAGE / 'mcp.json').read_text())
        self.assertEqual(config['mcpServers'], {'test-plugin': {
            'type': 'stdio',
            'command': 'node',
            'args': ['${PLUGIN_ROOT}/scripts/local-mcp.mjs'],
        }})
        self.assertNotIn('MOBILERUN_CLOUD_API_KEY', json.dumps(config))
        self.assertIn('http://localhost:8080/mcp/openai', (PACKAGE / 'scripts/local-mcp.mjs').read_text())

    def test_readme_describes_local_support_and_bridge_limits(self):
        readme = (PACKAGE / 'README.md').read_text()
        for phrase in ('macOS and Linux', 'Node.js 20.3 or later', 'Node.js 22 is recommended',
                       'regular cloud ChatGPT chats', '30-second timeout',
                       'do not blindly retry mutations', 'stateless JSON-RPC relay'):
            self.assertIn(phrase, readme)
        self.assertNotIn('viewer', readme.lower())

    def test_local_marketplace_keeps_original_and_adds_test_plugin(self):
        catalog = json.loads((ROOT / '.agents/plugins/marketplace.json').read_text())
        entries = {entry['name']: entry for entry in catalog['plugins']}
        self.assertIn('mobilerun', entries)
        self.assertIn('test-plugin', entries)
        self.assertEqual(entries['mobilerun']['source']['path'], './plugins/openai')
        self.assertEqual(entries['test-plugin']['source'], {
            'source': 'local', 'path': './plugins/test-plugin'})
        self.assertEqual(entries['test-plugin']['policy'].get('authentication'), 'ON_INSTALL')


class TestPluginArchiveTests(unittest.TestCase):
    def exporter(self):
        script = ROOT / 'scripts/package_test_plugin.py'
        self.assertTrue(script.is_file(), 'Missing portable Test Plugin ZIP exporter')
        spec = importlib.util.spec_from_file_location('package_test_plugin', script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_archive_has_only_portable_runtime_files(self):
        exporter = self.exporter()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'plugin with spaces'
            for name in exporter.DISTRIBUTION_FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('fixture ' + name)
            (root / '.env').write_text('not for distribution')
            (root / 'server').mkdir()
            (root / 'server/legacy-runtime.mjs').write_text('not the active connector')
            output = Path(temporary) / 'test-plugin.zip'
            exporter.package_plugin(root, output)
            with zipfile.ZipFile(output) as archive:
                self.assertIsNone(archive.testzip())
                self.assertEqual(set(archive.namelist()), set(exporter.DISTRIBUTION_FILES))
                self.assertIn('skills/onboarding/SKILL.md', archive.namelist())
                self.assertIn('skills/mobile-tasks/SKILL.md', archive.namelist())
                self.assertIn('skills/workflow-automation/SKILL.md', archive.namelist())
                self.assertEqual(set(archive.namelist()), set(exporter.DISTRIBUTION_FILES))
                self.assertNotIn('.env', archive.namelist())
                for name in archive.namelist():
                    self.assertEqual(archive.read(name), (root / name).read_bytes())

    def test_missing_or_symlinked_input_cannot_replace_existing_archive(self):
        exporter = self.exporter()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'plugin'
            for name in exporter.DISTRIBUTION_FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('fixture')
            output = Path(temporary) / 'test-plugin.zip'
            exporter.package_plugin(root, output)
            before = output.read_bytes()
            target = root / 'mcp.json'
            target.unlink()
            with self.assertRaises((OSError, ValueError)):
                exporter.package_plugin(root, output)
            self.assertEqual(output.read_bytes(), before)
            other = Path(temporary) / 'outside'
            other.write_text('outside package')
            target.symlink_to(other)
            with self.assertRaises((OSError, ValueError)):
                exporter.package_plugin(root, output)
            self.assertEqual(output.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
