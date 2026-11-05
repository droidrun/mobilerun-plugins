# Cursor local testing

Status: **PREPARED / NOT RUN**. Test the [Cursor package](../../plugins/cursor/README.md) at `plugins/cursor`. It includes a Cursor-native manifest, MCP configuration, logo, and Apache-2.0 license; it has no bundled onboarding skill. Static checks do not prove a live Cursor installation.

## Local package test

Authentication prerequisite: use only supported private client authentication at the configured public API URL. OAuth steps below are conditional on endpoint/client support; unavailable required flows are BLOCKED. Changing the repository package does not update a previously copied local installation automatically.

1. Record Cursor version and organization policy. Enterprise **Allow Local Plugin Imports** defaults off; obtain owner approval if needed.
2. Inspect `~/.cursor/plugins/local/mobilerun` before copying. Never overwrite an existing user package; resolve an occupied path with its owner. A marketplace-installed plugin of the same name overrides the local one—record/resolve that conflict without silently uninstalling anything.
3. Copy `plugins/cursor` contents into that folder, retaining `.cursor-plugin/plugin.json`, `mcp.json`, assets, README, and LICENSE. Use real files; external-target symlinks are skipped. Do not copy the repository, OpenAI package, or Claude package.
4. Restart Cursor or run **Developer: Reload Window**. Inspect **Customize** for Mobilerun, the MCP component, and errors. The root `.cursor-plugin/marketplace.json` is a separate repository catalog, not a file to mix into the local package.
5. Connect through Cursor's actual authorization UI and browser OAuth. Capture live tool inventory/errors without secrets.
6. Run five read-only checks: list devices, get fixture state, list installed apps, list tasks, get an existing task's status. Use exposed names/schemas and actual returned IDs. Match fixture results and verify no writes.
7. In a fresh/disconnected state verify the documented Cursor connection/recovery route. There is no bundled onboarding skill, so do not claim one loaded. Do not use ChatGPT-specific installation instructions as a Cursor setup step.
8. Reload again and verify discovery persists. Record required reconnection accurately. Restore only approved changes made for the test; never delete an existing package.

## MCP-only alternative

A direct custom-MCP connection through Cursor's current UI/config tests the hosted endpoint/OAuth only. Record **MCP-only**, not PASS for plugin import, skills, or packaging. Do not overwrite global servers or change unrelated settings.

## Evidence

Save version/policy, import path/package identity, Customize discovery, OAuth, five call traces, connection/recovery and reload results, and errors in [the private run record](run-template.md). Verify the final public source location separately before distribution.

Sources: [local-plugin testing](https://cursor.com/docs/plugins#test-plugins-locally), [supported formats](https://cursor.com/docs/plugins/building), checked November 5, 2026.
