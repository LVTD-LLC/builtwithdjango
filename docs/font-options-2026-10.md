# October 6 typography comparison

Rasul requested six homepage font options after the initial redesign. These are
historical previews. Rasul selected option 5 (Rubik + Nunito Sans) on October 6;
it is now the implementation target. All other options remain unselected.
The previews use the same homepage, logo, content, colors, and featured-card
styling, changing only heading/body fonts, heading weight and tracking.

| Option | Headings | Body/UI | Direction |
| --- | --- | --- | --- |
| 1 | Fraunces 600 | DM Sans | Playful editorial; recommended starting point |
| 2 | Bricolage Grotesque 600 | Manrope | Friendly, expressive sans-serif |
| 3 | Space Grotesk 600 | Work Sans | Independent developer publication |
| 4 | DM Serif Display 400 | DM Sans | Strong magazine-like contrast |
| 5 | Rubik 600 | Nunito Sans | Rounded and welcoming |
| 6 | IBM Plex Serif 600 | IBM Plex Sans | Bookish, technical, more restrained |

Font sources: Google Fonts specimens and CSS API, loaded into isolated local
preview pages only. Each font is actually downloaded and loaded before capture;
no screenshot relies on an unavailable font name or fallback approximation.

- https://fonts.google.com/specimen/Fraunces
- https://fonts.google.com/specimen/Bricolage+Grotesque
- https://fonts.google.com/specimen/Space+Grotesk
- https://fonts.google.com/specimen/DM+Serif+Display
- https://fonts.google.com/specimen/Rubik
- https://fonts.google.com/specimen/IBM+Plex+Serif

The original logo, removal of decorative eyebrows/arrows, direct section
headings, and stronger featured-project treatment are independent requested
refinements and ship without choosing a new font. Semantic post-type metadata
and advertisement disclosure remain, without eyebrow styling.

A selected production font should be self-hosted with its upstream license,
with only needed subsets/weights and a suitable fallback. Recheck final page
families for wrapping, contrast, focus and layout shift before deployment.
