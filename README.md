# Niche Intelligence — Public Demonstration

Live read-only demonstration: [Niche Intelligence](https://niche-intelligence-5enuxhsymfv7vrlcmhd5hr.streamlit.app/). Direct [Privacy Policy](https://niche-intelligence-5enuxhsymfv7vrlcmhd5hr.streamlit.app/privacy-policy), [Terms of Service](https://niche-intelligence-5enuxhsymfv7vrlcmhd5hr.streamlit.app/terms-of-service) and [reviewer information](https://niche-intelligence-5enuxhsymfv7vrlcmhd5hr.streamlit.app/about) are publicly accessible. All research results are synthetic. No YouTube key, private research or paid model service is deployed.

**Synthetic data. Read-only. No live YouTube connection. Not yet published.**

This is an isolated public-demo distribution of the actual Niche Intelligence dashboard. It reuses the original styling, research-page components and quota-monitor presentation. The full application remains a separate private local tool. No private Git history, credentials or production data was copied.

## Run locally

Use Python 3.13 and a dedicated environment:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8503
```

Do **not** create `.env` or `secrets.toml`. No environment variables, API keys, paid models or sibling application are required. `PUBLIC_DEMO_MODE=True` is fixed in `nicheintel/public_mode.py`, with a matching declaration in `site.json`. Environment configuration cannot switch this distribution into a live application.

Open the localhost address printed by Streamlit. Privacy, Terms and About pages are accessible before the temporary session acknowledgement. All eight research pages, five Settings tabs, safe filters, charts and synthetic downloads are available after acknowledgement. Draft legal details are clearly identified locally; the release gate blocks publication until the owner approves complete details.

## Read-only design

- Frozen analyses from the original deterministic fixture: 24 fictional creators, 1,920 videos, 12 subject clusters and 144 curated concept briefs. These are not real YouTube results.
- `assets/synthetic.sqlite3` is opened with `mode=ro`, `immutable=1`, `query_only=ON`, disabled extension loading and an SQL authorizer that rejects writes, ATTACH, pragmas and dangerous functions. The Store accepts only that fixed asset path and Demo mode.
- All outgoing API, model, collection, research-worker, import, maintenance, quota-reservation and persistent-edit entry points reject direct calls. Live implementations are not shipped.
- The public server reads precomputed result files; it does not run the research or analytics engines. Visitors cannot start even an offline collection worker. The workflow slider only explains an already completed synthetic example.
- Visitor filters and acknowledgement live in temporary Streamlit session state. No visitor changes are written to the shared fixture. No upload, account, payment or scheduling function exists.
- Assets have a SHA-256 manifest. No production `.env`, database, quota ledger, competitor records, private filesystem paths or full-app Git history belong in this repository.
- The hosting framework necessarily serves web traffic and may keep operational logs. This is not a network sandbox for Streamlit itself or a promise of anonymous hosting. Read the Privacy Policy.

## Publication status and destination

Owner-designated destination: **https://github.com/abhinav1401/niche-intelligence**, branch **main**, entrypoint **app.py**. This local repository has not been pushed. The destination's existing history/permissions must be inspected after authorisation; never force-push over existing work.

No public HTTPS app URL exists yet. Expected routes after actual deployment are `/`, `/privacy-policy`, `/terms-of-service` and `/about`. They must be verified against the real deployed hostname before entering Google's form.

The owner explicitly approved publication and the policy details on 31 October 2026. `site.json` contains only the approved public operator name, privacy/support contact and effective date. No private Cloud-account contact, address or credentials are included.

## Checks

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy nicheintel
.venv/bin/python scripts/security_check.py --allow-draft
# Release gate: must pass after the approved site details and manifest are complete:
.venv/bin/python scripts/security_check.py

# With a separate running local demo and installed Chrome:
PUBLIC_DEMO_TEST_URL=http://127.0.0.1:8503 \
  .venv/bin/python -m pytest tests/browser/test_public_demo.py -q
```

The security scanner inspects the working deployment tree, staged bytes and all blobs in this separate Git history. It suppresses matched secret values. A pre-push hook restricts the designated remote and runs the release gate when `chmod +x .githooks/pre-push` and `git config core.hooksPath .githooks` have been run. Browser uploads do not preserve executable bits, so cloned copies need that chmod step. It is a safeguard, not a substitute for explicit human approval or a complete security audit.

See [deployment instructions](docs/DEPLOYMENT.md), [publication contents](docs/PUBLICATION_SUMMARY.md), [demo versus private app](docs/DEMO_VS_PRIVATE.md), [security and verification](docs/SECURITY.md), and [legal review checklist](docs/LEGAL_REVIEW.md).
