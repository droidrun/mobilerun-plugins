# Mobilerun for OpenAI

A portable plugin for ChatGPT and Codex, containing one hosted Mobilerun MCP connection and an onboarding skill. The MCP owns tools and operational prompts; the bundle only adds connection/account guidance and OpenAI listing metadata. This is a local source package, not a published or approved listing.

## Package

- `plugin.json`: portable identity and OpenAI presentation, onboarding, and draft review cases.
- `mcp.json`: one Streamable HTTP server at `https://api.mobilerun.ai/v1/mcp`.
- `skills/onboarding/SKILL.md`: connection recovery and account/billing guidance.
- `assets/logo.svg`: existing 256×256 Mobilerun logo from `droidrun/mobilerun-mcp/assets/logo.svg`.
- `LICENSE`: MIT notice included for independent distribution.

The configuration contains no bearer header or bundled credential. Follow [Mobilerun's public authentication instructions](https://docs.mobilerun.ai/mcp-server#api-key-authentication). Configure credentials only through the host's private supported mechanism. Browser OAuth and dynamic registration at this URL have not been verified. Use OAuth only if advertised and supported for this endpoint. If the marketplace requires OAuth and it is unavailable here, treat that as a review blocker rather than disabling authentication or embedding a key.

## Test locally in ChatGPT desktop / Codex

The repo already includes `.agents/plugins/marketplace.json` pointing to `./plugins/openai`. Paths resolve from the repository root, not from `.agents/plugins/`.

1. Open this repository in a supported ChatGPT desktop/Codex environment and restart/refresh the desktop app's plugin sources.
2. In the Plugins Directory, select **Mobilerun local plugins** and install **Mobilerun**. Local-marketplace support varies by client and organization policy.
3. Configure authentication through the host's supported private mechanism. Browser OAuth at this URL is unverified; if the host requires an unavailable flow, stop and record BLOCKED. Run plugin setup to invoke the packaged onboarding skill.
4. In a new chat, ask “List my Mobilerun devices.” A returned empty list is a valid connection; no device purchase is required.

For a separate marketplace source, the documented CLI route is `codex plugin marketplace add <repository-root>`. A marketplace makes a plugin discoverable; it does not bypass host installation, trust, account, or authorization requirements.

### Test the hosted MCP in ChatGPT web

Go to [Plugins](https://chatgpt.com/plugins), select the plus button > **Add custom MCP server**, enter the hosted endpoint, and use the supported authentication flow before **Create as a plugin**. OAuth at this URL is unverified; if required but unavailable, record BLOCKED rather than choosing no authentication or embedding a key. This tests the hosted MCP, **not the full local package or onboarding skill**. Access depends on account/policy. Do not create or guess a `plugin_asdk_app` ID.

## Credits, costs, and data

Check the active workspace's current plan, offers, eligibility, and balance in [Mobilerun billing](https://cloud.mobilerun.ai/billing). The dashboard is authoritative; the plugin does not promise a fixed credit amount or extra signup offer. Personal and shared workspaces may have different balances.

Tasks and devices may consume credits or minutes. No billed task or resource creation is needed to test connectivity. This package cannot issue, move, or reset credits.

ChatGPT/Codex sends requested tool arguments to Mobilerun; authorized responses may contain device metadata, screenshots, UI state, and task results. OAuth is handled by the host and service in the browser. The package has no runtime, local storage, or telemetry. Service-side processing and retention still follow [Mobilerun privacy policy](https://cloud.mobilerun.ai/legal/privacy-policy), [terms](https://cloud.mobilerun.ai/legal/terms-of-service), and the host's policies.

## ZIP and public submission

Follow the repository's [archive build and validation instructions](../../README.md#check-locally) to create and check `mobilerun-openai.zip`. The archive must contain `plugin.json` and `mcp.json` at its root, without a wrapping directory.

Upload **only this package** through [OpenAI Plugins](https://platform.openai.com/plugins), using **With MCP**. Include MCP in the initial upload; adding MCP to a previously skills-only plugin is not supported. The portal accepts only one connected MCP server per plugin. Do not include repo marketplace files, app references, lifecycle hooks, credentials, or the Claude package in this ZIP.

Before submitting for review, the publisher must separately:

- Confirm organization/project ownership, submission permission, verified developer identity, and the portal category. The bundled publisher text is not proof of identity verification.
- Complete the exact domain challenge shown by the portal without replacing another plugin's token.
- Verify saved OAuth settings and complete the connection and tool scan. The bundle does not register or authorize an account itself.
- Supply a dedicated working reviewer account privately through **Review details**, with sample data, a ready fixture device, and existing tasks. Never put reviewer credentials in the ZIP. Ensure the account does not require reviewer-side MFA/code approval or private-network access.
- Run all **five positive and three negative cases** in `plugin.json` against that account, adapting fixture references to actual accessible data. Cases are proposed, not claimed executed, and no spend is automatically authorized by including them.
- Record a reviewer-accessible walkthrough and supply its real URL. `review.demo_recording_url` is deliberately omitted rather than filled with a fake link.
- Resolve required metadata, skill, connection, security, and tool-scan findings; submit only after testing. No country targeting or legal attestations are invented here.

## Verification boundaries

Use the [marketplace runbook](../../docs/marketplace-testing/openai.md) for all eight cases and the [video storyboard](../../docs/marketplace-testing/openai-video.md) for initial MCP review. The script is prepared; the actual recording and authenticated results are pending. The reviewed profile omits screenshot capture; the positive cases use device/app/task metadata instead.

Repository tests check package structure, portable metadata, endpoint, onboarding path, square SVG asset, license, marketplace resolution, and linked documentation. They do not prove OAuth, deployment entitlements, skill behavior in ChatGPT, or portal acceptance. Manual scenarios should cover disconnected tools, successful empty devices, permission denial, 402/minute exhaustion, network failure, already-claimed bonus, personal/shared context, and already-connected tasks. No public submission, domain change, account creation, or purchase is performed by this package.

Official references: [package format and local marketplaces](https://developers.openai.com/plugins/build/plugins), [submission and review fields](https://developers.openai.com/plugins/deploy/submission), [plugin guidelines](https://developers.openai.com/plugins/plugin-guidelines).
