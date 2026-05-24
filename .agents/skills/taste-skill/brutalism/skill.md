---
name: design-taste-brutalism
description: Senior UI/UX Engineer for severe, industrial, poster-like, and tactical brutalist interfaces. Uses the full Taste Skill baseline but tunes the output for hard structure, mechanical hierarchy, and anti-softness.
---

# High-Agency Brutalism Frontend Skill

> Routing note: enter this style through `../SKILL.md` first so the pack can choose the right style and component recipes before building.

## 1. ACTIVE BASELINE CONFIGURATION
* DESIGN_VARIANCE: 6 (1=Perfect Symmetry, 10=Artsy Chaos)
* MOTION_INTENSITY: 2 (1=Static/No movement, 10=Cinematic/Magic Physics)
* VISUAL_DENSITY: 3 (1=Art Gallery/Airy, 10=Pilot Cockpit/Packed Data)

**AI Instruction:** The standard baseline for this style is set to these values. Do not ask the user to edit this file. Otherwise, ALWAYS listen to the user: adapt these values dynamically based on what they explicitly request. Use these baseline (or user-overridden) values as your global variables to drive Sections 3 through 8.

## 2. DEFAULT ARCHITECTURE & CONVENTIONS
- DEPENDENCY VERIFICATION [MANDATORY]: Before importing any third-party library, check package.json. If it is missing, output the install command before using it.
- Framework & Interactivity: Default to React or Next.js. Prefer Server Components by default and isolate heavy interactivity in leaf client components.
- RSC SAFETY: Global state only belongs in client components. Wrap providers in a dedicated use client boundary.
- INTERACTIVITY ISOLATION: If strong motion, liquid glass, magnetic interactions, or heavy canvases are used, isolate them in their own client components.
- State Management: Use local useState or useReducer for local UI. Use global state only when it prevents real prop-drilling.
- Styling Policy: Use Tailwind CSS for most styling. Check package.json first and do not assume Tailwind version or plugin setup.
- ANTI-EMOJI POLICY: Do not use emojis in code, markup, text, alt text, labels, or decorative UI unless the user explicitly asks for them.
- IMAGE EXECUTION [CRITICAL]: If imagery would improve the page, include at least one real image in the hero or first two sections by default.
- VISUAL MEDIA DEFINITION: "Visual media" means actual photography, renders, illustrations, product shots, campaign imagery, or user-supplied images. Abstract gradients, particles, waveforms, or generic decorative assets do not count as the main image treatment.
- IMAGE SOURCING ORDER: First use user-supplied images when available. If image generation is available, generate fitting images when needed. If generation is not available, source fitting public web images instead of leaving the page image-less.
- COMPONENT EXECUTION [CRITICAL]: When the pack router or `components/style-recipes.md` points to shared component library files, actually open and consult those files before building. Do not skip them just to move faster.
- Responsiveness: Standardize breakpoints, contain layouts with real max widths, and aggressively simplify high-variance desktop layouts on mobile.
- Viewport Stability [CRITICAL]: Never use h-screen for the main hero. Use min-h-[100dvh] so mobile browser chrome does not break the first scene.
- Grid over Flex-Math: Do not use brittle width calc tricks for main layout. Use CSS Grid for reliable, exact structure.
- Icons: Use @phosphor-icons/react or @radix-ui/react-icons when icons are needed and keep stroke weight consistent.
- Interaction States: Always provide hover, active, focus, loading, empty, success, and error states when relevant.

## 3. DESIGN ENGINEERING DIRECTIVES (Bias Correction)

### Typography
- Define roles, not just tags: display, headline, title, body, caption or label, and data or mono if needed.
- Display headlines should feel intentional, not generic. Use stronger hierarchy than default Tailwind scales.
- Do not use Inter or a default system sans as the whole identity unless the prompt explicitly demands it.
- Use a real font pairing when the style benefits from it. If the page needs contrast, create it through family, weight, size, spacing, or width.
- H1 should usually land in one to three lines on desktop. Four lines is the hard ceiling. If it breaks further, rewrite, resize, or change the width.
- Body paragraphs and interface descriptions must use leading-normal or leading-relaxed. Never use tight line-height on text blocks longer than two lines.
- Long paragraphs should usually sit around 60 to 70ch. Full-width body copy is usually a mistake.
- Use clamp() for fluid sizes when appropriate and never let typography become absurdly huge or timidly small.
- Use tabular numerals for structured data, prices, tables, and metrics.
- Uppercase and mono belong to labels, metadata, codes, and short utility fragments only. Do not set whole reading paragraphs in uppercase or mono.

### Color and Brand
- Use one clear accent color and one clear neutral family. If everything is colorful, nothing is important.
- The AI purple-blue aesthetic is banned by default: no purple hero gradients, no neon violet glows, no cyan-indigo SaaS fog.
- Build a real color system with background, surface, text, muted text, border, accent, on-accent, success, warning, error, and focus roles.
- Warm and cool neutrals should not be mixed randomly. Pick a temperature and stay coherent.
- Use semantic colors functionally, not as decorative brand identity.
- Pure black #000000 should almost never be the final page background. Use a tuned off-black when the style wants darkness.
- If the page is dark, primary text must be high-contrast off-white, bone, or warm concrete. Never place dim gray body copy on near-black backgrounds.
- Prefer block fills, paper tones, concrete neutrals, and one signal accent over endless thin telemetry separators.
- Flat white pages with no tonal hierarchy fail just as hard as dark pages with neon accents.

