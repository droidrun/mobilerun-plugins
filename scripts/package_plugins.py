"""Build all provider ZIPs from explicit distribution file lists."""
from pathlib import Path
import json
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.sync_skills import check as check_shared_skills

SKILL_FILES = tuple(f'skills/{name}/SKILL.md' for name in ('onboarding', 'mobile-tasks'))
FILES = {
    'claude': ('.claude-plugin/plugin.json', '.mcp.json', 'README.md', 'LICENSE', 'assets/icon.png', *SKILL_FILES),
    'openai': ('plugin.json', 'mcp.json', 'README.md', 'LICENSE', 'assets/logo.svg', *SKILL_FILES),
    'cursor': ('.cursor-plugin/plugin.json', 'mcp.json', 'README.md', 'LICENSE', 'assets/logo.svg', *SKILL_FILES),
    'openclaw': ('.claude-plugin/plugin.json', '.mcp.json', 'README.md', 'LICENSE', *SKILL_FILES),
}
HOST = 'https://cloud.mobilerun.ai/api/mcp'
CONNECTORS = {
    'claude': {'type': 'http', 'url': HOST + '/claude'},
    'openai': {'type': 'streamable-http', 'url': HOST + '/openai'},
    'cursor': {'url': HOST + '/cursor'},
    'openclaw': {'transport': 'streamable-http', 'url': HOST},
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
    config_name = '.mcp.json' if provider in ('claude', 'openclaw') else 'mcp.json'
    config = json.loads(contents[config_name])
    expected = {'mcpServers': {'mobilerun': CONNECTORS[provider]}}
    if provider == 'openai':
        expected['$schema'] = 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json'
    if config != expected:
        raise ValueError(f'Invalid hosted MCP configuration in {provider}: {config_name}')
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
    stale = check_shared_skills(ROOT, providers=FILES)
    if stale:
        raise SystemExit('Shared skills are out of sync; run python3 scripts/sync_skills.py')
    for provider in FILES:
        target = export_provider(provider)
        print(f'Built {target.relative_to(ROOT)}: {target.stat().st_size:,} bytes')
