"""Provider routing and archive parity; missing deployed profiles retain working URLs."""
import json
from pathlib import Path
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = {
    'claude': ('.mcp.json', 'claude'),
    # Their provider-specific public routes currently return 404. Do not ship a broken URL.
    'cursor': ('mcp.json', None),
    'openai': ('mcp.json', 'openai'),
    'openclaw': ('.mcp.json', None),
    'test-plugin': ('mcp.json', 'openai'),
}


class ProviderProfileTests(unittest.TestCase):
    def test_every_package_selects_its_public_provider_profile(self):
        for package, (config, profile) in PACKAGES.items():
            with self.subTest(package=package):
                servers = json.loads((ROOT/'plugins'/package/config).read_text())['mcpServers']
                self.assertEqual(len(servers), 1)
                server = next(iter(servers.values()))
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
                    expected = 'https://cloud.mobilerun.ai/api/mcp' + (f'/{profile}' if profile else '')
                    self.assertEqual(server['url'], expected)


if __name__ == '__main__':
    unittest.main()
