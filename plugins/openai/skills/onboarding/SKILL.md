---
name: onboarding
description: Use when a user installs or sets up Mobilerun in ChatGPT or Codex, cannot see its tools, needs to authorize or reconnect the MCP, or asks about included credits and signup eligibility.
---

# Connect Mobilerun

Establish access and resolve account setup, then return to the user's original goal. Tools, resources, operational prompts, and task workflows belong to the hosted MCP—not this skill. An already connected user asking for device work should use the MCP's current guidance, without repeating signup.

## Setup

1. Check exposed Mobilerun tools and actual connection errors. Installing a package or enabling a plugin does not prove OAuth is complete. Missing tools alone do not prove expired authorization.
2. Have the user connect Mobilerun through the host's plugin/MCP connection interface using its supported private authentication mechanism. Complete browser OAuth only if the endpoint and host support it. For first-time accounts, link [Mobilerun Cloud](https://cloud.mobilerun.ai) for browser signup and any email-verification steps shown. Never ask for passwords, tokens, API keys, or verification codes in chat; do not claim to launch or finish authorization unless the host actually did so.
3. The bundled endpoint is `https://api.mobilerun.ai/v1/mcp`. Follow the [public authentication instructions](https://docs.mobilerun.ai/mcp-server#api-key-authentication) and use the host's supported private authentication mechanism; never paste a key into chat or distribute it in a package. For direct ChatGPT testing, the documented route is [Plugins](https://chatgpt.com/plugins) > plus button > **Add custom MCP server**, then **Create as a plugin**, where available. Select OAuth only if this endpoint advertises/supports it; otherwise report the client authentication limitation rather than pretending authorization succeeded. This tests the server connection, not the bundled skill. Account/admin policy may restrict custom connections.
4. For a full local bundle, the ChatGPT desktop app supports a repository/personal marketplace. A local folder is not automatically installed in ChatGPT web. Ask which surface the user uses only if that changes the needed setup step; do not send them to Claude-specific menus. Public-directory install and workspace availability depend on the actual listing and administrator policy.
5. After connection, call an available read-only tool such as `list_devices`, using the actual exposed tool name. Profiles can omit tools. If no suitable tool is exposed, say that access cannot yet be verified instead of inventing a status call. A successful empty list means connected with no visible devices; it is not an authentication failure.

## Recovery by evidence

| Evidence | Remedy |
| --- | --- |
| Tools missing | Check plugin installation, connection state, and workspace policy; do not assume login expired. |
| Explicit unauthenticated or expired authorization | Ask the user to reconnect in the host and complete browser OAuth. |
| Permission denied | Check intended account/workspace and connection permissions; do not bypass policy or switch identity automatically. |
| Insufficient credits / payment required | Check active workspace billing and the balance named by the error. Device minutes and agent credits are different allowances. Reconnecting does not reset a trial. |
| Network/service failure | Report the failure; retry a read only when appropriate. Never re-sign up as a remedy or blindly retry a write. |

## Included credits

Use [Mobilerun billing](https://cloud.mobilerun.ai/billing) as the authority for the current workspace's actual plan, offer, eligibility, and available balance. Do not promise a fixed credit amount or infer eligibility from the plugin.

Follow only offers and setup steps actually shown in the dashboard. Do not invent a claim button or award API, suggest re-signup to obtain another offer, or attempt a duplicate grant. Personal and shared workspaces may have different balances. Never grant or transfer credits, subscribe, or change billing context automatically.

## Handoff

Report verified access or the remaining user action, then continue the original request with server-provided guidance. Use `get-started` only if this host exposes MCP prompt invocation; do not manufacture a prompt-as-tool call or copy the server's workflow. Never provision a device, purchase anything, or run a billed task merely to test setup.

Example: `list_devices` returns `[]` successfully → “Mobilerun is connected; no devices are visible in this account.” Continue with the user's goal, not another OAuth loop.
