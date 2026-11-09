# Mobilerun for Cursor

Connect Cursor to the [Mobilerun](https://mobilerun.ai) hosted MCP for Android devices, tasks, apps, and automation. Actual tools depend on the connection's server profile and permissions. This package is not a verified Marketplace listing.

The package includes two practical skills in the standard `skills/<name>/SKILL.md` layout: `onboarding` for connection and first-device setup, and `mobile-tasks` for device/app control and bounded tasks. Tasks and devices can consume credits or minutes.

## Install locally

Copy this entire directory, including `.cursor-plugin/`, `assets/`, and `LICENSE`, to `~/.cursor/plugins/local/mobilerun`. Do not link to a repository outside the local-plugin directory: Cursor skips those symlinks. Do not overwrite an existing installation without checking it first.

Restart Cursor or run **Developer: Reload Window**, then open **Customize** and confirm the Mobilerun MCP component is present. Local-plugin imports must be allowed by organization policy; an installed marketplace plugin of the same name takes precedence.

The server URL is `https://cloud.mobilerun.ai/api/mcp/cursor`; there are no bundled API keys, tokens, or client secrets. Follow [Mobilerun's browser OAuth instructions](https://docs.mobilerun.ai/mcp-server#oauth-authentication) through Cursor's connection interface. Actual Cursor login remains unverified; if the required flow is unavailable, report the limitation. Ask “List my Mobilerun devices” to check access without creating resources or starting billed tasks. An empty list is valid. File installation is not proof of authentication or tool access.

This package explicitly selects the dedicated `/api/mcp/cursor` profile rather than the broader base endpoint. The dedicated route and its OAuth metadata returned 404 during an earlier check; current deployment, browser OAuth, and authenticated tool filtering must be verified before publication. The packaged URL does not prove that the profile is deployed. Existing cached installations may still use the base endpoint; inspect the loaded configuration after reinstalling.

## Privacy and terms

When you use the hosted MCP connection, Cursor sends the tool requests and arguments needed for your actions to Mobilerun; results are returned to Cursor. Depending on what you do, this can include task instructions, device and app information, screen content, screenshots, action histories, and results. Avoid sending secrets or sensitive data you are not authorized to share. Browser OAuth credentials are entered in the sign-in flow, not in the plugin files.

Review the [Mobilerun privacy policy](https://cloud.mobilerun.ai/legal/privacy-policy), [data processing agreement](https://cloud.mobilerun.ai/legal/dpa), and [terms of service](https://cloud.mobilerun.ai/legal/terms-of-service), as well as Cursor's applicable policies. The privacy policy describes use of anonymized trajectories and usage data for service improvement and AI model training.

## Public submission

Use [Cursor Marketplace publishing](https://cursor.com/marketplace/publish) only after validating this package and completing local client tests. Cursor's submission checklist requires a public Git repository. Verify that the submitted repository and package path are publicly accessible. No push or submission is performed by copying this package locally.

### Company submission note

The manifest identifies **Mobilerun** as the author and `support@mobilerun.ai` as the company contact. An authorized representative should paste this note into the submission form's description or notes field:

> This is an official company submission on behalf of Mobilerun. Please associate the publisher with Mobilerun and use support@mobilerun.ai for publishing and review correspondence. The submitting account belongs to an authorized company representative.

Author and marketplace-owner metadata provide attribution; they do not establish company ownership or shared management of the published listing. Confirm the owner/team and correspondence address in the signed-in form. If it only offers **Individual**, or ownership is unclear, contact `marketplace-publishing@cursor.com` before submitting. Do not assume a paid Teams plan is required for a public company listing.

Cursor's [April 2026 staff response](https://forum.cursor.com/t/cursor-plugin-submit-as-company-not-individual/156274/3) recommends company author metadata and a submission note, but describes the form at that time. A [September discussion](https://forum.cursor.com/t/cursor-marketplace-submission/170458/1) does not establish the current ownership flow. Neither replaces confirmation in the current form or from publishing support.

## Provenance and license

Based on the Cursor plugin from droidrun/mobilerun-mcp. See the [Mobilerun MCP documentation](https://docs.mobilerun.ai/mcp-server). The MCP URL and README were updated November 5, 2026 to use the API endpoint and document installation and verification boundaries. Shared onboarding and mobile-tasks skills were added November 6, 2026. The upstream Apache-2.0 license and attribution are retained; this package is not relicensed under the surrounding repository's MIT license.

Support: <https://docs.mobilerun.ai/support>

Official references: [local installation](https://cursor.com/docs/plugins#test-plugins-locally), [manifest and submission](https://cursor.com/docs/reference/plugins).
