"""Onboarding remains an actionable, self-contained first-use guide."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class OnboardingGuidanceTests(unittest.TestCase):
    def test_shared_guidance_has_practical_steps_not_audit_commentary(self):
        text = (ROOT / 'shared/onboarding-first-device.md').read_text()
        self.assertIn('## First useful run', text)
        self.assertIn('mobile-tasks', text)
        self.assertNotIn('workflow-automation', text)
        for phrase in ('testing-billing', 'evidence gap', 'billing unconfirmed',
                       'universally billing-free', 'consult current docs'):
            self.assertNotIn(phrase, text.lower())

    def test_host_setup_is_self_contained(self):
        endpoints = {'claude': '/api/mcp/claude', 'openai': '/api/mcp/openai',
                     'cursor': '/api/mcp', 'openclaw': '/api/mcp'}
        for provider, endpoint in endpoints.items():
            with self.subTest(provider=provider):
                text = (ROOT / f'plugins/{provider}/skills/onboarding/SKILL.md').read_text()
                self.assertIn('https://cloud.mobilerun.ai' + endpoint, text)
                self.assertIn('browser', text)
                self.assertIn('<!-- BEGIN SHARED FIRST DEVICE -->', text)
                self.assertNotIn('testing-billing', text)
                self.assertNotIn('Follow the [documented', text)

    def test_local_test_plugin_setup_does_not_send_credentials_to_browser_oauth(self):
        text = (ROOT / 'plugins/test-plugin/skills/onboarding/SKILL.md').read_text()
        intro = text.split('<!-- BEGIN SHARED FIRST DEVICE -->')[0]
        self.assertIn('http://localhost:8080/mcp/openai', intro)
        self.assertIn('stdio', intro)
        self.assertNotIn('https://cloud.mobilerun.ai/api/mcp', intro)
        self.assertIn('not browser OAuth', intro)
        self.assertIn('<!-- BEGIN SHARED FIRST DEVICE -->', text)


if __name__ == '__main__':
    unittest.main()
