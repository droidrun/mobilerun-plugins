"""Content/distribution contracts, not proof of live billing or host behavior."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ('claude', 'openai', 'cursor', 'openclaw', 'test-plugin')


class SharedSkillTests(unittest.TestCase):
    def test_removed_workflow_skill_has_no_source_entrypoints(self):
        roots = [ROOT / 'shared/skills', *(ROOT / f'plugins/{provider}/skills' for provider in PROVIDERS)]
        for root in roots:
            self.assertFalse((root / 'workflow-automation/SKILL.md').exists(), str(root))

    def test_every_package_has_exactly_two_skill_entrypoints(self):
        expected = {'onboarding/SKILL.md', 'mobile-tasks/SKILL.md'}
        for provider in PROVIDERS:
            folder = ROOT / f'plugins/{provider}/skills'
            actual = {path.relative_to(folder).as_posix()
                      for path in folder.rglob('SKILL.md')}
            self.assertEqual(actual, expected, provider)

    def test_existing_hosts_embed_shared_first_device_guidance(self):
        canonical = ROOT / 'shared/onboarding-first-device.md'
        self.assertTrue(canonical.is_file(), 'Missing canonical first-device guidance')
        guidance = canonical.read_text().strip()
        for provider in PROVIDERS:
            text = (ROOT / f'plugins/{provider}/skills/onboarding/SKILL.md').read_text()
            self.assertIn(guidance, text, provider)
        for phrase in ('Android cloud phone', 'device_slot', 'iOS', '402', 'ready'):
            self.assertIn(phrase, guidance)

    def test_operational_skills_are_canonical_in_every_package(self):
        for name in ('mobile-tasks',):
            canonical = ROOT / f'shared/skills/{name}/SKILL.md'
            self.assertTrue(canonical.is_file(), f'Missing canonical {name}')
            text = canonical.read_text()
            self.assertRegex(text, rf'^---\nname: {name}\ndescription: Use when[^\n]+\n---\n')
            for provider in PROVIDERS:
                copy = ROOT / f'plugins/{provider}/skills/{name}/SKILL.md'
                self.assertTrue(copy.is_file(), provider)
                self.assertEqual(copy.read_text(), text, provider)


if __name__ == '__main__':
    unittest.main()
