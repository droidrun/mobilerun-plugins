# Mobilerun for Cursor

Connect Cursor to the [Mobilerun](https://mobilerun.ai) hosted MCP for Android devices, tasks, apps, and automation. Actual tools depend on the connection's server profile and permissions. This package is not a verified Marketplace listing.

The package includes two practical skills in the standard `skills/<name>/SKILL.md` layout: `onboarding` for connection and first-device setup, and `mobile-tasks` for device/app control and bounded tasks. Tasks and devices can consume credits or minutes.

## Install locally

Copy this entire directory, including `.cursor-plugin/`, `assets/`, and `LICENSE`, to `~/.cursor/plugins/local/mobilerun`. Do not link to a repository outside the local-plugin directory: Cursor skips those symlinks. Do not overwrite an existing installation without checking it first.

Restart Cursor or run **Developer: Reload Window**, then open **Customize** and confirm the Mobilerun MCP component is present. Local-plugin imports must be allowed by organization policy; an installed marketplace plugin of the same name takes precedence.

The server URL is `https://cloud.mobilerun.ai/api/mcp`; there are no bundled API keys, tokens, or client secrets. Follow [Mobilerun's browser OAuth instructions](https://docs.mobilerun.ai/mcp-server#oauth-authentication) through Cursor's connection interface. Actual Cursor login remains unverified; if the required flow is unavailable, report the limitation. Ask “List my Mobilerun devices” to check access without creating resources or starting billed tasks. An empty list is valid. File installation is not proof of authentication or tool access.

The dedicated `/api/mcp/cursor` profile is deferred: that public route and its OAuth metadata returned 404 during verification. This package deliberately retains the existing base endpoint until the Cursor profile is added; it does not substitute another provider's profile.

## Public submission

Use [Cursor Marketplace publishing](https://cursor.com/marketplace/publish) only after validating this package and completing local client tests. Cursor requires public open-source Git source. Verify that the submitted repository and package path are publicly accessible. No push or submission is performed by copying this package locally.

## Provenance and license

Based on the Cursor plugin from [droidrun/mobilerun-mcp](https://github.com/droidrun/mobilerun-mcp). The MCP URL and README were updated November 5, 2026 to use the public API endpoint and document installation and verification boundaries. Shared onboarding and mobile-tasks skills were added November 6, 2026. The upstream Apache-2.0 license and attribution are retained; this package is not relicensed under the surrounding repository's MIT license.

Support: <https://github.com/droidrun/mobilerun-mcp/issues>

Official references: [local installation](https://cursor.com/docs/plugins#test-plugins-locally), [manifest and submission](https://cursor.com/docs/reference/plugins).
