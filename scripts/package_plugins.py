"""Build all provider ZIPs from explicit distribution file lists."""
from pathlib import Path
import shutil
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.package_test_plugin import package_plugin

FILES = {
    'claude': ('.claude-plugin/plugin.json', '.mcp.json', 'README.md', 'LICENSE', 'skills/onboarding/SKILL.md'),
    'openai': ('plugin.json', 'mcp.json', 'README.md', 'LICENSE', 'assets/logo.svg', 'skills/onboarding/SKILL.md'),
    'cursor': ('.cursor-plugin/plugin.json', 'mcp.json', 'README.md', 'LICENSE', 'assets/logo.svg'),
    'openclaw': ('.claude-plugin/plugin.json', '.mcp.json', 'README.md', 'LICENSE'),
}


def export_provider(provider: str) -> Path:
    package = ROOT / 'plugins' / provider
    destination = ROOT / 'zip' / f'mobilerun-{provider}.zip'
    contents = {}
    for name in FILES[provider]:
        path = package / name
        if any(part.is_symlink() for part in (path, *path.parents)
               if part == package or package in part.parents):
            raise ValueError(f'Refusing symlink in {provider}: {name}')
        if not path.is_file() or not path.resolve().is_relative_to(package.resolve()):
            raise ValueError(f'Missing distribution file in {provider}: {name}')
        contents[name] = path.read_bytes()
        if not contents[name]:
            raise ValueError(f'Empty distribution file in {provider}: {name}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, prefix='.provider-', suffix='.zip', delete=False) as file:
        temporary = Path(file.name)
    try:
        with ZipFile(temporary, 'w', ZIP_DEFLATED, compresslevel=9) as archive:
            for name, data in contents.items():
                info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
        with ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError(f'Archive integrity failed: {provider}')
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


if __name__ == '__main__':
    for provider in FILES:
        target = export_provider(provider)
        # Keep the existing ignored root-level archives in sync for compatibility.
        if provider in ('claude', 'openai', 'openclaw'):
            shutil.copyfile(target, ROOT / target.name)
        print(f'Built {target.relative_to(ROOT)}: {target.stat().st_size:,} bytes')
    target = ROOT / 'zip/test-plugin.zip'
    package_plugin(ROOT / 'plugins/test-plugin', target)
    print(f'Built {target.relative_to(ROOT)}: {target.stat().st_size:,} bytes')
