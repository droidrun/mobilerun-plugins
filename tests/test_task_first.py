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

    def test_any_device_requires_approval_unless_already_authorized(self):
        for name in ('shared/skills/mobile-tasks/SKILL.md',
                     'shared/skills/mobile-tasks/references/device-controls.md',
                     'shared/onboarding-first-device.md'):
            text = (ROOT / name).read_text().lower()
            self.assertIn('any new device unless the user already authorized its creation', text)
            self.assertIn('approval', text)
            self.assertNotIn('approval before creating any new paid device', text)

    def test_autonomous_execution_and_safety(self):
        skill = (ROOT / 'shared/skills/mobile-tasks/SKILL.md').read_text().lower()
        tasks = (ROOT / 'shared/skills/mobile-tasks/references/tasks.md').read_text().lower()
        devices = (ROOT / 'shared/skills/mobile-tasks/references/device-controls.md').read_text().lower()
        onboarding = (ROOT / 'shared/onboarding-first-device.md').read_text().lower()
        for term in ('best ready', 'resume', 'reasonable', 'expected output', 'retry once',
                     'device', 'task id', 'do not narrate', 'new device', 'purchases',
                     'plan changes', 'deleting', 'third parties', 'credentials'):
            self.assertIn(term, skill)
        self.assertIn('ambiguous submission', tasks)
        self.assertIn('do not duplicate', tasks)
        self.assertIn('resume', devices)
        self.assertIn('resume', onboarding)
        self.assertNotIn('resume a stopped device without appropriate authorization', devices + onboarding)
        self.assertNotIn('ask before creating devices or starting long', skill)

    def test_resume_cleanup_and_transition(self):
        for name in ('shared/onboarding-first-device.md',
                     'shared/skills/mobile-tasks/references/device-controls.md'):
            text = (ROOT / name).read_text().lower()
            self.assertIn('`stopped` after resume', text)
            self.assertIn('continue polling within the budget after a successful resume', text)
            self.assertIn('5 minutes or 10 calls', text)
            self.assertIn('unless the user wants it left running', text)
            self.assertNotIn('stop immediately on `stopped`', text)
            self.assertNotIn('stop immediately on `terminated` or `stopped`', text)
            self.assertNotIn('always stop a device resumed for the task', text)
            self.assertIn('minutes', text)
        tasks = (ROOT / 'shared/skills/mobile-tasks/references/tasks.md').read_text().lower()
        self.assertIn('resumed for the task', tasks)
        self.assertIn('leave it running', tasks)
        self.assertIn('stopping is within scope', tasks)
        self.assertNotIn('always stop a device', tasks)

    def test_task_purchase_prohibition(self):
        tasks = (ROOT / 'shared/skills/mobile-tasks/references/tasks.md').read_text().lower()
        self.assertIn('never initiate purchases', tasks)
        self.assertNotIn('entering credentials, purchases, data deletion', tasks)

    def test_approval_does_not_override_commerce_restrictions(self):
        for name in ('shared/skills/mobile-tasks/SKILL.md',
                     'shared/skills/mobile-tasks/references/features.md'):
            text = (ROOT / name).read_text().lower()
            self.assertIn('approval does not override', text)
            self.assertIn('included-only', text)
            self.assertIn('no-commerce', text)

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
