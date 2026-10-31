# Security and validation record

Prepared31 October 2026. This is an implementation review, not a penetration-test certification or a claim of Google approval.

## Boundary

Only this separate public-demo distribution is intended for publication. It contains a newly generated fictional database, frozen result files and selected presentation components. The private application, secrets, live data, production quota ledger, pipeline dependencies and private Git history are excluded. The source-of-truth production commit was `fcd418d`; reuse hashes are recorded separately.

The fixed public mode has no dotenv/secrets/environment-reading configuration path. YouTube, model, worker, mutation, import, maintenance and quota-reservation interfaces are explicit rejecting stubs. The actual research engines are not shipped. Browser widgets cannot invoke an unguarded alternative collector. No accounts, uploads, payments, shell-execution interface or scheduler exists.

The Store accepts only one fixed public fixture path and Demo mode. SQLite is opened read-only/immutable with query-only protection, disabled extensions and an authorizer rejecting writes, pragmas, ATTACH and dangerous functions. Rows/frame convenience methods cannot be used to bypass those restrictions. No runtime migration or fixture seeding occurs. Every bundled asset is checked against a fixed-name SHA-256 manifest.

The code uses Streamlit's normal escaped display for visitor text and static-only custom CSS. CORS and XSRF protection stay enabled; static file serving is disabled. Optional usage statistics are disabled for local runs; Community Cloud overrides `browser.gatherUsageStats` to `true`, so provider telemetry remains active on that host. This is explicitly disclosed in the Privacy Policy. User-facing error details are redacted. Native Streamlit header clearance is preserved. The app does not promise platform-wide CSP headers, deny-all hosting egress, log anonymity or encryption-at-rest settings it does not control. Host delivery and operational/security logging are described in the Privacy Policy.

## Checks completed

- Initial isolation/dashboard suite: 44 passed, including direct service calls, constructor bypass, raw SQL writes, ATTACH/extension attempts, immutable data hashes, secret environment sentinels, frozen synthetic exports and all original dashboard renderers. A precomputed datetime deserialisation issue was corrected before this pass.
- Runtime installed in a fresh separate Python 3.13 environment from the three pinned direct dependencies. `pip check` passed; the app launched with no `.env`, dotenv package, key configuration or sibling imports.
- The synthetic fixture build ran with outbound connections forbidden. Application unit/interaction tests also block socket connections and check asset hashes before/after each case.
- Every data-source marker in channel/video/snapshot tables is synthetic_demo. No real creator/video URLs or remote thumbnails are included. No provider reconciliation/import data is bundled.
- Working-tree scanner found no token/key/private-home-path pattern. It also inspects staged bytes and all blobs/commit metadata in this independent Git history; it suppresses matching values in output. It is a heuristic, not proof against every secret format.
- Draft scanning is allowed locally. Release scanning intentionally blocks missing legal details and publication approval. The pre-push hook additionally restricts the owner-designated remote.

Final test/browser/history/source-preservation results are recorded in `VERIFICATION.md` after the final checks. Screenshot capture previously encountered an automatic approval-review usage-limit failure; that action did not execute and was not bypassed. Browser DOM/render checks are separate from a completed public Cloud verification.

## Remaining release conditions

No push or deployment is authorised yet. Complete final owner/contact/legal approval, inspect the target repository's actual history and authenticated account, pass the release gate, obtain explicit publication approval, then deploy and verify real HTTPS/legal URLs in a signed-out browser. Cloud-hosted behaviour, logs, availability and platform configuration must be checked after deployment. No public Cloud verification has occurred at this stage.
