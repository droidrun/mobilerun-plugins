"""Structural checks of the actual installable bundle; not agent behavior tests."""
import json
from pathlib import Path
import re
import struct
import unittest
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/claude'


class ClaudeBundleTests(unittest.TestCase):
    def read(self, relative):
        path = PLUGIN / relative
        self.assertTrue(path.is_file(), f'Missing bundle component: {relative}')
        return path.read_text()

    def test_manifest(self):
        manifest = json.loads(self.read('.claude-plugin/plugin.json'))
        self.assertRegex(manifest['name'], r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
        self.assertRegex(manifest['version'], r'^\d+\.\d+\.\d+$')
        for field in ('description', 'license'):
            self.assertTrue(manifest[field].strip())
        self.assertTrue(manifest['author']['name'].strip())

    def test_remote_oauth_configuration(self):
        config = json.loads(self.read('.mcp.json'))
        self.assertEqual(config, {'mcpServers': {'mobilerun': {
            'type': 'http', 'url': 'https://cloud.mobilerun.ai/api/mcp/claude'}}})

    def test_directory_privacy_link(self):
        from urllib.parse import urlsplit
        manifest = json.loads(self.read('.claude-plugin/plugin.json'))
        privacy = urlsplit(manifest.get('privacyPolicyUrl', ''))
        self.assertEqual(privacy.scheme, 'https')
        self.assertTrue(privacy.netloc)

    def test_directory_icon_is_bundled_square_png(self):
        manifest = json.loads(self.read('.claude-plugin/plugin.json'))
        self.assertTrue(manifest.get('icon'), 'Missing listing icon reference')
        icon = (PLUGIN / manifest['icon']).resolve()
        self.assertTrue(icon.is_relative_to(PLUGIN.resolve()))
        data = icon.read_bytes()
        self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
        self.assertEqual(data[12:16], b'IHDR')
        width, height = struct.unpack('>II', data[16:24])
        self.assertEqual(width, height)
        self.assertGreaterEqual(width, 512)
        self.assertLessEqual(width, 2048)
        self.assertLess(len(data), 2 * 1024 * 1024)

    def test_readme_links_resolve_inside_bundle(self):
        for target in re.findall(r'\]\(([^)]+)\)', self.read('README.md')):
            if '://' in target or target.startswith('#'):
                continue
            resolved = (PLUGIN / target.split('#')[0]).resolve()
            self.assertTrue(resolved.is_relative_to(PLUGIN.resolve()),
                            f'Link leaves installed bundle: {target}')
            self.assertTrue(resolved.exists(), f'Missing bundled link: {target}')

    def test_self_contained_declarative_package(self):
        self.assertTrue(PLUGIN.is_dir(), 'Installable plugin folder missing')
        allowed = {'.claude-plugin/plugin.json', '.mcp.json', 'README.md', 'LICENSE',
                   'assets/icon.png',
                   *{f'skills/{name}/SKILL.md' for name in ('onboarding', 'mobile-tasks')}}
        files = set()
        for path in PLUGIN.rglob('*'):
            self.assertFalse(path.is_symlink(), f'Symlink in bundle: {path}')
            if path.is_file():
                files.add(path.relative_to(PLUGIN).as_posix())
                self.assertLess(path.stat().st_size, 256 * 1024)
        self.assertEqual(files, allowed)

    def test_skill_discoverable(self):
        text = self.read('skills/onboarding/SKILL.md')
        match = re.match(r'---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n', text)
        self.assertIsNotNone(match, 'Expected plain scalar skill metadata')
        self.assertEqual(match[1], 'onboarding')
        self.assertTrue(match[2].startswith('Use when'))
        self.assertLess(len(match[0]), 1024)

    def test_exact_two_skills_are_packaged(self):
        for name in ('onboarding', 'mobile-tasks'):
            text = self.read(f'skills/{name}/SKILL.md')
            self.assertIn(f'name: {name}', text)

    def test_listing_and_license(self):
        prose = re.sub(r'```.*?```', '', self.read('README.md'), flags=re.S)
        self.assertGreaterEqual(len(prose.split()), 40)
        self.assertEqual(self.read('LICENSE'), (ROOT / 'LICENSE').read_text())

    def test_repository_entry_points(self):
        for relative in ('README.md', 'plugins/README.md', 'docs/providers.md'):
            path = ROOT / relative
            self.assertTrue(path.is_file(), f'Missing repository entry point: {relative}')
            # Broken relative links prevent people reaching the actual bundle.
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' in target or target.startswith('#'):
                    continue
                self.assertTrue((path.parent / target.split('#')[0]).exists(),
                                f'Broken link from {relative}: {target}')


class OpenAIBundleTests(unittest.TestCase):
    plugin = ROOT / 'plugins/openai'

    def read(self, relative):
        path = self.plugin / relative
        self.assertTrue(path.is_file(), f'Missing OpenAI component: {relative}')
        return path.read_text()

    def test_portable_manifest_and_setup_entry(self):
        manifest = json.loads(self.read('plugin.json'))
        self.assertEqual(manifest['$schema'],
                         'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json')
        self.assertEqual(manifest['name'], 'mobilerun')
        self.assertEqual(manifest['version'], '0.1.0')
        self.assertEqual(manifest['license'], 'MIT')
        extension = manifest['extensions']['com.openai']
        skill = extension['onboardingSkill']
        self.assertTrue(skill.startswith('./skills/'))
        self.assertTrue((self.plugin / skill).is_file())
        self.assertNotIn('apps', extension)
        self.assertNotIn('hooks', extension)

    def test_single_remote_server_no_secrets(self):
        config = json.loads(self.read('mcp.json'))
        self.assertEqual(config, {
            '$schema': 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json',
            'mcpServers': {'mobilerun': {
                'type': 'streamable-http',
                'url': 'https://cloud.mobilerun.ai/api/mcp/openai'}}})

    def test_review_cases_use_supported_profile_tools(self):
        review = json.loads(self.read('plugin.json'))['extensions']['com.openai']['review']
        cases = review['test_cases']
        self.assertEqual(len(cases['positive']), 5)
        self.assertEqual(len(cases['negative']), 3)
        # Includes explicitly authorized provisioning; verify inventory per connection.
        supported = {'list_devices', 'get_device', 'list_apps_on_device',
                     'list_tasks', 'get_task_status', 'create_device'}
        for case in cases['positive']:
            with self.subTest(prompt=case['prompt']):
                tools = {name.strip() for name in case['tools_triggered'].split(',')}
                self.assertTrue(tools)
                self.assertLessEqual(tools, supported)
                self.assertTrue(case['expected_behavior'])
        for case in cases['negative']:
            self.assertTrue(case['description'])
            self.assertTrue(case['prompt'])
            self.assertTrue(case['expected_behavior'])
        strict_no_spend = cases['negative'][2]
        self.assertEqual(strict_no_spend['tools_triggered'], 'none (local validation only)')
        self.assertIn('Do not make a live API/MCP call', strict_no_spend['expected_behavior'])

    def test_device_creation_review_cases_respect_slots_and_free_quota(self):
        cases = json.loads((ROOT / 'tests/fixtures/openai-resource-review-cases.json').read_text())
        android = next(case for case in cases['positive'] if 'Android cloud phone' in case['description'])
        self.assertIn('create_device', android['tools_triggered'])
        for term in ('android_cloud_phone', 'free quota', 'concurrency', 'Do not purchase'):
            self.assertIn(term, android['expected_behavior'])
        ios = next(case for case in cases['negative'] if 'iOS' in case['description'])
        self.assertEqual(ios['tools_triggered'], 'list_devices (no create_device)')
        self.assertEqual(ios['prompt'], 'Create an iPhone using my included quota. Do not purchase anything.')
        for hint in ('slot', 'eligible', 'android', 'free minutes'):
            self.assertNotIn(hint, ios['prompt'].lower())
        for term in ('Do not call create_device', 'slot', 'Do not silently substitute Android'):
            self.assertIn(term, ios['expected_behavior'])

    def test_listing_assets_and_links(self):
        interface = json.loads(self.read('plugin.json'))['extensions']['com.openai']['interface']
        for key, limit in (('displayName', 30), ('shortDescription', 30),
                           ('longDescription', 4000), ('developerName', 80)):
            self.assertTrue(interface[key])
            self.assertLessEqual(len(interface[key]), limit)
        for key in ('websiteURL', 'supportURL', 'privacyPolicyURL', 'termsOfServiceURL'):
            self.assertTrue(interface[key].startswith('https://'))
        for key in ('composerIcon', 'logo'):
            relative = interface[key]
            self.assertTrue(relative.startswith('./assets/'))
            asset = self.plugin / relative
            self.assertTrue(asset.resolve().is_relative_to(self.plugin.resolve()))
            self.assertTrue(asset.is_file())
            svg = ET.fromstring(asset.read_text())
            self.assertEqual(svg.attrib['width'], svg.attrib['height'])
            self.assertGreaterEqual(int(svg.attrib['width']), 48)

    def test_self_contained_package(self):
        self.assertTrue(self.plugin.is_dir())
        files = set()
        for path in self.plugin.rglob('*'):
            self.assertFalse(path.is_symlink())
            if path.is_file():
                files.add(path.relative_to(self.plugin).as_posix())
        self.assertEqual(files, {'plugin.json', 'mcp.json', 'README.md', 'LICENSE',
                                 'assets/logo.svg', *{f'skills/{name}/SKILL.md' for name in ('onboarding', 'mobile-tasks')}})
        self.assertEqual(self.read('LICENSE'), (ROOT / 'LICENSE').read_text())

    def test_marketplace_resolves_openai_package(self):
        path = ROOT / '.agents/plugins/marketplace.json'
        self.assertTrue(path.is_file(), 'Missing OpenAI local marketplace')
        marketplace = json.loads(path.read_text())
        entry = next(item for item in marketplace['plugins'] if item['name'] == 'mobilerun')
        self.assertEqual(entry['source'], {'source': 'local', 'path': './plugins/openai'})
        self.assertTrue((ROOT / entry['source']['path'] / 'plugin.json').is_file())
        self.assertEqual(entry['policy']['authentication'], 'ON_INSTALL')


class MarketplaceArtifactTests(unittest.TestCase):
    def test_openclaw_archive_matches_bundle(self):
        package = ROOT / 'plugins/openclaw'
        target = ROOT / 'zip' / 'mobilerun-openclaw.zip'
        self.assertTrue(target.is_file(), 'Missing OpenClaw bundle archive')
        with zipfile.ZipFile(target) as archive:
            self.assertIsNone(archive.testzip())
            files = {p.relative_to(package).as_posix(): p.read_bytes()
                     for p in package.rglob('*') if p.is_file()}
            self.assertEqual({entry.filename for entry in archive.infolist()
                              if not entry.is_dir()}, set(files))
            for name, content in files.items():
                self.assertEqual(archive.read(name), content, name)

    def test_openclaw_single_marker_and_explicit_http_transport(self):
        package = ROOT / 'plugins/openclaw'
        self.assertTrue(package.is_dir(), 'Missing OpenClaw bundle')
        markers = ['.claude-plugin/plugin.json', '.cursor-plugin/plugin.json',
                   '.codex-plugin/plugin.json', 'plugin.json', 'openclaw.plugin.json']
        self.assertEqual([name for name in markers if (package / name).exists()],
                         ['.claude-plugin/plugin.json'])
        manifest = json.loads((package / markers[0]).read_text())
        self.assertEqual(manifest['name'], 'mobilerun')
        self.assertRegex(manifest['version'], r'^\d+\.\d+\.\d+$')
        self.assertEqual(json.loads((package / '.mcp.json').read_text()), {
            'mcpServers': {'mobilerun': {
                'url': 'https://cloud.mobilerun.ai/api/mcp/openclaw',
                'auth': 'oauth',
                'transport': 'streamable-http'}}})
        self.assertIn('contains no OpenClaw profile implementation', (package / 'README.md').read_text())
        self.assertEqual((package / 'LICENSE').read_text(), (ROOT / 'LICENSE').read_text())
        files = set()
        for path in package.rglob('*'):
            self.assertFalse(path.is_symlink())
            if path.is_file():
                files.add(path.relative_to(package).as_posix())
        self.assertEqual(files, {'.claude-plugin/plugin.json', '.mcp.json', 'README.md', 'LICENSE', 'assets/icon.png',
                                 *{f'skills/{name}/SKILL.md' for name in ('onboarding', 'mobile-tasks')}})

    def test_openai_upload_matches_source_and_has_root_mcp(self):
        package = ROOT / 'plugins/openai'
        with zipfile.ZipFile(ROOT / 'zip' / 'mobilerun-openai.zip') as archive:
            self.assertIsNone(archive.testzip())
            files = {p.relative_to(package).as_posix(): p.read_bytes()
                     for p in package.rglob('*') if p.is_file()}
            self.assertEqual({entry.filename for entry in archive.infolist()
                              if not entry.is_dir()}, set(files))
            for name, content in files.items():
                self.assertEqual(archive.read(name), content, name)
            config = json.loads(archive.read('mcp.json'))
            self.assertEqual(len(config['mcpServers']), 1)
            self.assertEqual(config['mcpServers']['mobilerun']['url'],
                             'https://cloud.mobilerun.ai/api/mcp/openai')

    def test_cursor_package_is_self_contained_and_credential_free(self):
        package = ROOT / 'plugins/cursor'
        self.assertTrue(package.is_dir(), 'Missing recovered Cursor package')
        manifest = json.loads((package / '.cursor-plugin/plugin.json').read_text())
        self.assertRegex(manifest['name'], r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
        self.assertEqual(manifest['license'], 'Apache-2.0')
        self.assertTrue((package / 'LICENSE').is_file())
        self.assertTrue((package / 'README.md').is_file())
        self.assertTrue((package / manifest['logo']).is_file())
        self.assertEqual(json.loads((package / 'mcp.json').read_text()), {
            'mcpServers': {'mobilerun': {'url': 'https://cloud.mobilerun.ai/api/mcp/cursor'}}})
        for path in package.rglob('*'):
            self.assertFalse(path.is_symlink())
            self.assertTrue(path.resolve().is_relative_to(package.resolve()))
            if path.is_file():
                self.assertNotIn(path.suffix, {'.pyc', '.exe', '.dylib', '.so'})
                self.assertNotIn(path.name, {'.DS_Store', '.env'})
        self.assertTrue((package / 'skills/onboarding/SKILL.md').is_file())
        for name in ('mobile-tasks',):
            self.assertTrue((package / f'skills/{name}/SKILL.md').is_file())

    def test_all_host_packages_have_synced_shared_skill_sources(self):
        from scripts.sync_skills import PROVIDERS, check
        self.assertEqual(set(PROVIDERS), {'claude', 'openai', 'cursor', 'openclaw', 'test-plugin'})
        self.assertEqual(check(ROOT), [])


class DocumentationTests(unittest.TestCase):
    def test_provider_readme_links_stay_in_installed_package(self):
        for provider in ('cursor', 'openai'):
            package = ROOT / 'plugins' / provider
            for target in re.findall(r'\]\(([^)]+)\)', (package / 'README.md').read_text()):
                if '://' in target or target.startswith('#'):
                    continue
                with self.subTest(provider=provider, target=target):
                    resolved = (package / target.split('#')[0]).resolve()
                    self.assertTrue(resolved.is_relative_to(package.resolve()),
                                    f'Link leaves installed package: {target}')
                    self.assertTrue(resolved.exists(), f'Missing bundled link: {target}')

    def test_relative_links(self):
        from source_files import source_files
        paths = [p for p in source_files(ROOT) if p.suffix == '.md'
                 and (p == ROOT / 'README.md' or p.relative_to(ROOT).parts[0] in {'docs', 'plugins'})]
        for path in paths:
            for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
                if '://' in target or target.startswith('#'):
                    continue
                self.assertTrue((path.parent / target.split('#')[0]).exists(),
                                f'Broken link from {path}: {target}')

if __name__ == '__main__':
    unittest.main()
