# Mobilerun provider packages

Mobilerun gives agents access to Android devices and automation through its existing MCP. This directory contains client packaging, not a fork of the MCP server.

- Hosted MCP profiles: Claude uses `https://cloud.mobilerun.ai/api/mcp/claude`; OpenAI and Test Plugin use `https://cloud.mobilerun.ai/api/mcp/openai`. Cursor/OpenClaw retain the existing base endpoint `https://cloud.mobilerun.ai/api/mcp` until their own profiles are available. Follow the [documented browser OAuth flow](https://docs.mobilerun.ai/mcp-server#oauth-authentication) through the host. Actual host login remains unverified; never put credentials in chat or a distributed bundle.
- Source packages: [Claude chat](claude/README.md), [OpenAI / ChatGPT](openai/README.md), [Cursor](cursor/README.md), and [OpenClaw compatible bundle](openclaw/README.md). Local packaging is not live compatibility or publication approval.
- Other targets and publishing boundaries: [provider overview](../docs/providers.md).
- Server source: [droidrun/mobilerun-mcp](https://github.com/droidrun/mobilerun-mcp).

The server owns tools, resources, operational prompts, permissions, task execution, and billed operations. The Claude onboarding skill only fills the connection/account gap before the server is available.

## Account and billing guidance

The [billing dashboard](https://cloud.mobilerun.ai/billing) is authoritative for the current workspace's plan, offers, eligibility, and available balance. Do not infer a credit entitlement from this repository. Packages cannot issue, transfer, or reset credits, and setup should not create resources or run billed tasks merely to test connectivity.
