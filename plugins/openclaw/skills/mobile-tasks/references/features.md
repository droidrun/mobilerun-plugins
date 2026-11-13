# Feature requirements

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

## Common errors and recovery

- **Not ready or app missing:** check state and installation job; wait or select the correct app.
- **Permission denied or unavailable operation:** check the connected workspace and exposed tool schema; respect the restriction.
- **402 or quota error:** report the returned reason; check the applicable workspace limit: slots, concurrency, device minutes or execution credits.
- **Failed or stalled task:** inspect status, summary and trajectory; explain the evidence and adjust the task only after deciding whether a new run is appropriate. Do not blindly retry an uncertain write.