### Layout and Hierarchy
- The hero must read as one complete first scene with a clear silhouette at first glance.
- The first screen should feel finished even when content is short. Use media, object scale, structure, or secondary counterweight to preserve the hero shape.
- Do not default to centered hero, three feature cards, testimonials, pricing, FAQ, and footer CTA.
- When DESIGN_VARIANCE is above 4, centered hero compositions are banned unless the prompt explicitly demands them.
- Navigation must fit cleanly at every breakpoint. No awkward wrapping, clipping, or generic chrome.
- Do not solve the whole page with cards. Use rails, image plates, split fields, bands, lists, tables, timelines, framed media, and structural whitespace.
- Brutalist structure should be built from a few large zones per screen, not dozens of micro-panels.
- Use block mass, offset slabs, image plates, and hard background bands before defaulting to thin rules everywhere.
- Each section must answer a user question and earn its place. If a section has no job, remove it.
- Spacing is structural meaning. Tight means same group, medium means related, large means a new chapter.
- Dense does not mean edge-to-edge packing. Preserve breathing room around major statements, media, and actions.
- Use content-driven breakpoints and let mobile become a cleaner layout, not a compressed desktop.

### Materiality, Cards, and Components
- Cards are allowed only when elevation or enclosure actually communicates hierarchy.
- Nested cards, boxes inside boxes, and decorative shells are banned by default.
- If a shadow is used, tint it to the page mood instead of using one generic black blur everywhere.
- Use lines, dividers, tonal changes, and composition before inventing another wrapper.
- Prefer heavier borders, filled blocks, and hard contrast moments over full-page 1px telemetry cages.
- One or two strong structural rules are better than fifty decorative stripes.
- Buttons, inputs, pills, and badges must follow one real system of radius, depth, and spacing.
- Do not let every section use the exact same panel treatment or the page will collapse into kit output.
- Avoid nested scroll containers inside showcase cards and panels. Expand the module, paginate it, or design the scrollbar intentionally if an internal scroll area is truly required.
- Default showcase surfaces should not expose ugly browser-default internal scrollbars.

### States, Forms, and Copy Behavior
- Loading states should preserve layout structure. Prefer skeletons or inline progress over empty spinners.
- Empty states must explain what is missing and what the user can do next.
- Error states must say what failed, how to fix it, and preserve user effort.
- Forms require labels above inputs, helper text when useful, and clear inline validation.
- Primary CTAs must say what happens next, not hide behind vague text like Learn more or Submit when specificity is possible.

## 4. CREATIVE PROACTIVITY, MOTION, AND PERFORMANCE

### Creative Proactivity
- Do not default to safe template sections. Use a few strong scene ideas instead of many weak sections.
- Pick one bold aesthetic direction and commit to it. Do not mix three style worlds because the UI feels empty.
- Use real visual anchors: photography, renders, diagrams, charts, objects, process frames, or typographic masses.
- Rare UI components are allowed only when they strengthen the chosen style and the actual page goal.
- The site should still feel specific if the logo is removed. If another startup logo could be swapped in with no tension, it failed.
- By default, include meaningful visual media in the hero or first two sections unless the user explicitly asks for text-only composition.
- Prefer larger, style-appropriate imagery over tiny decorative thumbnails or empty placeholder panels.
- If the concept is product-led, system-led, or analytical, use screenshots, diagrams, maps, timelines, or charts as visual proof instead of relying on text alone.
- Keep the page in one dominant lightness mode unless the user explicitly asks for deliberate light-dark switching.

### Motion and Interaction
- Motion must clarify, confirm, guide, or create affordance. If it only decorates, reduce it or remove it.
- Prefer transform and opacity. Never animate top, left, width, or height for ordinary UI motion.
- One focal motion language is stronger than ten unrelated animations.
- Avoid transition-all duration-300 everywhere, repeated fade-up stagger on every section, endless floating loops, and generic hover:scale-105.
- Respect prefers-reduced-motion and provide a reduced path that still preserves clarity.
- When MOTION_INTENSITY is high, use purposeful choreography: layout transitions, stateful loops, magnetic interactions, chapter reveals, or structured scroll scenes.
- Never mix heavy GSAP or Three.js choreography with generic UI motion in the same tree without a real concept.
- Motion should always match the chosen style.
- Unless the user explicitly asks for a static result, add at least one intentional hero reveal, one light scroll-entry system for major sections, and clear hover or press feedback on interactive elements.
- Hero entries can use fades, wipes, staggered text, image reveals, or restrained parallax depending on the style.
- Scroll motion should be sectional and tasteful, not the same generic fade-up on every element.
- Navigation, buttons, links, cards, and media should all have style-appropriate hover, focus, and active states.
- Use one or two micro-interactions so the page feels alive even when the motion dial stays low.

### Performance Guardrails
- Do not apply grain, blur, or noise to large scrolling containers. Use fixed pseudo-elements or isolated layers instead.
- Use will-change sparingly, not globally.
- Avoid dozens of independent animated objects at once.
- Reserve WebGL, canvas, and heavy shader work for moments where they are central to the experience.
- Keep z-index disciplined and systemic. Do not spam z-50 or modal-like layering without reason.
- Code must be production-ready, accessible, and semantically clean.

## 5. TECHNICAL REFERENCE (Dial Definitions)

### DESIGN_VARIANCE (Level 1-10)
- 1-3: predictable, disciplined, symmetrical, restrained
- 4-7: offset, asymmetrical, mixed scale, more varied composition
- 8-10: highly authored, poster-like, scene-led, large tension between empty and dense zones
- Mobile override: any asymmetry above md must collapse into a stable single-column layout when readability improves.

### MOTION_INTENSITY (Level 1-10)
- 1-3: mostly static, rely on hover, active, focus, and quick state feedback only
- 4-7: fluid UI transitions, stagger used selectively, richer overlays, restrained layout motion
- 8-10: chaptered reveals, scroll storytelling, magnetic interactions, product choreography, premium physics
- No matter the level, motion cannot delay access to content or violate reduced-motion expectations.

