# Publishing handoff

This handoff separates prepared source and ZIPs from checks that require an authenticated host, reviewer account, or publishing portal. It is not a marketplace approval or a certification of the deployed MCP server.

## Distribution artifacts

| Target | Source folder | Generated artifact / route |
| --- | --- | --- |
| Claude | `plugins/claude` | `zip/mobilerun-claude.zip`; submit the remote MCP connector separately, then the plugin bundle under the same organization and exact endpoint URL. |
| OpenAI | `plugins/openai` | `zip/mobilerun-openai.zip`; upload through the Plugins portal using the remote MCP route. |
| Cursor | `plugins/cursor` | Public Git repository with root `.cursor-plugin/marketplace.json`; `zip/mobilerun-cursor.zip` is also available for inspection/distribution. |
| OpenClaw | `plugins/openclaw` | `zip/mobilerun-openclaw.zip`; confirm the receiving registry's current bundle and review requirements. |
| Test Plugin | `plugins/test-plugin` | `zip/test-plugin.zip`; local development only, not a hosted production marketplace submission. |

All plugin manifests identify `https://github.com/droidrun/mobilerun-plugins` as their repository. Claude, Cursor, OpenAI, and OpenClaw remain at the initial `0.1.0` package version; Test Plugin is `0.3.0`. If an initial version has already been published in a portal, increment the relevant package version before uploading an update and follow that portal's update process.

Production ZIPs use explicit file allowlists and exclude the local bridge, credential setup helper, supplemental review fixtures, repository-level documentation, and development evidence. Generated archives are ignored by Git. No reviewer credentials belong in public source or ZIPs.

## Build and local verification

From the repository root:

```bash
python3 -B scripts/sync_skills.py --check
python3 -B scripts/package_plugins.py
python3 -B scripts/package_test_plugin.py
python3 -B -m unittest discover -s tests -v
claude plugin validate --strict plugins/claude
git diff --check
```

Before distributing a ZIP, confirm its integrity and exact byte-for-byte match with the intended package source. Commit reviewed source before submitting repository-based listings; a working-tree change is not present in the public branch until committed and pushed. Follow the [public-content checklist](publication.md), including history/ref review. Pattern scans are guardrails, not comprehensive proof that no sensitive data exists.

## OpenAI review materials

- The package contains five positive and three negative review cases. Supplemental Android-quota and iOS-slot scenarios are retained outside the plugin under `tests/fixtures/`.
- The recording URL is [the Mobilerun Loom walkthrough](https://www.loom.com/share/646c25f3773841f89164a0a12065e79b). Its presence in the manifest does not verify playback, anonymous access, or case coverage. Check it in a signed-out browser and demonstrate the submitted cases.
- The review case uses `get_task_status`, matching the intended provider-profile tool definition. Do not replace it with the generic documentation's older `get_task` name without checking the actual profile. Confirm the deployed inventory in the portal scan.
- The release notes describe the initial package contents. Reviewer credentials must be entered separately through the portal's private review-details flow.

## Checks still required before submission/publication

- [ ] Resolve the Cursor data-use policy gate: its [Publisher Terms sections 5.3 and 6.3](https://cursor.com/marketplace-publisher-terms) limit User Content use and prohibit training on Plugin Data/User Content. Mobilerun's published policies permit certain training/model-improvement uses. The service/legal owner must confirm compliant actual processing and applicable disclosures; do not invent a training exclusion in plugin documentation or treat anonymization as an automatic exception. This is a commitments/verification issue, not evidence of observed prohibited training.
- [ ] Commit and push the reviewed changes to the intended release branch; confirm each portal uses the intended version/commit. Do not publish a development-only package by mistake.
- [ ] Confirm public repository access, publisher identity, account permissions, name availability, and the organization that should own each listing.
- [ ] Install the actual bundled plugin in each intended host, verify skill loading, and complete browser OAuth using the real deployed endpoint. A custom connector alone does not test bundled skills.
- [ ] Verify authenticated tool discovery, every submitted review scenario, token refresh/reconnect, error handling, and permission boundaries. Do not create billed resources merely to test connectivity.
- [ ] Supply a dedicated reviewer account, suitable sample data/resources, and sign-in instructions through the approved private channel. Confirm it can exercise the required functionality without relying on another person's private account.
- [ ] Verify the Loom recording is accessible without sign-in/access requests and covers the submitted cases; do not treat an HTTP response or share URL as video verification.
- [ ] Complete portal/domain verification, connect and scan the deployed MCP, resolve required findings, and review policy/data-handling attestations against actual service behavior.
- [ ] For Claude, submit the hosted MCP separately and pair it with the bundle using the same organization and exact endpoint.
- [ ] For Cursor, follow the [company submission checklist](cursor-submission.md); author metadata does not establish company ownership/shared management. Confirm unclear publisher settings with Cursor support before submission.
- [ ] For OpenClaw, verify native installation, OAuth, tool access, and registry scanning. An accepted dry-run is not publication approval.

These items require evidence. Repository tests do not complete them. Preparing this handoff does not send an email, submit a listing, change repository visibility, merge a PR, or publish a release.

## Official references

- [Claude publishing routes](https://claude.com/docs/directory/publish.md) and [plugin checklist](https://claude.com/docs/plugins/pre-submission-checklist.md).
- [OpenAI submission and review](https://developers.openai.com/plugins/deploy/submission.md).
- [Cursor plugin reference and submission checklist](https://cursor.com/docs/reference/plugins#submitting-a-plugin).
