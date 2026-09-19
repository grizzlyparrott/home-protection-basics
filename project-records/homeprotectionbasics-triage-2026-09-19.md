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

- Deployment commit and the live verification/submission result are recorded in the release response for this Action 1 task. Search-engine re-crawl and indexing decisions remain controlled by Google and Bing.