### VISUAL_DENSITY (Level 1-10)
- 1-3: gallery mode, high whitespace, fewer objects, slower rhythm
- 4-7: daily app mode, balanced spacing and information load
- 8-10: cockpit mode, high information density, tighter spacing, less card chrome, numbers aligned precisely
- High density does not mean chaos. The denser the page, the calmer the grouping must become.

## 6. AI TELLS (Forbidden Patterns)

### Visual and Surface Tells
- purple or indigo default accent as the main brand color
- gradient text on H1 as the premium shortcut
- clinical bg-white or bg-gray-50 with no surface hierarchy
- flat black dark mode with neon cyan or violet accents
- rounded-2xl on everything
- glowing orb or blob backgrounds with no content role

### Layout Tells
- hero left text right image as the only idea
- three equal feature boxes below the hero
- template ordering: hero, features, testimonials, pricing, FAQ, CTA
- logo strip used as filler proof
- dashboard screenshot in the hero that nobody can actually read
- identical grid gaps, paddings, heights, and card shells everywhere

### Content and Copy Tells
- Transform your business, streamline workflows, unlock insights, all-in-one platform
- generic CTAs like Get Started when a specific action is possible
- fake testimonials, fake names, fake impossible metrics
- startup slop names, generic about pages, and repeated value props saying the same thing three times
- corporate filler openers like In today's fast-paced world
- emoji decoration unless the user explicitly asks for it

### Component and Code Tells
- shadcn defaults with no customization
- Lucide icons as the entire visual language
- pill badge spam
- cards inside cards inside cards
- no empty, loading, or error states
- use client everywhere and obvious scaffold fingerprints left visible

## 7. STYLE DIRECTION: Brutalism

**When to use this skill:** Use this skill when the user wants brutalist, anti-design, industrial poster, harsh editorial, raw web, hard-signage, or concrete-system aesthetics. Default to poster-led brutalism, not terminal-dashboard brutalism, unless the user explicitly asks for a system UI.

### Core Identity
- Brutalism here should feel blunt, physical, and authored.
- The page should feel like blocks, posters, signage, paper, concrete, steel, ink, and cropped evidence.
- Rawness must still feel controlled enough to use.
- Good brutalism is severe without becoming unreadable.
- The output should feel memorable in one screenshot, not merely busy.

### Brutalism Modes
- Poster Brutalism is the default: oversized type, hard blocks, one image slab, one or two strong color fields, and very clear actions.
- Editorial Brutalism is secondary: asymmetric reading layouts, documentary imagery, captions, notes, and strong chapter breaks.
- Industrial UI Brutalism is conditional: only use tables, telemetry, system strips, or control-room logic when the user explicitly wants operational software or data-heavy tooling.
- Do not drift into fake military dashboard mode unless the prompt clearly asks for that exact world.

### Palette and Material
- Favor bone, paper, concrete, soot, asphalt, oxidized metal, and one signal accent such as warning red, cobalt, acid yellow, or construction orange.
- Use the accent as emphasis, not wallpaper.
- Prefer hard fills, paper blocks, and contrast slabs over endless line-work.
- Red should feel like stamped ink, warning paint, or markup rather than luxury branding.
- No gradients, luxury glow, or soft atmospheric fog by default.

### Typography Character
- Use one brutal display face or condensed grotesk for impact and one plain readable face for body text.
- Large type should create architecture, but it must stay inside a controlled composition.
- Keep giant headlines to one, two, or three deliberate blocks. Never let brutalist type collapse into accidental six-line mush.
- Uppercase labels should be sparse and useful.
- Mono metadata should be selective, not the main reading experience.
- Body copy should be plainspoken, high-contrast, and surprisingly readable.

### Hero Direction
- Build one clear first scene from two or three large elements only: a headline slab, a media slab, and one support block or CTA zone.
- The hero must feel bounded and complete on first view.
- Do not leave a giant dead half-screen unless a media slab, color slab, or structural object is actively balancing it.
- Prefer 40/60, 50/50, or offset poster compositions over scattered micro-panels.
- One brutal image, render, scan, object cutout, or diagram should usually appear in the hero or immediately after it.
- If no image is used, replace it with a real graphic object such as a diagram, number slab, typographic wall, or block composition that actually carries visual weight.
- Do not cram headline, proof stats, long copy, and three support modules into the same hero scene.
- Let the hero breathe, but cap the composition with clear width boundaries so it feels strong rather than loose.

### Navigation Direction
- Use blunt text links, exposed rails, block buttons, chapter indices, or hard utility bars.
- Navigation should feel explicit and easy to scan, not hidden inside aesthetic noise.
- Keep labels short and readable.
- Avoid over-decorated nav strips, fake telemetry numbering, and stripe spam.
- The nav should support orientation, not cosplay as a control room.

### Layout Tendencies
- Use two or three dominant zones per section, not a hundred tiny compartments.
- Build hierarchy from large blocks, offset columns, image plates, thick borders, and hard background changes.
- Mix dense statements with real breathing room so the page can hit hard without becoming exhausting.
- Use visible structure, but do not trap every inch of the page inside a line grid.
- Brutalism should feel decisive, not cluttered.
- Prefer one major section per viewport over stacked mini-sections fighting for attention.
- Avoid ultra-wide empty panels with tiny amounts of content.
- Avoid squeezing three unrelated modules into one horizontal band just to look complex.
- Use generous section spacing, but keep content blocks visually connected so the page does not drift apart.
- Keep most reading layouts within disciplined text widths; brutalism can be large without becoming sloppy.

### Component Vocabulary
- Good fits: manifesto slab, image plate, chapter rail, quote wall, archive list, hard CTA banner, case-study strip, poster footer, evidence gallery, asymmetric comparison block.
- Optional fits: inventory table or status strip, but only when the content actually needs operational clarity.
- Weak fits: endless micro-metrics, fake declassified dashboards, rounded testimonial cards, plush widgets, soft onboarding illustrations, overbuilt pricing towers.

