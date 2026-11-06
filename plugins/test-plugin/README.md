# Test Plugin — public OpenAI MCP profile

Connects to **`https://cloud.mobilerun.ai/api/mcp/openai`** over Streamable HTTP, with browser OAuth handled by the host and Mobilerun's existing authorization service.

The portable MCP configuration uses the standard `type` and `url` fields. The host discovers OAuth from the protected endpoint; no fixed token or nonportable per-server authentication override is embedded.

**No Node.js, local MCP process, or `MOBILERUN_CLOUD_API_KEY` setup is required.** The plugin package may be installed locally, but MCP tools, devices and streams are remote. It does not provide offline or local-only execution.

## Install or update

1. Refresh/reinstall **Test Plugin** from the **Mobilerun local plugins** source in the ChatGPT desktop app. Restart the app after changing the package. The marketplace points to this plugin directory, not a ZIP.
2. Remove or disconnect the previous Test Plugin stdio connection if the client retains it. This package is now version **0.2.0**; the old version used a local API-key server.
3. Complete Mobilerun browser sign-in and consent when the client requests it.
4. Open a **new chat**, select Test Plugin with `@`, and try `list_devices` to verify authorized access. Do not provision devices or start paid tasks merely to test the connection.

For ZIP installation/import, use the client's supported package workflow. The archive has `plugin.json` and `mcp.json` at its root, with this README and LICENSE. No credentials, local server, dependencies or build inputs are included.

## Profile and OAuth verification

The connector URL explicitly selects the public **OpenAI** profile rather than the unqualified MCP endpoint. The OAuth protected-resource metadata for this exact URL is reachable and identifies Mobilerun's authorization server, which advertises authorization-code authentication with PKCE S256.

Unauthenticated discovery confirms that OAuth metadata is available; it does **not** prove a completed sign-in, the deployed profile's authenticated tool list, or working device streaming. Those need verification through your authorized connection. Profile selection also does not grant device/account permissions.

The host stores OAuth credentials. Do not paste tokens into this package, chat or source control. If no actions appear after installation, inspect the connection's login/startup status and ensure this new package—not the cached stdio version—is selected in a fresh chat.

## Maintainer packaging

From the repository root:

```bash
python3 scripts/package_test_plugin.py
python3 -m unittest discover -s tests -v
```

The exporter writes `zip/test-plugin.zip` with only four allowlisted files. The previous local stdio/viewer experiment is preserved separately in the `mcp-device-streaming` branch's worktree, not in this package. No build or deployment is needed to use the public connector.

## References

- [Mobilerun MCP OAuth](https://docs.mobilerun.ai/mcp-server#oauth-authentication)
- [Profile-specific protected-resource metadata](https://cloud.mobilerun.ai/.well-known/oauth-protected-resource/api/mcp/openai)
- [OpenAI packaging and local marketplace testing](https://developers.openai.com/plugins/build/plugins)
- [Agent Plugins specification](https://agent-plugins.org/specification)

Local marketplace installation and public-directory publication are separate. This package has not been submitted, approved, or verified in a live authenticated ChatGPT session. Original package files are MIT licensed.
