# Grok Bot local and in-app testing

Status: **PREPARED / NOT RUN** for both stages. No Grok-specific package exists here. The submission form accepts an MCP URL or public GitHub repository; the hosted URL is the candidate. Grok Bot is distinct from ordinary Grok, labeled coming soon on the form. Cursor results do not substitute for Grok Bot.

## Stage A — local protocol/client test

1. Open MCP Inspector on an approved development machine using its official instructions. If Node/npm exist and package execution is approved, the documented launcher is `npx @modelcontextprotocol/inspector`. Record the version. No tokens in command arguments or saved logs.
2. Select Streamable HTTP and `https://api.mobilerun.ai/v1/mcp`. Configure authentication privately through a mechanism supported by the endpoint and Inspector. Record actual authentication, initialization, and negotiation. A bare discovery or authentication-error response is not authenticated-test PASS.
3. Capture all `tools/list` pages with schemas/titles/annotations. Run authorized baseline reads: device list/detail, installed apps, task list/status. Use actual returned IDs, not literal placeholders.
4. Check safe input validation and disconnected/expired authorization in an isolated session. Do not induce outages, probe other tenants, run tasks, allocate resources, or invoke destructive calls.
5. Save results in the private run record. Inspector may select a different profile; keep its inventory separate from Stage B.

## Stage B — real Grok Bot in-app test

Browser OAuth at the configured API URL remains unverified. The steps below are conditional on actual in-app authentication support; an unavailable required flow is BLOCKED, not permission to embed a key.

1. Obtain authorized Grok Bot access and its current supported custom-plugin/MCP route from the UI or publisher support. The public form does not document a verified private installation sequence; do not invent one. If unavailable, record BLOCKED and leave the attestation unchecked.
2. Add the candidate endpoint through that supported route, finish OAuth, and verify discovery inside Grok Bot. Record app/version, route, workspace alias, inventory, and errors. Ordinary Grok, Inspector, and Cursor are not substitutes.
3. Run: “List my Mobilerun devices”; “Show the state of marketplace-review-device”; “List the installed apps on marketplace-review-device without changing anything”; “Show my recent tasks and the status of the most recent one without starting or retrying a task.” Record each prompt/result separately.
4. Run all three negative prompts from [the OpenAI cases](openai.md) as cross-client safety checks. Inspect actual calls for unauthorized access, credit resets, or spending. Apply the real Grok profile's constraints; do not assume identical OpenAI/Claude output policy.
5. Verify controlled-session reconnect, accurate errors, no unexpected writes, and consistency between results and assistant claims. Save sanitized evidence privately.

## Submission Testing Instructions — draft

> Connect the Mobilerun MCP at https://api.mobilerun.ai/v1/mcp using the client's supported private authentication mechanism and dedicated reviewer access. Browser OAuth at this URL has not been verified; if the client requires an unavailable flow, report BLOCKED. Use the existing `marketplace-review-device` and sample tasks. List devices, read the fixture state, list its installed apps, then list existing tasks and read the latest task's status. Do not create devices, allocate resources, run tasks, or change billing. Report missing tools, fixtures, or authorization rather than bypassing them. Credentials and fixture identifiers are supplied through the approved private review channel, not this public text.

Adapt this draft to the actual supported in-app route and fixtures before submission. It does not claim either stage ran.

- [ ] Local authenticated tests passed with evidence.
- [ ] Actual Grok Bot in-app tests passed with evidence.
- [ ] The form's “I've tested this plugin locally and in-app and confirmed it works as expected” attestation is truthful.

Do not attest, submit, or publish until both stages pass and the owner authorizes submission.

Sources: [submission form](https://x.ai/bot/marketplace/submit-a-plugin), [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector), checked November 5, 2026.
