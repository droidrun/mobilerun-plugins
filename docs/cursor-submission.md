# Cursor company submission

Prepare the public listing as **Mobilerun**, using `support@mobilerun.ai` for publishing and review correspondence. This checklist prepares the submission; it does not submit the plugin, send email, or establish company ownership.

## Package and publisher details

- Repository: `https://github.com/droidrun/mobilerun-plugins`
- Plugin folder: `plugins/cursor`
- Plugin manifest: `plugins/cursor/.cursor-plugin/plugin.json`
- Plugin identifier: `mobilerun`; availability must be checked during submission.
- Author: `Mobilerun`; email: `support@mobilerun.ai`.
- Root multi-plugin manifest: `.cursor-plugin/marketplace.json`, with Mobilerun owner metadata and an entry pointing to `./plugins/cursor`.
- Logo: `plugins/cursor/assets/logo.svg`, referenced by the plugin-relative path `assets/logo.svg`.
- Hosted MCP: `https://cloud.mobilerun.ai/api/mcp/cursor`. The package selects the dedicated profile; current deployment, OAuth discovery, and authenticated tool filtering remain unverified.

## Note to paste into the submission form

Use this only when the submitting account belongs to an authorized company representative:

> This is an official company submission on behalf of Mobilerun. Please associate the publisher with Mobilerun and use support@mobilerun.ai for publishing and review correspondence. The submitting account belongs to an authorized company representative.

Do not add an undocumented company-ownership field to the plugin manifest. `author.name` and the marketplace's `owner` describe attribution; they do not prove authenticated listing ownership, team access, or shared management.

## Before submitting

- [ ] Resolve the data-use policy gate with the service/legal owner. [Cursor Publisher Terms sections 5.3 and 6.3](https://cursor.com/marketplace-publisher-terms) limit use of User Content to providing functionality and prohibit model training on Plugin Data or User Content. [Mobilerun's privacy policy section 3.5](https://mobilerun.ai/privacy) permits anonymized trajectory/usage data for training; [service terms](https://mobilerun.ai/terms) also discuss model improvement. Confirm the actual processing and applicable disclosures satisfy Cursor's requirements. Anonymization alone does not establish an exception, and this checklist does not assert that prohibited training occurred. Do not submit while the applicable commitments remain unresolved.
- [ ] Review the exact public source, Git history, and artifacts using the [public-content checklist](publication.md). Confirm the repository is publicly accessible; changing repository visibility requires authorization.
- [ ] Confirm the plugin name is available and the submission selects `plugins/cursor` through the root marketplace manifest.
- [ ] Validate JSON, relative component paths, logo inclusion, skill frontmatter, and the README's installation/configuration guidance. Do not embed credentials or add undeclared variables.
- [ ] Rebuild archives with `python3 -B scripts/package_plugins.py` and run `python3 -B -m unittest discover -s tests -v` from the repository root. These are structural checks, not a replacement for Cursor testing.
- [ ] Install the package in Cursor using its documented local-plugin flow. Verify both skills, browser OAuth, actual tool discovery, and an authorized read-only call. Record failures rather than treating an installed folder as a successful connection.
- [ ] Check the current signed-in [publishing form](https://cursor.com/marketplace/publish). Confirm the selected publisher/team, company correspondence email, and who can manage the listing. Paste the company note into a suitable description/notes field.
- [ ] If the form only offers **Individual**, or company ownership/shared management is unclear, ask `marketplace-publishing@cursor.com` to confirm the correct process before submitting. Do not infer that purchasing Teams is necessary.
- [ ] Have an authorized representative review and submit. Cursor reviews submissions manually; package checks do not guarantee acceptance.

The authenticated publisher/team options and successful native Cursor OAuth/tool execution remain unverified. None of these unchecked steps is completed merely by adding this document.

## Publishing-support draft

To: `marketplace-publishing@cursor.com`

Subject: `Confirm Mobilerun company ownership for Cursor plugin submission`

> We are preparing an official Mobilerun plugin submission from an authorized company representative's account. The repository is https://github.com/droidrun/mobilerun-plugins and the plugin folder is plugins/cursor. The plugin author and marketplace owner metadata identify Mobilerun, with support@mobilerun.ai as the preferred contact.
>
> Please confirm how to associate the public listing with Mobilerun, route publishing/review correspondence to support@mobilerun.ai, and enable the intended company management access. If the signed-in form offers only Individual, should we wait for association by your team before submitting? Are there any account-role or plan requirements specifically for public company publishing?

This is a draft only; no email has been sent.

## Sources and limits

- [Current plugin reference and submission checklist](https://cursor.com/docs/reference/plugins#submitting-a-plugin): valid manifest/components, public Git repository, relative paths, README, local testing, and root marketplace manifest for multi-plugin repositories.
- [Cursor plugins and local testing](https://cursor.com/docs/plugins#test-plugins-locally).
- [April 2, 2026 staff response](https://forum.cursor.com/t/cursor-plugin-submit-as-company-not-individual/156274/3): company author metadata plus a submission-description note were the workaround for the then-account-bound form. This is dated guidance, not proof of the current form's limitations.
- [September company-team discussion](https://forum.cursor.com/t/cursor-marketplace-submission/170458/1): does not document a reliable current team-owner selection procedure.
- [Staff publishing contact](https://forum.cursor.com/t/cursor-marketplace-submission/170458/8): publishing questions go to `marketplace-publishing@cursor.com`.
- [Private team marketplaces](https://cursor.com/docs/plugins#team-marketplaces): their Teams/Enterprise requirements do not establish requirements for a public company listing.
