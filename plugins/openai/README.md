# Mobilerun for OpenAI

A portable plugin for ChatGPT and Codex with one hosted Mobilerun MCP connection and two practical skills for onboarding and mobile tasks.

## Package

- `plugin.json`: portable identity and OpenAI presentation, onboarding, and draft review cases.
- `mcp.json`: one Streamable HTTP server at `https://cloud.mobilerun.ai/api/mcp/openai`.
- `skills/onboarding/SKILL.md`: host-specific connection recovery plus synchronized Android-first guidance.
- `skills/mobile-tasks/SKILL.md`: device and app work, direct control, bounded tasks, results, and recovery.
- `assets/logo.svg`: existing 256×256 Mobilerun logo from `droidrun/mobilerun-mcp/assets/logo.svg`.
- `LICENSE`: MIT notice included for independent distribution.

The configuration contains no bearer header or bundled credential. The host handles browser OAuth. ChatGPT plugin loading is not verified by repository tests.

## Test locally in ChatGPT desktop / Codex

The repository includes a local marketplace entry pointing to this package. This repository-only setup file is not included in a standalone package archive.

1. Open this repository in a supported ChatGPT desktop/Codex environment and restart/refresh the desktop app's plugin sources.
2. In the Plugins Directory, select **Mobilerun local plugins** and install **Mobilerun**. Local-marketplace support varies by client and organization policy.
3. Follow the host's browser OAuth flow and use the packaged onboarding skill for setup and connection recovery.
4. In a new chat, ask “List my Mobilerun devices.” A returned empty list is a valid connection; no device purchase is required.

For a separate repository marketplace source, the documented CLI route is `codex plugin marketplace add <repository-root>`.

### Test the hosted MCP in ChatGPT web

Go to [Plugins](https://chatgpt.com/plugins), select the plus button > **Add custom MCP server**, enter the hosted endpoint, and follow browser OAuth before **Create as a plugin**. This tests the hosted MCP connection.

## Credits, costs, and data

For information about execution credits, see [Mobilerun's credits documentation](https://docs.mobilerun.ai/credits). Check the current balance in your active workspace's account settings. Tasks and devices may consume credits or minutes; connectivity can be checked by listing devices without creating a task or resource.

ChatGPT/Codex sends requested tool arguments to Mobilerun; authorized responses may contain device metadata, screenshots, UI state, and task results. OAuth is handled by the host and service in the browser. The package has no runtime, local storage, or telemetry. Service-side processing and retention still follow [Mobilerun privacy policy](https://cloud.mobilerun.ai/legal/privacy-policy), [terms](https://cloud.mobilerun.ai/legal/terms-of-service), and the host's policies.

## ZIP and public submission

From the repository root, create the archive with `cd plugins/openai && zip -r ../../mobilerun-openai.zip .`. Verify it contains `plugin.json` and `mcp.json` at its root, without a wrapping directory (for example, `unzip -l ../../mobilerun-openai.zip`). This README and command are source-package guidance; the submission ZIP should contain the plugin files, not this README or repository-level marketplace files.

Upload **only this package** through [OpenAI Plugins](https://platform.openai.com/plugins), using **With MCP**. Include MCP in the initial upload; adding MCP to a previously skills-only plugin is not supported. The portal accepts only one connected MCP server per plugin. Do not include repo marketplace files, app references, lifecycle hooks, credentials, or the Claude package in this ZIP.

Developer/domain verification, authentication checks, and marketplace review are separate from package installation. Follow the provider's current submission requirements; this source package does not establish approval.

The manifest's `review.demo_recording_url` points to the [Mobilerun demo recording](https://www.loom.com/share/646c25f3773841f89164a0a12065e79b). Before submitting, verify that reviewers can watch it without signing in or requesting access and that it demonstrates the submitted review cases. Video accessibility and coverage have not been verified by the repository checks. Review cases are draft materials and have not been run against a reviewer account. OpenAI's current submission guide requires five positive and three negative cases and an accessible walkthrough video for MCP review.

## Verification boundaries

Repository tests check package structure, portable metadata, endpoint, both skills, square SVG asset, license, marketplace resolution, and linked documentation. They do not exercise the host's plugin-loading interface.

Official references: [package format and local marketplaces](https://developers.openai.com/plugins/build/plugins), [submission and review fields](https://developers.openai.com/plugins/deploy/submission), [plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines). OpenAI's submission metadata explicitly supports `review.demo_recording_url`; its published guide also specifies square icons at least 48×48 pixels and all four HTTPS listing URLs for MCP review.
