# HPB-A3 factual visual standard

- Create one original, source-controlled `1200 × 675` SVG per article, plus a matching `1200 × 675` PNG social card. The SVG is the article hero and schema image; the PNG is the Open Graph/Twitter image for broad scraper compatibility.
- Prefer explanatory diagrams, comparison cards, decision flows, and checklists. Do not use decorative stock imagery, generated people, product endorsements, or unsourced measurements.
- Each SVG needs an accessible `<title>` and `<desc>`; each article needs specific image alt text and a visible caption that states the safety boundary.
- Safety diagrams describe general guidance only. Cite the controlling primary source in the article and state when manufacturer instructions, a local authority, qualified professional, policy, or code governs.
- Keep SVGs self-contained: no external fonts, scripts, or linked images. Preserve the `1200 × 675` viewBox and current HPB color palette.
- Add `og:image`, `twitter:image`, image dimensions/alt tags, and an `ImageObject` in Article schema. Verify every referenced asset and metadata URL after deployment.
- These hero visuals are intentionally eager because they are the first visual content in the article. Use `loading="lazy"` only for future below-the-fold visuals.
- `measurement.js` records source-reference clicks and related-cluster navigation through existing GA4 `gtag`; the outage checklist also records a print action. Never send personal or sensitive data in event parameters.
