# Mobilerun plugins

Mobilerun integration packages organized by agent provider. The active packages connect to the public MCP; Test Plugin explicitly selects its OpenAI profile with browser OAuth.

## Available now

| Project | Provider | Package |
| --- | --- | --- |
| Mobilerun | Claude chat | [Bundle and installation instructions](plugins/claude/README.md) |
| Mobilerun | OpenAI / ChatGPT and Codex | [Bundle, local marketplace, and submission instructions](plugins/openai/README.md) |
| Mobilerun | Cursor | [Cursor-native package and local installation](plugins/cursor/README.md) |
| Mobilerun | OpenClaw | [Compatible MCP bundle and publication preflight](plugins/openclaw/README.md) |

Claude selects `https://cloud.mobilerun.ai/api/mcp/claude`; OpenAI selects `https://cloud.mobilerun.ai/api/mcp/openai`. Cursor and OpenClaw retain `https://cloud.mobilerun.ai/api/mcp` until their dedicated profiles are available. Mobilerun documents [browser OAuth](https://docs.mobilerun.ai/mcp-server#oauth-authentication); actual host login remains unverified. Claude and OpenAI also include provider-specific onboarding for connection problems and included credits. These packages do not grant credits, implement device workflows, or bundle credentials.

## Test package

[Test Plugin](plugins/test-plugin/README.md) is listed in the local marketplace and connects to `https://cloud.mobilerun.ai/api/mcp/openai` using browser OAuth. No local MCP process, Node.js, or account API-key setup is required. Its ZIP is generated under the Git-ignored `zip/` directory; completed OAuth, the deployed authenticated tool list, and live streaming remain unverified.

The device-streaming experiment is isolated in a separate worktree on branch `mcp-device-streaming`; it is not included in this branch's plugin packages or ZIP exports.

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

These public-MCP packages need no dependency installation or compilation. ZIPs are generated locally and are not committed. From the repository root, refresh all five archives before running the tests:

```bash
python3 scripts/package_plugins.py
```

Then validate the generated artifacts and source:

```bash
python3 -B -m unittest discover -s tests -v
claude plugin validate plugins/claude
```

All archives are written to Git-ignored `zip/`. The existing root-level Claude, OpenAI and OpenClaw archive paths are refreshed as identical compatibility copies. The exporter uses explicit file lists, so it does not ship development dependencies, local runtimes, or secrets.

The Claude command requires its CLI. Static checks validate the bundle's shape, not live OAuth, agent decisions, or marketplace acceptance. Follow each package README for upload packaging and manual scenarios. Hosted provider folders ship directly; experimental source/build packages use an explicit runtime-file allowlist. Never put credentials or development scratch files in an upload.

## Distribution

Review the [public-content checklist](docs/publication.md) before sharing repository source, ZIPs, recordings, or reviewer materials. Keep private working notes and account-specific evidence outside the public repository.

For Claude chat, upload a ZIP of the provider folder to test privately. A public directory listing requires separate plugin-bundle and MCP connector submissions, which can be paired under the same organization and endpoint. No publishing is performed by this repository's tests.

For OpenAI, the repo-local marketplace includes the existing hosted `plugins/openai` and the separate public-profile `plugins/test-plugin`. Use the ChatGPT desktop app for local-package testing, or connect the hosted MCP separately in ChatGPT web. Installing a package locally does not make its MCP execution local. Public ZIP submission, identity/domain verification, authentication/tool scans, reviewer access, and recorded test evidence are separate steps.

## License

[MIT](LICENSE), except the recovered Cursor package, which retains its upstream Apache-2.0 license. Each independently distributed package includes its own license notice.
