# Selected typography (option 5)

Rasul selected Rubik headings + Nunito Sans body/UI on 2026-10-06.
SIL Open Font License 1.1; unmodified upstream licenses included.

Sources: https://fonts.google.com/specimen/Rubik and
https://fonts.google.com/specimen/Nunito+Sans. Licenses from
https://github.com/google/fonts/tree/main/ofl/rubik and
https://github.com/google/fonts/tree/main/ofl/nunitosans.

WOFF2 variable fonts downloaded from Google's CSS2 API on 2026-10-06:
- `family=Rubik:wght@400..900&display=swap`
- `family=Nunito+Sans:ital,wght@0,400..900;1,400..900&display=swap`

Latin and Latin Extended subsets preserve names with diacritics; other scripts
use system fallbacks. Unicode ranges keep unused subsets from loading. Rubik
headings use 600; Nunito Sans supports existing 400–900 UI weights and real
body italics. Font display is swap; there is no runtime Google Fonts request.
Webpack/Django serve local assets with the normal static caching pipeline.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `rubik-normal-latin-ext.woff2` | 19,400 | `09472f217ad1ebb61a7669cf532f9f2f80685e07652ee862fde9a79665aef479` |
| `rubik-normal-latin.woff2` | 35,348 | `691cd1d9b4c0cdf31a1dcf04259c86f92c85e69f6622abab7964d81e36890691` |
| `nunitosans-italic-latin-ext.woff2` | 30,344 | `f3093f72aabbc08b8f00f185aef1b9503519a227c3d75a057dc7a3c47d7c6151` |
| `nunitosans-italic-latin.woff2` | 33,080 | `8904d953726b43ded1a16bfd43398325d2382dd50780c10f18d048e0e73f84a8` |
| `nunitosans-normal-latin-ext.woff2` | 27,908 | `c648ee5bfda70d44b9fb628f4114d1cc4f984d050cbb4881052237ede3638a2e` |
| `nunitosans-normal-latin.woff2` | 31,076 | `29e3890496844a9ea81975c52771c587c872b4eb317026422d1995b88d21b57d` |
