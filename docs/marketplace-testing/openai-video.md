# OpenAI walkthrough recording plan

**Script/storyboard only. Recording: NOT CREATED. URL: PENDING.** No synthetic video, placeholder link, or simulated tool output counts as evidence.

## Before recording

- Execute and pass [P1–P5 and N1–N3](openai.md) using the dedicated reviewer account. Fix failures before the final recording.
- Use synthetic data and a clean browser profile. Hide notifications, bookmarks, unrelated tabs, emails, billing details, tokens, and console secrets. Do not record passwords or reviewer credentials.
- Record readable client text and expanded tool calls/results with operator-selected screen-recording software. This file does not automate recording.
- Record client, date, version/archive identity, endpoint, and route. Distinguish full-package from hosted-MCP-only testing.

## Storyboard / narration

Suggested pacing is 5–8 minutes, not a provider-imposed duration. Keep tool latency visible or label cuts; never edit a failure into apparent success.

| Segment | On screen | Suggested narration |
| --- | --- | --- |
| Intro | Listing/connection and version | “This is Mobilerun's hosted MCP, using a dedicated synthetic reviewer workspace. This walkthrough covers five positive and three negative cases.” |
| Connection | Endpoint and connected state; safe consent flow if available | “Authorization is handled in the browser. Installation alone does not prove OAuth. Credential entry is excluded.” Do not claim fresh OAuth if showing an existing session. |
| P1 | Exact prompt, `list_devices`, result | “Only devices accessible to this account are listed.” |
| P2 | Exact prompt, fixture selection, `get_device` | “This is the existing fixture's returned state; nothing is provisioned or changed.” |
| P3 | Exact prompt, `list_apps_on_device`, metadata | “These apps come from the fixture. No app is installed, launched, or deleted.” |
| P4 | Exact prompt and `list_tasks` result | “These are existing task identifiers and status metadata, not newly started work.” |
| P5 | Exact prompt and `get_task_status` | “The reviewed profile omits task messages/output, so no explanation is invented.” |
| N1 | Unauthorized-account prompt, response and trace | “The assistant refuses unauthorized access and does not attempt a bypass.” |
| N2 | Duplicate-credit prompt, response and trace | “The plugin cannot reset trials or grant/transfer credits. Live workspace offers determine eligibility.” |
| N3 | No-spend prompt, read-only call and response | “Connectivity is checked without creating resources or running a task. Existing fixtures may still consume device minutes.” |
| Close | Eight-case results and actual timestamps | “These results correspond to this account, connection, and version. The review instructions provide the same fixtures privately.” |

## Recording acceptance checklist

- [ ] Every exact prompt, actual response, and tool evidence is readable.
- [ ] All eight cases have matching result rows and video timestamps.
- [ ] Edits are labeled; no reconstructed results or fake authorization.
- [ ] Sensitive frames, captions, audio, and link metadata are reviewed/redacted.
- [ ] Owner approves destination/audience before upload or sharing.
- [ ] Real URL opens for the reviewer without owner-only permissions or inaccessible access controls.
- [ ] URL is added to final review details/manifest only after verification.

Check boxes only after completion. See [OpenAI initial-review requirements](https://developers.openai.com/plugins/deploy/submission).
