# Changelog

All notable changes to this project are documented by date, newest first.
Each `YYYY-MM-DD` heading groups all changes for that day by type, without
release versions or an Unreleased section. Historical dated entries retain
their recorded dates; previously undated entries use their Git history dates.

## Types of changes

**Added** for new features.
**Changed** for changes in existing functionality.
**Deprecated** for soon-to-be removed features.
**Removed** for now removed features.
**Fixed** for any bug fixes.
**Security** in case of vulnerabilities.

## 2026-09-24

### Added

- Dry-run-first `cleanup_duplicate_project_domains` command with domain/keeper selection and non-deleting deactivation of legacy duplicates.

### Changed

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
