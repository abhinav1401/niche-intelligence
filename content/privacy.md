# Privacy Policy

**Niche Intelligence · Effective date: {{EFFECTIVE_DATE}}**

## Operator and contact

Niche Intelligence is a product currently operated by **{{OPERATOR_NAME}}**, an independent individual developer. Privacy questions, complaints and deletion requests: **{{PRIVACY_CONTACT}}**. Support: **{{SUPPORT_CONTACT}}**. The existing live application is a private research tool; this website is a separate, read-only demonstration. A possible future freemium service has not launched.

## This public demonstration

The dataset contains fictional creators, generated video metadata, synthetic statistics and precomputed examples of our own research metrics. It contains no real YouTube research database. This deployment does not use YouTube API Services, request YouTube or Google authorisation, retrieve live video data, call model providers, or accept file uploads. No YouTube video players, third-party thumbnails, advertisements, marketing analytics or payment processing are embedded by the application.

Your navigation, privacy acknowledgement, chart selections and filters exist only in a temporary Streamlit browser session. They are not written to the shared synthetic database. The application does not create a visitor account or maintain a persistent visitor profile. Session lifetime is controlled by the hosting platform and connection; closing a tab is not a guarantee of immediate platform-level deletion. Do not enter sensitive information into filters.

## Hosting and technical information

This demonstration is hosted on Streamlit Community Cloud, operated by Streamlit/Snowflake. To deliver and protect the website, the hosting platform may process IP addresses, browser/device information, request and connection information, cookies or similar technologies, usage/viewership statistics, and operational/security logs. Although the repository sets `browser.gatherUsageStats=false`, Community Cloud's [documented platform configuration](https://docs.streamlit.io/deploy/streamlit-community-cloud/status) overrides that setting to `true`. Hosting telemetry and [platform app analytics](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/app-analytics) therefore remain enabled in this deployment. The developer does not set hosting log-retention periods and does not promise that visits are anonymous, untracked or unlogged.

Deployment testing observed hosting telemetry requests to `data.streamlit.io` and `webhooks.fivetran.com`, as well as analytics services loaded by the hosting wrapper. These are separate from YouTube research requests; no YouTube research or paid-model service is used by this demo. The application does not add a marketing analytics SDK. This distinction does not mean that the hosting platform disables its own analytics or third-party processing.

See [Streamlit's Privacy Policy](https://streamlit.io/privacy-policy) and the [Snowflake Privacy Notice](https://www.snowflake.com/en/legal/privacy/privacy-policy/) for their practices and rights processes. GitHub stores the public demonstration source code; visiting repository links is subject to [GitHub's Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement). Platform processing locations, retention and transfers depend on those providers. No particular storage region or encryption-at-rest guarantee is made here.

## The separate private live application

The live application uses **YouTube Data API v3**, a YouTube API Service, for permitted research collection. It can process publicly available channel identifiers, names, descriptions, subscriber counts where visible, upload-playlist identifiers, video identifiers and links, titles, descriptions, publication dates, duration, public view/like/comment counts where available, thumbnails, categories and collection times. It does not download video files or comment text, and public competitor data does not reveal audience retention, engaged views or swipe-away rates.

Public observations are stored in local SQLite files on the operator's computer, with separate demo/live stores. Research labels, reviewed notes, ideas, coverage and audit records support the private workflow. Applicable live derived classification, analytics and recommendations remain gated pending actual policy acceptance/permission. No Google approval is represented by this demonstration.

The live system defaults to deletion of non-authorised public statistical observations after 30 days and refresh or deletion of stale metadata within that period, when maintenance runs. Longer statistical retention is disabled unless the existing setting records actual applicable permission, and is then capped at 36 calendar months. That conditional capability is not a claim of approval. Cached API payloads and run-response receipts have bounded retention; generated reports containing expired API material are redacted during maintenance. User-managed exports/backups require separate retention handling. The operator must run maintenance and manage copies; the application is not an always-on deletion service when closed.

API quota accounting records endpoint, request time, cost buckets, status, retries and research-run identifiers to enforce budgets and diagnose failures. It does not store API keys. Local accounting is separate from provider-reported usage and may not include other applications sharing the project. An optional read-only Google Cloud Monitoring integration requires separately authorised credentials; it is not connected to this public demonstration.

## Sharing, optional services and future changes

The live collector sends the relevant public search terms, resource identifiers and API credentials to Google/YouTube to fulfil API requests. Optional paid-model features, when explicitly configured in the private tool, send selected titles, truncated descriptions or creative briefs to that configured provider. No such model service is enabled here. Authorised Studio or other research exports may be manually imported privately; no public upload or Google sign-in flow is offered by this demonstration. If a future service introduces accounts, subscriptions, OAuth, additional analytics or new sharing, its notices and consent flows must be reviewed before those features launch. This document does not claim those planned features already exist.

## Requests and your choices

Contact **{{PRIVACY_CONTACT}}** with the relevant channel/video identifiers or a description of the information involved; do not send passwords or API keys. The operator will review access, correction, deletion or exclusion requests, verify identity where necessary, and apply relevant platform requirements and law. Applicable YouTube user-data deletion requirements include action as soon as possible and within seven calendar days for qualifying user deletion requests. This is a manual contact process, not a visitor deletion button or a claim that all hosting logs can be erased by the developer. Ask Streamlit/Snowflake directly about information they control. Deleting our stored information does not delete anything from YouTube.

This demonstration has no OAuth grants to revoke. If the private application's authorised access is used, Google's [account permissions page](https://security.google.com/settings/security/permissions) provides a revocation route in addition to contacting the operator; applicable deletion and revocation requirements still apply.

## YouTube and Google notices

The live application uses YouTube API Services and is subject to the [YouTube Terms of Service](https://www.youtube.com/t/terms), [YouTube API Services Terms of Service](https://developers.google.com/youtube/terms/api-services-terms-of-service), [Developer Policies](https://developers.google.com/youtube/terms/developer-policies), and any actually accepted [additional derived-metrics/storage policies](https://developers.google.com/youtube/terms/derived-metrics-policy). Google's processing is described in the [Google Privacy Policy](https://policies.google.com/privacy). External links open services with their own practices.

## Updates

The effective date identifies this version. Material changes to processing or any commercial launch require an updated notice and any required agreement before access. No compliance certification or legal jurisdiction is asserted by this notice.
