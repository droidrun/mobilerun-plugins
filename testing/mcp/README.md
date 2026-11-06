# Standard MCP test setup

Use this tracked setup for remote plugin testing instead of copying scripts from private reports.

```text
Plugin host → temporary public HTTPS tunnel → loopback credential bridge → authenticated MCP
```

Production provider packages and the optional local stdio Test Plugin are not modified. No real credentials or temporary hostname belong in source control.

## Requirements

- POSIX/macOS/Linux, Python 3.10+, and Node.js 20.3+; use a maintained Node release. Credential ownership/permission checks and process signal handling are not validated on Windows.
- `cloudflared` installed for an actual public tunnel; not needed for unit tests or building ZIPs.
- An already running local MCP server at `http://127.0.0.1:8080/mcp/openai`. This harness does not build/start Docker or alter its configuration.
- An owner-only regular credential file at `~/.config/mobilerun/local-mcp.json`, or an external path in `MOBILERUN_LOCAL_CREDENTIAL_FILE`. Use the existing setup helper: `node plugins/test-plugin/scripts/setup-local-auth.mjs`. Never paste a key in chat or put it in a ZIP.

## Start explicitly

**Anyone who gets the public URL can use all exposed tools through the bridge owner's account**, including device access/control and credit-consuming operations. The private key stays on the machine, but that does not restrict visitors' account access. Development use only. There is no OAuth, tenant isolation, or client authentication at this test endpoint.

```bash
python3 testing/mcp/setup.py start --allow-public-account-access
```

Add `--build` to generate both remote test ZIPs as soon as the tunnel prints its new URL.

Keep the command running while using the plugins. It starts only its own bridge and temporary tunnel. The origin MCP must already be running. It does not install login services, change production auth, or start Docker. The public hostname changes when the tunnel restarts.

The local bridge binds only `127.0.0.1:8081` and forwards only `POST /mcp/openai` to the selected loopback upstream. It does not expose other localhost ports or arbitrary origin paths. Both plugins intentionally use the origin's **OpenAI policy profile**, not the Claude-specific route.

For a different origin/bridge port, see `python3 testing/mcp/setup.py start --help`.

## Check the endpoint

Copy the URL printed by `start`, including `/mcp/openai`:

```bash
python3 testing/mcp/setup.py check --url https://example.test/mcp/openai
```

This performs initialization and tool discovery only. It does not create devices, execute tasks, or call `list_devices`. Successful discovery proves transport, not account validity or host conversation tool attachment. Replace the example hostname with the running tunnel's URL.

## Build both static test ZIPs

```bash
python3 testing/mcp/package_plugins.py --url https://example.test/mcp/openai
```

Outputs (Git-ignored):

- `zip/test-plugin-openai.zip`: portable manifest and remote Streamable HTTP connection, version 0.4.0.
- `zip/test-plugin-claude.zip`: Claude manifest and HTTP MCP connection, version 0.4.0.

Both include onboarding and mobile-tasks, no client credential, and no local launcher. Builds are deterministic for the same source/URL. The origin source packages and `zip/test-plugin.zip` local fallback are untouched. Refresh the test ZIPs whenever the temporary hostname changes. Do not ship these account-delegating development artifacts as production connectors.

For ChatGPT, this setup was reported working in **Work** mode; regular chat can load skills without exposing bundled MCP tools. No claim of regular-chat support follows from a healthy endpoint. For Claude, load the extracted plugin directory in a compatible plugin host (Claude Code supports `claude --plugin-dir ./extracted-plugin`); validate and test that host separately. Uploading files alone is not evidence of callable tools.

## Stop and cleanup

Press **Ctrl-C** in the foreground `start` command to stop its bridge and tunnel. Startup failure also cleans up children. No broad process-name killing or unrelated Docker shutdown is performed. Stop your separately started Docker MCP/runtime yourself when finished. Keep credentials private; no runtime state is committed.

## Automated test cases

Build standard artifacts, then run the normal repository suite:

```bash
python3 scripts/package_plugins.py
python3 scripts/package_test_plugin.py
python3 -B -m unittest discover -s tests -v
```

The `test_mcp_bridge`, `test_mcp_setup`, and `test_mcp_test_packages` tests use synthetic credentials, fake processes, and loopback HTTP servers. They require no Cloudflare account, Docker, paid account calls, or internet. Node-based tests require Node; inspect skips when checking a machine without it.

Coverage includes credential-file validation, header isolation, route restrictions, redirect refusal, notifications, body bounds, upstream failure, timeout/concurrency controls, lifecycle failure cleanup, URL validation, deterministic provider ZIPs, and protection of standard artifacts. Test names and assertions define the exact tested boundary; native host loading remains manual.

## Manual host acceptance cases

| Case | Expected result |
| --- | --- |
| Import and enable each test ZIP | Skills and the configured remote MCP connection are recognized. |
| Ask to list devices | Host calls `list_devices`; returns accessible devices or a successful empty list. Only run with account owner's permission. |
| Skills load, tools absent | Report host attachment failure; do not claim a dead tunnel or successful device access. |
| Stop tunnel, retry connection | Report connection unavailable; do not fabricate device results. |
| Restart tunnel, use old ZIP | Old URL does not become current automatically; rebuild and reimport with the new URL. |
| Ask for a no-spend installation check | Use initialization/discovery only; no device provisioning or task execution. |
| Request unsupported operation | Explain the limitation; do not invent tool names or call unrelated tools. |

Record host/version/mode, tool selected, arguments, result/error, and confirmation behavior in private test evidence. Do not commit device identifiers, account responses, or recordings containing secrets.
