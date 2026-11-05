# Claude prompts and tool testing

Status: **PREPARED / NOT RUN IN CLAUDE**. These are three reproducible candidates, not claims of working client results. Apply [shared fixtures and safety gates](README.md).

## Real-client setup

Authentication prerequisite: use `https://api.mobilerun.ai/v1/mcp` with the host's supported private credential mechanism. Browser OAuth steps below apply only if that endpoint/client supports them; otherwise record BLOCKED. Never bundle a key.

Add the endpoint through **Customize > Connectors** as a custom connector and finish browser OAuth. Organization policy may require an owner. Enable it through **+ > Connectors** in chat. Custom connectors use the actual Claude runtime; Inspector success alone is insufficient.

Test the [Claude package](../../plugins/claude/README.md) separately via plugin upload when available, including onboarding. A custom connector alone does not prove the bundle loaded. Capture every page of the connection's advertised tools/annotations. Confirm tool titles and applicable `readOnlyHint`, `destructiveHint`, `idempotentHint`, and `openWorldHint` annotations reflect behavior. Missing/misleading metadata must be corrected in the MCP, not through duplicate local tools.

## Three prompt candidates

Run in separate new chats with the uniquely named ready fixture and existing task. Save exact final prompts/clarifications for submission.

| ID | Prompt | Expected tool path and result |
| --- | --- | --- |
| C1 | List my Mobilerun devices and show the state of marketplace-review-device. Do not create or change anything. | `list_devices` → `get_device` with returned ID. Actual state/metadata only; clarify ambiguity. |
| C2 | List the installed apps on marketplace-review-device, including returned package names and versions. Do not install, launch, or delete anything. | `list_devices` → `list_apps_on_device`. Matches synthetic app fixture; no invented fields. |
| C3 | Show my recent Mobilerun tasks and get the status of the most recent one. Do not start or retry any task. | `list_tasks` → `get_task_status` with returned ID. Actual status/step count/success when present, no fabricated output or completion reason. |

Use only fields and tools actually returned by the connection. Missing tools mean BLOCKED, not a working prompt. Empty lists prove connectivity but not populated-fixture acceptance.

## Every-advertised-tool ledger

These prompts cover five baseline tools only. **Claude submission requires testing every advertised tool**, not merely three prompt paths.

1. Save the complete live `tools/list` inventory privately. Expand [the run template](run-template.md) to exactly one row per advertised name, including tools unused by prompts. Compare the row set against all inventory pages; source allowlists are not a substitute.
2. For each tool record title, annotations, schema, fixture, expected success/error, side effects, approval evidence, actual sanitized arguments/result, and status. Never save credential contents.
3. Run authorized reads against synthetic fixtures. Check safe schema rejection using a benign missing required field or wrong type where safe; do not fuzz production or use third-party IDs.
4. Before writes/actions, task execution, allocations, resets/deletes, or credential operations, obtain explicit approvals from the shared gates. Prepare disposable targets and restore/cleanup plans. Exercise each approved tool and verify resulting state with a read. Avoid duplicate writes after timeouts.
5. Include expired/revoked authorization, controlled permission denial, empty data, service failure, and supported insufficient-capacity/credit cases. Use approved controlled setups or label simulations; never induce outages, spend balances, or revoke production credentials merely for errors.
6. Restore approved fixtures and reconcile rows. Any FAIL, NOT RUN, or BLOCKED tool means coverage is incomplete. Resolve blockers or deliberately change the MCP's advertised profile through separately authorized work, then retest. Do not hide untested tools.

Initial baseline rows: `list_devices`, `get_device`, `list_apps_on_device`, `list_tasks`, `get_task_status`—all NOT RUN. Remaining rows must come from the actual inventory, not guessed names. Billed/destructive operations remain blocked pending explicit approval.

## Submission gate

- [ ] C1–C3 pass in actual Claude, with final prompts and evidence.
- [ ] Every advertised tool has executed satisfactory results and accurate metadata.
- [ ] OAuth/reconnect and controlled errors are evidenced.
- [ ] Dedicated reviewer access works without owner intervention.
- [ ] Bundle and connector results are identified separately.

Sources: [Claude testing](https://claude.com/docs/connectors/building/testing.md), [submission requirements](https://claude.com/docs/connectors/building/submission.md), checked November 5, 2026.
