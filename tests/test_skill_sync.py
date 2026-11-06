"""Safety and CLI contracts for synchronizing canonical provider skills."""
from contextlib import redirect_stderr, redirect_stdout
import importlib
from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sync = importlib.import_module('scripts.sync_skills')
package_test = importlib.import_module('scripts.package_test_plugin')


class SkillSyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'shared').mkdir()
        (self.root / 'shared/onboarding-first-device.md').write_text('Canonical onboarding')
        for name in sync.SKILLS:
            canonical = self.root / f'shared/skills/{name}/SKILL.md'
            canonical.parent.mkdir(parents=True, exist_ok=True)
            canonical.write_text(f'Canonical {name}')
        for provider in sync.PROVIDERS:
            onboarding = self.root / f'plugins/{provider}/skills/onboarding/SKILL.md'
            onboarding.parent.mkdir(parents=True)
            onboarding.write_text(f'Host intro\n{sync.START}\nold content\n{sync.END}\nHost outro\n')

    def tearDown(self):
        self.temp.cleanup()

    def test_sync_repairs_stale_copies_and_check_then_passes(self):
        pending = sync.synchronize(self.root)
        self.assertEqual(len(pending), 15)
        self.assertEqual(sync.check(self.root), [])
        for provider in sync.PROVIDERS:
            text = (self.root / f'plugins/{provider}/skills/onboarding/SKILL.md').read_text()
            self.assertIn(f'{sync.START}\nCanonical onboarding\n{sync.END}', text)
            for name in sync.SKILLS:
                self.assertEqual((self.root / f'plugins/{provider}/skills/{name}/SKILL.md').read_text(),
                                 f'Canonical {name}')

    def test_cli_check_reports_drift_without_writing(self):
        before = (self.root / 'plugins/claude/skills/onboarding/SKILL.md').read_text()
        output = StringIO()
        with mock.patch.object(sync, 'ROOT', self.root), redirect_stderr(output):
            result = sync.main(['--check'])
        self.assertEqual(result, 1)
        self.assertIn('Out of sync', output.getvalue())
        self.assertEqual((self.root / 'plugins/claude/skills/onboarding/SKILL.md').read_text(), before)

    def test_missing_canonical_or_provider_file_fails_closed(self):
        (self.root / 'shared/skills/mobile-tasks/SKILL.md').unlink()
        with self.assertRaises(ValueError):
            sync.check(self.root)
        (self.root / 'shared/skills/mobile-tasks/SKILL.md').write_text('Canonical mobile-tasks')
        (self.root / 'plugins/openai/skills/onboarding/SKILL.md').unlink()
        with self.assertRaises(ValueError):
            sync.check(self.root)

    def test_missing_and_malformed_marker_pairs_fail(self):
        target = self.root / 'plugins/claude/skills/onboarding/SKILL.md'
        for content in ('no markers', f'{sync.START}\n{sync.START}\n{sync.END}',
                        f'{sync.END}\n{sync.START}'):
            target.write_text(content)
            with self.subTest(content=content), self.assertRaises(ValueError):
                sync.check(self.root)

    def test_symlink_sources_targets_and_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other) / 'outside.md'
            outside.write_text('outside')
            target = self.root / 'plugins/claude/skills/mobile-tasks/SKILL.md'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(outside)
            with self.assertRaises(ValueError):
                sync.check(self.root)
            target.unlink()
            target.write_text('stale mobile-tasks')
            (self.root / 'plugins/openai/skills').rename(self.root / 'plugins/openai/skills-real')
            (self.root / 'plugins/openai/skills').symlink_to(self.root / 'plugins/openai/skills-real')
            with self.assertRaises(ValueError):
                sync.check(self.root)

    def test_test_plugin_cli_rejects_canonical_drift_before_packaging(self):
        output = StringIO()
        with mock.patch.object(package_test, 'ROOT', self.root), redirect_stderr(output):
            result = package_test.main([])
        self.assertEqual(result, 1)
        self.assertIn('out of sync', output.getvalue().lower())
        self.assertFalse((self.root / 'zip/test-plugin.zip').exists())

    def test_test_plugin_cli_rejects_stale_custom_package(self):
        sync.synchronize(self.root)
        custom = self.root / 'custom-package'
        for name in package_test.DISTRIBUTION_FILES:
            path = custom / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('stale custom content')
        output = self.root / 'custom.zip'
        with mock.patch.object(package_test, 'ROOT', self.root), redirect_stderr(StringIO()):
            result = package_test.main(['--package', str(custom), '--output', str(output)])
        self.assertEqual(result, 1)
        self.assertFalse(output.exists())

    def test_standalone_test_plugin_script_runs_from_repository_root(self):
        destination = self.root / 'built.zip'
        result = subprocess.run([sys.executable, str(package_test.ROOT / 'scripts/package_test_plugin.py'),
                                 '--output', str(destination)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(destination.is_file())


if __name__ == '__main__':
    unittest.main()
