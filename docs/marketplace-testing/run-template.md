# Private marketplace run record — template

Copy outside the public repository. Keep raw traces, credentials, private IDs, recordings, and reviewer links out of shipped packages. All rows start **NOT RUN**.

## Environment

- Run/date/operator:
- Provider/client/version:
- Route: full package / hosted MCP only / Inspector / real in-app:
- Package version and archive SHA-256:
- Endpoint, deployment/profile (if verifiable):
- Workspace/fixture aliases (private mapping to actual IDs):
- OAuth/reconnect results (no secrets):
- Complete inventory reference/timestamp and page count:
- Approved actions/resources/spend limit (none by default):

## Case results

Copy applicable rows: OpenAI P1–P5/N1–N3; Claude C1–C3; Cursor import/discovery/OAuth/five reads/onboarding/reload; Grok Stage A and Stage B individual checks. Use one row per check, never a group PASS that hides failures.

| Case | Exact prompt/steps | Expected | Actual calls and observed response | Status | Sanitized evidence / video timestamp | Blocker or follow-up |
| --- | --- | --- | --- | --- | --- | --- |
| Copy applicable case ID | Pending | From runbook | Not executed | NOT RUN | Pending | Pending |

## Every-tool coverage

One row per advertised tool, including tools unused by prompts. Compare row names against all `tools/list` pages. Claude requires every-tool testing. An empty ledger is not coverage; PASS requires observed evidence.

| Tool / title | Schema and annotation evidence | Side effects / approval | Fixture and sanitized arguments | Expected success/error and state checks | Actual result / evidence | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Populate from actual tools/list | Pending | Unreviewed; do not call | Pending | Pending | Not executed | NOT RUN |

## Sign-off

- Inventory count / ledger count / PASS / FAIL / BLOCKED / NOT RUN:
- Deployed inventory versus source mismatches:
- Unexpected side effects, costs, or sensitive output:
- Cleanup/restore authorization and verified result:
- Video status, approved destination, reviewer access verified:
- Credentials delivered privately and independently verified:
- Remaining blockers and owner:
- Submission authorized by owner: NO (default):
