# Mobilerun plugins

Thin Mobilerun integration packages organized by agent provider. Each package connects to the existing MCP; tools and operational guidance stay on the server.

## Available now

| Project | Provider | Package |
| --- | --- | --- |
| Mobilerun | Claude chat | [Bundle and installation instructions](plugins/claude/README.md) |
| Mobilerun | OpenAI / ChatGPT and Codex | [Bundle, local marketplace, and submission instructions](plugins/openai/README.md) |
| Mobilerun | Cursor | [Cursor-native package and local installation](plugins/cursor/README.md) |
| Mobilerun | OpenClaw | [Compatible MCP bundle and publication preflight](plugins/openclaw/README.md) |

All packages include a hosted MCP connection reference. Claude and OpenAI also include provider-specific onboarding for connection problems and included credits. Packages do not grant credits, implement device workflows, or bundle API keys or other credentials. Connecting to the hosted MCP may require credentials configured privately through the host.

## Repository convention

```text
plugins/<provider>/            # self-contained installable package
.agents/plugins/marketplace.json # OpenAI repo-local testing catalog
docs/providers.md              # provider targets, routes, and evidence
tests/                         # local package validation
```

Add providers directly under `plugins/`; no `projects/mobilerun` nesting. Each provider folder owns its required manifest/configuration, README, license, and optional skills. Choose the native provider format rather than copying a Claude manifest into another provider. Avoid symlinks or references outside the installable folder. Add shared tooling only after actual packages need it. See [package boundaries and account guidance](plugins/README.md).

See the [provider overview](docs/providers.md) for package formats and verification boundaries. A source package is not a verified live installation or approved listing.

## Check locally

The [marketplace testing pack](docs/marketplace-testing/README.md) contains OpenAI review cases and video preparation, Claude prompts and tool coverage, Cursor local checks, and Grok Bot local/in-app checks. Prepared instructions are not evidence of executed tests.

No dependency installation or compilation is needed. ZIPs are generated locally and are not committed. From the repository root, build them before running the tests; repeat this after changing any package file:

```bash
python3 - <<'PY'
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

for provider in ('claude', 'openai', 'openclaw'):
    package = Path('plugins') / provider
    files = sorted(package.rglob('*'))
    if any(path.is_symlink() for path in files):
        raise SystemExit(f'Refusing symlink in {package}')
    target = Path(f'mobilerun-{provider}.zip')
    with ZipFile(target, 'w', compression=ZIP_DEFLATED) as archive:
        for path in files:
            if path.is_file():
                archive.writestr(path.relative_to(package).as_posix(), path.read_bytes())
    print(target)
PY
```

Then validate the generated artifacts and source:

```bash
python3 -B -m unittest discover -s tests -v
claude plugin validate plugins/claude
```

The Claude command requires its CLI. Static checks validate the bundle's shape, not live OAuth, agent decisions, or marketplace acceptance. Follow each package README for upload packaging and manual scenarios. Every file under a provider package is shipped; do not put credentials or development scratch files there.

## Distribution

Review the [public-content checklist](docs/publication.md) before sharing repository source, ZIPs, recordings, or reviewer materials. Keep private working notes and account-specific evidence outside the public repository.

For Claude chat, upload a ZIP of the provider folder to test privately. A public directory listing requires separate plugin-bundle and MCP connector submissions, which can be paired under the same organization and endpoint. No publishing is performed by this repository's tests.

For OpenAI, the repo-local marketplace points only to `plugins/openai`. Use the ChatGPT desktop app for full local-package testing, or connect the hosted MCP separately in ChatGPT web. Public ZIP submission, domain verification, OAuth/tool scans, reviewer access, and recorded test evidence are separate steps.

## License

[MIT](LICENSE), except the recovered Cursor package, which retains its upstream Apache-2.0 license. Each independently distributed package includes its own license notice.
