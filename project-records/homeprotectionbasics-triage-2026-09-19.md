# HomeProtectionBasics triage / revival assessment - 2026-09-19

## Baseline relevant to Action 1

- Google Search Console had an accepted sitemap with 265 discovered URLs, but it had last read it on 2026-07-27. Google reported 19 indexed URLs and 32 crawled-but-not-indexed URLs.
- Bing Webmaster Tools had no submitted sitemap.
- The site uses GitHub Pages from the repository `main` branch. `robots.txt` permits crawling and points to `https://homeprotectionbasics.com/sitemap.xml`.
- The prior live audit found legacy `/favicon.png` references returning 404 and an empty `guides/basic-disaster-readiness-checklist.html` placeholder returning 404. The later SEO-hardening merge already removed that empty file and its invalid internal references before this Action 1 release; its absence is preserved here.

## Action 1 - crawl/indexing hygiene implementation - 2026-09-19

Scope was limited to discovery/indexing hygiene. No article body copy, site design, imagery, monetization, canonical URLs, or public article filenames were rewritten.

- Removed 167 legacy `<link rel="icon" href="/favicon.png">` declarations. The referenced asset does not exist. Each affected page retains working favicon declarations for the existing SVG, ICO, PNG, Apple-touch-icon, and manifest assets.
- Made `build_sitemap.py` independent of the invoking directory: it now always writes `sitemap.xml` at the repository root. This prevents a blank sitemap from being produced when the script is run from a different working directory.
- Excluded `project-records/` along with generated artifacts and scripts from sitemap discovery. The sitemap generator continues to use each page's canonical URL, skip noindex/missing/invalid canonical pages, and omit `404.html`.
- Regenerated `sitemap.xml` and the maintained `artifacts/sitemap-report.json`: 265 unique canonical URLs, zero duplicate URLs, zero missing canonicals, zero invalid canonical mappings, and no placeholder or artifact URL.
- Retained the existing robots policy because it is valid (`User-agent: *` and the canonical sitemap URL). No noindex, canonical, or robots directive directly blocking valid public pages was found in this release check.

## Validation before release

- Custom crawl validator: 265 local public pages, 265 sitemap URLs, 2,900 internal anchors, 0 failures. It validates every changed internal link plus canonical and sitemap URL/file correspondence.
- Link-repair dry run after the edit: 265 files checked, 0 remaining broken mapped links, 0 remaining `/favicon.png` references.
- Sitemap generator: 265 URLs; 0 duplicate, canonical-mismatch, missing-canonical, or invalid-canonical exclusions.
- Existing phase-one normalizer validation: 130 files checked, no validation failures, idempotence confirmed after its expected first normalization pass.
- `check_articles.py` could not run because its required `homeprotectionbasics-outline.md` is absent. It was not changed because it is unrelated to crawl/indexing hygiene.

## Release follow-up

- Deployed through the approved GitHub Pages `main` release path: commit `81ba42b9732392a87e3e7222789da3cb550f4205` on 2026-09-19.
- Live verification: homepage, `robots.txt`, `sitemap.xml`, the valid SVG favicon, and the emergency-kit guide returned HTTP 200; all 265 sitemap URLs returned HTTP 200. The legacy favicon reference and the old placeholder URL are absent from the live sitemap.
- Bing Webmaster Tools: submitted `https://homeprotectionbasics.com/sitemap.xml` on 2026-09-19. Bing displayed a successful-submission confirmation and recorded 265 discovered URLs; status is `Processing` while it recrawls (previous crawl was 2026-09-14).
- Google Search Console: resubmitted the same sitemap on 2026-09-19. Google displayed `Sitemap submitted successfully`; the sitemap table immediately shows submitted and last-read dates of 2026-09-19, `Success`, and 265 discovered pages.
- Search-engine recrawl cadence and final indexing decisions remain outside site control.

## HPB-A2 - priority content-cluster refresh - 2026-09-19

Scope was limited to ten URLs selected from the completed audit's demonstrated Google/Bing demand. Existing URLs, canonical URLs, search intent, navigation, and sitemap inclusion were retained. No image program, affiliate/monetization work, redesign, or broad conversion work was started.

### Pages refreshed

- Smoke-alarm cluster: `fire-safety/smoke-detector-placement-guide.html`, `photoelectric-vs-ionization-alarms.html`, `replacing-smoke-detectors.html`, `hardwired-vs-battery-smoke-detectors.html`, and `what-causes-smoke-detectors-to-chirp-or-beep.html`.
- Home-security/window-lock cluster: `home-security/home-security-systems-explained.html`, `window-lock-types-explained.html`, and `diy-vs-pro-security-systems.html`.
- Power-outage cluster: `emergency-prep/power-outage-prep-basics.html` and `guides/power-outage-readiness-checklist.html`.

### Material safety/trust corrections

- Replaced blanket smoke-alarm placement, spacing, type, replacement, garage, hardwiring, and chirp-fix assertions with USFA-backed general guidance plus explicit manufacturer, local-fire-authority, adopted-code, rental, and qualified-electrician boundaries. Removed the unsupported generic 30-foot spacing rule and the prior implication that one alarm type is universally better.
- Replaced claims that monitoring, cellular backup, a lock, professional installation, or a particular system feature guarantees protection or response. Added provider-contract, local dispatch/registration, privacy, emergency-egress, and qualified-installation limits.
- Added CPSC fall-prevention and fire-egress limits for window stops and guards; explicitly states that screens are not fall protection and that bedroom/egress openings must remain releasable as applicable.
- Corrected power-outage safety: CDC's outdoors-and-more-than-20-feet generator rule, no indoor combustion devices or gas-oven heating, CO-alarm use, qualified transfer-equipment requirement, and FoodSafety.gov food-temperature/time rules.

### Editorial/source implementation

- Added visible `Reviewed and updated: September 19, 2026` notes, visible primary-source reference sections, and `dateModified` Article schema to every refreshed page. Page metadata, Open Graph, Twitter, and Article schema descriptions now match the cautious updated claims.
- Primary sources used: U.S. Fire Administration smoke-alarm guidance and position statement; CDC power-outage and carbon-monoxide guidance; FoodSafety.gov emergency food-safety guidance; CPSC window-safety guidance; and CISA's physical/personal-security guidance.

### Validation and release preparation

- Targeted validation: 10 pages, 100 internal anchors, canonical/schema/review-date/source/sitemap checks, 0 failures.
- Existing normal phase-one article validation: 130 pages checked, 0 failures.
- Sitemap regenerated after content commit: 265 URLs; 0 duplicate, canonical-mismatch, missing-canonical, or invalid-canonical exclusions. `lastmod` values now reflect the current Action 1/Action 2 commit history.
- Deployed on the approved GitHub Pages `main` path in commits `e2575eaf46351ce8972ef1b14b622360066d5b61` and `7486fd5` on 2026-09-19. Live verification of all 10 refreshed URLs passed: HTTP 200, unchanged canonical URL, visible review date, visible source section, and `dateModified` Article schema.
