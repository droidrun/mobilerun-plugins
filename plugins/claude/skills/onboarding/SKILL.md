---
name: onboarding
description: Use when a user is setting up Mobilerun for the first time, cannot see its connector tools, needs to authorize or reconnect Mobilerun, or asks about signup credits and account eligibility.
---

# Mobilerun onboarding

Help the user establish access, then return to their goal. The hosted MCP owns device operations, task workflows, tool descriptions, resources, and operational prompts. This skill only covers connection and account onboarding; skip it for ordinary work on an already connected account.

## Connection

1. Inspect available connector tools and any actual error before recommending a fix. Do not invent an authentication-status tool.
2. When Mobilerun is missing or authorization is required, direct the user to **Customize > Plugins > Mobilerun > Connectors** in Claude. The endpoint is `https://api.mobilerun.ai/v1/mcp`. Follow the [public authentication instructions](https://docs.mobilerun.ai/mcp-server#api-key-authentication) and the host's supported private credential configuration. Complete browser OAuth only if supported and advertised; otherwise report the host authentication limitation. Never ask for a key in chat or embed one in the bundle. For a new account, sign up at [Mobilerun Cloud](https://cloud.mobilerun.ai) in the browser. On Team/Enterprise, an organization Owner may need to add the connector before members connect their own accounts.
3. The user completes sign-in, email verification, and consent in the browser. Installing a plugin does not complete authorization. Never ask for passwords, API keys, tokens, or verification codes in chat, and never claim to launch or finish OAuth unless the host actually did so.
4. After connection, use an exposed read-only tool such as `list_devices` to check access. Use the actual tool name supplied by the host; profiles may omit it. If no suitable tool is exposed, report that verification is unavailable rather than manufacturing a call. A successful empty list means connected with no visible devices, not failed login.

## Match the remedy to the evidence

| Observation | Next step |
| --- | --- |
| No tools visible | Check plugin connector installation, organization availability, and connection state. Missing tools alone do not prove expired authorization. |
| Explicit unauthenticated/expired authorization | Reconnect through Claude's connector interface and complete browser sign-in. |
| Permission denied | Explain the missing access; ask the user to check the intended account/workspace and connection permissions. Do not bypass policy or switch accounts automatically. |
| Insufficient credits or payment required | Check the current workspace's billing information. Reconnecting does not reset a trial or replenish credits. Follow the returned error: device minutes and task credits can be different balances. |
| Network/service failure | Report the failure; retry a read only when reasonable. Do not treat it as a signup problem or repeatedly retry writes. |

## Included credits

Send the user to [Mobilerun Cloud billing](https://cloud.mobilerun.ai/billing) to check the active workspace, current plan, offer, remaining credits, and any setup or verification steps actually shown. The live dashboard is authoritative; do not claim a balance from configuration or grant credits yourself.

Follow only offers and eligibility steps actually shown in the dashboard. Do not promise a fixed credit amount, invent a claim button or award API, recommend re-signup to obtain another offer, or attempt a duplicate grant. Personal and shared workspaces may have different balances. Do not transfer credits, change billing context, or subscribe on the user's behalf during onboarding.

## Finish

State what is verified and what still needs user action, then continue with the original request using the MCP's current guidance. If the host exposes MCP prompts, its `get-started` prompt is available for first-device guidance; do not assume Claude chat exposes prompt invocation. Never copy that workflow here, provision a device, purchase anything, or run a billed task merely to prove setup.

Example: a successful `list_devices` returning `[]` warrants “Mobilerun is connected; this account has no visible devices,” followed by the server's guidance for the user's goal—not another login loop.
