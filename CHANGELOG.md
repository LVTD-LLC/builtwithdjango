# Changelog

All notable changes to this project are documented by date, newest first.
Each `YYYY-MM-DD` heading groups all changes for that day by type, without
release versions or an Unreleased section. Historical dated entries retain
their recorded dates; previously undated entries use their Git history dates.

## 2026-10-08

### Added
- Enabled IndexNow ownership verification and automatic public URL notifications after deployment and hourly, with retryable change/removal checkpoints and full sitemap timestamps.

### Changed
- Made open-source projects and practical guides easier to discover from the project directory, clarified source-code filter options, and added a short workflow for learning from a real project's code.

## 2026-10-07

### Fixed
- Corrected the authentication tutorial’s custom-user explanation, account URL wiring, allauth settings, migration guidance, and development command; replaced the weak-password walkthrough with validator-respecting instructions.

## 2026-10-06

### Changed
- Applied the selected Rubik headings and Nunito Sans body/UI typography across the app, using locally hosted variable fonts with bundled open-font licenses.
- Restored the original navbar logo, removed decorative eyebrow labels and repetitive homepage slogans/arrows, and made featured projects more visible with a green panel and clear badge.
- Redesigned the app with a cream-and-green editorial system, framed project screenshots, readable blog layouts, consistent forms, and responsive navigation focused on Projects and Blog.
- Simplified the homepage to projects, recent posts, and newsletter signup; moved jobs, tools, and the podcast archive to footer navigation while retaining existing URLs.
- Replaced floating advertisements with an in-flow labeled sponsor strip and the scripted webring panel with a simple directory link.
- Added server-rendered project and blog search, post-type filtering, clear reset controls, and result counts.
- Unified all published post categories under `/blog/`; redirected the legacy articles index to it and removed duplicate navigation and sitemap links.
- Unpublished the 12 owner-selected articles from public pages, RSS, and the sitemap while preserving their Markdown sources as drafts. Kept all 13 requested tutorials and the three unlisted monthly updates unchanged.

### Fixed
- Improved keyboard focus for code blocks and native like dialogs, corrected code contrast, and styled password-recovery screens consistently.
- Applied the public non-spam project boundary to homepage listings, removed the tablet navigation gap, and corrected project form label associations.
- Displayed the corrected article’s comparisons as readable lists in the existing Markdown renderer.
- Corrected the ContentTypes, signals, and query-expression article: document primary-key and integrity limits, use a swappable-user signal receiver, and distinguish F updates from Q predicates and transaction guarantees.

## 2026-10-05

### Changed
- Clarified the Django secret-key generator's search title and description, aligned its structured metadata, and recorded its content revision date in the sitemap. Tool behavior is unchanged.

## 2026-10-04

### Fixed
- Corrected the cursor guide’s unsupported named-cursor example, ORM window-function claim, and unverified import-speed benchmark; clarified backend and transaction limits with current Django references.

## 2026-10-03

### Fixed
- Maker profiles now link only to published, active, non-spam projects, preventing cards that lead visitors to unavailable listings.

## 2026-10-01

### Fixed
- Made the existing Django articles index discoverable from the Guides hub and shared Explore footer.

## 2026-09-30

### Fixed
- Corrected the frontend comparison's Built with Django stack, Next.js authentication, and Cookiecutter Django integration claims, with primary-source links.

## Types of changes

**Added** for new features.
**Changed** for changes in existing functionality.
**Deprecated** for soon-to-be removed features.
**Removed** for now removed features.
**Fixed** for any bug fixes.
**Security** in case of vulnerabilities.

## 2026-09-29

### Fixed

- Kept the power-features article's generic-relation explanation within narrow mobile screens.

- Corrected unsupported survey and benchmark claims in the Django power-features article, with documented trade-offs and runnable examples.

## 2026-09-28

### Fixed

- Applied analytics URL redaction recursively to SDK attribution and middleware paths, including account recovery URLs.
- Restored PostHog browser ingestion by preserving its public ingestion token; joined browser/server identities, reset identity after logout, and deduplicated retried Stripe analytics events.

### Added

- Added Web Vitals, form engagement and validation, scroll milestones, and project publication/screenshot failure analytics with masked replay, secret-safe URLs, and no exception-local capture.

### Changed

- Added numbered project pagination with nearby and end-page links, preserving active filters and page-specific canonicals while shortening discovery paths.

## 2026-09-27

### Fixed

