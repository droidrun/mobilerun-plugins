"""Structural contracts for canonical operational guidance, not live API tests."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class OperationalSkillsTests(unittest.TestCase):
    def skill(self, name):
        path = ROOT / 'shared' / 'skills' / name / 'SKILL.md'
        self.assertTrue(path.is_file(), f'Missing canonical skill: {path}')
        text = path.read_text()
        self.assertRegex(text, rf'^---\nname: {name}\ndescription: Use when[^\n]+\n---\n')
        self.assertLessEqual(len(text.split()), 1100)
        for banned in ('testing-billing', 'billing unconfirmed', 'billing-free', 'evidence gap', 'risk section'):
            self.assertNotIn(banned, text.lower())
        self.assertNotRegex(text.lower(), r'(fetch|consult|read) (the )?(external |online |current )?docs')
        return text.lower()

    def assert_terms(self, text, terms):
        for term in terms:
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_mobile_task_recipe(self):
        self.assert_terms(self.skill('mobile-tasks'), (
            'list_devices', 'create_device', 'get_device', 'list_apps_on_device',
            'observe', 'tap', 'run_task', 'maxsteps', 'get_task_status',
            'get_task_summary', 'stop_task', 'screenshot', 'recording', 'credential',
            'terminal', 'duplicate', 'minutes', 'credits', 'reset', 'termination',
            'approval', 'example', 'common', 'schema', 'submitted'))

    def test_mobile_terminal_states_and_summary_fallback(self):
        text = self.skill('mobile-tasks')
        self.assert_terms(text, ('completed', 'failed', 'cancelled', 'where exposed',
                                 'status and output fields'))

    def test_paused_task_handoff_stops_polling_without_resubmission(self):
        text = self.skill('mobile-tasks')
        self.assert_terms(text, ('on `paused`, stop polling', 'last verified status',
                                 'task id', 'user input', 'do not automatically resubmit or resume'))

    def test_device_readiness_has_bounded_handoff_in_both_recipes(self):
        recipes = (ROOT / 'shared' / 'onboarding-first-device.md',
                   ROOT / 'shared' / 'skills' / 'mobile-tasks' / 'SKILL.md')
        for path in recipes:
            with self.subTest(path=path):
                text = path.read_text().lower()
                self.assert_terms(text, ('5 minutes', '10 calls', '`terminated`',
                                         '`maintenance`', '`unknown`', '`stopped`',
                                         'device id', 'last verified state',
                                         'do not create a replacement'))

    def test_actual_mobile_call_and_billing_contracts(self):
        text = self.skill('mobile-tasks')
        self.assert_terms(text, ('subscription', 'minute', 'auto', 'deviceid', 'taskid',
                                 'install_requested', 'succeeded', 'nextoffset'))


if __name__ == '__main__':
    unittest.main()
