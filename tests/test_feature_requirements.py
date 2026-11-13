"""Static guards for contextual feature guidance; not agent-behavior tests."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MOBILE = ROOT / 'shared/skills/mobile-tasks/SKILL.md'
FEATURES = ROOT / 'shared/skills/mobile-tasks/references/features.md'
ONBOARDING = ROOT / 'shared/onboarding-first-device.md'


class FeatureRequirementsTests(unittest.TestCase):
    def test_mobile_conditional_resource_requirements(self):
        text = FEATURES.read_text().lower()
        section = text.split('## feature requirements', 1)[-1].split('\n## ', 1)[0]
        for term in ('only', 'requested', 'limitation', 'subscription slots', 'minute',
                     'concurrency', 'execution credits', 'automation', 'numbers', 'sms',
                     'country', 'included capacity', 'separate resource', 'mailboxes',
                     'connected', 'service entitlement', 'proxies', 'traffic', 'byo',
                     'esim', 'carrier', 'device', 'apps', 'files', 'recording', 'integrations',
                     'included-only', 'missing tools'):
            with self.subTest(term=term):
                self.assertIn(term, section)

    def test_onboarding_account_questions_are_conditional(self):
        text = ONBOARDING.read_text().lower()
        self.assertIn('only when', text)
        self.assertIn('active workspace', text)
        self.assertIn('account usage settings', text)
        self.assertIn('subscription slots', text)
        self.assertIn('concurrency', text)
        self.assertIn('https://docs.mobilerun.ai/credits', text)

    def test_links_and_commerce_guard(self):
        for path in (FEATURES, ONBOARDING):
            text = path.read_text().lower()
            with self.subTest(path=path):
                self.assertNotRegex(text, r'https?://cloud\.mobilerun\.ai/(billing|checkout|upgrade)')
                self.assertNotRegex(text, r'<!--|\b(buy now|upgrade now|top up now)\b')
                self.assertNotRegex(text, r'\b(all|every) (features?|capabilities|resources?) (require|requires) (a )?(paid|premium|upgrade)')
        mobile = FEATURES.read_text().lower()
        self.assertIn('https://docs.mobilerun.ai/mcp-server', mobile)
        self.assertRegex(mobile, r'only (?:offer|share).{0,180}confirmed entitlement limitation')

    def test_mobile_remains_compact_and_no_new_shared_skill(self):
        self.assertLessEqual(len(MOBILE.read_text().split()), 1100)
        self.assertEqual([p.parent.name for p in (ROOT / 'shared/skills').glob('*/SKILL.md')], ['mobile-tasks'])

    def test_reviewed_scope_and_recovery_guards(self):
        mobile = FEATURES.read_text().lower()
        self.assertIn('subscription android phones', mobile)
        self.assertIn('tool/profile restrictions', mobile)
        self.assertIn('no prices, plan lists or upgrade prompts', mobile)
        recovery = next(line for line in mobile.splitlines() if '**402 or quota error:**' in line)
        for limit in ('slots', 'concurrency', 'minutes', 'credits'):
            self.assertIn(limit, recovery)
        for path in (FEATURES, ONBOARDING):
            text = path.read_text().lower()
            with self.subTest(path=path):
                self.assertIn('confirmed entitlement limitation', text)
                self.assertIn('not for missing tools or connectivity errors', text)
                self.assertNotIn('a feature is unavailable', text)
                self.assertNotIn('a requested feature is unavailable', text)


if __name__ == '__main__':
    unittest.main()
