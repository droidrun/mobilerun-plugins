# Mobilerun provider packages

Mobilerun gives agents access to Android devices and automation through its existing MCP. This directory contains client packaging, not a fork of the MCP server.

- Hosted MCP profiles: Claude uses `https://cloud.mobilerun.ai/api/mcp/claude`; OpenAI uses `https://cloud.mobilerun.ai/api/mcp/openai`. Cursor/OpenClaw retain the existing base endpoint `https://cloud.mobilerun.ai/api/mcp` until their own profiles are available. Follow the [documented browser OAuth flow](https://docs.mobilerun.ai/mcp-server#oauth-authentication) through the host. Actual host login remains unverified; never put credentials in chat or a distributed bundle.
- Test Plugin uses a Node.js stdio bridge to `http://localhost:8080/mcp/openai` in a compatible desktop-local execution environment. It does not connect regular cloud-backed ChatGPT chats to localhost. Its local server requires an API key configured outside the package; live host authentication is unverified.
- The local bridge and credential setup helper are test-only. `python3 scripts/package_plugins.py` builds production provider archives without Test Plugin; `python3 scripts/package_test_plugin.py` builds the local test archive explicitly. Neither production packages nor their exporter depend on the local adapter.
- Source packages: [Claude chat](claude/README.md), [OpenAI / ChatGPT](openai/README.md), [Cursor](cursor/README.md), and [OpenClaw compatible bundle](openclaw/README.md). Local packaging is not live compatibility or publication approval.
- Other targets and publishing boundaries: [provider overview](../docs/providers.md).
- Server source: [droidrun/mobilerun-mcp](https://github.com/droidrun/mobilerun-mcp).

The server provides tools, resources, permissions, and task execution. Every provider package includes the same three practical skills: `onboarding` for connection and first-device setup, `mobile-tasks` for device/app control and bounded agent tasks, and `workflow-automation` for reusable actions, triggers, and hosted-assistant conversations. Tasks, devices, and recurring workflows can consume credits or minutes. OpenClaw includes the same skill files; OpenClaw skill loading is not tested here.

Run `python3 scripts/sync_skills.py` after changing canonical files in `shared/`; use `python3 scripts/sync_skills.py --check` to detect drift. Package exporters include all three skills.
