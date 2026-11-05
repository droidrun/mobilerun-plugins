# Mobilerun for Claude

Connect Claude chat to Mobilerun's hosted MCP to work with Android devices and agent tasks. This bundle adds account-onboarding guidance and a remote connector reference. Device workflows, tools, permissions, and operational prompts come from the MCP, not a second implementation in this plugin.

## Install in Claude chat

This is a source bundle, not a published directory listing. Follow the repository's [archive build and validation instructions](../../README.md#check-locally) to create `mobilerun-claude.zip` containing only this package.

The archive must have `.claude-plugin/plugin.json` at its root, or inside a single top-level folder. Do not zip the whole repository. In Claude, choose **Customize > Plugins > Add > Upload plugin**, select the archive, and open the Mobilerun plugin's **Connectors** tab. Add/connect Mobilerun and follow the browser OAuth flow. Actual Claude login remains unverified; if the required flow is unavailable, record BLOCKED. Team/Enterprise users may first need an Owner to add the connector.

Endpoint: `https://cloud.mobilerun.ai/api/mcp`. Follow [Mobilerun's documented OAuth instructions](https://docs.mobilerun.ai/mcp-server#oauth-authentication). No credentials belong in the package or conversation. Installing the plugin alone does not authorize access. A separate custom connector tests the MCP, not the bundled skill; inability to authenticate through that client's supported flow remains a blocker.

## Use it

- “Help me connect Mobilerun.”
- “What credits are included with my account?”
- “List my Mobilerun devices.”
- Once connected: “List the apps installed on my test device.”

The onboarding skill handles setup and recovery, then returns control to MCP guidance. A successful empty device list is a valid connection. Authorization, workspace access, network failures, and billing errors need different remedies.

## Credits and costs

Check your current workspace, plan, offers, eligibility, and remaining balance at [Mobilerun billing](https://cloud.mobilerun.ai/billing). Use only offers actually shown in the dashboard; this plugin does not promise a fixed credit amount or an additional signup offer. Personal and shared workspaces may have different balances. This plugin cannot grant, transfer, or reset credits.

Tasks and devices may be billable. Onboarding does not buy resources or run a billed task as a connectivity test. Device-minute allowances and task credits are different balances; use the actual error and dashboard to choose a remedy.

## Data and authorization

Claude sends the tool arguments needed for your requested operations to Mobilerun through the hosted MCP. Responses can include device metadata, screenshots, UI state, task output, and other account data allowed by your connection. OAuth authorization is completed in the browser and managed by the host/service. The plugin has no runtime, local data store, telemetry, or token-handling code. Mobilerun and Claude still process data under their own service policies; no plugin-local storage does not mean no service-side retention.

## Verification

From the repository root:

```bash
python3 -m unittest discover -s tests -v
claude plugin validate plugins/claude
```

The first command checks package structure, JSON, metadata, and license inclusion. It does not prove agent behavior or live OAuth. The second requires an installed Claude CLI. For local Claude Code loading, use `claude --plugin-dir ./plugins/claude`; this is not a substitute for chat testing.

Live Claude chat installation, OAuth, billing entitlements, and Anthropic portal validation require separate verification; local checks do not establish directory approval.

## Publishing

Submit `plugins/claude` as the plugin folder, not the repository root. The remote MCP also needs its own connector submission. Use the same endpoint and owning organization to pair the listings. No submission or publication is performed by the local tests.

References: [Claude bundle format and upload testing](https://claude.com/docs/plugins/build.md), [directory publishing routes](https://claude.com/docs/directory/publish.md), [Mobilerun documentation](https://docs.mobilerun.ai).
