"""Selected provider routing and archive parity; not deployment verification."""
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    'claude': ('.mcp.json', 'claude'),
    'cursor': ('mcp.json', 'cursor'),
    'openai': ('mcp.json', 'openai'),
    # OpenClaw retains the base route pending its dedicated profile.
    'openclaw': ('.mcp.json', None),
    'test-plugin': ('mcp.json', 'local'),
}


class ProviderProfileTests(unittest.TestCase):
    def test_every_package_selects_its_public_provider_profile(self):
        for package, (config, profile) in PACKAGES.items():
            with self.subTest(package=package):
                servers = json.loads((ROOT/'plugins'/package/config).read_text())['mcpServers']
                self.assertEqual(len(servers), 1)
                server = next(iter(servers.values()))
                if profile == 'local':
                    self.assertEqual(server, {'type': 'stdio', 'command': 'node',
                                              'args': ['${PLUGIN_ROOT}/scripts/local-mcp.mjs']})
                    self.assertIn('http://localhost:8080/mcp/openai',
                                  (ROOT/'plugins'/package/'scripts/local-mcp.mjs').read_text())
                else:
                    expected = 'https://cloud.mobilerun.ai/api/mcp' + (f'/{profile}' if profile else '')
                    self.assertEqual(server['url'], expected)
                    self.assertNotIn('command', server)
                    self.assertNotIn('headers', server)

    def test_zip_exports_match_provider_connections(self):
        for package, (config, profile) in PACKAGES.items():
            with self.subTest(package=package):
                filename = 'test-plugin.zip' if package == 'test-plugin' else f'mobilerun-{package}.zip'
                path = ROOT/'zip'/filename
                self.assertTrue(path.is_file(), f'Missing refreshed archive: {filename}')
                with zipfile.ZipFile(path) as archive:
                    self.assertIsNone(archive.testzip())
                    self.assertEqual(archive.read(config), (ROOT/'plugins'/package/config).read_bytes())
                    server = next(iter(json.loads(archive.read(config))['mcpServers'].values()))
                    if profile == 'local':
                        self.assertEqual(server['type'], 'stdio')
                        self.assertEqual(server['args'], ['${PLUGIN_ROOT}/scripts/local-mcp.mjs'])
                        self.assertEqual(archive.read('scripts/local-mcp.mjs'),
                                         (ROOT/'plugins'/package/'scripts/local-mcp.mjs').read_bytes())
                        self.assertIn(b'http://localhost:8080/mcp/openai', archive.read('scripts/local-mcp.mjs'))
                    else:
                        expected = 'https://cloud.mobilerun.ai/api/mcp' + (f'/{profile}' if profile else '')
                        self.assertEqual(server['url'], expected)


if __name__ == '__main__':
    unittest.main()