### Media and Imagery
- Media is mandatory. Include at least one meaningful image, scan, render, texture slab, diagram, or photographic crop in the hero or first two sections.
- Images should feel raw, documentary, industrial, editorial, or object-like.
- Use high-contrast crops, thresholded photography, product fragments, paper scans, marked-up diagrams, or stark still-life compositions.
- Visuals should feel like evidence, print matter, or matter itself.
- Avoid polished lifestyle scenes, empty screenshot placeholders, and decorative black rectangles that contribute no image weight.
- Give images real physical size. A brutalist page usually wants fewer images, shown larger.
- Let media occupy a meaningful share of the section instead of reducing it to a thumbnail beside oversized text blocks.

### Motion Profile
- Motion should be minimal, abrupt, and structural: hard cuts, wipes, panel swaps, block reveals, ticker movement, or restrained slides.
- No floaty easing, soft parallax fog, or playful bounce.
- Keep interaction feedback obvious and tactile.
- If motion starts feeling cyberpunk, arcade, or sci-fi telemetry, simplify it immediately.

### UX Guardrails For This Style
- Brutalism is not an excuse for unreadable contrast.
- Brutalism is not an excuse for tiny labels or compressed paragraph spacing.
- Brutalism is not an excuse for hiding actions inside decorative layout.
- Buttons must still look clickable, forms must still be easy to use, and sections must still answer clear questions.
- Use a few big moves with clear interaction, not many hostile micro-decisions.
- Prefer cleaner section pacing over maximal density.
- If a screen already has one strong statement, do not force two more blocks into the same view.
- Negative space should support impact, not create awkward emptiness.
- Sections should feel roomy, legible, and intentional rather than squeezed or over-engineered.

### Creative Arsenal For This Style
- poster-scale typography with one hard image crop
- offset paper blocks or construction-board color fields
- stamped labels, chapter markers, and annotation lines used sparingly
- stark before-and-after image pairings
- thick-rule section breaks instead of many tiny dividers
- bold CTA banners with one blunt verb and one obvious next action

### Style-Specific Avoidances
- fake military dashboard aesthetics by default
- terminal cosplay and cyberpunk telemetry overload
- too many hazard stripes, serial numbers, or tiny status labels
- full-page hairline grids with no block hierarchy
- giant dark surfaces with no image, object, or content weight
- unreadably dim paragraph text
- soft shadows, plush cards, and rounded major structure
- colorful multi-accent compositions
- friendly SaaS illustration language

### Copy Tone
- blunt, direct, and human
- declarative over aspirational
- nouns, verbs, evidence, and actions over slogan fog
- use coded labels only when they genuinely improve the atmosphere or structure
- never let the copy become roleplay if it hurts clarity

### Current Production Priorities
- Add restrained brutalist motion by default: hard fades, block reveals, image wipes, hover inversion, and obvious press states.
- Use larger image plates or background media in the hero and early sections so the page does not become text-only.
- Prefer roomy poster pacing: one strong section per viewport instead of squeezed multi-module screens.
- Navigation should feel harsher and more authored than a default link row, but still remain clear and usable.

### Components Library
- Consult `../components/README.md` before inventing custom modules, hero systems, or interaction patterns from scratch.
- Use `../components/gsap-explore.md` for official GSAP motion scenes, scroll patterns, cursor systems, and CodePen-linked demos.
- Use `../components/aceternity-ui.md` for dramatic hero modules, Framer-heavy surfaces, cards, nav experiments, and backgrounds.
- Use `../components/21st-community.md` for pragmatic UI primitives, community layouts, shader ideas, and production interface pieces.
- Use `../components/reactbits.md` for text animation, micro-interactions, animated effects, and composed React component ideas.
- Adapt every borrowed pattern to the current style; never paste a source pattern in unchanged.
- For this style, start with the `Brutalism` section in `../components/style-recipes.md`.
- Strong first picks: GSAP `directional-marquee` / `draw-a-path`, React Bits `split-text` / `scrambled-text`, and larger Aceternity layout surfaces rebuilt into harder blocks.

## 8. FULL TASTE CORE OVERLAY

### 8.1 CORE PRIORITY
- This section is the deep rule layer for the current style pack.
- If an earlier shortcut rule conflicts with this section, this section wins.
- Apply every rule through the lens of the current style direction instead of flattening everything into one generic aesthetic.
- The current style must still feel unmistakably like its own world after all guardrails are applied.
- Do not output a safe average landing page just because the system has many constraints.
- Use the style direction to choose what to emphasize, not to excuse sloppy composition.
- Every page should feel authored, not statistically assembled.
- Every major section should have a reason to exist.
- Every component should either clarify, persuade, orient, or convert.
- Remove decorative filler that does not create hierarchy, identity, or trust.
- Prefer fewer stronger ideas over many weak UI gestures.
- The result must feel premium, deliberate, and production-minded.

### 8.2 ACTIVE BASELINE INTERPRETATION
- DESIGN_VARIANCE controls structural risk, asymmetry, and compositional surprise.
- MOTION_INTENSITY controls how alive the interface feels, from almost static to cinematic choreography.
- VISUAL_DENSITY controls how tightly information is packed and how much empty space is preserved.
- Always adapt those values to the user's request if they clearly ask for a calmer, bolder, cleaner, denser, or more expressive result.
- If the user does not specify values, follow the baseline defined at the top of the current style skill.
- If the style identity and the user request conflict, blend them instead of ignoring one side.
- For example, a restrained user request inside a brutalist skill should become controlled brutalism, not generic SaaS.
- For example, a high-motion request inside a minimal skill should become quiet precision motion, not flashy noise.
- For example, a dense dashboard request inside an editorial skill should become structured editorial data, not boxed admin panels.
- Use the three dials continuously during generation instead of setting them once and forgetting them.

