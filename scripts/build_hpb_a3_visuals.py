#!/usr/bin/env python3
"""Build HPB-A3's reusable, factual SVG visual system for the ten priority pages."""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VISUAL_DIR = ROOT / "assets" / "hpb-a3"
BASE_URL = "https://homeprotectionbasics.com"
WIDTH, HEIGHT = 1200, 675
GA4_ID = "G-7NMENZF6EK"
GA4_SNIPPET = f'''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA4_ID}');
</script>'''

PAGES = {
    "fire-safety/smoke-detector-placement-guide.html": {
        "slug": "smoke-alarm-placement", "kind": "placement", "title": "Smoke alarm coverage",
        "subtitle": "Sleeping rooms • sleeping areas • every level",
        "alt": "Simplified three-level home diagram showing general smoke-alarm coverage inside bedrooms, outside sleeping areas, and on each level, with a note to check the alarm label and local rules.",
        "caption": "General USFA guidance visualized—not a code plan. Follow the alarm instructions and local authority for a specific home.",
        "cards": [("Bedroom", ["Alarm inside", "sleeping room"]), ("Sleeping area", ["Alarm outside", "separate area"]), ("Every level", ["Include", "basement"])],
    },
    "fire-safety/photoelectric-vs-ionization-alarms.html": {
        "slug": "smoke-alarm-types", "kind": "comparison", "title": "Two sensing approaches",
        "subtitle": "Coverage and placement matter as much as technology",
        "alt": "Comparison diagram stating that photoelectric alarms tend to respond faster to smoldering-fire smoke, ionization alarms tend to respond faster to flaming-fire smoke, and both or dual-sensor coverage is recommended by USFA.",
        "caption": "Both technologies can detect smoke. This comparison shows general USFA guidance; it does not select a product or override local requirements.",
        "cards": [("Photoelectric", ["Tends to respond", "faster to smoldering", "fire smoke"]), ("Ionization", ["Tends to respond", "faster to flaming", "fire smoke"]), ("Coverage", ["Both types or", "dual-sensor", "where people sleep"])],
    },
    "fire-safety/replacing-smoke-detectors.html": {
        "slug": "replace-smoke-alarms", "kind": "flow", "title": "Replace, then verify coverage",
        "subtitle": "The test button does not reset service life",
        "alt": "Three-step flow diagram: check the manufacture date and label, replace at end of life or after a failed test, then test the replacement and interconnected coverage.",
        "caption": "USFA's general benchmark is 10 years from manufacture; the individual alarm label and compatible system instructions control.",
        "cards": [("1. Check", ["Manufacture date", "and label"]), ("2. Replace", ["End-of-life, failed", "test, or directed"]), ("3. Verify", ["Test unit and", "interconnection"])],
    },
    "fire-safety/hardwired-vs-battery-smoke-detectors.html": {
        "slug": "hardwired-vs-battery", "kind": "comparison", "title": "Power source is not sensing type",
        "subtitle": "Both still need placement, testing, and replacement",
        "alt": "Comparison diagram explaining that hardwired smoke alarms commonly use backup batteries and may interconnect, while battery alarms may use replaceable or sealed long-life batteries; both require label-based maintenance.",
        "caption": "Hardwired installation and system changes require qualified electrical help. Follow the exact product and local requirements.",
        "cards": [("Hardwired", ["Household power", "often battery backup", "may interconnect"]), ("Battery", ["Replaceable or", "sealed long-life", "battery models"]), ("Both", ["Test monthly", "replace per label", "keep coverage"])],
    },
    "fire-safety/what-causes-smoke-detectors-to-chirp-or-beep.html": {
        "slug": "smoke-alarm-chirp", "kind": "flow", "title": "A safe chirp-check sequence",
        "subtitle": "Treat a full alarm or signs of fire as an emergency",
        "alt": "Troubleshooting flow diagram: if there is smoke, fire, or uncertainty, evacuate and call 911; otherwise use the model manual, check the age and approved battery, and seek qualified help for hardwired or unresolved faults.",
        "caption": "Chirp patterns are model-specific. Do not remove a battery or change house wiring to stop a sound.",
        "cards": [("Emergency?", ["Smoke, fire, or", "uncertainty: leave", "and call 911"]), ("No sign of fire", ["Find model manual", "check age and", "approved battery"]), ("Still unresolved", ["Hardwired or linked", "system: qualified", "help or manufacturer"])],
    },
    "home-security/home-security-systems-explained.html": {
        "slug": "security-system-layers", "kind": "layers", "title": "A security system is one layer",
        "subtitle": "Coverage, alert path, and household routine work together",
        "alt": "Layered home-security diagram showing physical locks and lighting, entry and motion detection, power and connectivity, and monitoring terms and privacy as complementary considerations.",
        "caption": "Layers can reduce risk; they do not guarantee prevention, dispatch, or a particular outcome.",
        "cards": [("Physical layer", ["Locks", "lighting", "visibility"]), ("Detection", ["Entry contacts", "motion paths", "alerts"]), ("Response", ["Backup power", "connectivity", "service terms"])],
    },
    "home-security/window-lock-types-explained.html": {
        "slug": "window-lock-balance", "kind": "layers", "title": "Window hardware has three jobs",
        "subtitle": "Security • fall prevention • emergency escape",
        "alt": "Window safety balance diagram showing compatible locking hardware, child-fall prevention measures, and releasable emergency-egress hardware; it notes that screens are not fall protection.",
        "caption": "A bedroom or egress opening must remain usable as required by the product instructions and applicable code.",
        "cards": [("Security", ["Compatible latch", "or lock", "maintained fit"]), ("Fall prevention", ["Guards or stops", "when appropriate", "screens are not guards"]), ("Escape", ["Releasable from", "inside when", "required"])],
    },
    "home-security/diy-vs-pro-security-systems.html": {
        "slug": "diy-vs-professional", "kind": "comparison", "title": "Choose the installation path",
        "subtitle": "Match the work to the home, terms, and required expertise",
        "alt": "Comparison graphic stating that DIY can suit compatible non-electrical equipment and regular testing, while professional help is appropriate for electrical work, complex systems, permits, or required documentation; both need testing and terms review.",
        "caption": "Neither installation path guarantees prevention or emergency response. Provider terms and local requirements control.",
        "cards": [("DIY may fit", ["Compatible equipment", "no electrical changes", "owner tests system"]), ("Professional help", ["Electrical work", "complex building", "permit or support need"]), ("Either path", ["Test alerts", "read service terms", "keep exits clear"])],
    },
    "emergency-prep/power-outage-prep-basics.html": {
        "slug": "power-outage-safety", "kind": "flow", "title": "Power-outage safety priorities",
        "subtitle": "Prepare • protect from CO • make temperature-based decisions",
        "alt": "Three-stage power-outage diagram showing preparation supplies, generator use outdoors more than 20 feet from windows doors and vents with a CO alarm indoors, and food-safety checks based on time and temperature.",
        "caption": "CDC and FoodSafety.gov general guidance shown here; local emergency instructions and product manuals control during an event.",
        "cards": [("Prepare", ["Lighting, charging", "thermometers", "medical plan"]), ("Prevent CO", ["Generator outdoors", "more than 20 feet", "from openings"]), ("Protect food", ["Keep doors closed", "use time and", "temperature guidance"])],
    },
    "guides/power-outage-readiness-checklist.html": {
        "slug": "power-outage-checklist", "kind": "checklist", "title": "Power-outage readiness at a glance",
        "subtitle": "A practical check before the lights go out",
        "alt": "Four-panel power-outage checklist graphic covering lighting and communications, food and medication plans, generator and carbon-monoxide safety, and recovery steps after power returns.",
        "caption": "Use official local alerts during an event. This visual supports the checklist; it does not replace medical, electrical, or public-health directions.",
        "cards": [("Light & communicate", ["Flashlights", "power banks", "weather radio"]), ("Food & medication", ["Thermometers", "safe water", "care plan"]), ("Generator & CO", ["Outdoors only", ">20 ft from openings", "working CO alarm"]), ("After power", ["Check temperatures", "reset systems", "restock supplies"])],
    },
}

