# Provider packages

Each package uses a format supported by its intended host. Package availability does not establish live authentication, directory publication, or marketplace approval.

| Provider | Distribution route | Package / verification boundary |
| --- | --- | --- |
| Claude | Plugin bundle and remote connector directory | [Mobilerun bundle implemented](../plugins/claude/README.md). Current official docs call for separate connector and bundle submissions; pairing is possible. Not submitted or approved. |
| OpenAI / ChatGPT | Plugin submission and review | [Portable package implemented](../plugins/openai/README.md), with a repo-local marketplace for desktop testing. Live OAuth, portal scans, reviewer tests and approval remain unverified. |
| Cursor | Marketplace submission and review | [Cursor-native MCP package](../plugins/cursor/README.md). Local packaging and file installation do not establish client loading, authentication, tool access, or public source availability. |
| OpenClaw | Portable bundle publication | [MCP-only Claude-format bundle implemented](../plugins/openclaw/README.md). ClawHub 0.25.1 publish dry-run accepts it as a bundle; standalone inspector rejects the non-native root, so inspector validation remains blocked. No native envelope or standalone skill. Actual install/OAuth/tools, scan, source-release provenance, and publication remain unverified. |

Only packages present in this repository are listed. Consult each host's current public documentation before installation or submission.

## Claude: verified format, unverified live installation

Official documentation checked November 5, 2026:

- [Bundle structure and testing](https://claude.com/docs/plugins/build.md): `.claude-plugin/plugin.json`, root `.mcp.json`, `skills/<name>/SKILL.md`, and README/license. Skills and remote connectors work in chat; agents and hooks do not.
- [Quickstart](https://claude.com/docs/plugins/quickstart.md): remote HTTP OAuth reference, no bundled credentials; `claude plugin validate` is local validation only.
- [Publishing routes](https://claude.com/docs/directory/publish.md): submit the hosted MCP separately, use the same URL and organization to pair with a plugin, and make repository source public before the bundle listing goes live.
- [Pre-submission checks](https://claude.com/docs/plugins/pre-submission-checklist.md): portal validation and security review are additional checks, not established by local tests.

## OpenAI: source package and remaining review work

Official [packaging](https://developers.openai.com/plugins/build/plugins) and [submission](https://developers.openai.com/plugins/deploy/submission) docs checked November 5, 2026 support portable root `plugin.json`, `mcp.json` with `streamable-http`, and `extensions.com.openai.onboardingSkill`. The bundle has listing links, the existing Mobilerun logo, and five positive/three negative proposed review cases. Cases have not been run against a reviewer account.

The OpenAI packages select `https://cloud.mobilerun.ai/api/mcp/openai`; Claude selects `/api/mcp/claude`. Cursor and OpenClaw retain the base `https://cloud.mobilerun.ai/api/mcp` pending their dedicated profiles. Mobilerun documents [OAuth auto-discovery and browser authentication](https://docs.mobilerun.ai/mcp-server#oauth-authentication). Connect through the host's OAuth flow; actual login in each host remains unverified. Do not put credentials in distributed bundles or chat. The canonical portable MCP schema disallows per-server `extensions`, although OpenAI documents an auth extension there. Advanced overrides require checking the portal's accepted schema. Missing required authentication support remains a review blocker; do not use `none` for this protected endpoint.

The repo-local marketplace supports desktop authoring/testing. It does not publish to ChatGPT web or the public directory. A separate custom-MCP connection tests only the hosted server. Marketplace verification and approval are not established by these source packages.

The separate [Test Plugin](../plugins/test-plugin/README.md) now explicitly targets `https://cloud.mobilerun.ai/api/mcp/openai`. Its version 0.2.0 replaces the earlier local stdio configuration with public-profile Streamable HTTP and OAuth discovery. It needs no local MCP runtime or manually configured API key. Profile-specific OAuth metadata is reachable; completed sign-in, the authenticated deployed tool list and live viewer behavior remain unverified.

## Public profile routing

| Package | Profile / endpoint suffix | Status |
| --- | --- | --- |
| Claude | `/api/mcp/claude` | Profile-specific unauthenticated OAuth discovery verified. |
| OpenAI, Test Plugin | `/api/mcp/openai` | Profile-specific unauthenticated OAuth discovery verified. |
| Cursor | `/api/mcp` retained | `/api/mcp/cursor` and its OAuth resource metadata returned 404; dedicated profile deferred. |
| OpenClaw | `/api/mcp` retained | `/api/mcp/openclaw` and its OAuth resource metadata returned 404; dedicated profile deferred. |

These checks do not establish authenticated tool access or UI compatibility. Cursor/OpenClaw are not silently mapped to another provider's profile; their existing base connection remains until those profiles are added.