### 8.3 DEFAULT ARCHITECTURE & CONVENTIONS
- Before importing any third-party package, check `package.json` first.
- If a package is missing, output the install command before using it.
- Never assume a motion or icon package exists.
- Prefer React or Next.js unless the user clearly wants another stack.
- Default to Server Components when using the Next.js App Router.
- Put global providers into explicit client wrappers.
- Isolate heavy interaction into leaf client components.
- Keep server components responsible for layout, data wiring, and stable structure.
- Keep client components responsible for touch, drag, hover, local state, and animation.
- Use local state for isolated interactions.
- Use global state only when it prevents deep prop drilling across real complexity.
- Prefer Tailwind CSS for most styling unless the project clearly depends on another system.
- Check the Tailwind major version before using version-specific syntax.
- Do not mix Tailwind v4 patterns into a v3 project.
- Do not overbuild custom utility abstractions when direct classes are clearer.
- Standardize breakpoints around `sm`, `md`, `lg`, and `xl`.
- Contain layouts with `max-w-[1400px] mx-auto`, `max-w-7xl`, or a style-appropriate equivalent.
- Never use brittle flex percentage math where CSS Grid is the better structural tool.
- Default full-height heroes to `min-h-[100dvh]`, not `h-screen`.
- Treat mobile viewport behavior as a first-class layout concern.
- Use either `@phosphor-icons/react` or `@radix-ui/react-icons` when icons are needed.
- Keep icon stroke weight consistent across the page.
- Avoid icon soup; use icons only when they clarify meaning or rhythm.
- Avoid emojis by default; only use them if the user explicitly asks for them.
- Keep code output clean, modular, and ready to be integrated without a cleanup pass.

### 8.4 DESIGN ENGINEERING DIRECTIVES
- The model must actively fight its own tendency toward bland hero sections.
- The model must actively fight its own tendency toward equal cards in a row.
- The model must actively fight its own tendency toward purple-blue AI branding.
- The model must actively fight its own tendency toward oversized generic H1 blocks with weak support copy.
- The model must actively fight its own tendency toward symmetric everything.
- Headlines should default to strong contrast, tight tracking, and deliberate line breaks.
- Body copy should stay readable, calm, and measured.
- Default to one dominant accent color and one neutral palette family.
- Avoid mixing warm and cool neutrals without a clear reason.
- Use typography to build identity before reaching for visual gimmicks.
- Use spacing to create status and calm before reaching for more containers.
- Use containers only when they signal grouping, depth, or interaction.
- A card is not a design system.
- A bento block is not automatically premium.
- A gradient is not automatically art direction.
- Default to one strong primary action and one lower-contrast secondary action.
- Avoid dead pages that only show best-case success states.
- Always think through loading, empty, hover, active, disabled, and error states.
- Treat forms as precision systems, not as anonymous input stacks.
- Labels go above inputs.
- Helper text belongs in markup when it makes the action easier.
- Error text belongs directly under the field it refers to.
- Active states should feel physical, not decorative.
- Press feedback should slightly compress or shift, not explode.

### 8.5 CREATIVE PROACTIVITY
- Go beyond default glassmorphism if transparent material is used.
- Add inner borders and subtle inner highlights so translucent layers feel physical.
- If motion intensity is above medium, add purposeful perpetual motion to selected elements.
- Do not animate everything at once.
- Give motion a job: guidance, emphasis, status, rhythm, or delight.
- Use Framer Motion layout transitions when cards or panels change size or order.
- Use staggered orchestration for entrances rather than dumping everything onto the screen simultaneously.
- When using cursor-follow interactions, avoid React state for per-frame updates.
- Use motion values and transforms outside the React render loop for continuous interaction.
- Make premium motion feel weighty, not floaty.
- Favor spring curves over default ease-in-out.
- Keep high-motion behavior isolated and easy to remove if the user asks for restraint.
- Use motion to express the current style family, not to overwrite it.
- Minimal styles want quiet motion.
- Editorial styles want paced and elegant motion.
- Dashboard styles want utility motion and live-state motion.
- Brutalist styles want blunt, confident, visible motion.
- Luxe styles want controlled depth and soft reveal motion.
- Product styles can tolerate more spectacle if the hierarchy stays sharp.

### 8.6 PERFORMANCE GUARDRAILS
- Never animate `top`, `left`, `width`, or `height` when transform or opacity can do the job.
- Keep grain, noise, and blur effects off scrolling surfaces.
- Push decorative overlays to fixed or isolated layers when possible.
- Avoid spraying `z-50` through the whole page.
- Build a real layering system for nav, content, overlays, and dialogs.
- Avoid giant client components for otherwise static pages.
- Memoize perpetual or looping widgets when they would otherwise trigger parent re-renders.
- Keep animation cleanup explicit inside effects.
- Never mix GSAP and Framer Motion inside the same component tree without a hard reason.
- Use GSAP or WebGL only when the concept truly needs them.
- Treat CPU-heavy spectacle as exceptional, not default.
- Premium output must still feel stable on mobile hardware.

### 8.7 TECHNICAL REFERENCE: DESIGN_VARIANCE
- Levels 1 to 3 should feel predictable, aligned, and calm.
- Levels 1 to 3 favor centered or symmetrical structures only when the style itself supports that restraint.
- Levels 4 to 5 should introduce offsets, layered overlaps, and more dynamic whitespace.
- Levels 4 to 5 should begin to break repetitive section formulas.
- Levels 6 to 7 should feel authored and directional.
- Levels 6 to 7 can use split layouts, offset media, and strong grid imbalance.
- Levels 8 to 10 should feel intentional and unmistakably designed.
- Levels 8 to 10 can use asymmetry, long whitespace fields, unconventional cropping, and gallery-like pacing.
- High variance on desktop must still collapse aggressively and cleanly on mobile.
- Never let high variance produce horizontal scroll or broken reading order.

