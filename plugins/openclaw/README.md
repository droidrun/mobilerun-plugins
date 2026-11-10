# Mobilerun for OpenClaw

A compatible MCP bundle for OpenClaw. This is a **Claude-format bundle consumed by OpenClaw**, not a native OpenClaw plugin. Exactly one format marker, `.claude-plugin/plugin.json`, identifies the bundle. It includes `onboarding` for connection and first-device setup, and `mobile-tasks` for device/app control and bounded tasks. No hooks, local runtime, or dependencies are included.

The root `.mcp.json` declares one hosted server at `https://cloud.mobilerun.ai/api/mcp/openclaw`, explicitly using `streamable-http` and `auth: "oauth"`. This is the intended OpenClaw profile URL; deployment availability is **unverified**, and historical verification returned 404 for this route and its OAuth metadata. The inspected MCP server source contains no OpenClaw profile implementation. Do not fall back to the broader base MCP endpoint: that endpoint does not establish OpenClaw-specific restrictions. The MCP server controls which tools are available; no dedicated profile restrictions or deployment behavior are claimed here.

## Install and sign in

Install the bundle in OpenClaw, then open the Mobilerun plugin’s page. Select **Sign in**, or **Accounts → Sign in**, to complete browser authorization. This flow requires an operator with administrator access. Keep passwords, tokens, and sign-in codes in the browser flow. For a server declared by this plugin, do not run `openclaw mcp login`: that CLI flow is for saved `mcp.servers` entries. If the plugin server is not shown, stop and contact support@mobilerun.ai; do not add another connector automatically.

### Standalone connection alternative

Only when intentionally not using the plugin, configure the server once in your OpenClaw `mcp.servers` settings, then use the standalone MCP sign-in flow. Do not combine this with the plugin connector:

```json
{
  "mcp": {
    "servers": {
      "mobilerun": {
        "url": "https://cloud.mobilerun.ai/api/mcp/openclaw",
        "transport": "streamable-http",
        "auth": "oauth"
      }
    }
  }
}
```

This example selects the intended route; it does not verify that the route or OAuth metadata is deployed.

## Validate and preview publication

From the repository root, with Node.js 22.13+ on the 22.x line or Node.js 24+:

```bash
npx --yes clawhub@0.25.1 package validate ./plugins/openclaw --out /path/to/local/reports --json
npx --yes clawhub@0.25.1 package publish ./plugins/openclaw --family bundle-plugin --bundle-format claude --name mobilerun --version 0.1.0 --display-name Mobilerun --dry-run --json
```

The pinned CLI is validation tooling, not a bundle dependency. Keep reports outside the installable directory. A successful dry-run resolves publication metadata without uploading; it does not prove authentication, runtime tool registration, security-scan acceptance, or marketplace approval. Do not run a real publish without publisher authorization. Source attribution must identify the actual released files: uncommitted files are not proven by the checkout's existing commit.

### Tooling compatibility

Use `bundle-plugin` with `claude` format. Explicit `--name` prevents the package directory name from becoming the listing name; explicit `--version` is required by this CLI even though the bundle manifest declares a version.

ClawHub 0.25.1's bundled Plugin Inspector 0.4.5 expects a native `package.json` or `openclaw.plugin.json` root and cannot inspect this bundle-only layout. Do not add a native manifest to silence that error; it changes format detection. Publication dry-run, bundle-aware validation, and live runtime checks are distinct gates. Before a real publish, verify that the resolved source commit and subpath identify the exact released files.

ClawHub bundle-plugin listings use the bundled `assets/icon.png` (PNG, at most 512 KiB); manifest icon paths/URLs are ignored. This package includes the existing 512×512 Mobilerun icon. No custom manifest icon field is needed.

## Local installation and verification

With a compatible OpenClaw host installed:

```bash
openclaw plugins install ./plugins/openclaw
openclaw plugins inspect mobilerun
```

Review the source before accepting any install trust prompt. Confirm inspection reports `Format: bundle`, bundle format `claude`, and the Mobilerun MCP capability. Then use the Mobilerun plugin’s page to sign in as above. Verify the running Gateway and an actual read-only tool call only after deployment is confirmed. Cold inspection and endpoint selection tests are not runtime proof.

## Authentication, costs, and data

The hosted MCP requires account authorization. This package contains no token, API key, client secret, or account credentials. OpenClaw 2026.11.2 supports `auth: "oauth"` for bundled MCP HTTP servers and exposes browser sign-in on the plugin’s page. This is host-side support, not successful Mobilerun authorization or route availability, and does not establish compatibility with every agent adapter. If sign-in is unavailable or the route returns an error, stop and contact support rather than disabling authentication or putting credentials into the bundle or chat.

After successful authorization, ask to list existing Mobilerun devices without creating resources or running tasks. An empty list is a valid successful response. Do not create a billed device or task merely to verify setup. Check your active workspace balance in the Mobilerun dashboard; this bundle cannot grant or transfer credits.

Requested tool arguments are sent to Mobilerun, and authorized tool responses may contain account/device metadata or other service data. The package has no local runtime or telemetry. See [privacy](https://cloud.mobilerun.ai/legal/privacy-policy), [terms](https://cloud.mobilerun.ai/legal/terms-of-service), and [support](https://docs.mobilerun.ai/support).

## Verification boundaries

Package preparation and static validation are separate from local installation, OAuth, tool calls, publication, and approval. No public listing or authenticated runtime behavior is claimed by this source package.

Official references: [bundle formats and mapped MCP capabilities](https://docs.openclaw.ai/plugins/bundles), [ClawHub validation and publication](https://docs.openclaw.ai/clawhub/cli).
