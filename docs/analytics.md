# PostHog analytics

Project: Built with Django (52923), https://us.posthog.com/project/52923.
Existing event names intentionally stay unchanged for historical reports.

## September 28 audit

Seven-day baseline: 63,736 `request completed`, 11,715 `project viewed`,
17 `project submitted`, no `$pageview`, and one `$pageleave`. Server events
include crawlers and **must not** be used as browser traffic/unique visitors.
The browser SDK loaded successfully but ingestion returned HTTP 400 because
`property_denylist` removed the SDK's **public ingestion token**. Removing that
entry produced HTTP 200 with the same SDK and project. Never put `token` in
this list; redact application credentials/URLs, not the SDK protocol field.
Session replay was also disabled at the project level.

## Coverage

| Journey | Browser intent/experience | Server outcome |
|---|---|---|
| Discovery | `$pageview`, `$pageleave`, autocapture, navigation, CTAs, outbound links | project/post/job/developer/podcast views, search results |
| Engagement | 25/50/75/100% scroll milestones, heatmaps, dead clicks, Web Vitals | request status and duration |
| Submission/profile | form started/submitted, native validation blocked | project submitted/updated, profile updated, form validation failed |
| Publication | — | project published after commit; screenshot fetch failures |
| Accounts | identify before initial pageview, reset on anonymous page after logout | signup/login/logout/email confirmation |
| Newsletter | form intent | newsletter subscribed (local submission, not provider delivery confirmation) |
| Payments | checkout intent/return | verified Stripe events; deterministic UUID per event name + Stripe event ID |
| Failures | unhandled browser errors, masked replay | server exceptions (without locals), HTTP 5xx as request failed |

The site currently uses full-document navigation, not a loaded Turbo runtime.
SDK `history_change` capture covers initial pageviews and history changes.
Do not add a second manual pageview handler. If enabling Turbo later, move
identity/page context refresh into its navigation lifecycle and test logout.

## Identity and privacy

- Authenticated IDs remain `str(user.pk)` in both runtimes.
- Server events read the SDK's existing project-specific cookie for anonymous
  distinct/session IDs, plus existing form/header hints. These are untrusted
  analytics hints, never authorization. Malformed/oversized cookies are ignored.
- Without a browser cookie, session hash or request-local random IDs replace
  IP/user-agent fingerprinting. Anonymous request events are personless.
- Browser person profiles are `identified_only`; no profile per crawler.
- Replay masks all text and inputs, blocks form controls/private elements,
  excludes bodies/headers, and omits noisy like polling. Keep these client-side
  protections even when changing project-level settings.
- URL credentials, sensitive query values, fragments, and account/user path
  tokens are redacted. Form events contain structure/error codes, never values.
- Server exception locals are disabled; screenshot logs no longer print the
  credential-bearing provider URL. Existing authenticated profile properties
  remain unchanged server-side.
- Existing search terms and public project metadata remain collected. Account
  recovery, private forms, source code, tokens, and passwords are not engagement
  payloads. Do not enable replay network body/header or console capture.

## Verification and operations

Run `npm run test:analytics`, `pytest`, and `npm run build`. Verify browser
HTTP ingestion success **and** query arrival, not merely `posthog.__loaded`.
Browser automation is filtered as bot traffic by the SDK; disable that filter
only in an isolated synthetic test tab, never in shipped configuration.
Label probes `synthetic=true` with a unique `audit_id`; exclude from reports.

Post-deploy: visit home/projects/blog and form pages at desktop/mobile sizes,
verify one initial pageview per document, form/scroll events, masked replay,
and session/identity continuity between browser and server. Do not fabricate
real signups, submissions or payments to test analytics.

Daily ingestion health query (management API, personal key server-side only):

```sql
SELECT event, count(), max(timestamp)
FROM events
WHERE timestamp > now() - INTERVAL 24 HOUR
GROUP BY event ORDER BY count() DESC
```

Check browser `$pageview`, server `request completed`, error volume, and
web-vitals/replay arrival separately. A quiet conversion event is not proof of
failure. No recurring health job is installed by this change. Python SDK queue
retries are bounded; deterministic Stripe UUIDs prevent replay inflation but
are not a durable delivery outbox. Future work can add an outbox if guaranteed
analytics delivery becomes a requirement.

Rollback: revert the PR and deploy prior image. Replay can independently be
disabled with project `session_recording_opt_in=false`; no database changes.