### 8.8 TECHNICAL REFERENCE: MOTION_INTENSITY
- Levels 1 to 2 should rely on hover, focus, and press states only.
- Levels 1 to 2 should feel still, precise, and intentional.
- Levels 3 to 4 can add small fade, slide, and reveal choreography.
- Levels 3 to 4 should remain almost invisible to the user.
- Levels 5 to 6 can add stagger, shared layout transitions, and low-key perpetual motion.
- Levels 5 to 6 are the default sweet spot for premium web interfaces.
- Levels 7 to 8 can add scroll choreography, richer motion mapping, and stronger component behavior.
- Levels 7 to 8 require tight discipline so the page still reads clearly.
- Levels 9 to 10 should be reserved for strong creative concepts.
- Levels 9 to 10 should feel cinematic, not chaotic.
- Never use scroll listeners for advanced motion when a motion framework can handle the effect more safely.
- Never let motion break input focus, readability, or layout stability.

### 8.9 TECHNICAL REFERENCE: VISUAL_DENSITY
- Levels 1 to 2 should feel like a gallery or luxury brochure.
- Levels 1 to 2 should preserve very large vertical gaps and strong breathing room.
- Levels 3 to 4 should feel refined and spacious.
- Levels 3 to 4 are strong defaults for premium marketing sites.
- Levels 5 to 6 should feel balanced and practical.
- Levels 5 to 6 are a strong default for product pages and mixed-content sites.
- Levels 7 to 8 should feel compact but still readable.
- Levels 7 to 8 fit dashboards, tools, and operational interfaces.
- Levels 9 to 10 should feel cockpit-like and intense.
- Levels 9 to 10 should use very strong information hierarchy so compression does not become noise.
- At high density, use dividers, rhythm, and typography before reaching for more nested cards.
- At high density, numbers and status elements should become more systematic and more aligned.

### 8.10 AI TELLS (FORBIDDEN PATTERNS)
- Avoid neon glows as the default signal for modernity.
- Avoid pure black when an off-black or charcoal would feel richer.
- Avoid oversaturated accents sitting on muted neutrals without relationship.
- Avoid huge gradient headlines as a default trick.
- Avoid default generic mouse cursor experiments.
- Avoid Inter as the automatic answer for every interface.
- Avoid serif fonts on dashboards or product UIs that need technical clarity.
- Avoid giant screaming H1 blocks that dominate five or six lines without structure.
- Avoid mathematically perfect but emotionally dead spacing.
- Avoid equal three-card feature rows as the default content block.
- Avoid generic placeholder people.
- Avoid generic SVG profile eggs.
- Avoid round fake numbers like `99.99%` and `50%`.
- Avoid startup slop brand names.
- Avoid filler verbs like `Elevate`, `Unleash`, and `Revolutionize` unless the user explicitly wants ad-copy energy.
- Avoid broken or random external images.
- Avoid using shadcn defaults without customization.
- Avoid making every section a bordered rounded rectangle.
- Avoid dumping every idea into one hero.
- Avoid converting every style into the same SaaS bento page.
- Avoid making the page feel like a prompt artifact.
- Avoid weak section transitions where one block just stops and the next begins without relationship.
- Avoid a top-heavy page where all effort goes into the first screen and the rest collapses into cards.
- Avoid overly long headline wrapping that looks accidental.
- Avoid microcopy that sounds like a template engine wrote it.

### 8.11 CREATIVE ARSENAL
- Consider asymmetric hero structures before centered hero structures.
- Consider split-screen layouts with a disciplined text side and a strong visual side.
- Consider masonry or modular gallery composition when the style supports it.
- Consider dock-like navigation behavior when the concept wants playful precision.
- Consider magnetic buttons when the motion level supports tactility.
- Consider gooey or fluid navigation only for expressive styles that can carry it.
- Consider dynamic island style status components for live or adaptive interfaces.
- Consider radial menus or floating action systems only when the interaction model supports them.
- Consider mega-menu reveals for brand-heavy or editorial projects.
- Consider bento grids only when the content mix truly benefits from modular presentation.
- Consider scroll-stacked cards for narratives that need sequence.
- Consider horizontal scroll galleries when the content is inherently comparative or panoramic.
- Consider curtain reveals or split-screen scrolls when the concept benefits from theatrical pacing.
- Consider parallax tilt or spotlight borders for selected cards, not every surface.
- Consider holographic or foil-like reflection only in styles that justify that materiality.
- Consider morphing modal transitions when the user flow benefits from continuity.
- Consider kinetic marquees only when the typography and message are strong enough to carry repetition.
- Consider text scramble or mask reveal effects only when the content theme supports them.
- Consider circular text paths only when they add identity instead of novelty noise.
- Consider animated SVG line drawing when the brand language is geometric or diagrammatic.
- Consider mesh-gradient or blurred-color atmospheres only when they support the palette and not the other way around.
- Consider lens-blur depth only when depth is a real compositional tool.
- Consider GSAP scrolltelling or WebGL backgrounds only when the idea clearly exceeds standard UI motion.
- Consider stronger editorial pacing between sections rather than using yet another component.
- Consider one memorable interaction per page instead of twenty forgettable ones.

### 8.12 MOTION-ENGINE BENTO PARADIGM
- When a page includes dashboards, feature systems, or modular product stories, use a more advanced bento philosophy.
- Major containers can use larger radii when the current style supports softness or gallery polish.
- Cards should only exist when they create hierarchy, focus, or interaction.
- Labels and supporting descriptions can sit outside cards when that improves clarity.
- Use perpetual micro-interactions selectively so the layout feels alive.
- Use springs that feel weighted, not jittery.
- Use layout animations for reorder, resize, and state changes.
- Keep looping widgets isolated from the parent layout.
- Strong card archetypes include intelligent lists, command inputs, live status surfaces, wide data streams, and contextual focus tools.
- Every animated card should feel like a product behavior, not a loading gimmick.
- The motion language of the bento area must still fit the active style family.

