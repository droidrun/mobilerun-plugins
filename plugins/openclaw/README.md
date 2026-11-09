# Mobilerun for OpenClaw

A compatible MCP bundle for OpenClaw. This is a **Claude-format bundle consumed by OpenClaw**, not a native OpenClaw plugin. Exactly one format marker, `.claude-plugin/plugin.json`, identifies the bundle. It includes `onboarding` for connection and first-device setup, and `mobile-tasks` for device/app control and bounded tasks. OpenClaw skill loading is not tested here. No hooks, local runtime, or dependencies are included.

The root `.mcp.json` declares one hosted server at `https://cloud.mobilerun.ai/api/mcp`, explicitly using `streamable-http` rather than the default SSE transport. Mobilerun documents [browser OAuth](https://docs.mobilerun.ai/mcp-server#oauth-authentication) for this endpoint; use the host's connection flow and do not put credentials in the bundle or chat. OpenClaw runtime authentication remains unverified. Tools, prompts, permissions, and task execution remain on the MCP server. Available tools depend on the authenticated connection and server profile.

The dedicated `/api/mcp/openclaw` profile is deferred: that public route and its OAuth metadata returned 404 during verification. This package retains the existing base endpoint until the OpenClaw profile is added; it does not substitute another provider's profile.

## Validate and preview publication

From the repository root, with Node.js 22.13+ on the 22.x line or Node.js 24+:

```bash
npx --yes clawhub@0.25.1 package validate ./plugins/openclaw --out /path/to/local/reports --json
npx --yes clawhub@0.25.1 package publish ./plugins/openclaw --family bundle-plugin --bundle-format claude --name mobilerun --version 0.1.0 --dry-run --json
```

The pinned CLI is validation tooling, not a bundle dependency. Keep reports outside the installable directory. A successful dry-run resolves publication metadata without uploading; it does not prove authentication, runtime tool registration, security-scan acceptance, or marketplace approval. Do not run a real publish without publisher authorization. Source attribution must identify the actual released files: uncommitted files are not proven by the checkout's existing commit.

### Tooling compatibility

Use `bundle-plugin` with `claude` format. Explicit `--name` prevents the package directory name from becoming the listing name; explicit `--version` is required by this CLI even though the bundle manifest declares a version.

ClawHub 0.25.1's bundled Plugin Inspector 0.4.5 expects a native `package.json` or `openclaw.plugin.json` root and cannot inspect this bundle-only layout. Do not add a native manifest to silence that error; it changes format detection. Publication dry-run, bundle-aware validation, and live runtime checks are distinct gates. Before a real publish, verify that the resolved source commit and subpath identify the exact released files.

## Local installation and verification

With a compatible OpenClaw host installed:

```bash
openclaw plugins install ./plugins/openclaw
openclaw plugins inspect mobilerun
```

Review the source before accepting any install trust prompt. Confirm inspection reports `Format: bundle`, bundle format `claude`, and the Mobilerun MCP capability. Then verify the running Gateway and an actual read-only tool call. Cold inspection alone is not runtime proof.

## Authentication, costs, and data

The hosted MCP requires account authorization. This package contains no token, API key, client secret, or account credentials. Complete authentication using your host's supported connection flow; HTTP bundle detection is not proof that the installed OpenClaw version supports the required OAuth flow. If browser authorization is unavailable, stop and resolve host authentication support rather than disabling authentication or putting credentials into the bundle or chat.

After successful authorization, ask to list existing Mobilerun devices without creating resources or running tasks. An empty list is a valid successful response. Do not create a billed device or task merely to verify setup. Check your active workspace balance in the Mobilerun dashboard; this bundle cannot grant or transfer credits.

Requested tool arguments are sent to Mobilerun, and authorized tool responses may contain account/device metadata or other service data. The package has no local runtime or telemetry. See [privacy](https://cloud.mobilerun.ai/legal/privacy-policy), [terms](https://cloud.mobilerun.ai/legal/terms-of-service), and [support](https://docs.mobilerun.ai/support).

## Verification boundaries

Package preparation and static validation are separate from local installation, OAuth, tool calls, publication, and approval. No public listing or authenticated runtime behavior is claimed by this source package.

Official references: [bundle formats and mapped MCP capabilities](https://docs.openclaw.ai/plugins/bundles), [ClawHub validation and publication](https://docs.openclaw.ai/clawhub/cli).
