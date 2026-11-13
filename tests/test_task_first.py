"""Task-first entrypoint and reference distribution contracts."""
from pathlib import Path
import unittest

from scripts import package_plugins, package_test_plugin
from testing.mcp import package_plugins as remote

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = 'skills/mobile-tasks/references/tasks.md'


class TaskFirstTests(unittest.TestCase):
    def test_ready_before_task_submission(self):
        text = (ROOT / 'shared/skills/mobile-tasks/SKILL.md').read_text().lower()
        first = text.split('## core loop', 1)[1].split('\n2.', 1)[0]
        self.assertIn('`ready` before `run_task`', first)
        self.assertIn('references/device-controls.md', first)

    def test_paid_device_always_requires_approval(self):
        for name in ('shared/skills/mobile-tasks/SKILL.md',
                     'shared/skills/mobile-tasks/references/device-controls.md',
                     'shared/onboarding-first-device.md'):
            text = (ROOT / name).read_text().lower()
            self.assertNotIn('paid device when none exists', text)
            self.assertIn('paid device', text)
            self.assertIn('approval', text)

    def test_autonomous_execution_and_safety(self):
        skill = (ROOT / 'shared/skills/mobile-tasks/SKILL.md').read_text().lower()
        tasks = (ROOT / 'shared/skills/mobile-tasks/references/tasks.md').read_text().lower()
        devices = (ROOT / 'shared/skills/mobile-tasks/references/device-controls.md').read_text().lower()
        onboarding = (ROOT / 'shared/onboarding-first-device.md').read_text().lower()
        for term in ('best ready', 'resume', 'reasonable', 'expected output', 'retry once',
                     'device', 'task id', 'do not narrate', 'paid device', 'purchases',
                     'plan changes', 'deleting', 'third parties', 'credentials'):
            self.assertIn(term, skill)
        self.assertIn('ambiguous submission', tasks)
        self.assertIn('do not duplicate', tasks)
        self.assertIn('resume', devices)
        self.assertIn('resume', onboarding)
        self.assertNotIn('resume a stopped device without appropriate authorization', devices + onboarding)
        self.assertNotIn('ask before creating devices or starting long', skill)

    def test_entrypoint_routes_device_goals_to_tasks(self):
        text = (ROOT / 'shared/skills/mobile-tasks/SKILL.md').read_text().lower()
        for term in ('run_task', 'get_task_status', 'expected output', 'low-level', 'manual', 'references/tasks.md'):
            self.assertIn(term, text)
        self.assertLess(len(text.split()), 400)

    def test_references_are_allowlisted_for_every_package(self):
        for files in package_plugins.FILES.values():
            self.assertIn(REFERENCE, files)
        self.assertIn(REFERENCE, package_test_plugin.DISTRIBUTION_FILES)
        for provider in ('claude', 'openai'):
            self.assertIn(REFERENCE, remote.package_contents(provider, 'https://example.com/mcp/openai'))
