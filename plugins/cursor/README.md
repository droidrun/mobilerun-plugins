# Mobilerun for Cursor

Connect Cursor to the [Mobilerun](https://mobilerun.ai) hosted MCP for Android devices, tasks, apps, and automation. Actual tools depend on the connection's server profile and permissions. This package is not a verified Marketplace listing.

## Install locally

Copy this entire directory, including `.cursor-plugin/`, `assets/`, and `LICENSE`, to `~/.cursor/plugins/local/mobilerun`. Do not link to a repository outside the local-plugin directory: Cursor skips those symlinks. Do not overwrite an existing installation without checking it first.

Restart Cursor or run **Developer: Reload Window**, then open **Customize** and confirm the Mobilerun MCP component is present. Local-plugin imports must be allowed by organization policy; an installed marketplace plugin of the same name takes precedence.

The server URL is `https://api.mobilerun.ai/v1/mcp`; there are no bundled API keys, tokens, or client secrets. Follow [public authentication instructions](https://docs.mobilerun.ai/mcp-server#api-key-authentication) and configure credentials privately through Cursor's supported connection settings; use OAuth only if offered/supported by the endpoint. Ask “List my Mobilerun devices” to check access without creating resources or starting billed tasks. An empty list is valid. File installation is not proof of authentication or tool access.

## Public submission

Use [Cursor Marketplace publishing](https://cursor.com/marketplace/publish) only after validating this package and completing local client tests. Cursor requires public open-source Git source. Verify that the submitted repository and package path are publicly accessible. No push or submission is performed by copying this package locally.

## Provenance and license

Based on the Cursor plugin from [droidrun/mobilerun-mcp](https://github.com/droidrun/mobilerun-mcp). **MCP URL and README modified November 5, 2026** to use the public API endpoint and document installation and verification boundaries. The upstream Apache-2.0 license and attribution are retained; this package is not relicensed under the surrounding repository's MIT license.

Support: <https://github.com/droidrun/mobilerun-mcp/issues>

Official references: [local installation](https://cursor.com/docs/plugins#test-plugins-locally), [manifest and submission](https://cursor.com/docs/reference/plugins).
