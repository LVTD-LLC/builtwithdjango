# Built with Django Design System

## Source of truth

This file describes the intended visual and interaction language for humans and
coding agents. The executable color tokens, spacing, radii, shadows, and shared
`bw-*` component classes live in `frontend/src/styles/tailwind.css`. Update that
file and this guidance together when the system changes.

`tailwind.config.js` defines content discovery, safelisted dynamic classes, and
the typography/forms plugins. Reuse the existing component classes before
adding page-specific Tailwind combinations.

## Direction

An independent editorial directory: OpenAlternative's discovery structure,
Typewolf's screenshot-led publication, and Supabase's restrained light UI.
Projects and the blog lead; jobs, tools, and the podcast archive live in the
footer. Reference rationale and measurement limits: `docs/redesign-2026-10.md`.

Use a warm cream canvas, white screenshot frames, charcoal-green text, fine
neutral borders, and one dark-green action color. Self-hosted Rubik (600) supplies
playful headings; Nunito Sans serves body text, forms and controls (option 5,
selected by Rasul). Keep code in monospace. Font provenance and OFL licenses
are in `frontend/src/fonts/`; reuse the font tokens, never a remote font embed.
Avoid decorative gradients and motion.

## Visual principles

- Lead with real screenshots and community content rather than abstract
  decoration.
- Use the `bw-bg`, surface, ink, border, primary, and accent token family;
  do not introduce a new palette for one page.
- Prefer bordered surfaces and restrained shadows. Reserve stronger elevation
  for menus and meaningful hover states.
- Use green for navigation, primary actions, and identity; use pale green for quiet emphasis and featured labels.
- Keep headings measured and editorial, with readable body copy and generous line
  height.
- Avoid generic SaaS gradients, glassmorphism, excessive pills, decorative
  metric cards, and repetitive feature grids.
- Do not add decorative eyebrow labels or repeated arrow glyphs. Use direct
  headings; keep useful metadata and advertising disclosure in normal text.

## Layout

- Use `bw-container` for focused content and `bw-container-wide` for showcase
  grids and broader landing sections.
- Use `bw-section` for consistent vertical rhythm.
- Project discovery is screenshot-led: cards should keep stable media ratios,
  concise descriptions, and clear external/project actions.
- Forms should remain narrow enough to scan, with visible labels, inline errors,
  and clear primary/cancel actions.
- On mobile, collapse navigation and grids cleanly, keep controls touch-friendly,
  and avoid horizontal overflow from URLs, titles, or metadata.

## Components

- **Header:** use the original Django hexagon logo, not a text monogram.
  Sticky, opaque, separated by a border; navigation
  must remain keyboard- and mobile-accessible.
- **Buttons:** use `bw-button` with the existing primary, secondary, or accent
  variants. Destructive actions need an explicit, accessible danger treatment;
  add a shared variant before repeating page-local styles.
- **Cards:** use `bw-card`; project cards use the dedicated
  `bw-project-card*` structure and should not hide screenshots behind ornament.
- **Menus:** use `bw-menu-panel` and `bw-menu-item` with explicit expanded
  state and reliable outside-click behavior.
- **Forms:** visible labels, high-contrast focus state, helpful validation, and
  no placeholder-only instructions.
- **Empty states:** explain what is missing and offer the next useful action.
- **Status and sponsorship:** featured project cards use a pale-green surface,
  green outline, and high-contrast Featured badge. Label state in text; never
  rely on color alone.

## Interaction and accessibility

- Target WCAG AA contrast and preserve the global `:focus-visible` treatment.
- Keep the skip link and semantic landmarks in the base template.
- All icon-only controls need an accessible name.
- Screenshots need useful project-specific alt text; decorative images use an
  empty alt attribute.
- Preserve reduced-motion behavior and avoid motion that is required to
  understand state.
- Turbo, Stimulus, and Alpine enhancements must leave forms and navigation
  understandable when JavaScript is delayed or unavailable where practical.

## Product guardrails

- Do not visually prioritize ads or monetization above project discovery,
  learning, or community proof.
- Do not remove sponsorship and commercial surfaces during redesign without an
  explicit product decision; integrate them clearly and honestly.
- Owners need an obvious edit affordance on their project, while anonymous and
  unrelated users must not see misleading ownership controls.
- Pending or missing screenshots need a deliberate fallback, not a broken image
  or collapsed card.
