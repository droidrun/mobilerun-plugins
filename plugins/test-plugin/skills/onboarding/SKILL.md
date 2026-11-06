---
name: onboarding
description: Use when a user connects Test Plugin, checks the installation, has no devices, wants a first Android cloud phone, or needs account or connection help.
---

# Get started with Test Plugin

Enable Test Plugin in the host's plugin/MCP interface. Node.js 20+ and a local MCP server at `http://localhost:8080/mcp/openai` are required. The stdio bridge obtains the server's API key from `MOBILERUN_CLOUD_API_KEY` or a local configuration file outside the package. Never put credentials in chat or the plugin package. Local authentication errors require checking the server and bridge credential setup, not browser OAuth. Do not follow the shared browser sign-in recovery instruction below for this local connection. If already connected, proceed directly to the user's goal.

<!-- BEGIN SHARED FIRST DEVICE -->
## Connect and choose a goal

Use the Mobilerun tools exposed by the host. When `list_devices` is available, call it to check the connection and discover existing phones. A successful empty list means **connected, with no devices yet**. If it is missing, use the host setup steps above and report that a live connection check is not yet available. When the user requests a no-spend or local-only installation check, inspect the plugin manifest and MCP configuration without live calls, phone creation, or task execution.

Ask what the user wants to do only when their goal is missing. Useful starting points: test an app, complete a mobile task, or inspect a phone. If the goal is already clear, continue with it.

## First useful run

1. **Reuse a suitable device** from the list. If none exists, recommend an **Android cloud phone** as the first-device option for a new user without an upgraded device plan. Keep an explicit iOS choice instead of replacing it with Android.
2. **Create the requested phone** with `create_device` and the exposed schema: `android_cloud_phone` for Android, or `ios_phone` for an explicitly requested, eligible iOS device. Device provisioning uses plan capacity or device minutes; agent tasks use execution credits. If creation has not been requested, explain the chosen phone and usage, then get the user's go-ahead. An informed request to create it is sufficient authorization; do not ask again for the same action.
3. **Wait for readiness.** Keep the returned device ID and poll `get_device` at a reasonable interval until `ready`, for at most 5 minutes or 10 calls, whichever comes first (or a shorter host limit). Stop immediately on `terminated` or `stopped`; `maintenance` and `unknown` may be temporary, but stop when the budget expires. If not ready, report the device ID and last verified state and ask how to proceed. Do not create a replacement or resume a stopped device without appropriate authorization. If provisioning returns an error, use the recovery table below rather than creating duplicates.
4. **Do the user's work.** Use the bundled [mobile-tasks](../mobile-tasks/SKILL.md) guide for app installation, direct phone control, a one-off agent task, or task results. No documentation lookup is needed.

If the user asks for a “physical phone,” explain that an Android cloud phone is a hosted Android device accessed remotely, not their own handset. For an owned phone, use the exposed personal-device connection operation if available and have the user complete device-side setup; otherwise explain that this connection cannot register it. A `device_slot` is not a substitute for an Android cloud phone. If the user explicitly requests iOS, keep that choice and use the account's iOS eligibility instead of silently switching platforms.

## Account and connection recovery

| Result | Next step |
| --- | --- |
| No Mobilerun tools | Enable the plugin/MCP connection in the host and check workspace availability. |
| Authentication expired / unauthenticated | Reconnect in the host and complete browser sign-in. |
| Permission denied | Check the selected account/workspace and its access permissions. |
| `DEVICE_TYPE_UNAVAILABLE` / 422 | Choose an available type; recommend Android for a new user's first phone. |
| `SUBSCRIPTION_REQUIRED` | Explain the requested device's plan requirement; offer Android when appropriate. |
| `PAYMENT_REQUIRED` / 402 | Use the returned reason to check device minutes, execution credits, or concurrency in the active workspace. |
| `RESOURCE_EXHAUSTED` / 429 | Check available plan slots/concurrency before provisioning again. |
| Interrupted creation | Inspect the device list and returned device ID before submitting another create request. |

For plan, included-credit, or balance questions, use the active workspace's [billing page](https://cloud.mobilerun.ai/billing). Follow its actual account setup steps. Reconnecting does not change balances.

Finish with the connection result, selected device ID/state, and the next action for the user's goal—not another setup questionnaire.

**Example:** “Mobilerun is connected; there are no devices yet. I'll use an Android cloud phone for your app test, wait for it to be ready, then install the app and check the login screen.”
<!-- END SHARED FIRST DEVICE -->