### 8.13 HERO AND PAGE CHECKSUM RULES
- The hero must have a fixed visual envelope.
- The hero must read as a complete first scene on common laptop screens.
- The hero must not feel like it spills by accident into the next section.
- Transitions can exist, but the hero still needs a clear boundary and checksum.
- If content is short, preserve the hero frame with space, media, or supporting detail instead of letting it collapse.
- If content is long, edit the content before letting the hero break.
- The hero should usually communicate one dominant promise, one support idea, and one next step.
- Use one major visual anchor in the hero.
- If the hero uses no image, replace it with a real spatial or typographic concept.
- If the hero uses an image, crop it with intent.
- The header and hero should feel related, not like different pages stacked together.
- Every later section should feel designed to follow the hero, not copied from a generic library.

## 9. PAGE AND COMPONENT CONSTRUCTION MATRIX

### 9.1 HERO SYSTEMS
- Use a split hero when the style benefits from clear text-versus-image tension.
- Use an offset hero when the style benefits from asymmetry and pacing.
- Use a framed hero when the style benefits from object-like composition.
- Use a gallery hero when the style benefits from multiple curated images.
- Use a tall editorial hero when the style benefits from reading rhythm.
- Use a command hero when the page is product-led and interaction-led.
- Use a metrics hero when proof and numbers drive credibility.
- Use a proof-first hero when testimonials or trusted logos matter more than spectacle.
- Use a narrative hero when the story is the product.
- Use a cinematic hero when product surfaces, light, and motion carry the promise.
- Give the hero one primary headline, one supporting paragraph, and one to two actions.
- Keep the paragraph within a readable measure.
- Keep button groups disciplined and aligned.
- Use supporting micro-labels sparingly.
- Support the hero with one meaningful secondary detail such as proof, process, or preview.
- On mobile, stack the hero into a clean reading order without collapsing its visual identity.

### 9.2 NAVIGATION SYSTEMS
- The navigation should feel like part of the style, not an afterthought.
- Navigation can be inline, floating, docked, framed, editorial, or utility-led depending on the style.
- Keep the nav height stable.
- Ensure labels fit without awkward wrapping.
- If the nav is sparse, use spacing with intent so it feels premium rather than empty.
- If the nav is dense, use grouping and alignment so it feels organized.
- Use one clear active-state treatment.
- Use hover states that match the motion intensity.
- If the nav includes buttons, those buttons must visually belong to the same system as the rest of the page.
- Do not let the nav dominate the hero.
- Do not let the nav disappear as an unstyled line of text.
- Use sticky behavior only when it improves orientation.

### 9.3 SECTION PACING
- Each section needs a unique job.
- Alternate density, alignment, or media treatment across adjacent sections.
- Avoid repeating the same section shell three times in a row.
- Use shifts in scale, whitespace, or material to create progression.
- Introduce proof before the user starts doubting.
- Introduce detail before the user gets bored.
- Introduce interaction before the page starts feeling static.
- Use quieter sections after visually intense sections.
- Use tighter sections after broad atmospheric sections.
- Keep section intros short and useful.
- Avoid isolated orphan labels with no follow-through.
- Give every section a strong leading edge.

### 9.4 CARD AND SURFACE SYSTEMS
- Prefer open composition before adding another container.
- Use border, background, shadow, blur, or depth only when they serve a real role.
- Cards can frame proof, product, quotes, controls, or grouped content.
- Cards should not become the default answer for every paragraph.
- Mix carded and uncarded sections to preserve page rhythm.
- Use large radii only when the style direction justifies softness.
- Use hard edges when the style direction wants tension or rigor.
- Use internal spacing that matches the information density.
- Avoid giant empty cards with tiny amounts of content.
- Avoid excessive nested cards.
- If multiple cards appear together, vary emphasis so they do not all feel equal.
- Use dividers and negative space as alternatives to surface chrome.

### 9.5 IMAGERY AND MEDIA
- Images should feel chosen, not inserted.
- Use fewer better images rather than many weak placeholders.
- Cropping is a design decision, not a fallback.
- Pair image treatment with the style family.
- Editorial styles want quieter, more curated media.
- Product styles want clearer product storytelling and lighting.
- Dashboard styles want meaningful interface previews instead of decorative blobs.
- Luxe styles want tone, shadow, and restraint.
- Soft styles want warm depth and approachable texture.
- Swiss and minimal styles want precise framing and disciplined ratios.
- Use captions only when they improve comprehension or mood.
- Give media enough size to matter.

### 9.6 TYPOGRAPHY AND COPY BLOCKS
- Headlines need deliberate line breaks.
- Do not leave wrapping to chance.
- Balance long and short lines so the headline shape feels intentional.
- Use support copy to clarify, not to repeat the headline.
- Avoid overlong paragraphs under major headings.
- Break longer arguments into compact blocks.
- Use eyebrow labels only when they add orientation.
- Use quote blocks only when the quote is strong enough.
- Use lists when scan speed matters.
- Use prose when tone and trust matter.
- Use mono sparingly and with purpose.
- Let typography do some of the design work instead of pushing everything into containers.

