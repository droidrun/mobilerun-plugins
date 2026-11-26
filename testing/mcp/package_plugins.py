"""Build both remote MCP test plugins from a supplied temporary HTTPS URL."""
import argparse
import json
import os
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


def validate_url(url: str, *, local: bool = False) -> str:
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
            or (not re.fullmatch(r'/[0-9a-f]{64,}/mcp/openai', parts.path) if local else parts.path != '/mcp/openai') or parts.query or parts.fragment
            or (port is not None and not 1 <= port <= 65535)):
        raise ValueError('Expected HTTPS URL ending /mcp/openai without credentials, query, or fragment')
    return url


def package_contents(provider: str, url: str, local: bool = False) -> dict[str, bytes]:
    source = ROOT / 'plugins' / ('claude' if provider == 'claude' else 'test-plugin')
    claude = provider == 'claude'
    manifest_path = '.claude-plugin/plugin.json' if claude else 'plugin.json'
    manifest = json.loads(_regular_file(source, manifest_path).read_text())
    manifest.update(name='mobilerun-test' if claude else 'mobilerun', version=VERSION,
                    description='Temporary remote MCP test connection. Anyone with the URL can act as the bridge account owner.')
    if claude:
        manifest['displayName'] = 'Mobilerun Test'
    else:
        interface = manifest['extensions']['com.openai']['interface']
        interface.update(displayName='Mobilerun', composerIcon='./assets/logo.svg', logo='./assets/logo.svg',
                         shortDescription='Remote MCP test', longDescription=(
            'Remote MCP test connection for ChatGPT Work. No client authentication or local Node.js '
            'bridge is required. Regular chat tool attachment remains unverified. Anyone with the URL '
            'can act through the bridge owner account. Development use only.'
        ))
        manifest['keywords'] = ['mobilerun', 'mcp', 'testing', 'remote']
    server = {'type': 'http' if claude else 'streamable-http', 'url': url}
    config = {'mcpServers': {'mobilerun-test': server}}
    if not claude:
        config = {'$schema': 'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json', **config}
    test_server_guidance = (
        'Use only the `mobilerun-test` MCP server for test checks and actions. '
        'If only production Mobilerun tools are available, report the test connection as unverified.'
    )
    shared = _regular_file(ROOT, 'shared/onboarding-first-device.md').read_text()
    shared = shared.replace('Use the Mobilerun tools exposed by the host. When `list_devices` is available,',
                            'When `list_devices` from `mobilerun-test` is available,')
    recovery = (
        'Have the launcher operator check that `start-local.sh` is running and that '
        '`MOBILERUN_API_KEY` is valid. If the tunnel was restarted, reimport a fresh ZIP. '
        'No client login is used.' if local else
        'Check that the private credential bridge is running; no client login is used.'
    )
    shared = shared.replace('Reconnect in the host and complete browser sign-in.', recovery)
    if local:
        shared = shared.replace(
            '| No Mobilerun tools | Enable the plugin/MCP connection in the host and check workspace availability. |',
            f'| No test tools or transport error | Enable the test connection in the host. {recovery} |',
        )
        shared = shared.replace('Check the selected account/workspace and its access permissions.',
                                'Check the permissions of the account that owns the launcher API key.')
    onboarding = (
        '---\nname: onboarding\ndescription: Use when checking the Mobilerun tunnel test '
        'connection, finding devices, or setting up a first phone.\n---\n\n'
        '# Connect the remote test plugin\n\n'
        f'Enable the plugin MCP connection to `{url}` in a compatible host. '
        'No client authentication, client API key, browser sign-in, or local Node.js launcher is required. '
        'The server-side bridge supplies its owner credential privately. Never ask for a key in chat. '
        'Anyone with this URL can access the exposed tools as the owner, including phone control and '
        f'credit-consuming operations. The tunnel is temporary. {test_server_guidance} '
        'If test tools are unavailable, report that '
        'host tool attachment is unverified; do not infer a dead tunnel or successful connection.\n\n'
        + shared
    )
    host = 'Claude' if claude else 'ChatGPT Work'
    profile_guidance = ('This uses the host-specific MCP policy profile.' if local else
                        'This uses the bridge route /mcp/openai and the origin OpenAI policy profile, '
                        'not a Claude-specific profile.')
    runtime_guidance = ('Keep `testing/mcp/start-local.sh` running while using this plugin.' if local else
                        'The Mac, Docker MCP origin, bridge, and tunnel must remain running.')
    readme = (
        f'# {host} remote MCP test plugin\n\nVersion: {VERSION}.\n\nEndpoint: `{url}`\n\n'
        'No client authentication is required. No credentials are bundled. Anyone with the URL can '
        'use all exposed tools as the bridge owner, including device control and credit-consuming '
        'actions. Development testing only; stop the tunnel when finished.\n\n'
        f'{profile_guidance} {runtime_guidance} '
        'Quick Tunnel restarts change the hostname; rebuild both ZIPs with the new URL.\n\n'
        f'Bundled skills: onboarding and mobile-tasks. {test_server_guidance} '
        'Verify initialization and tool discovery first, then explicitly request `list_devices` '
        'from `mobilerun-test` to verify account access. Do not create devices just '
        'to test installation. Backend usage is still subject to the account plan and billing.\n\n'
        + ('Extract the ZIP and load its folder in a compatible Claude plugin host. With Claude Code, '
           'use `claude --plugin-dir ./extracted-plugin`. Other Claude surfaces may require their own '
           'connector setup; importing skills does not prove MCP tool availability. Native host use '
           'must be tested separately.\n' if claude else
           'Import in the supported ChatGPT plugin UI and enable the connection. This setup was '
           'reported working in ChatGPT Work; tool attachment in regular chats is not established.\n')
    )
    contents = {
        manifest_path: (json.dumps(manifest, indent=2) + '\n').encode(),
        '.mcp.json' if claude else 'mcp.json': (json.dumps(config, indent=2) + '\n').encode(),
        'README.md': readme.encode(),
        'LICENSE': _regular_file(source, 'LICENSE').read_bytes(),
        'skills/onboarding/SKILL.md': onboarding.encode(),
        'skills/mobile-tasks/SKILL.md': _regular_file(source, 'skills/mobile-tasks/SKILL.md').read_bytes(),
    }
    if claude:
        icon = manifest['icon']
        contents[icon] = _regular_file(source, icon).read_bytes()
    else:
        contents['assets/logo.svg'] = _regular_file(ROOT / 'plugins' / 'openai', 'assets/logo.svg').read_bytes()
    # Include all additional skill files (such as shared references), but never symlinks.
    skills = source / 'skills'
    for path in sorted(skills.rglob('*')):
        if path.is_symlink():
            raise ValueError('Refusing symlink in skill tree')
        if path.is_file():
            name = path.relative_to(source).as_posix()
            if name not in contents:
                contents[name] = _regular_file(source, name).read_bytes()
    return contents


