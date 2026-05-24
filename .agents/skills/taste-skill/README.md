# Taste Skill Pack

This directory is now a multi-style frontend skill pack with a single main entrypoint.

## Start here

- Main router: `SKILL.md`
- Shared component system: `components/`
- Style-specific skills: one `skill.md` inside each style folder

The intended flow is:

1. the agent reads `SKILL.md` first
2. `SKILL.md` chooses the best style for the brief
3. the agent opens that style's `skill.md`
4. the agent uses `components/style-recipes.md` and the rest of `components/` to strengthen the build

## Included styles

- `brutalism`
- `cinematic-product`
- `dark-luxe`
- `dashboards`
- `editorial-premium`
- `gallery-minimal`
- `minimalism`
- `monochrome-modern`
- `premium-bento`
- `quiet-luxury`
- `soft`
- `soft-brutalism`
- `swiss-system`
- `warm-modern`

## Architecture

- `SKILL.md` is the router and style selector.
- Each style folder contains the actual style logic.
- `components/style-recipes.md` maps component patterns to the right style.
- The rest of `components/` acts as the shared research and inspiration library.

## Why this structure

- Users only need to install the folder once.
- The agent can pick the best style automatically.
- Shared component knowledge stays centralized instead of being duplicated everywhere.
- Style skills stay focused while still benefiting from the larger component library.

## Notes

- `_legacy` was removed from the production structure.
- `redesign` was removed for a later update.
- This is no longer a pure one-file-per-skill standalone system. It is now a coordinated pack.
