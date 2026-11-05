"""Publication checks on distributable content, not on live account behavior."""
from pathlib import Path
import re
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class PublicationSafetyTests(unittest.TestCase):
    # Split example patterns so this public test does not contain a real private URL,
    # personal path, credential, or proprietary identifier itself.
    forbidden = {
        'private workspace link': re.compile(
            r'https?://(?:app\.' + r'notion\.com|(?:www\.)?' + r'notion\.so|linear\.app)/'),
        'personal absolute path': re.compile(
            r'/(?:Users|home)/[A-Za-z0-9_.-]+/|/private/var/|[A-Z]:\\Users\\'),
        'private key material': re.compile(
            r'-----BEGIN (?:RSA |EC |OPENSSH )?' + r'PRIVATE KEY-----'),
        'credential literal': re.compile(
            r'gh[pousr]_[A-Za-z0-9]{24,}|github_pat_[A-Za-z0-9_]{30,}'
            r'|sk-[A-Za-z0-9_-]{24,}|AKIA[A-Z0-9]{16}'
            r'|eyJ[A-Za-z0-9_-]{12,}\.eyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}'),
        'internal source path': re.compile(
            r'\b(?:packages|apps)/[A-Za-z0-9_./-]+\.(?:ts|tsx)\b'),
        'hard-coded credit entitlement': re.compile(
            r'\b\d[\d,]*[ -]+(?:monthly[ -]+|one-off[ -]+)?credits?\b', re.I),
    }

    def check_content(self, label, content):
        for category, pattern in self.forbidden.items():
            # Do not include matched secret values in assertion output.
            self.assertFalse(bool(pattern.search(content)), f'{label}: {category}')

    def test_public_text_excludes_private_material(self):
        files = [ROOT / 'README.md']
        for directory in ('plugins', 'docs', '.agents', '.cursor-plugin'):
            files.extend(p for p in (ROOT / directory).rglob('*')
                         if p.is_file() and p.suffix in {'.md', '.json', '.svg'})
        for path in files:
            with self.subTest(file=str(path.relative_to(ROOT))):
                self.check_content(str(path.relative_to(ROOT)), path.read_text())

    def test_internal_records_are_not_in_public_tree(self):
        self.assertFalse((ROOT / 'docs' / 'superpowers').exists())
        self.assertFalse((ROOT / '.superpowers').exists())
        self.assertFalse(list((ROOT / 'docs').rglob('local-preflight-*.md')))

    def test_future_work_plans_are_not_published(self):
        self.assertFalse(list((ROOT / 'docs' / 'marketplace-testing').rglob('*')))
        for path in [ROOT / 'README.md', *(ROOT / 'plugins').rglob('*.md')]:
            self.assertNotIn('docs/marketplace-testing/', path.read_text())

    def test_upload_archives_exclude_private_material_and_match_sources(self):
        for provider in ('claude', 'openai', 'openclaw'):
            with self.subTest(provider=provider):
                package = ROOT / 'plugins' / provider
                expected = {p.relative_to(package).as_posix(): p.read_bytes()
                            for p in package.rglob('*') if p.is_file()}
                with zipfile.ZipFile(ROOT / f'mobilerun-{provider}.zip') as archive:
                    entries = [entry for entry in archive.infolist() if not entry.is_dir()]
                    self.assertEqual(len(entries), len(expected))
                    self.assertEqual({entry.filename for entry in entries}, set(expected))
                    for entry in entries:
                        data = archive.read(entry.filename)
                        self.assertTrue(data == expected[entry.filename],
                                        f'{provider}/{entry.filename}: stale archive')
                        self.check_content(f'{provider}/{entry.filename}',
                                           data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
