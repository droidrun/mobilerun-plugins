# Public-content checklist

Publish only the provider package or reviewed repository source intended for distribution.

## Keep out of public source and archives

- Credentials, access tokens, private keys, verification codes, and account-specific configuration.
- Private workspace links, customer records, reviewer credentials, account/device/task identifiers, and raw tool responses.
- Internal plans, execution logs, local environment reports, personal filesystem paths, and unpublished backend implementation details.
- Unpublished pricing, credit entitlements, or offer-eligibility rules. Direct users to the live dashboard and public service documentation instead.
- Build caches, environment files, and development reports.

Retain required license notices and attribution, public product/support links, the intended public MCP endpoint, and information users need to install and authorize the integration.

## Before distribution

1. Run `python3 -B -m unittest discover -s tests -v` after rebuilding every affected ZIP. The tests inspect public text and archive contents and check that archives match their source packages. Pattern checks are a guardrail, not a guarantee that all sensitive content is detected.
2. Review every file in the exact upload artifact. Do not ZIP the repository root or include local evidence folders.
3. Review Git history and all refs before publishing a repository. Removing a file or adding an ignore rule does not remove previous commits. If sensitive information was committed, coordinate a history cleanup or publish from a clean repository; rotate any exposed credentials separately.
4. Review recorded demonstrations and reviewer materials separately. Share private credentials and evidence only through the provider's approved private channel.

Repository checks do not establish live authentication, provider approval, or release provenance. Inspect the exact committed source and final artifact before submission.