def build_packages(url: str, output_dir: Path, *, local: bool = False) -> list[Path]:
    url = validate_url(url, local=local)
    output_dir = Path(output_dir).absolute()
    if output_dir.is_symlink():
        raise ValueError('Refusing symlinked output directory')
    # macOS exposes its temporary directory through the system /var symlink.
    output_dir = output_dir.resolve()
    if check(ROOT):
        raise ValueError('Shared skills are out of sync; run scripts/sync_skills.py')
    claude_url = url.removesuffix('/openai') + '/claude' if local else url
    packages = [package_contents('openai', url, local), package_contents('claude', claude_url, local)]
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


def build_local_packages(base_url: str, output_dir: Path) -> list[Path]:
    parts = urlsplit(base_url)
    if not re.fullmatch(r'/[0-9a-f]{64,}', parts.path) or parts.query or parts.fragment:
        raise ValueError('Expected a private token URL')
    return build_packages(base_url + '/mcp/openai', output_dir, local=True)


def copy_packages_to_downloads(outputs: list[Path]) -> list[Path]:
    """Copy local test archives atomically, keeping their private permissions."""
    downloads = Path.home() / 'Downloads'
    downloads.mkdir(mode=0o700, exist_ok=True)
    destinations = []
    for output in outputs:
        destination = downloads / output.name
        if destination.is_symlink() or (destination.exists() and not destination.is_file()):
            raise ValueError('Refusing non-regular destination')
        fd, name = tempfile.mkstemp(prefix='.local-mcp-', suffix='.zip', dir=downloads)
        temporary = Path(name)
        try:
            with os.fdopen(fd, 'wb') as file:
                file.write(output.read_bytes())
            if destination.is_symlink() or (destination.exists() and not destination.is_file()):
                raise ValueError('Refusing non-regular destination')
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
        destinations.append(destination)
    return destinations


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
