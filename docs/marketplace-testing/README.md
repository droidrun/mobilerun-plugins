# Marketplace testing pack

Prepared November 5, 2026. **No authenticated provider-client tests or video recording have been completed by this pack.** No submission, publication, purchase, or fixture provisioning is authorized by these instructions.

Record executed checks and account-specific evidence outside the public repository. Repository tests do not count as in-client test completion.

| Provider | Runbook | Current status |
| --- | --- | --- |
| OpenAI | [5 positive + 3 negative cases](openai.md), [video storyboard](openai-video.md) | Cases/script prepared; execution and video pending |
| Claude | [3 prompt candidates + every-tool tests](claude.md) | Prepared; working-in-client status unverified |
| Cursor | [local tests](cursor.md) | Cursor-native package available; client execution pending |
| Grok Bot | [local and in-app tests](grok-bot.md) | Prepared; both execution stages pending |

## Shared reviewer fixtures

- Use a dedicated, least-privilege reviewer account with synthetic data, not a personal production workspace. Deliver credentials only through the provider's private reviewer channel. Follow its requirements for MFA/verification and ensure the reviewer can actually sign in.
- Arrange one existing ready device with a unique name such as `marketplace-review-device`, synthetic installed apps with known package/version values, and at least one existing task with a known ID and status. Record exact IDs and expected metadata privately. Generic prompts mentioning “my test device” assume this unique fixture; ambiguity must trigger clarification, not guessing.
- Confirm live workspace balance and device availability before testing. A pre-existing running device may continue consuming minutes even when test calls are read-only. This pack does not create fixtures, grant credits, switch workspaces, or approve spending.
- Keep a non-sensitive empty-account fixture if available to verify that an empty list is a successful connection. Do not create accounts automatically.
- Endpoint: `https://api.mobilerun.ai/v1/mcp`. Follow [public authentication instructions](https://docs.mobilerun.ai/mcp-server#api-key-authentication) and configure authentication privately through the host's supported mechanism. Test browser OAuth only if supported, and record any missing required authentication flow as BLOCKED. Never paste passwords, bearer tokens, API keys, or verification codes into prompts or evidence.

## Inventory and safety gates

Capture **all pages of the actual `tools/list` response** for each provider connection, with names, titles, descriptions, input schemas, and annotations. Record client version, server deployment/version if available, workspace alias, profile, and timestamp. Client identity may select different tools; an Inspector inventory is not proof of the host's inventory.

The prepared read-only cases use `list_devices`, `get_device`, `list_apps_on_device`, `list_tasks`, and `get_task_status`. Confirm their availability and response fields from the actual connection. Do not assume screenshot capture, task output, or other content is exposed. If live tools differ, resolve the mismatch before claiming readiness; do not silently broaden access or select a full-access profile.

Read-only baseline calls require no billable operation. For **each** tool beyond that baseline, review its actual schema and side effects before calling it:

| Class | Gate |
| --- | --- |
| Reads | Authorized synthetic data only; prevent secret/PII exposure in saved results |
| Device actions or configuration | Disposable fixture and explicit approval of action/restore procedure |
| Task execution, resource creation, included-capacity allocation | Explicit action, resource and maximum-spend approval; included capacity is not blanket permission |
| Deletes, resets, credential changes | Named disposable target and explicit destructive-action approval; never use real credentials |

Never infer safety from the name or annotation alone. No blind retries of writes; follow actual idempotency support. A denied approval means **BLOCKED**, not PASS. Do not invoke destructive tools merely to complete a ledger.

## Evidence and result recording

Copy [the run template](run-template.md) into private evidence storage for each session. Use **NOT RUN**, **PASS**, **FAIL**, or **BLOCKED**; never promote preparation or a simulation to PASS. Keep one row per case and one row per advertised tool. Save sanitized request/response traces, observed client responses, and video timestamps. A plausible assistant response without tool evidence is insufficient.

Keep raw traces, credentials, account/device/task IDs, recordings, and reviewer links outside this public repository and upload ZIPs. Share only approved, sanitized evidence through the designated review channel. Do not publish or upload a video automatically. An expected refusal proves that prompt boundary only, not server-side tenant isolation; backend authorization tests require approved controlled accounts/fixtures.

## Release gate

Run repository tests and validate ZIP roots separately from live tests. Complete each provider runbook, resolve failures, and verify the installed version matches the archive. Record reviewer access privately. Do not attest to local/in-app testing or add a video URL until the evidence exists. No commits or submissions are part of this preparation.