- Repaired three article links to the existing GitHub authentication guide instead of nonexistent social-auth URLs.

## 2026-09-25

### Fixed

- Replaced the performance guide’s unsupported CDN benchmark and nonexistent study citation with official Django static-file deployment guidance.

## 2026-09-24

### Added

- Dry-run-first `cleanup_duplicate_project_domains` command with domain/keeper selection and non-deleting deactivation of legacy duplicates.

### Changed

- Reverted PR #120's domain-level project restrictions and cleanup command: shared hosts such as GitHub can contain distinct projects. Exact-URL uniqueness remains unchanged; no project records were cleaned up.
- Retired the domain-lock model while preserving applied migration history and its unused table for rolling-deployment compatibility.
- Moved all 28 blog posts into version-controlled Markdown with preserved URLs, dates, tags, and icons; blog pages, homepage guides, RSS, sitemap, and authenticated reads now use repository content.
- Retired database blog publishing: API writes return 405 and legacy admin records are read-only, with original data retained for rollback.
- Grouped the changelog by date instead of release version and updated contributor guidance to keep future entries date-based.

### Fixed

- Prevent duplicate project domains across submissions and URL edits, including URL variants and concurrent submissions, before notifications or scraping are queued.

## 2026-09-23

### Fixed

- Restored broken article links to the guides, project showcase, secret-key generator, and HTML formatter with permanent redirects to their existing pages.
- Excluded the sign-in-only project submission form from the public sitemap while preserving its login and submission flow.

## 2026-07-28

### Added

- Let signed-in project submitters update their linked listing metadata and screenshot.

## 2026-06-13

### Fixed

- Returned a signup form error instead of a server error when duplicate username submissions race validation.

## 2026-06-12

### Changed

- Rebuilt project likes to render counts from annotated project queries and use a single toggle request instead of per-card like API reads.

## 2026-06-11

### Fixed

- Reduced noisy Sentry errors when direct project HTML fetches are blocked but the Jina Reader fallback succeeds.

## 2026-05-26

### Added

- Restored production PostHog activation from the Built with Django public project key and added explicit checkout return/cancel analytics events for job, sponsored job, and Django Developers checkout flows.

### Changed

- Stopped capturing noisy project-like API requests in PostHog request analytics and session recording network logs while keeping explicit like/unlike events.

## 2026-05-25

### Changed

- Simplified the landing page by removing the hero showcase, proof strip, and quick-link card band.
- Expanded the home page project and guide sections to show six items and gave guides and jobs full-width sections.

### Fixed

- Made the bottom-right desktop ad use a solid surface instead of an opacity fade.

## 2025-12-08

### Added

- API endpoint to publish posts.
- Page to show all articles
- Proper DRF Auth
- RSS

## 2025-02-13

### Added

- Support for getting ip address of user and passing it to buttondown
- Support for logfire
- Version usage for buttondown
- Added admin command to unpublish projects
- Added Jina Reader API and Pydantic AI to programmatically analyze newly submitted project

### Changed

- better Logfire and Sentry support
- updated a bunch of libraries which cause a few failures. so fixed all of these.
- buttondown api version we are using

### Removed

- Usage of opentelemetry directly
- Kolo and Posthog Sentry middleware

## 2025-02-08

### Added

- Project search functionality with autocomplete
- Pagination for projects list page

### Fixed

- Visit Website button is correct vertically aligned.

## 2025-01-15

### Added

- Testimonials on Ad pagee

### Fixed

- Image width for Testimonial

## 2024-06-12

### Added

- Added a task to check if project is active.

## 2022-07-10

### Added

- Complete Redesign.
- Ability to comment on guides.

## 2022-04-07

### Added

- Ability to sort projects based on # of likes and comments.

## 2022-02-11

### Added

- Added a bunch of fields to users model.
- Added support for Django_q
- As a consequence added a feature where screenshot is added automatically
- Moved email notifications to background tasks

### Changed

- Only registered users can now submit projects.
- We will now slowly move away from the "Maker" model towards users being the makers.

### Removed

- Removed Support Button for now.

### Fixed

- Fixed the email that gets sent to me when someone submits a project.

## 2022-02-07

### Added

- Exit Intent Email Form

### Fixed

- Paid job posts show up first now
- Job posts more than 2 months old are now removed

## 2022-02-04

### Added

- Filter Field with "Is Open Search".
- Remote boolean and Timezone fields to Job Posts.
