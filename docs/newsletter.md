# Listmonk newsletter

## Services and credentials

- Listmonk admin: https://listmonk.builtwithdjango.com/admin/
- Existing Buttondown archive: https://newsletter.builtwithdjango.com (unchanged).
- CapRover host: `138.201.126.181`; apps `builtwithdjango-listmonk` and
  `builtwithdjango-listmonk-db`. Listmonk 6.2.0 uses the same verified image as
  Built with Bend; PostgreSQL 17 uses a separate private overlay network.
- Persistent volumes hold `/listmonk/uploads` and `/var/lib/postgresql/data`.
- Admin, database and SMTP credentials: Infisical `Openclaw / prod /
  /projects/builtwithdjango`, keys `LISTMONK_ADMIN_USER`,
  `LISTMONK_ADMIN_PASSWORD`, `LISTMONK_DB_PASSWORD`, `LISTMONK_SMTP_PASSWORD`.
- Mailgun: existing `mg.builtwithdjango.com` domain, independent
  `newsletter@mg.builtwithdjango.com` SMTP credential. Existing transactional
  credentials are not changed. STARTTLS at `smtp.mailgun.org:587` with TLS
  verification. Sender: `Rasul at Built with Django <rasul@builtwithdjango.com>`.
  This is outbound mail setup, not a new receiving mailbox.

## Website and consent

`NEWSLETTER_LISTMONK_URL=http://builtwithdjango-listmonk:9000` and
`NEWSLETTER_LIST_UUID` configure the public double-opt-in list. The site receives
no Listmonk admin credential. `NEWSLETTER_TRUST_PROXY=True` is only appropriate
behind the existing trusted CapRover proxy, which appends the real client IP.
Direct application ports must remain private.

All website newsletter forms use `POST /newsletter/`. Django validates CSRF and
email, checks a honeypot and a Redis-backed 10-request/IP/hour budget, and calls
the public subscription API without preconfirming anyone. Rate-limit cache
failure fails closed. IPs are stored only as keyed hashes for this budget.
Malformed provider responses, timeouts and unavailable configuration return 503
with the form retained. Success means a confirmation was requested, not that
mail was delivered or consent confirmed. The analytics event is
`newsletter confirmation requested`, without email/hash properties.

Listmonk owns confirmation and unsubscribe state. The public proxy blocks direct
`/api/public/subscription` and redirects subscription forms to the website, so
requests cannot bypass the app's abuse controls. Tokenized confirmation and
preferences URLs remain accessible. Preserve those proxy rules during updates.

Existing Buttondown contacts, historical Django email rows, archive DNS and
Buttondown draft tasks are retained. They are **not imported or synchronized**.
The legacy account-signup Buttondown integration also remains unchanged. Do not
assume this is a migration of the historical audience. No editorial schedule or
campaign is created. New Listmonk editions must be drafted and sent separately.
Use an unsubscribe link in every campaign; Mailgun continues enforcing its
existing domain-level bounce and complaint suppressions. Provider suppressions
are not mirrored into Listmonk by this setup. Open/click tracking is disabled in
Listmonk; shared Mailgun domain settings are preserved.

## Operations and rollback

Check HTTPS `/health`, running service replicas, and list opt-in settings. Test
homepage signup using an operator-owned inbox, verify receipt and SPF/DKIM/DMARC,
follow confirmation, then unsubscribe the test address. Never test on customers.

Backups use the host's existing `restic-main` discovery of PostgreSQL containers
and Docker volumes. Take an initial `pg_dump -Fc`, restore it into a disposable
DB, and verify an offsite restore before relying on the service. Before upgrades,
back up database/uploads and test restoring. Pin and track each Listmonk instance
in the control-plane service inventory; no automatic upgrades.

Rollback website signup by reverting this PR or disabling the configuration
(recoverable unavailable response). Preserve Listmonk data and old Buttondown
state; do not destroy volumes or downgrade an already migrated database.

## Newsletter appearance

The default Listmonk campaign template (ID 1, `Built with Django — editorial`)
uses the versioned source in `ops/newsletter/campaign.html`. It matches the
website's cream/green palette, original hexagon logo, and editorial typography.
It wraps HTML/Markdown campaign content; it does not change Buttondown archives,
confirmation emails, transactional templates, audiences, or sending schedules.

- Rubik/Nunito Sans are progressive enhancements from the site's self-hosted
  assets. Gmail/Outlook may use Segoe UI/Arial instead. Keep the fallback stack.
- Layout uses presentation tables, inline structural styles, a 600px maximum
  reading width, and a mobile padding adjustment. Content headings/links are
  styled by the template; avoid campaign body styles that override the palette.
- Preserve `{{ template "content" . }}`, `{{ UnsubscribeURL }}`, and
  `{{ MessageURL }}`. No tracking pixel is added by this template.
- Keep essential information as live text, not images. The logo remains optional
  when a recipient blocks images. Use absolute HTTPS image URLs and alt text.
- For changes: retrieve and privately back up the current template through
  `GET /api/templates/1`; check for running/scheduled/paused campaigns using it;
  then `PUT /api/templates/1` with `name`, `type: "campaign"`, and the source
  `body`. Read back the saved body and default flag, and render an existing
  **draft** using `GET /api/campaigns/{id}/preview`. Updating the template does
  not send that draft. Use existing authorized admin/API access, never store
  credentials or subscriber exports in this repository.
- Inspect the server-rendered result at mobile/desktop widths, including logo,
  unsubscribe/view links, long text and images. Browser previews do not prove
  rendering in Gmail, Apple Mail, Outlook, or forced dark mode; a specifically
  authorized test send is the next inbox check.
- Roll back by restoring the saved template fields with the same API call.
  Preserve the default flag and do not change campaign status. When branding
  assets change, update the absolute hashed image/font URLs here as well.

Verified 2026-10-12: template API compilation/readback and server-rendered draft
preview; no broadcast or test send accompanied this styling update.
