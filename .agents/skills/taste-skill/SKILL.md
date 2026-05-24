---
name: design-taste-skill-pack
description: Master router for the Taste Skill Pack. Reads the user brief, chooses the most suitable UI style, then delegates to the matching style skill plus the shared components library.
---

# Taste Skill Pack Router

You are the entrypoint for this entire frontend taste system.

Use this file first. Do not jump straight into a style folder before making a style decision.

## 1. Core job

Your job is to:
- read the user's brief
- infer the strongest fitting visual direction
- open the matching style skill
- use the shared component library and style recipes to strengthen the result
- produce a premium output without generic AI UI habits

Default stack: React or Next.js. Unless the user explicitly requests another framework or stack, assume React/Next.js conventions by default.

If the user already names a style, use that style unless it directly conflicts with the brief.
Treat an explicit style request as a strong override, not a weak hint.

If the user does not name a style, you must choose one yourself. Do not ask the user to pick from a long list unless the brief is genuinely split across very different directions.

## 2. Required workflow

Follow this sequence every time:

1. Read the prompt and identify:
   - product type
   - brand mood
   - target audience
   - desired energy level
   - content density
   - whether the page should feel editorial, technical, premium, soft, cinematic, strict, or experimental
2. Check whether the user explicitly requested one of the pack styles.
3. If yes, route directly to that style folder.
4. If not, select the single best-matching style folder from this pack.
5. Read that style's `skill.md`.
6. Read `components/style-recipes.md` and use the matching section for that chosen style.
7. Pull extra ideas from the shared `components/` library only when they reinforce the chosen style.
8. Build in the chosen style first. Use components to strengthen the result, not to derail it.

## 3. Explicit style override

If the user explicitly asks for one of these styles, honor it directly:

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

Also honor obvious close phrasings such as:

- `brutalist` -> `brutalism`
- `cinematic product` -> `cinematic-product`
- `dark luxe` -> `dark-luxe`
- `editorial premium` -> `editorial-premium`
- `gallery minimal` -> `gallery-minimal`
- `monochrome modern` -> `monochrome-modern`
- `premium bento` -> `premium-bento`
- `quiet luxury` -> `quiet-luxury`
- `soft brutalism` -> `soft-brutalism`
- `swiss` or `swiss design` -> `swiss-system`
- `warm modern` -> `warm-modern`

When the style is explicitly named, do not ask the user to choose again.
Route straight into that style and use the component recipes for it.

## 4. Style selection map

Use this routing logic:

- `minimalism`
  - Choose for: restrained, calm, elegant, highly reduced interfaces
  - Good for: startups, consulting, quiet product pages, high-clarity landing pages
- `editorial-premium`
  - Choose for: sophisticated, typographic, magazine-like, cultural, story-led brands
  - Good for: studios, fashion, hospitality, premium service brands
- `dashboards`
  - Choose for: dense software UI, metrics, operator tools, admin products, data-heavy platforms
  - Good for: SaaS, analytics, control panels, B2B software
- `swiss-system`
  - Choose for: rational, grid-led, typographic clarity, strong structure, institutional confidence
  - Good for: design-forward brands, portfolios, systems products, cultural institutions
- `brutalism`
  - Choose for: raw, bold, confrontational, poster-like, industrial layouts with real breathing room
  - Good for: experimental brands, art-tech, manifesto pages, strong campaign concepts
- `cinematic-product`
  - Choose for: immersive launches, dramatic reveals, product-as-hero storytelling
  - Good for: hardware, premium tech, launch pages, visual product narratives
- `dark-luxe`
  - Choose for: moody premium interfaces, dark polished brands, sensual or exclusive atmospheres
  - Good for: premium SaaS, nightlife, luxury services, dark brand worlds
- `gallery-minimal`
  - Choose for: image-led layouts, exhibition pacing, visual storytelling, portfolio-style composition
  - Good for: photographers, agencies, artists, curated showcases
- `monochrome-modern`
  - Choose for: black/white or tightly reduced mono systems with modern product clarity
  - Good for: portfolios, agencies, minimal tech brands, design products
- `premium-bento`
  - Choose for: modular premium product sections, advanced feature storytelling, polished motion cards
  - Good for: modern SaaS, AI products, feature-driven launches
- `quiet-luxury`
  - Choose for: understated wealth, premium calm, soft refinement, expensive restraint
  - Good for: hospitality, wellness, interior, fashion, premium services
- `soft`
  - Choose for: approachable, friendly, optimistic, rounded interfaces with gentle warmth
  - Good for: consumer apps, communities, education, lifestyle products
- `soft-brutalism`
  - Choose for: bold structure with warmer edges, playful severity, contemporary fashion-tech energy
  - Good for: creator tools, trend brands, culture products, bold startups
- `warm-modern`
  - Choose for: contemporary, human, warm, polished websites that should not feel cold or sterile
  - Good for: agencies, service brands, consumer products, modern company sites

## 5. Choosing without user input

If the user is vague, decide by these signals:

- high typography + storytelling -> `editorial-premium`
- strict grid + rational clarity -> `swiss-system`
- pure reduction + calm -> `minimalism`
- modular product selling + premium UI blocks -> `premium-bento`
- bold campaign + poster energy -> `brutalism`
- dark premium mood -> `dark-luxe`
- image-led showcase -> `gallery-minimal`
- soft consumer friendliness -> `soft`
- warm professional polish -> `warm-modern`
- dense functional software -> `dashboards`

Do not default to the same style every time. Make a real selection.

## 6. Shared components rule

After choosing a style, you must use the shared support files:

- `components/style-recipes.md`
- the relevant notes inside `components/`

Use them like this:

- first: anchor yourself in the chosen style skill
- second: use `style-recipes.md` to find strong component patterns for that exact style
- third: actually open the referenced component library files before building when the recipes point to them
- fourth: use the broader component library to enrich motion, hero treatment, galleries, navigation, hover states, media blocks, charts, and transitions

Do not treat the component library as optional inspiration when the recipes explicitly point to it.
Do not skip opening those files just to move faster.
Do not blindly paste flashy components into every design.

Only use components that fit the style's pacing, materiality, and density.

## 7. Quality bar

The final result must:

- feel intentionally art-directed
- avoid generic card spam
- avoid weak nav bars
- include real images when imagery would clearly improve the page, especially in the hero or first two sections
- treat "visual media" as actual photography, renders, illustrations, campaign imagery, or user-supplied images, not just gradients, particles, abstract shapes, or decorative effects
- if image generation is available, generate fitting images when needed
- if generation is not available, source fitting public web images instead of leaving the page image-less
- include appropriate motion, reveals, hover states, and micro-interactions when the chosen style benefits from them
- keep sections paced so one strong scene can breathe at a time
- respect readability, spacing, and hierarchy

## 8. Anti-slop routing rule

Never generate a generic fallback UI just because the prompt is broad.

If the brief is broad:
- choose the strongest plausible style
- commit to it
- use the component library to raise quality

If the brief mixes two neighboring moods, choose the dominant style and borrow only light support from the component recipes. Do not mash multiple style skills together into a confused result unless the user explicitly asks for a hybrid.
