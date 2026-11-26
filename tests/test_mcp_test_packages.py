"""Repeatable remote test artifacts must never mutate production packages."""
import hashlib
import importlib.util
import json
import io
import os
import socket
import sys
from pathlib import Path
import subprocess
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'testing/mcp/package_plugins.py'
URL = 'https://example.test/mcp/openai'


class MCPTestPackageTests(unittest.TestCase):
    def launcher_environment(self, folder):
        log = Path(folder) / 'calls.log'
        for name in ('docker', 'git', 'node', 'cloudflared', 'curl', 'openssl'):
            stub = Path(folder) / name
            stub.write_text('#!/bin/sh\nprintf "%s\\n" "$0" >> "$STUB_LOG"\nexit 99\n')
            stub.chmod(0o755)
        (Path(folder) / 'python3').symlink_to(sys.executable)
        environment = os.environ.copy()
        environment.update(PATH=folder + os.pathsep + '/usr/bin:/bin', STUB_LOG=str(log),
                           MOBILERUN_API_KEY='fake-test-key')
        return environment, log

    def test_launcher_validates_and_uses_configured_host_port(self):
        script = ROOT / 'testing/mcp/start-local.sh'
        text = script.read_text()
        self.assertIn('MOBILERUN_LOCAL_MCP_PORT', text)
        self.assertIn('process.env.MOBILERUN_LOCAL_MCP_PORT', text)
        self.assertIn('127.0.0.1:$port:8080', text)
        self.assertIn('127.0.0.1:$port/health', text)
        self.assertIn('host:`127.0.0.1:${port}`', text)
        self.assertEqual(text.count("host:'127.0.0.1', port, method:req.method"), 2)
        self.assertNotIn('127.0.0.1:18080', text)
        self.assertNotIn('port:18080', text)
        self.assertIn('sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)', text)
        with tempfile.TemporaryDirectory() as folder:
            environment, log = self.launcher_environment(folder)
            for port in ('', '0', '65536', '18081', 'abc', '-1', '999999999999999999999'):
                with self.subTest(port=port):
                    environment['MOBILERUN_LOCAL_MCP_PORT'] = port
                    result = subprocess.run(['/bin/bash', str(script), '--no-build'], env=environment,
                                            capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('MOBILERUN_LOCAL_MCP_PORT', result.stderr)
                    self.assertFalse(log.exists() and log.read_text())

    def test_launcher_rejects_occupied_port_before_starting_processes(self):
        with tempfile.TemporaryDirectory() as folder, socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen()
            port = listener.getsockname()[1]
            environment, log = self.launcher_environment(folder)
            environment['MOBILERUN_LOCAL_MCP_PORT'] = str(port)
            result = subprocess.run(['/bin/bash', str(ROOT / 'testing/mcp/start-local.sh'), '--no-build'],
                                    env=environment, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(f'Cannot use 127.0.0.1:{port}', result.stderr)
            self.assertFalse(log.exists() and log.read_text())

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
                        self.assertEqual(manifest['name'], 'mobilerun-test' if 'claude' in path.name else 'mobilerun')
                        config = json.loads(archive.read('.mcp.json' if 'claude' in path.name else 'mcp.json'))
                        self.assertEqual(list(config['mcpServers']), ['mobilerun-test'])
                        if 'claude' in path.name:
                            self.assertEqual(manifest['displayName'], 'Mobilerun Test')
                            self.assertEqual(archive.read(manifest['icon']), (ROOT / 'plugins/claude/assets/icon.png').read_bytes())
                        else:
                            interface = manifest['extensions']['com.openai']['interface']
                            self.assertEqual(interface['displayName'], 'Mobilerun')
                            for key in ('composerIcon', 'logo'):
                                self.assertEqual(interface[key], './assets/logo.svg')
                                self.assertEqual(archive.read(interface[key].removeprefix('./')),
                                                 (ROOT / 'plugins/openai/assets/logo.svg').read_bytes())
                            self.assertIn('Anyone with the URL', interface['longDescription'])
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
                    expected_url = 'https://example.test/' + 'a' * 64 + ('/mcp/claude' if claude else '/mcp/openai')
                    self.assertEqual(server['url'], expected_url)
                    onboarding = archive.read('skills/onboarding/SKILL.md').decode()
                    self.assertIn(expected_url, onboarding)
                    self.assertIn('No client authentication', onboarding)
                    self.assertNotIn('complete browser sign-in', onboarding)
                    self.assertNotIn('Check the selected account/workspace', onboarding)
                    self.assertIn('MOBILERUN_API_KEY', onboarding)
                    self.assertIn('reimport a fresh ZIP', onboarding)
                    readme = archive.read('README.md').decode()
                    self.assertIn(expected_url, readme)
                    self.assertIn('start-local.sh', readme)
                    for name, text in [('onboarding', onboarding), ('README', readme)]:
                        with self.subTest(archive=output.name, document=name):
                            self.assertIn('Use only the `mobilerun-test` MCP server for test checks and actions.', text)
                            self.assertIn('If only production Mobilerun tools are available, report the test connection as unverified.', text)
                            self.assertIn('`list_devices` from `mobilerun-test`', text)
                    with self.subTest(archive=output.name, recovery='missing tools or transport error'):
                        recovery = next((line for line in onboarding.splitlines()
                                         if line.startswith('| No test tools or transport error |')), '')
                        self.assertIn('launcher operator', recovery)
                        self.assertIn('`start-local.sh` is running', recovery)
                        self.assertIn('If the tunnel was restarted, reimport a fresh ZIP.', recovery)
                        self.assertIn('do not infer a dead tunnel', onboarding)

    def test_local_packages_are_copied_to_a_missing_downloads_directory(self):
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, HOME=folder):
            downloads = Path(folder) / 'Downloads'
            outputs = builder.build_local_packages('https://example.test/' + 'a' * 64, Path(folder) / 'zip')
            builder.copy_packages_to_downloads(outputs)
            self.assertEqual(stat.S_IMODE(downloads.stat().st_mode), 0o700)
            self.assertEqual({path.name for path in downloads.iterdir()}, {path.name for path in outputs})
            for output in outputs:
                destination = downloads / output.name
                self.assertEqual(destination.read_bytes(), output.read_bytes())
                self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)

    def test_downloads_copy_replaces_existing_zip_with_private_permissions(self):
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, HOME=folder):
            output = Path(folder) / 'test-plugin-claude.zip'
            output.write_bytes(b'new archive')
            destination = Path(folder) / 'Downloads' / output.name
            destination.parent.mkdir()
            destination.write_bytes(b'old archive')
            destination.chmod(0o644)

            self.assertEqual(builder.copy_packages_to_downloads([output]), [destination])
            self.assertEqual(destination.read_bytes(), b'new archive')
            self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)

    def test_downloads_copy_refuses_symlink_and_preserves_target(self):
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, HOME=folder):
            output = Path(folder) / 'test-plugin-claude.zip'
            output.write_bytes(b'new archive')
            target = Path(folder) / 'keep.zip'
            target.write_bytes(b'keep')
            destination = Path(folder) / 'Downloads' / output.name
            destination.parent.mkdir()
            destination.symlink_to(target)

            with self.assertRaises(ValueError):
                builder.copy_packages_to_downloads([output])

            self.assertEqual(destination.readlink(), target)
            self.assertEqual(target.read_bytes(), b'keep')

    def test_downloads_copy_removes_staged_file_if_replacement_fails(self):
        builder = self.load_builder()
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, HOME=folder):
            output = Path(folder) / 'test-plugin-claude.zip'
            output.write_bytes(b'new archive')
            destination = Path(folder) / 'Downloads' / output.name
            destination.parent.mkdir()
            destination.write_bytes(b'old archive')

            def fail_replace(staged, target):
                self.assertEqual(staged.read_bytes(), b'new archive')
                self.assertEqual(target, destination)
                raise OSError('simulated replacement failure')

            with patch.object(Path, 'replace', autospec=True, side_effect=fail_replace):
                with self.assertRaisesRegex(OSError, 'simulated replacement failure'):
                    builder.copy_packages_to_downloads([output])

            self.assertEqual(destination.read_bytes(), b'old archive')
            self.assertEqual(list(destination.parent.glob('.local-mcp-*')), [])

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
