# Provider packages

Each package uses a format supported by its intended host. Package availability does not establish live authentication, directory publication, or marketplace approval.

| Provider | Distribution route | Package / verification boundary |
| --- | --- | --- |
| Claude | Plugin bundle and remote connector directory | [Mobilerun bundle implemented](../plugins/claude/README.md). Current official docs call for separate connector and bundle submissions; pairing is possible. Not submitted or approved. |
| OpenAI / ChatGPT | Plugin submission and review | [Portable package implemented](../plugins/openai/README.md), with a repo-local marketplace for desktop testing. Live OAuth, portal scans, reviewer tests and approval remain unverified. |
| Cursor | Marketplace submission and review | [Cursor-native MCP package](../plugins/cursor/README.md). Local packaging and file installation do not establish client loading, authentication, tool access, or public source availability. |
| OpenClaw | Portable bundle publication | [Claude-format bundle implemented](../plugins/openclaw/README.md), including onboarding and billing guidance. The package carries skill files, but OpenClaw runtime skill loading is unverified. ClawHub 0.25.1 publish dry-run accepts it as a bundle; standalone inspector rejects the non-native root. Actual install/OAuth/tools, scan, provenance, and publication remain unverified. |

Only packages present in this repository are listed. Consult each host's current public documentation before installation or submission.

## Claude: verified format, unverified live installation

Official documentation checked November 5, 2026:

- [Bundle structure and testing](https://claude.com/docs/plugins/build.md): `.claude-plugin/plugin.json`, root `.mcp.json`, `skills/<name>/SKILL.md`, and README/license. Skills and remote connectors work in chat; agents and hooks do not.
- [Quickstart](https://claude.com/docs/plugins/quickstart.md): remote HTTP OAuth reference, no bundled credentials; `claude plugin validate` is local validation only.
- [Publishing routes](https://claude.com/docs/directory/publish.md): submit the hosted MCP separately, use the same URL and organization to pair with a plugin, and make repository source public before the bundle listing goes live.
- [Pre-submission checks](https://claude.com/docs/plugins/pre-submission-checklist.md): portal validation and security review are additional checks, not established by local tests.

## OpenAI: source package and remaining review work

Official [packaging](https://developers.openai.com/plugins/build/plugins) and [submission](https://developers.openai.com/plugins/deploy/submission) docs checked November 5, 2026 support portable root `plugin.json`, `mcp.json` with `streamable-http`, and `extensions.com.openai.onboardingSkill`. The bundle has listing links, the existing Mobilerun logo, and five positive/three negative proposed review cases. Cases have not been run against a reviewer account.

The hosted OpenAI package selects `https://cloud.mobilerun.ai/api/mcp/openai`; Claude selects `/api/mcp/claude`; Cursor selects `/api/mcp/cursor`, with deployment and authenticated filtering still unverified. OpenClaw retains the base `https://cloud.mobilerun.ai/api/mcp` pending its dedicated profile. Mobilerun documents [OAuth auto-discovery and browser authentication](https://docs.mobilerun.ai/mcp-server#oauth-authentication). Connect through the host's OAuth flow; actual login in each host remains unverified. Do not put credentials in distributed bundles or chat. The canonical portable MCP schema disallows per-server `extensions`, although OpenAI documents an auth extension there. Advanced overrides require checking the portal's accepted schema. Missing required authentication support remains a review blocker; do not use `none` for this protected endpoint.

The repo-local marketplace supports desktop authoring/testing. It does not publish to ChatGPT web or the public directory. A separate custom-MCP connection tests only the hosted server. Marketplace verification and approval are not established by these source packages.

The separate [Test Plugin](../plugins/test-plugin/README.md) version 0.3.0 uses a Node.js stdio bridge to `http://localhost:8080/mcp/openai`. It requires a compatible desktop-local execution environment, Node.js 20.3 or later, a running local server, and an API key configured outside the package. Use a maintained Node.js release. Local fixture tests verify request forwarding; authenticated native-host access, rendering, and video playback remain unverified. This adapter does not connect regular cloud-backed ChatGPT chats to localhost; that requires a separately configured tunnel or reachable authenticated endpoint.

Production packaging (`python3 scripts/package_plugins.py`) builds only the four hosted provider packages, independently of Test Plugin. The local bridge and credential setup helper are test-only and excluded from production archives. Generate the test archive separately with `python3 scripts/package_test_plugin.py`. This separation does not remove or change the actual MCP server that provides tools and serves the viewer.

## Public profile routing

| Package | Profile / endpoint suffix | Status |
| --- | --- | --- |
| Claude | `/api/mcp/claude` | Profile-specific unauthenticated OAuth discovery verified. |
| OpenAI | `/api/mcp/openai` | Profile-specific unauthenticated OAuth discovery verified. |
| Test Plugin | `http://localhost:8080/mcp/openai` via stdio bridge | Local server and API key required; live host connection unverified. |
| Cursor | `/api/mcp/cursor` selected | Dedicated route and OAuth metadata previously returned 404; current deployment and authenticated tool filtering require verification. |
| OpenClaw | `/api/mcp` retained | `/api/mcp/openclaw` and its OAuth resource metadata returned 404; dedicated profile deferred. |

These checks do not establish authenticated tool access or UI compatibility. Cursor/OpenClaw are not silently mapped to another provider's profile; their existing base connection remains until those profiles are added.
