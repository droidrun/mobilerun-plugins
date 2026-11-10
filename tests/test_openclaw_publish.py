"""OpenClaw bundle publication metadata and user-facing connection guidance."""
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'plugins' / 'openclaw'
ENDPOINT = 'https://cloud.mobilerun.ai/api/mcp/openclaw'


class OpenClawPublishTests(unittest.TestCase):
    def test_plugin_declares_dedicated_http_oauth_server_with_one_bundle_marker(self):
        config = json.loads((PACKAGE / '.mcp.json').read_text())
        self.assertEqual(config, {'mcpServers': {'mobilerun': {
            'url': ENDPOINT, 'auth': 'oauth', 'transport': 'streamable-http'}}})
        markers = ('.claude-plugin/plugin.json', '.cursor-plugin/plugin.json',
                   '.codex-plugin/plugin.json', 'plugin.json', 'openclaw.plugin.json')
        self.assertEqual([marker for marker in markers if (PACKAGE / marker).exists()],
                         ['.claude-plugin/plugin.json'])

    def test_openclaw_sign_in_instructions_do_not_duplicate_plugin_connector(self):
        readme = (PACKAGE / 'README.md').read_text()
        onboarding = (PACKAGE / 'skills/onboarding/SKILL.md').read_text()
        for text in (readme, onboarding):
            self.assertIn('plugin’s page', text)
            self.assertIn('Accounts', text)
            self.assertIn('Sign in', text)
            self.assertIn('openclaw mcp login', text)
            self.assertIn('do not', text.lower())
            self.assertIn('404', text)
            self.assertIn('support@mobilerun.ai', text)
        self.assertIn('Standalone connection alternative', readme)
        self.assertIn('Only when intentionally not using the plugin', readme)
        self.assertIn(ENDPOINT, readme)

    def test_root_provider_summary_uses_intended_profile_and_discloses_deployment_gap(self):
        readme = (ROOT / 'README.md').read_text()
        self.assertIn(ENDPOINT, readme)
        self.assertIn('deployment availability is unverified', readme)
        self.assertIn('do not substitute the broader base endpoint', readme)

    def test_clawhub_plugin_icon_is_bundled_png_within_size_and_dimensions(self):
        icon = PACKAGE / 'assets/icon.png'
        data = icon.read_bytes()
        self.assertLessEqual(len(data), 512 * 1024)
        self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
        width, height = struct.unpack('>II', data[16:24])
        self.assertEqual((width, height), (512, 512))
        self.assertEqual(data, (ROOT / 'plugins/claude/assets/icon.png').read_bytes())
        self.assertIn('assets/icon.png', (PACKAGE / 'README.md').read_text())


if __name__ == '__main__':
    unittest.main()
