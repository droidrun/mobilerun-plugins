"""Guard provider package overviews against stale skill inventory and claims."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ('claude', 'openai', 'cursor', 'openclaw', 'test-plugin')
SKILLS = ('onboarding', 'mobile-tasks')


class ReadmeSkillInventoryTests(unittest.TestCase):
    def test_provider_overviews_name_both_skills_without_legacy_billing_copy(self):
        paths = [ROOT / 'plugins/README.md'] + [ROOT / 'plugins' / provider / 'README.md'
                                                for provider in PROVIDERS]
        for path in paths:
            text = path.read_text().lower()
            with self.subTest(path=path.relative_to(ROOT)):
                for skill in SKILLS:
                    self.assertIn(skill, text)
                for stale in ('testing/billing', 'universally free', 'billing reference',
                              'evidence-based testing'):
                    self.assertNotIn(stale, text)

    def test_repository_overview_describes_same_skills_for_each_provider(self):
        text = (ROOT / 'README.md').read_text().lower()
        for skill in SKILLS:
            self.assertIn(skill, text)
        self.assertIn('all providers', text)


if __name__ == '__main__':
    unittest.main()
