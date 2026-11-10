# Mobilerun plugins

Mobilerun integration packages organized by agent provider. The provider packages connect to the public MCP. Development connections are isolated from production packages.

## Available now

| Project | Provider | Package |
| --- | --- | --- |
| Mobilerun | Claude chat | [Bundle and installation instructions](plugins/claude/README.md) |
| Mobilerun | OpenAI / ChatGPT and Codex | [Bundle, local marketplace, and submission instructions](plugins/openai/README.md) |
| Mobilerun | Cursor | [Cursor-native package and local installation](plugins/cursor/README.md) |
| Mobilerun | OpenClaw | [Compatible MCP bundle and publication preflight](plugins/openclaw/README.md) |

All providers include the same two practical skills: `onboarding` for host connection and first-device setup, and `mobile-tasks` for device/app control and bounded agent tasks. Their MCP server tools perform the operations; tasks and devices can consume credits or minutes. Claude selects `https://cloud.mobilerun.ai/api/mcp/claude`; OpenAI selects `https://cloud.mobilerun.ai/api/mcp/openai`; OpenClaw selects `https://cloud.mobilerun.ai/api/mcp/openclaw`. Cursor retains `https://cloud.mobilerun.ai/api/mcp`. The OpenClaw route is declared for its intended dedicated profile, but deployment availability is unverified and historical verification returned 404; do not substitute the broader base endpoint. Mobilerun documents [browser OAuth](https://docs.mobilerun.ai/mcp-server#oauth-authentication). Credentials are not bundled.

## Test package

The **standard cross-host MCP test setup** lives in [`testing/mcp/`](testing/mcp/README.md): a credential bridge, explicit opt-in temporary HTTPS tunnel, transport checks, and separate remote ChatGPT and Claude test ZIP builders. Its regression tests run in the normal suite with fake credentials and loopback servers. They never start Docker or a public tunnel. Runtime URLs and credentials are not committed.

Use `python3 testing/mcp/setup.py --help` for the test lifecycle and `python3 testing/mcp/package_plugins.py --help` for remote ZIP generation. ChatGPT Work was reported working with this setup; regular-chat tool attachment and native Claude use remain separate host checks. Public exposure is never automatic.

The optional local-only fallback remains separate:

[Test Plugin](plugins/test-plugin/README.md) version 0.3.0 connects through a local Node.js stdio bridge to `http://localhost:8080/mcp/openai`. It requires a compatible desktop-local execution environment, Node.js 20.3 or later, the local MCP server, and an API key stored outside the plugin. Use a maintained Node.js release. Its ZIP is generated under the Git-ignored `zip/` directory. This is not the cloud OAuth connector and does not enable localhost access from regular cloud-backed ChatGPT chats; authenticated host execution and live streaming must be verified separately.

The device-streaming experiment is isolated in a separate worktree on branch `mcp-device-streaming`; it is not included in this branch's plugin packages or ZIP exports.

## Repository convention

```text
plugins/<provider>/            # self-contained installable package
.agents/plugins/marketplace.json # OpenAI repo-local testing catalog
docs/providers.md              # provider targets, routes, and evidence
tests/                         # local package validation
testing/mcp/                   # standard bridge/tunnel test setup and remote ZIP builders
```

Add providers directly under `plugins/`; no `projects/mobilerun` nesting. Each provider folder owns its required manifest/configuration, README, license, and optional skills. Choose the native provider format rather than copying a Claude manifest into another provider. Avoid symlinks or references outside the installable folder. Add shared tooling only after actual packages need it. See [package boundaries and account guidance](plugins/README.md).

See the [provider overview](docs/providers.md) for package formats and verification boundaries. A source package is not a verified live installation or approved listing.

## Check locally

The production provider packages need no dependency installation or compilation. ZIPs are generated locally and are not committed. Build the four production archives independently of Test Plugin:

```bash
python3 scripts/package_plugins.py
```

The local adapter and credential setup helper belong only to Test Plugin, not production. Build its separate archive explicitly before running the full repository test suite:

```bash
python3 scripts/package_test_plugin.py
```

Then validate the generated artifacts and source:

```bash
python3 -B -m unittest discover -s tests -v
claude plugin validate plugins/claude
```

Both builders write their default archives to Git-ignored `zip/`. Explicit file lists exclude development dependencies and secrets. Only the separately built Test Plugin includes the local bridge and setup helper; its credential file remains outside the package.

The Claude command requires its CLI. Static checks validate the bundle's shape, not live OAuth, agent decisions, or marketplace acceptance. Follow each package README for upload packaging and manual scenarios. Hosted provider folders ship directly; experimental source/build packages use an explicit runtime-file allowlist. Never put credentials or development scratch files in an upload.

## Distribution

Review the [public-content checklist](docs/publication.md) before sharing repository source, ZIPs, recordings, or reviewer materials. Keep private working notes and account-specific evidence outside the public repository.

For Claude chat, upload a ZIP of the provider folder to test privately. A public directory listing requires separate plugin-bundle and MCP connector submissions, which can be paired under the same organization and endpoint. No publishing is performed by this repository's tests.

For OpenAI, the repo-local marketplace includes the hosted `plugins/openai` and the separate local-development `plugins/test-plugin`. Test Plugin requires a desktop-local mode capable of launching its bridge; merely using the ChatGPT desktop app does not make a cloud-backed chat local. Connect the hosted MCP separately for regular ChatGPT chats. The hosted package remains remote even when installed locally. Account/device APIs and streams remain remote services. Public ZIP submission, identity/domain verification, authentication/tool scans, reviewer access, and recorded test evidence are separate steps.

## License

[MIT](LICENSE), except the recovered Cursor package, which retains its upstream Apache-2.0 license. Each independently distributed package includes its own license notice.
