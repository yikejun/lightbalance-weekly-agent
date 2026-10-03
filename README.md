# LightBalance personal weekly Agent

Review training and recovery from an explicitly shared 28-day snapshot. The model decides whether to maintain, adjust or request more information using supplied evidence. Code validates the structured result, tracks one attempt per week and requires a user decision. This is not medical advice or a complete guideline review.

This distribution contains code, an exercise-name catalog and sourced evidence summaries. It does not contain user records, photographs, accounts, credentials, signing certificates or server configuration. No iOS app binaries are included.

Python 3.11+; test using `python3 -m unittest discover -v`.

For ChatGPT plan usage, review the official requirements:
- https://developers.openai.com/siwc/token-sharing-open-source
- https://developers.openai.com/siwc/token-sharing-open-source/self-hosted-vms

Each person operates their own runtime and authorizes their own eligible account. Do not offer a shared hosted service or reuse another user's credentials. Eligibility and account scope must be established before setting PLUS_DEPLOYMENT_ELIGIBILITY_CONFIRMED=yes. Publishing code is not account approval.

Extract `plus-bridge-source.zip` to obtain the `Plus/` directory. The optional Plus bridge uses the included official Sign in with ChatGPT devkit. See Plus/devkit/LICENSE and THIRD_PARTY_NOTICES.md for separate third-party licensing. Install its dependencies with `npm ci` in Plus. Mac login uses Keychain-backed encryption and a system browser; server encryption uses systemd credentials. Never publish runtime/ or encrypted credential files. Keep a distinct persistent host ID for a VM and follow the official credential-transfer workflow.

Provider configurations:
- WEEKLY_PROVIDER=disabled: no inference.
- WEEKLY_PROVIDER=api: set WEEKLY_API_KEY_FILE and WEEKLY_MODEL; billed separately.
- WEEKLY_PROVIDER=plus: set WEEKLY_BRIDGE_TOKEN_FILE and an account-available WEEKLY_MODEL, with the eligibility guard satisfied.

The HTTP endpoint binds only 127.0.0.1:8789 and needs a strong WEEKLY_CLIENT_TOKEN_FILE. Use your own HTTPS reverse proxy. Consent defaults off; upload snapshots explicitly. Run a weekly job with `python3 weekly_service.py --run --database <private-path>`. Scheduler setup, mobile client and HTTPS hosting remain the operator's responsibility.

Endpoints (Bearer authentication): GET /v1/inbox; POST /v1/consent, /v1/snapshot, /v1/generate, /v1/reports/<ISO-week>/decision. Missing or stale data does not trigger inference. No automatic retry or automatic plan publishing.

On macOS, compile the local credential helper inside `Plus` with `swiftc keychain-helper.swift -o keychain-helper` before signing in. The helper source is MIT licensed; the bundled SDK retains its own license.
