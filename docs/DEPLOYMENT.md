# Streamlit Community Cloud deployment runbook

## Current state

The owner explicitly approved publication and the operator/contact/policy details on 31 October 2026. Release checks and deployment verification are recorded in `VERIFICATION.md`; do not treat this runbook as proof of a successful deployment or a live URL.

The target selected by the owner is `abhinav1401/niche-intelligence`, branch `main`, entrypoint `app.py`. Only this independent deployment directory is eligible; do not add a remote to or push the private research project. Never upload its `.env`, `data`, exports or history.

## Before publication

1. Obtain explicit approval for the exact publication contents in `PUBLICATION_SUMMARY.md`, this target repository and public hosting.
2. Obtain final approval for the legal operator, public privacy/support contact, effective date and policy wording. Fill `site.json`; set `legal_review_confirmed=true` and `publication_approved=true` only after that approval. The owner approved these fields on 31 October 2026; drafts with missing details must not go live.
3. Rerun the full tests, browser checks, lint/type checks and `python scripts/security_check.py` **without** `--allow-draft`. Update the publication file/hash manifest after the approved contact changes. Inspect Git's staged file list and diff.
4. Check the target repository's ownership, visibility, existing history and branch protections while authenticated to the owner-authorised account. If history already exists, clone/fetch and preserve it; use a review branch or reconcile explicitly. Never use force push or assume it is an empty repository. If it contains private files/history, stop and choose an authorised clean repository/approach rather than make it public.
5. Inspect the entire history that would become public, including any destination history. The scanner covers this new local history; it cannot certify an uninspected remote.
6. Push only this reviewed deployment repository/branch. Authentication may require the owner to sign in to GitHub. Do not paste access tokens into source, URLs or terminal commands.

A hook in `.githooks/pre-push` restricts push destinations and checks release readiness. Enable it locally with `git config core.hooksPath .githooks`. Do not bypass it to publish a draft. Authentication and repository operations are deliberately not performed by the public application.

## Community Cloud settings

After approval and the authorised push:

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) using the authorised GitHub account. Connect only the necessary repository access.
2. Select **Create app → Yup, I have an app**.
3. Repository: `abhinav1401/niche-intelligence`; branch: `main`; file path: `app.py`.
4. Advanced settings: choose **Python 3.13**. The direct runtime dependencies are pinned in `requirements.txt`; no system packages or external model files are required.
5. **Leave Secrets empty.** No YouTube key, model key, OAuth token, private `.env` or real database belongs on this deployment.
6. Choose an available subdomain if desired; do not claim that a preferred name is available before deployment. Confirm intended public visibility, then deploy only with the owner's authorisation.
7. Verify a successful build and visit the actual HTTPS URL in a signed-out/incognito browser. Record that real hostname; a local preview does not prove Cloud success.

These instructions follow the official [Community Cloud deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), reviewed 31 October 2026. Community Cloud offers no special API access or policy approval, and its host may sleep inactive apps. Hosting terms, availability and limits remain the provider's responsibility.

## Mandatory post-deployment verification

- Main HTTPS URL works without a GitHub login, displays **Public Demonstration — Synthetic Data**, and offers all eight pages after the session acknowledgement.
- Direct `/privacy-policy`, `/terms-of-service` and `/about` links open without acknowledgement/login and contain approved operator/contact details and no placeholders.
- Desktop and 390px mobile navigation, all five Settings tabs, safe filters and chart controls work; workspace heading remains below Streamlit's header.
- No live mode, research/refresh worker, uploads, model calls, saving or quota reservations are possible. Check browser network logs: only hosting assets/traffic, no YouTube/API/model requests or embedded media.
- No secrets are configured, no private data files exist, and the deployed commit matches the reviewed contents.
- Record the repository/branch/commit, actual URLs, deployment date and test results. Do not submit guessed URLs to Google.

## Google application fields

Only after the actual hostname and routes are verified:

| Form field | Value |
|---|---|
| Primary Access URL | Actual deployed root HTTPS URL |
| Privacy Policy URL | Same verified hostname plus `/privacy-policy` |
| Terms of Service URL | Same verified hostname plus `/terms-of-service` |

Add `/about` as reviewer guidance where the form permits explanatory notes. State that this is a synthetic, read-only demonstration of a separate private application; the pending live-derived features are explained there. Do not describe it as the complete live system or as Google-approved.

## Maintenance

Update pinned dependencies and repeat isolation/browser checks before changes are deployed. Regenerate synthetic results only in an isolated offline build; never replace them with a copy of private research. Keep external exports, screenshots and local test logs out of the public repository. If the future product changes processing, accounts, payments or permissions, review the policies, security model and applicable YouTube acceptance before enabling them.
