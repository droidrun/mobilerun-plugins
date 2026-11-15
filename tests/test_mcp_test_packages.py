"""Repeatable remote test artifacts must never mutate production packages."""
import hashlib
import importlib.util
import json
import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'testing/mcp/package_plugins.py'
URL = 'https://example.test/mcp/openai'


class MCPTestPackageTests(unittest.TestCase):
    def test_launcher_requires_an_existing_git_checkout_before_starting(self):
        environment = os.environ.copy()
        environment.pop('MOBILERUN_MCP_REPO', None)
        script = str(ROOT / 'testing/mcp/start-local.sh')
        result = subprocess.run(['bash', script], env=environment, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('MOBILERUN_MCP_REPO', result.stderr)
        with tempfile.TemporaryDirectory() as folder:
            environment['MOBILERUN_MCP_REPO'] = folder
            result = subprocess.run(['bash', script], env=environment, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('git checkout', result.stderr)

    def test_manifest_assets_exist_in_local_and_remote_archives(self):
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as folder:
            for mode in ('remote', 'local'):
                output = Path(folder) / mode
                archives = (builder.build_packages(URL, output) if mode == 'remote' else
                            builder.build_local_packages('https://example.test/' + 'a' * 64, output))
                for path in archives:
                    with self.subTest(mode=mode, archive=path.name), zipfile.ZipFile(path) as archive:
                        manifest = json.loads(archive.read('.claude-plugin/plugin.json' if 'claude' in path.name else 'plugin.json'))
                        def assets(value):
                            if isinstance(value, dict):
                                for key, item in value.items():
                                    if isinstance(item, str) and (item.startswith('assets/') or item.startswith('./assets/')):
                                        yield item.removeprefix('./')
                                    else:
                                        yield from assets(item)
                            elif isinstance(value, list):
                                for item in value:
                                    yield from assets(item)
                        for asset in assets(manifest):
                            self.assertIn(asset, archive.namelist())

    def test_local_packages_use_distinct_profile_routes_and_test_guidance(self):
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as folder:
            outputs = builder.build_local_packages('https://example.test/' + 'a' * 64, Path(folder))
            for output in outputs:
                claude = 'claude' in output.name
                with zipfile.ZipFile(output) as archive:
                    config = json.loads(archive.read('.mcp.json' if claude else 'mcp.json'))
                    server, = config['mcpServers'].values()
                    self.assertEqual(server['url'], 'https://example.test/' + 'a' * 64 + ('/mcp/claude' if claude else '/mcp/openai'))
                    self.assertIn('No client authentication', archive.read('skills/onboarding/SKILL.md').decode())
                    self.assertNotIn('complete browser sign-in', archive.read('skills/onboarding/SKILL.md').decode())
                    if claude:
                        manifest = json.loads(archive.read('.claude-plugin/plugin.json'))
                        self.assertEqual(manifest['name'], 'mobilerun-tunnel-test')

    def load_builder(self):
        self.assertTrue(SCRIPT.is_file(), 'Tracked remote test package builder missing')
        spec = importlib.util.spec_from_file_location('mcp_test_package_builder', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_builds_both_provider_formats_and_current_skills(self):
        builder = self.load_builder()
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (ROOT / 'plugins').rglob('*') if p.is_file()}
        with tempfile.TemporaryDirectory() as folder:
            outputs = builder.build_packages(URL, Path(folder))
            self.assertEqual({p.name for p in outputs},
                             {'test-plugin-openai.zip', 'test-plugin-claude.zip'})
            for output in outputs:
                with self.subTest(output=output.name), zipfile.ZipFile(output) as archive:
                    self.assertIsNone(archive.testzip())
                    claude = 'claude' in output.name
                    config = json.loads(archive.read('.mcp.json' if claude else 'mcp.json'))
                    server, = config['mcpServers'].values()
                    self.assertEqual(server, {'type': 'http' if claude else 'streamable-http', 'url': URL})
                    manifest = json.loads(archive.read('.claude-plugin/plugin.json' if claude else 'plugin.json'))
                    self.assertEqual(manifest['version'], '0.4.0')
                    self.assertIn('skills/onboarding/SKILL.md', archive.namelist())
                    self.assertIn('skills/mobile-tasks/SKILL.md', archive.namelist())
                    self.assertFalse(any('workflow-automation' in n or n.startswith('scripts/')
                                         for n in archive.namelist()))
                    onboarding = archive.read('skills/onboarding/SKILL.md').decode()
                    self.assertIn('No client authentication', onboarding)
                    self.assertNotIn('complete browser sign-in', onboarding)
                    self.assertIn('ChatGPT Work' if not claude else 'Claude', archive.read('README.md').decode())
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in before})

    def test_invalid_urls_fail_without_touching_outputs(self):
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'test-plugin-openai.zip'
            output.write_bytes(b'keep')
            for url in ['http://example.test/mcp/openai', 'https://user:secret@example.test/mcp/openai',
                        'https://@example.test/mcp/openai', 'https://:pass@example.test/mcp/openai',
                        'https://example.test/mcp/openai?key=secret', 'https://example.test/mcp/openai#x',
                        'https://example.test/wrong', 'https://example.test/mcp/openai\n',
                        'https://example.test:bad/mcp/openai']:
                with self.subTest(url=url), self.assertRaises(ValueError):
                    builder.build_packages(url, Path(folder))
                self.assertEqual(output.read_bytes(), b'keep')

    def test_deterministic_allowlisted_output_and_no_standard_zip_overwrite(self):
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as folder:
            outdir = Path(folder)
            standard = outdir / 'test-plugin.zip'
            standard.write_bytes(b'standard local package')
            first = {p.name: p.read_bytes() for p in builder.build_packages(URL, outdir)}
            second = {p.name: p.read_bytes() for p in builder.build_packages(URL, outdir)}
            self.assertEqual(first, second)
            self.assertEqual(standard.read_bytes(), b'standard local package')
            for blob in first.values():
                with zipfile.ZipFile(io.BytesIO(blob)) as archive:
                    for name in archive.namelist():
                        self.assertNotIn(b'dr_sk_', archive.read(name))
                        self.assertFalse(name.startswith('/') or '..' in Path(name).parts)

    def test_symlinked_outputs_are_rejected_without_replacing_targets(self):
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as folder:
            outdir = Path(folder)
            victim = outdir / 'victim'
            victim.write_bytes(b'keep')
            (outdir / 'test-plugin-claude.zip').symlink_to(victim)
            with self.assertRaises(ValueError):
                builder.build_packages(URL, outdir)
            self.assertEqual(victim.read_bytes(), b'keep')
            self.assertFalse((outdir / 'test-plugin-openai.zip').exists())


if __name__ == '__main__':
    unittest.main()
