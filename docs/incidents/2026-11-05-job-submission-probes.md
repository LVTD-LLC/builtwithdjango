# Job submission probes — 2026-11-05

## Findings and limits

- The nginx access-log slice for 15:30–15:39 UTC contains 178 POSTs to
  `/jobs/new`: 47 redirects after accepted submissions, 108 invalid-form
  responses, and 23 CSRF rejections. Other scanner requests probed SQL
  expressions and common database-file paths.
- Read-only database inspection for 15:25–15:50 UTC found 47 new job records,
  all unapproved and unpaid. The public list/detail queries require approval.
- Captured PostgreSQL logs from 15:25 UTC onward contain no SQL-error markers.
  Submission persistence uses the ORM rather than interpolated raw SQL.
  These checks found no evidence of SQL execution; they do **not** constitute
  an exhaustive forensic exclusion of compromise or establish request timing
  for time-based probes.
- Four checkout 500 responses were also present. A production diagnostic
  reproduced Stripe HTTP 401 with an expired API key. Price selection and a
  checkout dry run with the provider call stubbed succeed. No payment was
  made and no successful checkout session was created by the diagnostic.
  This credential issue is separate from SQL-injection prevention and remains
  an operational follow-up; do not substitute another product's key.
- Sentry API access returned 403, so historical exception details were not
  available through that credential. The checkout finding comes from a
  current production reproduction, not recovered historical Sentry events.

## Evidence handling

Raw access logs, database/web log captures, the read-only job-record snapshot
and inspected proxy configuration are retained in a root-only directory on
production: `/captain/data/private-incidents/bwd-2026-11-05/`.
A private operator copy and checksums were also retained. Raw form text, client
addresses and credentials are intentionally excluded from this repository.
No incident records were approved, published or deleted during the response.

## Mitigation

See [job abuse controls](../../TECH.md#job-submission-abuse-controls).
Production nginx overwrites `X-Real-IP`; the application web service has no
published direct port. Turnstile does not require moving DNS to Cloudflare.
The configured Cloudflare token lists no `builtwithdjango.com` zone, so no
zone-level WAF/DNS changes were made. Shared-cache application throttling is
used alongside hostname-bound Turnstile verification.

Deploy web and worker revisions together. Validate live challenge rendering,
rejection without database/queue side effects, 429 handling and normal worker
execution. Keep the existing unapproved incident records as evidence until a
separately approved cleanup.