def esc(value: str) -> str:
    return html.escape(value, quote=True)

def label(x: int, y: int, value: str, size: int, color: str = "#eef6ff", weight: int = 400, anchor: str = "start") -> str:
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{esc(value)}</text>'

def card(x: int, y: int, w: int, h: int, heading: str, lines: list[str], accent: str) -> str:
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="#162438" stroke="#2e4665" stroke-width="2"/>']
    out.append(f'<rect x="{x}" y="{y}" width="10" height="{h}" rx="5" fill="{accent}"/>')
    out.append(label(x + 38, y + 52, heading, 26, "#ffffff", 700))
    for index, line in enumerate(lines):
        out.append(label(x + 38, y + 96 + index * 34, line, 21, "#c8d8ea"))
    return "".join(out)

def base(page: dict[str, str], body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
<title id="title">{esc(page['title'])}</title><desc id="desc">{esc(page['alt'])}</desc>
<rect width="1200" height="675" fill="#0f1520"/><path d="M0 552 C260 480 432 648 720 550 S1030 458 1200 545 L1200 675 L0 675 Z" fill="#12253a"/>
<rect x="48" y="42" width="250" height="36" rx="18" fill="#17324d"/>{label(173, 67, "HOME PROTECTION BASICS", 17, "#8bc5ff", 700, "middle")}
{label(48, 128, page['title'], 42, "#ffffff", 700)}{label(48, 166, page['subtitle'], 23, "#b8d6f3")}{body}
<line x1="48" y1="625" x2="1152" y2="625" stroke="#2e4665" stroke-width="2"/>{label(48, 655, "Factual visual • General guidance • Check product instructions and local requirements", 16, "#a9bdd3")}
</svg>'''

def comparison(page: dict[str, str]) -> str:
    body = '<path d="M76 212 H1124" stroke="#365575" stroke-width="2"/>'
    for i, (heading, lines) in enumerate(page["cards"]):
        body += card(68 + i * 378, 232, 344, 320, heading, lines, ["#8bc5ff", "#f5b971", "#85d6b6"][i])
    return base(page, body)

def flow(page: dict[str, str]) -> str:
    body = ''
    for i, (heading, lines) in enumerate(page["cards"]):
        x = 68 + i * 376
        body += card(x, 246, 312, 280, heading, lines, ["#8bc5ff", "#f5b971", "#85d6b6"][i])
        if i < 2:
            body += f'<path d="M{x + 322} 386 H{x + 358}" stroke="#8bc5ff" stroke-width="5"/><path d="M{x + 358} 386 l-14 -11 m14 11 l-14 11" stroke="#8bc5ff" stroke-width="5" fill="none"/>'
    return base(page, body)

def layers(page: dict[str, str]) -> str:
    body = '<circle cx="600" cy="410" r="156" fill="#152f48" stroke="#2e607e" stroke-width="3"/><circle cx="600" cy="410" r="112" fill="#193955" stroke="#4b7fa3" stroke-width="3"/><path d="M530 420 v70 h140 v-70 l-70 -62z" fill="#8bc5ff" opacity=".88"/><rect x="580" y="446" width="40" height="44" rx="5" fill="#0f1520"/>'
    body += label(600, 535, "A safer home uses layers", 22, "#dceeff", 700, "middle")
    for (heading, lines), (x, y, h) in zip(page["cards"], [(68, 254, 168), (856, 254, 168), (856, 425, 175)]):
        body += card(x, y, 276, h, heading, lines, "#85d6b6" if y == 425 else "#8bc5ff")
    return base(page, body)

def placement(page: dict[str, str]) -> str:
    body = '<path d="M220 540 V384 L408 270 L596 384 V540" fill="#152e46" stroke="#8bc5ff" stroke-width="4"/><path d="M596 540 V414 L744 324 L892 414 V540" fill="#17324d" stroke="#8bc5ff" stroke-width="4"/>'
    for x, y, room in [(318, 462, "Bedroom"), (494, 462, "Bedroom"), (704, 492, "Sleeping area")]:
        body += f'<circle cx="{x}" cy="{y}" r="20" fill="#f5b971"/><circle cx="{x}" cy="{y}" r="7" fill="#0f1520"/>' + label(x, y + 52, room, 18, "#dceeff", 700, "middle")
    body += '<line x1="194" y1="540" x2="918" y2="540" stroke="#85d6b6" stroke-width="7"/>' + label(556, 586, "Every level, including basement", 20, "#bdebd7", 700, "middle")
    for i, (heading, lines) in enumerate(page["cards"]):
        body += card(68 + i * 360, 190, 292, 145, heading, lines, "#8bc5ff" if i != 1 else "#f5b971")
    return base(page, body)

def checklist(page: dict[str, str]) -> str:
    body = ''
    for i, (heading, lines) in enumerate(page["cards"]):
        x, y = (68 + (i % 2) * 550, 220 + (i // 2) * 188)
        body += f'<rect x="{x}" y="{y}" width="510" height="154" rx="20" fill="#162438" stroke="#2e4665" stroke-width="2"/>' + label(x + 34, y + 44, heading, 25, "#ffffff", 700)
        for j, line in enumerate(lines):
            yy = y + 82 + j * 27
            body += f'<rect x="{x + 34}" y="{yy - 17}" width="17" height="17" rx="3" fill="none" stroke="#85d6b6" stroke-width="3"/>' + label(x + 64, yy, line, 19, "#c8d8ea")
    return base(page, body)

BUILDERS = {"comparison": comparison, "flow": flow, "layers": layers, "placement": placement, "checklist": checklist}

def figure(page: dict[str, str]) -> str:
    src = f"/assets/hpb-a3/{page['slug']}.svg"
    return f'''<figure class="hpb-visual" data-hpb-visual="{page['slug']}"><img src="{src}" width="1200" height="675" alt="{esc(page['alt'])}" decoding="async" fetchpriority="high"/><figcaption>{page['caption']}</figcaption></figure>'''

def metadata(page: dict[str, str]) -> str:
    url = f"{BASE_URL}/assets/hpb-a3/social/{page['slug']}.png"
    return f'''<meta property="og:image" content="{url}"/><meta property="og:image:secure_url" content="{url}"/><meta property="og:image:type" content="image/png"/><meta property="og:image:width" content="1200"/><meta property="og:image:height" content="675"/><meta property="og:image:alt" content="{esc(page['alt'])}"/><meta name="twitter:image" content="{url}"/><meta name="twitter:image:alt" content="{esc(page['alt'])}"/>'''

def update_page(relative: str, page: dict[str, str]) -> None:
    path = ROOT / relative
    source = path.read_text(encoding="utf-8")
    if GA4_ID not in source:
        source = source.replace('</head>', GA4_SNIPPET + '\n</head>', 1)
    if f'/assets/hpb-a3/{page["slug"]}.svg' in source:
        source = source.replace('<meta content="summary" name="twitter:card"/>', '<meta content="summary_large_image" name="twitter:card"/>')
        source, metadata_count = re.subn(r'<meta property="og:image" content="[^"]+"/><meta property="og:image:secure_url" content="[^"]+"/><meta property="og:image:type" content="[^"]+"/><meta property="og:image:width" content="1200"/><meta property="og:image:height" content="675"/><meta property="og:image:alt" content="[^"]+"/><meta name="twitter:image" content="[^"]+"/><meta name="twitter:image:alt" content="[^"]+"/>', metadata(page), source, count=1)
        if metadata_count != 1:
            raise RuntimeError(f"Missing existing HPB-A3 metadata: {relative}")
        path.write_text(source, encoding="utf-8", newline="\n")
        return
    source = source.replace('<link href="/style.css" rel="stylesheet"/>', '<link href="/style.css" rel="stylesheet"/>\n<link href="/assets/hpb-a3/visuals.css" rel="stylesheet"/>')
    source = source.replace('<meta content="summary" name="twitter:card"/>', '<meta content="summary_large_image" name="twitter:card"/>')
    source = source.replace('</head>', metadata(page) + '\n</head>', 1)
    source, figure_count = re.subn(r'(<p class="article-meta">.*?</p>)', r'\1\n' + figure(page), source, count=1, flags=re.S)
    if figure_count != 1:
        raise RuntimeError(f"Missing article-meta anchor: {relative}")
    image_schema = f'''"image": {{"@type": "ImageObject", "url": "{BASE_URL}/assets/hpb-a3/{page['slug']}.svg", "width": {WIDTH}, "height": {HEIGHT}, "caption": "{page['title']}"}},'''
    source, schema_count = re.subn(r'("dateModified"\s*:\s*"2026-09-19",)', r'\1\n    ' + image_schema, source, count=1)
    if schema_count != 1:
        raise RuntimeError(f"Missing dateModified schema anchor: {relative}")
    source = source.replace('<hr/><p><strong>Next:</strong>', '<hr/><p class="hpb-related-links"><strong>Next:</strong>')
    source = source.replace('<hr/><p><strong>More detail:</strong>', '<hr/><p class="hpb-related-links"><strong>More detail:</strong>')
    if relative == "guides/power-outage-readiness-checklist.html":
        source = source.replace('</figure>', '</figure>\n<p class="hpb-article-action"><button type="button" class="hpb-print-button" data-hpb-print>Print this checklist</button></p>', 1)
    source = source.replace('</body>', '<script defer src="/assets/hpb-a3/measurement.js"></script>\n</body>', 1)
    path.write_text(source, encoding="utf-8", newline="\n")

def main() -> None:
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    for relative, page in PAGES.items():
        (VISUAL_DIR / f"{page['slug']}.svg").write_text(BUILDERS[page["kind"]](page), encoding="utf-8", newline="\n")
        update_page(relative, page)
        print(relative)

if __name__ == "__main__":
    main()
