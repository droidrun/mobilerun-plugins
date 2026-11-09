"""Build both remote MCP test plugins from a supplied temporary HTTPS URL."""
import argparse
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.sync_skills import _regular_file, check

VERSION = '0.4.0'
ARTIFACTS = ('test-plugin-openai.zip', 'test-plugin-claude.zip')


def validate_url(url: str) -> str:
    """Require the public bridge route, without credentials or URL ambiguity."""
    if not isinstance(url, str) or re.search(r'[\s\\]', url):
        raise ValueError('Expected an HTTPS bridge URL without whitespace')
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        raise ValueError('Invalid bridge URL') from None
    if (parts.scheme != 'https' or not parts.hostname
            or parts.username is not None or parts.password is not None
            or parts.path != '/mcp/openai' or parts.query or parts.fragment
            or (port is not None and not 1 <= port <= 65535)):
        raise ValueError('Expected HTTPS URL ending /mcp/openai without credentials, query, or fragment')
    return url


def package_contents(provider: str, url: str) -> dict[str, bytes]:
    source = ROOT / 'plugins' / ('claude' if provider == 'claude' else 'test-plugin')
    claude = provider == 'claude'
    manifest_path = '.claude-plugin/plugin.json' if claude else 'plugin.json'
    manifest = json.loads(_regular_file(source, manifest_path).read_text())
    manifest.update(name='mobilerun-tunnel-test' if claude else 'test-plugin', version=VERSION,
                    description='Temporary remote MCP test connection. No client authentication required.')
    if claude:
        manifest['displayName'] = 'Mobilerun Tunnel Test'
    else:
        interface = manifest['extensions']['com.openai']['interface']
        interface.update(shortDescription='Remote MCP test', longDescription=(
            'Remote MCP test connection for ChatGPT Work. No client authentication or local Node.js '
            'bridge is required. Regular chat tool attachment remains unverified. Anyone with the URL '
            'can act through the bridge owner account. Development use only.'
        ))
        manifest['keywords'] = ['mobilerun', 'mcp', 'testing', 'remote']
    server = {'type': 'http' if claude else 'streamable-http', 'url': url}
    config = {'mcpServers': {'mobilerun-tunnel-test' if claude else 'test-plugin': server}}
    if not claude:
        config = {'$schema': 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json', **config}
    shared = _regular_file(ROOT, 'shared/onboarding-first-device.md').read_text()
    shared = shared.replace('Reconnect in the host and complete browser sign-in.',
                            'Check that the private credential bridge is running; no client login is used.')
    onboarding = (
        '---\nname: onboarding\ndescription: Use when checking the Mobilerun tunnel test '
        'connection, finding devices, or setting up a first phone.\n---\n\n'
        '# Connect the remote test plugin\n\n'
        f'Enable the plugin MCP connection to `{url}` in a compatible host. '
        'No client authentication, client API key, browser sign-in, or local Node.js launcher is required. '
        'The server-side bridge supplies its owner credential privately. Never ask for a key in chat. '
        'Anyone with this URL can access the exposed tools as the owner, including phone control and '
        'credit-consuming operations. The tunnel is temporary. If tools are unavailable, report that '
        'host tool attachment is unverified; do not infer a dead tunnel or successful connection.\n\n'
        + shared
    )
    host = 'Claude' if claude else 'ChatGPT Work'
    readme = (
        f'# {host} remote MCP test plugin\n\nVersion: {VERSION}.\n\nEndpoint: `{url}`\n\n'
        'No client authentication is required. No credentials are bundled. Anyone with the URL can '
        'use all exposed tools as the bridge owner, including device control and credit-consuming '
        'actions. Development testing only; stop the tunnel when finished.\n\n'
        'This uses the bridge route /mcp/openai and the origin OpenAI policy profile, not a '
        'Claude-specific profile. The Mac, Docker MCP origin, bridge, and tunnel must remain running. '
        'Quick Tunnel restarts change the hostname; rebuild both ZIPs with the new URL.\n\n'
        'Bundled skills: onboarding and mobile-tasks. Verify initialization and tool discovery first, '
        'then explicitly request list_devices to verify account access. Do not create devices just '
        'to test installation. Backend usage is still subject to the account plan and billing.\n\n'
        + ('Extract the ZIP and load its folder in a compatible Claude plugin host. With Claude Code, '
           'use `claude --plugin-dir ./extracted-plugin`. Other Claude surfaces may require their own '
           'connector setup; importing skills does not prove MCP tool availability. Native host use '
           'must be tested separately.\n' if claude else
           'Import in the supported ChatGPT plugin UI and enable the connection. This setup was '
           'reported working in ChatGPT Work; tool attachment in regular chats is not established.\n')
    )
    return {
        manifest_path: (json.dumps(manifest, indent=2) + '\n').encode(),
        '.mcp.json' if claude else 'mcp.json': (json.dumps(config, indent=2) + '\n').encode(),
        'README.md': readme.encode(),
        'LICENSE': _regular_file(source, 'LICENSE').read_bytes(),
        'skills/onboarding/SKILL.md': onboarding.encode(),
        'skills/mobile-tasks/SKILL.md': _regular_file(source, 'skills/mobile-tasks/SKILL.md').read_bytes(),
    }


def build_packages(url: str, output_dir: Path) -> list[Path]:
    url = validate_url(url)
    output_dir = Path(output_dir).absolute()
    if output_dir.is_symlink():
        raise ValueError('Refusing symlinked output directory')
    # macOS exposes its temporary directory through the system /var symlink.
    output_dir = output_dir.resolve()
    if check(ROOT):
        raise ValueError('Shared skills are out of sync; run scripts/sync_skills.py')
    packages = [package_contents(provider, url) for provider in ('openai', 'claude')]
    outputs = [output_dir / name for name in ARTIFACTS]
    if any(p.is_symlink() or (p.exists() and not p.is_file()) for p in outputs):
        raise ValueError('Refusing nonregular output archive')
    output_dir.mkdir(parents=True, exist_ok=True)
    for output, contents in zip(outputs, packages):
        with tempfile.NamedTemporaryFile(dir=output_dir, prefix='.mcp-test-', suffix='.zip', delete=False) as file:
            temporary = Path(file.name)
        try:
            with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                for name, data in contents.items():
                    entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                    entry.compress_type = zipfile.ZIP_DEFLATED
                    entry.external_attr = 0o100644 << 16
                    archive.writestr(entry, data)
            with zipfile.ZipFile(temporary) as archive:
                if archive.testzip() is not None:
                    raise ValueError('Archive integrity check failed')
            temporary.replace(output)
        finally:
            temporary.unlink(missing_ok=True)
    return outputs


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'zip')
    args = parser.parse_args(argv)
    try:
        outputs = build_packages(args.url, args.output_dir)
    except (ValueError, OSError):
        print('Cannot build test packages: check URL, source files, and output directory.', file=sys.stderr)
        return 1
    for output in outputs:
        print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