### 9.7 COMPONENT LIBRARY
- Consider a proof rail with selective logos and one sharp supporting statement.
- Consider a staggered testimonial stack instead of a generic review carousel.
- Consider a split comparison module with asymmetrical weight.
- Consider a feature timeline with visible momentum.
- Consider a sticky chapter index for long-form editorial pages.
- Consider a command bar preview for product-forward concepts.
- Consider a layered screenshot deck with depth and ordering.
- Consider a swipe stack for case studies or portfolio highlights.
- Consider a pinned metric strip that evolves through the page.
- Consider a quiet FAQ with strong typography instead of loud accordions.
- Consider a dock-like utility bar for tool or app concepts.
- Consider a floating inquiry or booking panel for service sites.
- Consider a process rail that shows actual transitions and not just numbered circles.
- Consider a note-card system for editorial or research-heavy pages.
- Consider a case-study triptych with unequal panel sizes.
- Consider a wide image ledger with adjacent technical notes.
- Consider a gallery strip that expands on hover.
- Consider a comparison shelf with one dominant option and one supporting option.
- Consider a stats slab with strong numeric typography and no unnecessary card chrome.
- Consider a contextual toolbar that appears near selected content.
- Consider a layered callout that overlaps a strict grid.
- Consider a dynamic island style status module for active systems.
- Consider a notification stack that demonstrates system behavior.
- Consider a command-input demo with visible progression.
- Consider a focus-mode document module for intelligence or workflow tools.
- Consider a pricing area that uses contrast and pacing instead of three equal cards.
- Consider a founder note or editorial letter for premium brands.
- Consider a structured footer that continues the visual language instead of ending abruptly.

### 9.8 RARE UI MOVES
- Use spotlight borders on only one or two hero surfaces.
- Use directional hover fills on premium buttons.
- Use subtle image trails only for expressive high-motion concepts.
- Use kinetic marquee bands when the typography is strong enough.
- Use curtain reveals when the section needs theatrical entry.
- Use sticky scroll stacks for sequential proof.
- Use split-screen opposing motion for contrast-heavy layouts.
- Use circular text only when it reinforces a visual motif.
- Use animated line drawing for diagrammatic stories.
- Use hover-based accordion galleries for editorial or brand work.
- Use float-in action bars for contextual workflows.
- Use parallax tilt sparingly and only on surfaces that can carry depth.
- Use shimmer skeletons that match real layout dimensions.
- Use ripple click effects only when the style tolerates visible feedback.
- Use breathing status dots for live systems.
- Use overshoot badges for event arrival or notification moments.
- Use auto-sorting stacks for AI or prioritization concepts.
- Use seamless horizontal data streams when the content is cyclical.
- Use morphing modal expansions for continuity between trigger and dialog.
- Use radial menus only when they match the product behavior.

### 9.9 OUTPUT ALGORITHM
- First decide the page's central promise.
- Then decide the hero system.
- Then decide the navigation posture.
- Then decide the section sequence.
- Then decide where proof enters.
- Then decide where imagery enters.
- Then decide whether cards are necessary.
- Then decide the motion posture based on the current style and motion dial.
- Then decide the conversion moment.
- Then decide the closing section and footer tone.
- Then refine line breaks, spacing, and surface hierarchy.
- Then add states, polish, and implementation details.

## 10. FAILURE MODES AND RECOVERY LOOP
- If the result looks like a template, increase structural specificity.
- If the result looks empty, improve composition before adding more filler content.
- If the result looks crowded, remove containers before shrinking typography.
- If the result looks generic, strengthen typography and layout before adding effects.
- If the result looks like generic AI SaaS, remove the equal cards and the purple-blue palette first.
- If the hero wraps awkwardly, rewrite the headline instead of accepting the break.
- If the sections all look the same, vary the section grammar.
- If the page feels too safe, add one memorable component or layout move.
- If the page feels chaotic, reduce simultaneous variation and protect the reading path.
- If motion feels cheap, slow it down and give it weight.
- If motion feels absent, add focused entry choreography and tactile states.
- If images feel random, reduce their count and improve their role.
- If proof feels tacked on, move it earlier and integrate it into the page narrative.
- If the design feels over-carded, unwrap half the content and rebuild spacing.
- If the design feels under-designed, strengthen the page skeleton before adding novelty.
- If the style identity is disappearing, reassert the current style's typography, surfaces, and composition rules.
- If implementation complexity starts dominating the idea, simplify the interaction and keep the visual ambition.
- If the user asks for a calmer or bolder version, change the dials and regenerate the structure accordingly.

### 10.1 QUICK DECISION SHORTCUTS
- If the user asks for premium, increase restraint before increasing decoration.
- If the user asks for bold, increase structure contrast before increasing chaos.
- If the user asks for minimal, remove weak components before shrinking everything.
- If the user asks for luxury, improve material, spacing, and type before adding gold accents.
- If the user asks for editorial, improve pacing and copy hierarchy before adding serif everywhere.
- If the user asks for product, sharpen proof and interaction before adding more feature boxes.
- If the user asks for dashboard, improve system clarity before adding more charts.
- If the user asks for playful, keep the composition disciplined so the play has a frame.
- If the user asks for futuristic, avoid default blue glow tropes.
- If the user asks for calm, reduce simultaneous motion and reduce accent spread.
- If the user asks for energetic, intensify rhythm and transitions without breaking readability.
- If the user gives little detail, choose one strong visual thesis and build around it.
- If the result feels mid, strengthen typography, hero framing, and section rhythm first.
- If you are unsure, choose the more intentional option, not the more common option.
- Always preserve the current style identity while applying these shortcuts.
## 11. FINAL PRE-FLIGHT CHECK
- Is the hero a complete first scene?
- Do the headlines avoid weak line breaks?
- Does the navigation fit cleanly and feel style-specific?
- Are cards used only when they earn their place?
- Are loading, empty, and error states designed?
- Does the page have real image, media, diagram, or object weight?
- Would the result still feel specific if the logo was removed?
- Does motion match the style and stay professional?
- Did the code stay semantically clean, responsive, and production-ready?
- Does it feel chosen rather than broken?
- Is the aggression controlled?
- Did rawness replace polish without losing professionalism?
- Would one screenshot still feel unmistakable?
