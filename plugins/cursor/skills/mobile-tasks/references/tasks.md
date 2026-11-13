# Task execution

## Bounded agent task

1. Describe a specific task, app, desired outcome, constraints and stopping point. Instruct the task to stop before actions requiring approval, including entering credentials, purchases, data deletion, or messages or payments to third parties. Choose bounded settings such as `maxSteps` only if the exposed schema supports them. Use stored credential references where supported and approved, never raw secrets in task text or chat.
2. Submit `run_task` once with the device and instruction. Save the returned task ID and initial status: **submitted is not completed**. Do not resubmit simply to check progress; an ambiguous submission can create a duplicate. Inspect task history/status before deciding what to do next.
3. Poll `get_task_status` at a reasonable interval until a terminal status (`completed`, `failed`, or `cancelled`) or the host's time limit. On `paused`, stop polling, report the task ID and last verified status, and obtain any necessary user input; do not automatically resubmit or resume. If the task asks a question that can be answered reasonably within scope, use `send_task_message`; its delivery is queued, so inspect the trajectory for application. Ask only for essential input or an action requiring approval. Use `stop_task` if the user requests cancellation and inspect the resulting status.
4. At terminal status retrieve `get_task_summary` where exposed; otherwise report the actual status and output fields available from `get_task_status`. Use trajectory and available screenshot/UI-state media for supporting evidence. Status fields may omit the final message. Report task ID, actual status, observed outcome, evidence and any remaining user action. If still running, report that fact and how to resume monitoring.
5. If the task failed or finished with an ambiguous result, inspect the evidence and retry once with a refined goal before reporting. Retry only when the prior task is terminal and repeating is safe, within scope and spending limits. Never retry a cancelled task or repeat an external or irreversible action without approval. Do not retry an unresolved submission or a task still running. Poll the retry and report its actual outcome and task ID.
6. Stop a device when the user requests cleanup or the agreed work is finished and stopping is within scope. Reset erases device data; termination is irreversible. Obtain explicit approval for either, describing the data loss first.

Minimal calls, using actual IDs and instruction: `run_task({deviceId: "device-id", task: "Open the app and inspect Settings"})`; then `get_task_status({taskId: "task-id"})`. When using `get_task_trajectory`, page with the returned `nextOffset` until finished.


## Example

For “navigate to settings and return battery status”, submit: `run_task({deviceId: "device-id", task: "Open Settings, find the battery status, and report the displayed battery level and charging state."})`. Poll `get_task_status` and report the verified result.

For an ambiguous submission, use `list_tasks` and inspect matching task status before retrying. Do not duplicate a task that may still be running; do not assume submission failed.
