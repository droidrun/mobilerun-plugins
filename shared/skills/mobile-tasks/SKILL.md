---
name: mobile-tasks
description: Use when a user wants to navigate a Mobilerun device, read its screen, check battery status, change settings, use or test an app, run or inspect a task, or manage a device.
---

# Mobile devices and tasks

## Core loop

1. Pick the best ready device for the goal; use `list_devices` and `get_device` as needed. Respect an explicitly requested device. If none is ready, resume a suitable stopped device. Wait until `ready` before `run_task`, using the [bounded readiness procedure](references/device-controls.md).
2. Make reasonable interpretations without confirmation. Load [task guidance](references/tasks.md), write the goal, expected output, scope and stopping point, then submit `run_task`. For example: open Settings and report the displayed battery level and charging state.
3. Poll `get_task_status` until terminal, paused, or the host time limit. Retrieve `get_task_summary` where exposed. If a task fails or its result is ambiguous, retry once with a refined goal when safe. Report the result, device and task ID; if still running, report its status. Do not narrate tool steps.
4. Use low-level controls only when explicitly requested or clearly better for a trivial atomic action. Never tell the user to perform the goal manually while tasks are available.

## Guardrails

Tasks use execution credits; devices use capacity or minutes. Respect the user's scope, spending limits and tool/profile restrictions. Never bypass restrictions or expose secrets. Obtain approval before creating any new paid device unless the user explicitly authorized that creation. Ask before purchases or plan changes, deleting data or apps (including reset or termination), sending messages or payments to third parties, or entering credentials. Also ask when essential information cannot reasonably be inferred or a task requires user input.

## References

Load only when needed:
- [Task writing, polling and recovery](references/tasks.md): submissions, statuses, results and task messages.
- [Device and low-level controls](references/device-controls.md): readiness, apps, observation and direct actions.
- [Feature requirements and errors](references/features.md): account limits, entitlements and troubleshooting.
