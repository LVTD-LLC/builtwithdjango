# October 2026 redesign

## Direction and scope

Rasul authorized a first production pass across the app on October 6. Projects
and the blog are primary. Jobs remain available for future activity; podcast
episodes remain an explicitly labeled archive. Tools retain their routes and
footer discovery. No content or production records are deleted.

TastefulKit MCP references (screenshots and DESIGN.md inspected):
- OpenAlternative — https://openalternative.co/ — native discovery controls,
  compact metadata, clear catalogue hierarchy.
- Typewolf — https://www.typewolf.com/ — editorial serif headings, warm canvas,
  framed project screenshots and reading-first article lists.
- Supabase (light-theme reference) — https://supabase.com/ — restrained green,
  fine borders, consistent controls. Not its marketing-page structure.

The implementation uses Django templates and existing Tailwind 3. No new browser
framework, font service, image generation, or component dependency is needed.

## Information architecture

- Always-visible Projects / Blog links at all widths; no hamburger dependency.
- Submit project and account access on desktop; account access, primary browsing,
  and contextual/footer submission links on mobile.
- Homepage: short introduction, six projects, six latest published posts,
  newsletter. No empty job section or podcast promotion.
- Native GET search/filter forms for projects and posts, with reset and empty
  states. Filtered pages retain canonical destinations and use noindex,follow.
- Job board, developer directory, both tools, archive, advertising, submissions,
  and source repository remain reachable from the footer.
- Advertising is a clearly labeled, in-flow footer strip, not a floating panel.
- Webring discovery becomes a normal directory link; removes shadow-DOM polling
  and runtime restyling of a third-party widget.

## Measurement and limits

Read-only PostHog project 52923 query, rolling 30 days on October 6, found
recorded pageviews including project index (341), blog index (41), jobs index
(29), secret-key tool (25), and formatter (22). Counts may include automated
verification and are not claimed as unique human demand. Some `$pathname`
properties contain full URLs, so URL normalization must precede section-level
comparisons. This is directional evidence for retaining tool URLs, not deleting
them. No Search Console/OpenSEO or conversion-uplift claim is made.

## Reliability

Homepage project query now follows the published/active/non-spam boundary.
Server-side search preserves the same boundary and existing like ordering.
Native controls work without JS. Existing auth, ownership, forms, analytics
initialization, URLs, canonical metadata, sitemaps, and publication workflows
remain in place. No migrations are needed.

## Rollback

Revert this redesign PR and redeploy through the normal master-branch workflow.
There is no data migration or content deletion to reverse.

## Verification

- 157 Python tests pass, including public visibility, server search/filtering,
  account-recovery shell, and keyboard-reachable Markdown regression coverage.
- Six analytics JavaScript regression tests pass.
- Node 22.23.3 production build passes; no new runtime dependencies.
- Django system check and migration-drift check pass.
- Initial browser sweep: 52 public page/viewport combinations (320, 390, 768,
  1440 CSS pixels), with explicit CDP viewport verification. No page overflow.
- Browser findings fixed: code colors, keyboard-scrollable code, native auth
  dialog/focus restoration, and project editor button contrast. The configured
  Markdown library is explicit because several legacy apps use the same name.
- Signed-in browser checks use an isolated SQLite fixture account and public
  screenshot copies, not production accounts or writes.

Automated accessibility checks are bounded checks, not a claim of full WCAG
certification. Production rollout and final live verification are recorded in
this PR's delivery report.
- Final secondary-page sweep: 16 additional desktop/mobile checks (makers,
  advertising, terms, support, newsletter, job submission, developer pricing,
  invalid email confirmation) passed status, layout, and axe checks.
- Local authenticated flows passed: login, project submission validation, owner
  edit form, profile, logout confirmation, password change, reversible like
  toggle, and dialog Escape/focus restoration. No production writes used.
- CI initially exposed a test-fixture dependency on a locally built Webpack
  manifest. The new Python rendering tests now stub bundle tags like an
  isolated backend test; real assets remain verified by build/browser checks.
