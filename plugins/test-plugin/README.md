# Test Plugin — local MCP connection

**Local testing only.** The bridge and credential setup helper in this directory are excluded from all production provider packages. Test Plugin includes the same three practical skills as the hosted packages: `onboarding` for connection and first-device setup, `mobile-tasks` for device/app control and bounded tasks, and `workflow-automation` for reusable actions and triggers. Build this ZIP explicitly with `python3 scripts/package_test_plugin.py`; `python3 scripts/package_plugins.py` builds only the four hosted provider packages and does not require Test Plugin.

Test Plugin connects through a local stdio bridge to **`http://localhost:8080/mcp/openai`**. Local setup is supported on POSIX systems, including macOS and Linux, and requires Node.js 20.3 or later (`AbortSignal.any`); Node.js 22 is recommended. It requires a running local Mobilerun MCP server on port 8080. The bridge communicates with a compatible desktop-local Work or Codex process over stdio and with the local server over Streamable HTTP. This does not connect regular cloud ChatGPT chats; no tunnel is provisioned or implied, and no cloud-host configuration fields are required. The host does not need to inject an HTTP API key into the plugin configuration.

The local server requires a Mobilerun API key, supplied to the bridge through `MOBILERUN_CLOUD_API_KEY` or `~/.config/mobilerun/local-mcp.json`. Store the key securely outside the plugin and ZIP; never paste it into chat or source control. Consult the included local authentication setup helper for secure setup. A local authentication error requires checking the bridge credentials and server, not browser OAuth. Local server authentication is not bypassed.

The bridge is a narrow, stateless JSON-RPC relay: it accepts newline-delimited JSON requests over stdio, forwards each request to the configured loopback HTTP endpoint, and emits JSON responses. It does not implement sessions, SSE, or tunnels. Upstream requests have a 30-second timeout. If an operation times out, its completion may be ambiguous; do not blindly retry mutations. Account, device, and WebRTC streaming services remain remote. This is not an offline phone or a promise of local device execution. Device provisioning and tasks may incur charges; check the active workspace billing dashboard.

## Install or update

1. Start the local MCP server. From this repository root, run `node plugins/test-plugin/scripts/setup-local-auth.mjs` and enter the key at its hidden local terminal prompt. The helper saves it outside the package in `~/.config/mobilerun/local-mcp.json` with private permissions. Do not put the key in the command line or chat.
2. Disconnect the old cloud-backed Test Plugin connection. Refresh or reinstall **Test Plugin** version **0.3.0** from the local plugins source or the rebuilt ZIP, then restart the host. Do not reuse a saved cloud URL override. The marketplace points to this directory, not the ZIP.
3. Open a new chat, select Test Plugin, and use `list_devices` to verify access. Do not provision devices or run paid tasks merely to test the connection.

Host support for executing the bridge and authenticated access must be verified in the actual host; installing the package alone does not establish a working connection. If the host cannot run this stdio bridge, another compatible local adapter is needed.

## Maintainer packaging

From the repository root:

```bash
python3 scripts/package_test_plugin.py
python3 -m unittest discover -s tests -v
```

The exporter writes `zip/test-plugin.zip` with allowlisted plugin files and no credentials or local server. Local marketplace installation and public-directory publication are separate. This package has not been submitted, approved, or verified in a live authenticated ChatGPT session. Original package files are MIT licensed.
