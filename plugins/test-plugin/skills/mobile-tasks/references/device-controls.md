# Device preparation and low-level controls

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

1. Identify the target app, goal, scope and any explicit stop condition. Reuse a suitable device: `list_devices`, then `get_device` for its state. Pick the best ready device; if none is ready, resume a suitable stopped device without asking. Respect a requested device and spending limits. For a new paid device when none exists, explain the applicable subscription capacity or minute usage and obtain approval; for a first unspecified device recommend an Android cloud phone.
2. Poll `get_device` at a reasonable interval until `ready` before interacting, for at most 5 minutes or 10 calls, whichever comes first (or a shorter host limit). Stop immediately on `terminated` or `stopped`; `maintenance` and `unknown` may be temporary, but stop when the budget expires. If not ready, report the device ID and last verified state. Do not create a replacement without approval. If creation times out, inspect existing devices before retrying; where `clientRequestId` is exposed, reuse the original key for the same creation request.
3. Check `list_apps_on_device` and `apps_list`. If needed and authorized, install the requested package or bundle using the exposed schema. `install_requested` acknowledges the request; inspect `manage_device_apps_list_installs` for `running`, `succeeded`, or `failed`, then launch after success. Confirm with the user before uninstalling an app because local data may be removed.

## Direct control: observe → act → observe

1. Obtain UI state or a screenshot; identify the app and target. Paginate or filter long UI trees where available.
2. Tap a visible target, swipe, type into the focused field, or navigate; stay in scope.
3. Observe again and verify the expected state before acting. Report the visible result, not merely a tap. If a control is absent, refresh and navigate rather than repeatedly guessing coordinates.
