---
name: mobile-tasks
description: Use when a user wants to operate a Mobilerun device, test an app, run a mobile agent task, inspect its results, or manage its device.
---

# Mobile devices and tasks

Choose direct control for inspection or an agent task for a bounded goal. Use exposed tools and current schemas; profiles differ. Keep the user's app, device and requested action in scope.

## Feature requirements

Explain only the requested feature or actual limitation. Respect included-only and no-commerce tool/profile restrictions and user constraints: never initiate purchases or bypass restrictions. No prices, plan lists or upgrade prompts.

| Feature | Relevant requirement |
| --- | --- |
| More phones | Subscription slots, minute balance and concurrency are distinct limits; subscription Android phones need a dedicated proxy. Auto minute fallback is not guaranteed. |
| Tasks and automation | Agent execution and workflow building/runs use execution credits. |
| Numbers and SMS | A number is a separate resource; country availability, SMS capability and included capacity vary. If included capacity is absent, respect included-only scope. |
| Mailboxes | A connected mailbox or included capacity may be available; a separate service entitlement or setup may be needed. |
| Proxies | Included capacity and traffic allowance vary; BYO proxy requires compatible setup. |
| eSIM | Carrier service and device capability are needed. |
| Apps, files, recording, integrations | Availability and setup vary; integrations may require connection and authorization, not a universal paid upgrade. |

Check balances in active workspace account usage settings. Only offer [resource capabilities](https://docs.mobilerun.ai/mcp-server) for a relevant account/feature-requirement question or confirmed entitlement limitation, not for missing tools or connectivity errors. Optional information, not a runtime lookup.

## Tool-intent map

| Intent | Tool examples, where exposed |
| --- | --- |
| Find or provision | `list_devices`, `get_device`, `create_device` |
| Device lifecycle | `manage_device_resume`, `manage_device_stop`, `manage_device_reboot`, `manage_device_reset`, `terminate_device` |
| Find, install, launch | `apps_list`, `list_apps_on_device`, `manage_device_apps_install`, `manage_device_apps_list_installs`, `manage_device_apps_start` |
| Observe and act | UI state or screenshot tools; `device_action_tap`, `device_action_swipe`, keyboard and global-action tools |
| Agent execution | `run_task`, `get_task_status`, `get_task_summary`, `get_task_trajectory`, `send_task_message`, `stop_task` |
| Evidence | `get_task_media_screenshot`, `get_task_media_ui_state`; device screenshot or recording tools |

Names and arguments vary by profile. If unavailable, report the operation and offer an exposed alternative; do not bypass restrictions or pass REST options through an MCP tool.

## Prepare the device and app

1. Identify the target app, device, goal, scope and any explicit stop condition. Reuse a suitable device: `list_devices`, then `get_device` for its state. If stopped, resume it when authorized. For a new device, explain the applicable subscription capacity or minute usage and create the requested type; for a first unspecified device recommend an Android cloud phone.
2. Poll `get_device` at a reasonable interval until `ready` before interacting, for at most 5 minutes or 10 calls, whichever comes first (or a shorter host limit). Stop immediately on `terminated` or `stopped`; `maintenance` and `unknown` may be temporary, but stop when the budget expires. If not ready, report the device ID and last verified state and ask how to proceed. Do not create a replacement or resume a stopped device without appropriate authorization. If creation times out, inspect existing devices before retrying; where `clientRequestId` is exposed, reuse the original key for the same creation request.
3. Check `list_apps_on_device` and `apps_list`. If needed and authorized, install the requested package or bundle using the exposed schema. `install_requested` acknowledges the request; inspect `manage_device_apps_list_installs` for `running`, `succeeded`, or `failed`, then launch after success. Confirm with the user before uninstalling an app because local data may be removed.

## Direct control: observe → act → observe

1. Obtain UI state or a screenshot; identify the app and target. Paginate or filter long UI trees where available.
2. Tap a visible target, swipe, type into the focused field, or navigate; stay in scope.
3. Observe again and verify the expected state before acting. Report the visible result, not merely a tap. If a control is absent, refresh and navigate rather than repeatedly guessing coordinates.

## Bounded agent task

1. Describe a specific task, app, desired outcome, constraints and stopping point. Choose bounded settings such as `maxSteps` only if the exposed schema supports them. Use stored credential references where supported, never raw secrets in task text or chat.
2. Submit `run_task` once with the device and instruction. Save the returned task ID and initial status: **submitted is not completed**. Do not resubmit simply to check progress; an ambiguous submission can create a duplicate. Inspect task history/status before deciding what to do next.
3. Poll `get_task_status` at a reasonable interval until a terminal status (`completed`, `failed`, or `cancelled`) or the host's time limit. On `paused`, stop polling, report the task ID and last verified status, and obtain any necessary user input; do not automatically resubmit or resume. If the task asks a question, use `send_task_message` when appropriate; its delivery is queued, so inspect the trajectory for application. Use `stop_task` if the user requests cancellation and inspect the resulting status.
4. At terminal status retrieve `get_task_summary` where exposed; otherwise report the actual status and output fields available from `get_task_status`. Use trajectory and available screenshot/UI-state media for supporting evidence. Status fields may omit the final message. Report task ID, actual status, observed outcome, evidence and any remaining user action. If still running, report that fact and how to resume monitoring.
5. Stop a device when the user requests cleanup or the agreed work is finished and stopping is within scope. Reset erases device data; termination is irreversible. Obtain explicit approval for either, describing the data loss first.

Minimal calls, using actual IDs and instruction: `run_task({deviceId: "device-id", task: "Open the app and inspect Settings"})`; then `get_task_status({taskId: "task-id"})`. When using `get_task_trajectory`, page with the returned `nextOffset` until finished.

## Common errors and recovery

- **Not ready or app missing:** check state and installation job; wait or select the correct app.
- **Permission denied or unavailable operation:** check the connected workspace and exposed tool schema; respect the restriction.
- **402 or quota error:** report the returned reason; check the applicable workspace limit: slots, concurrency, device minutes or execution credits.
- **Failed or stalled task:** inspect status, summary and trajectory; explain the evidence and adjust the task only after deciding whether a new run is appropriate. Do not blindly retry an uncertain write.

## Example

“Test that Settings opens.” Launch the app on the ready device, observe, tap Settings, and observe again. Report the result and screen evidence.
