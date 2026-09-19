"""Validate HPB-A3 visual, metadata, and internal-link requirements for the ten priority pages."""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

from build_hpb_a3_visuals import BASE_URL, HEIGHT, PAGES, ROOT, WIDTH


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def local_target(href: str) -> Path | None:
    if href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlparse(href)
    if parsed.scheme and parsed.netloc not in ("homeprotectionbasics.com", "www.homeprotectionbasics.com"):
        return None
    path = parsed.path
    if not path:
        return ROOT / "index.html"
    if path.endswith("/"):
        return ROOT / path.lstrip("/") / "index.html"
    return ROOT / path.lstrip("/")


def validate_svg(path: Path) -> None:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        fail(f"invalid SVG {path}: {exc}")
    if root.attrib.get("viewBox") != f"0 0 {WIDTH} {HEIGHT}" or root.attrib.get("width") != str(WIDTH) or root.attrib.get("height") != str(HEIGHT):
        fail(f"wrong SVG dimensions: {path}")
    source = path.read_text(encoding="utf-8")
    if "<title " not in source or "<desc " not in source:
        fail(f"missing SVG accessible name/description: {path}")
    if re.search(r"<(?:image|script)[ >]|(?:href|src)=\"https?://", source, flags=re.I):
        fail(f"SVG must be self-contained: {path}")
    if path.stat().st_size > 10_000:
        fail(f"SVG exceeds visual-system budget: {path}")


def validate_page(relative: str, page: dict[str, str]) -> None:
    path = ROOT / relative
    source = path.read_text(encoding="utf-8")
    slug = page["slug"]
    hero = f"/assets/hpb-a3/{slug}.svg"
    social = f"{BASE_URL}/assets/hpb-a3/social/{slug}.png"
    expected = [
        f'<link href="/assets/hpb-a3/visuals.css" rel="stylesheet"/>',
        'https://www.googletagmanager.com/gtag/js?id=G-7NMENZF6EK',
        f'<figure class="hpb-visual" data-hpb-visual="{slug}"><img src="{hero}" width="1200" height="675"',
        f'fetchpriority="high"',
        f'<meta content="summary_large_image" name="twitter:card"/>',
        f'<meta property="og:image" content="{social}"/>',
        f'<meta property="og:image:type" content="image/png"/>',
        f'<meta name="twitter:image" content="{social}"/>',
        f'"@type": "ImageObject", "url": "{BASE_URL}{hero}", "width": {WIDTH}, "height": {HEIGHT}',
        '<script defer src="/assets/hpb-a3/measurement.js"></script>',
        f'<link href="{BASE_URL}/{relative}" rel="canonical"/>',
    ]
    for value in expected:
        if value not in source:
            fail(f"missing A3 requirement in {relative}: {value}")
    if 'loading="lazy"' in re.search(r'<figure class="hpb-visual".*?</figure>', source, flags=re.S).group(0):
        fail(f"above-the-fold hero must not be lazy-loaded: {relative}")
    if source.count(f'data-hpb-visual="{slug}"') != 1:
        fail(f"expected exactly one visual in {relative}")
    if not (ROOT / hero.lstrip("/")).is_file() or not (ROOT / urlparse(social).path.lstrip("/")).is_file():
        fail(f"missing hero or social asset for {relative}")
    for href in re.findall(r'href="([^"]+)"', source):
        target = local_target(href)
        if target and not target.is_file():
            fail(f"broken internal link in {relative}: {href} -> {target}")
    if relative == "guides/power-outage-readiness-checklist.html" and 'data-hpb-print' not in source:
        fail("missing checklist print measurement hook")


def main() -> None:
    for relative, page in PAGES.items():
        validate_svg(ROOT / "assets" / "hpb-a3" / f"{page['slug']}.svg")
        validate_page(relative, page)
    js = (ROOT / "assets" / "hpb-a3" / "measurement.js").read_text(encoding="utf-8")
    for event in ("hpb_checklist_print", "hpb_source_open", "hpb_cluster_navigation"):
        if event not in js:
            fail(f"missing GA4 measurement event: {event}")
    print(f"PASS: HPB-A3 visual system validated for {len(PAGES)} priority pages")


if __name__ == "__main__":
    main()
