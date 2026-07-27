#!/usr/bin/env python3
"""Phase 1 article normalization tooling for Home Protection Basics.

This script builds a page inventory and applies a deterministic, minimally
intrusive normalizer to article pages.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup, NavigableString, Tag


ROOT_DIR = Path(__file__).resolve().parents[4]
CANARY_PAGES = {
    "fire-safety/smoke-detector-placement-guide.html",
    "fire-safety/replacing-smoke-detectors.html",
    "fire-safety/alarms-for-high-ceiling-homes.html",
    "fire-safety/photoelectric-vs-ionization-alarms.html",
    "guides/kitchen-fire-safety-checklist.html",
}
BASE_SITE = "https://homeprotectionbasics.com"
GA_ID = "G-7NMENZF6EK"
OUT_ROOT = ROOT_DIR / "artifacts" / "article-normalization" / "phase1"
OUT_ROOT.mkdir(parents=True, exist_ok=True)

MARKDOWN_RE = re.compile(r"\*\*(.+?)\*\*")
SECTION_LINKS = {
    "fire-safety": "Fire Safety",
    "home-security": "Home Security",
    "insurance-basics": "Insurance Basics",
    "emergency-prep": "Emergency Prep",
    "guides": "Checklists & Guides",
}
BROKEN_LINK_REPAIR_MAP = {
    "../guides/home-fire-safety-checklist.html": "/guides/monthly-home-safety-checklist.html",
    "/guides/home-fire-safety-checklist.html": "/guides/monthly-home-safety-checklist.html",
    "../insurance-basics/flood-preparedness-basics.html": "/emergency-prep/flood-preparedness-basics.html",
    "/home-security/security-lighting-basics.html": "/home-security/security-lighting-placement.html",
    "../guides/heating-equipment-safety-checklist.html": "/emergency-prep/fuel-storage-safety-basics.html",
    "../guides/fire-escape-plan-checklist.html": "/fire-safety/home-fire-escape-plan-checklist.html",
    "/guides/home-security-walkthrough-checklist.html": "/guides/home-safety-annual-review.html",
    "../guides/children-home-safety-checklist.html": "/guides/in-home-child-safety-inspection.html",
    "insurance-proof-and-documents.html": "/insurance-basics/insurance-proof-and-documents.html",
}


def collect_html_files() -> list[Path]:
    return sorted(
        [
            p
            for p in ROOT_DIR.rglob("*.html")
            if p.is_file() and not p.name.startswith(".")
        ]
    )


def rel_path(path: Path) -> str:
    return str(path.relative_to(ROOT_DIR)).replace("\\", "/")


def load_soup(path: Path) -> BeautifulSoup:
    raw = path.read_text(encoding="utf-8", errors="replace")
    return BeautifulSoup(raw, "html.parser")


def write_soup(path: Path, soup: BeautifulSoup) -> None:
    path.write_text(str(soup), encoding="utf-8")


def expected_canonical(rel: str) -> str:
    if rel == "index.html":
        return f"{BASE_SITE}/"
    if rel.endswith("/index.html"):
        return f"{BASE_SITE}/{Path(rel).parent.as_posix()}/"
    return f"{BASE_SITE}/{rel}"


def classify_page(rel: str, soup: BeautifulSoup) -> str:
    if rel == "index.html":
        return "homepage"
    if rel == "404.html" or rel == "guides/basic-disaster-readiness-checklist.html":
        return "utility/legal"
    if rel.endswith("/index.html"):
        if rel == "guides/index.html":
            return "guide hub"
        return "category hub"

    title = soup.title.get_text(strip=True) if soup.title else ""
    canonical = soup.find("link", rel="canonical") is not None
    h1_count = len(soup.find_all("h1"))
    article_count = len(soup.find_all("article"))
    if title and canonical and h1_count == 1 and article_count >= 1:
        return "article"
    if title and canonical:
        return "article"
    return "unknown/manual review"


def header_variant(soup: BeautifulSoup) -> str:
    header = soup.find("header")
    if not header:
        return "missing"
    has_title = bool(header.find("a", class_="site-title"))
    nav = header.find("nav")
    if not nav:
        return "header-without-nav"
    has_container = bool(header.find(class_="container"))
    return "standard" if has_container and has_title and bool(nav.find_all("li")) else "partial"


def navigation_variant(soup: BeautifulSoup) -> str:
    nav = soup.find("nav")
    if not nav:
        return "missing"
    items = nav.find_all("li", recursive=False)
    if not items:
        return "empty"
    states = ["active" if not li.find("a") else "linked" for li in items]
    return f"{len(items)}-item:{'/'.join(states)}"


def footer_variant(soup: BeautifulSoup) -> str:
    footer = soup.find("footer")
    if not footer:
        return "missing"
    if footer.find("span", id="current-year"):
        return "standard"
    return "non-standard"


def jsonld_types(soup: BeautifulSoup) -> list[str]:
    types: list[str] = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        text = tag.get_text(strip=True)
        if not text:
            continue
        try:
            obj = json.loads(text)
            if isinstance(obj, list):
                objs = obj
            else:
                objs = [obj]
            for entry in objs:
                if isinstance(entry, dict):
                    t = entry.get("@type")
                    if isinstance(t, str) and t not in types:
                        types.append(t)
        except json.JSONDecodeError:
            continue
    return types


def classify_links(rel: str, soup: BeautifulSoup) -> dict:
    counts = {
        "root_relative": 0,
        "parent_relative": 0,
        "self_relative": 0,
        "external": 0,
        "other_relative": 0,
        "anchor_only": 0,
        "other": 0,
    }

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"].strip()
        if href.startswith("#"):
            counts["anchor_only"] += 1
            continue
        if href.startswith(("mailto:", "tel:", "javascript:")):
            counts["other"] += 1
            continue
        if href.startswith("http://") or href.startswith("https://"):
            counts["external"] += 1
            continue
        if href.startswith("/"):
            counts["root_relative"] += 1
            continue
        if href.startswith("../"):
            counts["parent_relative"] += 1
            continue
        if href.startswith("./"):
            counts["self_relative"] += 1
            continue
        if href:
            counts["other_relative"] += 1

    active = [k for k, v in counts.items() if v > 0]
    return {
        "style": ", ".join(active) if active else "none",
        "counts": counts,
    }


def find_malformed_html(soup: BeautifulSoup) -> list[str]:
    issues = []
    for tag in ["html", "head", "body", "main", "title", "article"]:
        count = len(soup.find_all(tag))
        if count == 0:
            issues.append(f"missing <{tag}>")
        elif tag in {"main", "article", "title"} and count > 1:
            issues.append(f"multiple <{tag}>")

    return issues


def has_literal_markdown(soup: BeautifulSoup) -> bool:
    article = soup.find("article") or soup.body
    if not article:
        return False

    text = article.get_text(" ", strip=False)
    return bool(MARKDOWN_RE.search(text))


def markdown_to_strong(soup: BeautifulSoup, article: Tag) -> bool:
    changed = False
    nodes = list(article.find_all(string=True))
    for node in nodes:
        if not isinstance(node, NavigableString):
            continue
        if isinstance(node.parent, Tag) and node.parent.name in {"script", "style"}:
            continue
        raw = str(node)
        if not MARKDOWN_RE.search(raw):
            continue
        replaced = MARKDOWN_RE.sub(r"<strong>\1</strong>", raw)
        fragment = BeautifulSoup(replaced, "html.parser")
        parent = node.parent
        if parent is None:
            continue
        new_nodes = list(fragment.contents)
        node.insert_before(*new_nodes)
        node.extract()
        changed = True
    return changed


def current_section_from_path(rel: str) -> str:
    if "/" in rel:
        top = rel.split("/")[0]
        return SECTION_LINKS.get(top, "")
    return ""


def ensure_active_nav(soup: BeautifulSoup, rel: str) -> bool:
    nav = soup.find("nav")
    if not nav:
        return False
    section = current_section_from_path(rel)
    if not section:
        return False

    changed = False
    links = nav.find_all("li")
    for li in links:
        text = li.get_text(" ", strip=True)
        if text in SECTION_LINKS.values():
            if li.find("a"):
                # preserve clickability for category link, but mark active state consistently.
                anchor = li.find("a")
                current = anchor.get_text(strip=True) == section
                if current:
                    if anchor.get("aria-current") != "page":
                        anchor["aria-current"] = "page"
                        changed = True
                elif anchor.get("aria-current") == "page":
                    # Clean up stale marks on previously normalized pages that did not retain section context.
                    del anchor.attrs["aria-current"]
                    changed = True
                if current and anchor.get("data-active") != "true":
                    anchor["data-active"] = "true"
                    changed = True
                elif current and "data-active" in anchor.attrs:
                    changed = False
            else:
                classes = set(li.get("class", []))
                if "is-current" not in classes:
                    classes.add("is-current")
                    li["class"] = sorted(classes)
                    changed = True
    return changed


def ensure_article_shell(soup: BeautifulSoup) -> bool:
    changed = False
    main = soup.find("main")
    article = soup.find("article")
    if not main or not article:
        return False

    main_class = set(main.get("class", []))
    if "article-main" not in main_class:
        main_class.add("article-main")
        main["class"] = sorted(main_class)
        changed = True

    article_class = set(article.get("class", []))
    if "article-shell" not in article_class:
        article_class.add("article-shell")
        article_class.add("container")
        article["class"] = sorted(article_class)
        changed = True

    for table in article.find_all("table"):
        if table.parent and table.parent.name == "div" and "article-table-wrap" in table.parent.get("class", []):
            continue
        wrapper = soup.new_tag("div")
        wrapper["class"] = ["article-table-wrap"]
        table.wrap(wrapper)
        changed = True
    return changed


def ensure_ga(soup: BeautifulSoup) -> bool:
    scripts = soup.find_all("script")
    ga_configs = []
    for script in scripts:
        if script.string and GA_ID in script.string:
            if "gtag('config', '" + GA_ID + "')" in script.string or f'gtag("config", "{GA_ID}")' in script.string:
                ga_configs.append(script)
    return len(ga_configs) == 1


def normalize_links(soup: BeautifulSoup, rel: str) -> bool:
    current_path = Path(rel)
    changed = False
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if href.startswith(("#", "mailto:", "tel:", "javascript:", "http://", "https://")):
            continue
        if href == "/":
            continue
        if href in {"/.", "./", "../", ".", ""}:
            if href != "/":
                tag["href"] = "/"
                changed = True
            continue
        if href in BROKEN_LINK_REPAIR_MAP:
            tag["href"] = BROKEN_LINK_REPAIR_MAP[href]
            changed = True
            continue
        split = urlsplit(href)
        if split.scheme or split.netloc:
            continue
        path = split.path
        fragment = split.fragment

        if path.startswith("/"):
            candidate = ROOT_DIR / path.lstrip("/")
        else:
            candidate = (ROOT_DIR / current_path.parent / path).resolve()
            try:
                candidate = candidate.relative_to(ROOT_DIR)
            except ValueError:
                continue
            candidate = ROOT_DIR / candidate

        if not candidate.exists():
            continue

        if path.startswith("http://") or path.startswith("https://"):
            continue

        if split.path == "/":
            normalized = "/"
        else:
            normalized = "/" + str(candidate.relative_to(ROOT_DIR)).replace("\\", "/")
        if split.query:
            normalized = f"{normalized}?{split.query}"
        if fragment:
            normalized = f"{normalized}#{fragment}"

        if normalized != href:
            tag["href"] = normalized
            changed = True
    return changed


def build_inventory() -> list[dict]:
    rows = []
    confirmed_articles: list[str] = []

    for path in collect_html_files():
        rel = rel_path(path)
        soup = load_soup(path)

        classification = classify_page(rel, soup)
        title = soup.title.get_text(strip=True) if soup.title else ""
        canonical = soup.find("link", rel="canonical")
        canonical_url = canonical.get("href", "") if canonical else ""
        jsonld = jsonld_types(soup)
        h1_count = len(soup.find_all("h1"))
        article_count = len(soup.find_all("article"))
        stylesheet_refs = [l.get("href", "") for l in soup.find_all("link", rel="stylesheet")]

        head = soup.head or soup
        analytics_presence = bool(soup.find(string=re.compile(re.escape(GA_ID))))
        malformed = find_malformed_html(soup)
        rel_style = classify_links(rel, soup)

        rows.append(
            {
                "file": rel,
                "classification": classification,
                "title": title,
                "canonical_url": canonical_url,
                "h1_count": h1_count,
                "article_element_count": article_count,
                "stylesheet_references": stylesheet_refs,
                "analytics_presence": analytics_presence,
                "header_variant": header_variant(soup),
                "navigation_variant": navigation_variant(soup),
                "footer_variant": footer_variant(soup),
                "jsonld_presence": bool(jsonld),
                "jsonld_types": jsonld,
                "obvious_malformed_html": bool(malformed),
                "obvious_malformed_html_issues": malformed,
                "literal_markdown_in_rendered_content": has_literal_markdown(soup),
                "relative_link_style": rel_style,
            }
        )

        if classification == "article":
            confirmed_articles.append(rel)

    confirmed_articles.sort()
    phase1_count = (len(confirmed_articles) + 1) // 2
    phase1_set = set(confirmed_articles[:phase1_count])
    canary_exceptions = []
    for page in CANARY_PAGES:
        if page not in phase1_set:
            phase1_set.add(page)
            canary_exceptions.append(page)

    for row in rows:
        row["phase1_included"] = row["file"] in phase1_set and row["classification"] == "article"

    report = {
        "generated_at": str(datetime.utcnow()),
        "base_url": BASE_SITE,
        "total_html_files": len(rows),
        "confirmed_articles": len(confirmed_articles),
        "phase1_count": len(phase1_set),
        "phase2_count": len(confirmed_articles) - len(phase1_set),
        "phase1_split_method": "lexicographic path order",
        "phase1_first_half": sorted(confirmed_articles[:phase1_count]),
        "phase1_total_list": sorted(phase1_set),
        "phase2_list": sorted(set(confirmed_articles) - phase1_set),
        "canary_pages": sorted(CANARY_PAGES),
        "canary_exceptions_added": canary_exceptions,
    }
    return rows, report


def write_inventory() -> dict:
    rows, report = build_inventory()
    inventory_path = OUT_ROOT / "inventory.json"
    list_path = OUT_ROOT / "inventory.csv"

    with inventory_path.open("w", encoding="utf-8") as f:
        json.dump({"report": report, "pages": rows}, f, indent=2, ensure_ascii=False)

    # Minimal CSV for fast external review.
    headers = [
        "file",
        "classification",
        "title",
        "canonical_url",
        "h1_count",
        "article_element_count",
        "stylesheet_references",
        "analytics_presence",
        "header_variant",
        "navigation_variant",
        "footer_variant",
        "jsonld_types",
        "obvious_malformed_html",
        "literal_markdown_in_rendered_content",
        "relative_link_style",
        "phase1_included",
    ]

    with list_path.open("w", encoding="utf-8") as f:
        f.write(",".join(headers) + "\n")
        for row in rows:
            rel_style = row["relative_link_style"]["style"]
            f.write(",".join([
                row["file"].replace(",", " "),
                row["classification"],
                row["title"].replace(",", " "),
                row["canonical_url"],
                str(row["h1_count"]),
                str(row["article_element_count"]),
                ";".join(row["stylesheet_references"]),
                str(row["analytics_presence"]),
                row["header_variant"],
                row["navigation_variant"],
                row["footer_variant"],
                "|".join(row["jsonld_types"]),
                str(row["obvious_malformed_html"]),
                str(row["literal_markdown_in_rendered_content"]),
                rel_style,
                str(row["phase1_included"]),
            ]) + "\n")

    with (OUT_ROOT / "phase1_summary.json").open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    (OUT_ROOT / "phase1_files.txt").write_text(
        "\n".join(report["phase1_total_list"]) + "\n",
        encoding="utf-8",
    )
    (OUT_ROOT / "phase2_files.txt").write_text(
        "\n".join(report["phase2_list"]) + "\n",
        encoding="utf-8",
    )

    return report


def load_inventory(report_path: Path | None = None) -> tuple[list[dict], dict]:
    if report_path is None:
        report_path = OUT_ROOT / "inventory.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    return payload["pages"], payload["report"]


def normalize_page(path: Path) -> bool:
    rel = rel_path(path)
    soup = load_soup(path)
    changed = False

    article = soup.find("article")
    if not article:
        return False

    # Keep existing canonical metadata untouched (required URL preservation).
    if not article:
        return False

    changed |= ensure_article_shell(soup)
    changed |= ensure_active_nav(soup, rel)
    changed |= normalize_links(soup, rel)
    changed |= markdown_to_strong(soup, article)
    if changed:
        write_soup(path, soup)
    return changed


def normalize_targets(target: str) -> list[str]:
    rows, report = build_inventory()
    all_pages = [row["file"] for row in rows if row["classification"] == "article"]

    if target == "canary":
        return sorted(CANARY_PAGES)

    if target == "phase1":
        return report["phase1_total_list"]

    if target == "phase2":
        all_set = set(all_pages)
        return sorted(all_set - set(report["phase1_total_list"]))

    return []


def apply_normalization(target: str) -> dict:
    targets = normalize_targets(target)
    if not targets:
        return {"target": target, "normalized": [], "errors": ["no targets"]}

    normalized = []
    for rel in targets:
        p = ROOT_DIR / rel
        if not p.exists():
            continue
        if normalize_page(p):
            normalized.append(rel)

    return {"target": target, "normalized": normalized, "errors": []}


def validate_pages(target: str, from_inventory: bool = True) -> dict:
    rows, report = build_inventory()
    phase1_set = set(report["phase1_total_list"])
    if target == "canary":
        check_set = set(normalize_targets("canary"))
    elif target == "phase1":
        check_set = phase1_set
    else:
        check_set = phase1_set

    if from_inventory:
        checks = [row for row in rows if row["classification"] == "article" and row["file"] in check_set]
    else:
        checks = [row for row in rows if row["classification"] == "article"]
    failures = []
    for row in checks:
        rel = row["file"]
        if target == "phase1" and rel not in phase1_set:
            continue
        if target == "phase2" and rel in phase1_set:
            continue

        p = ROOT_DIR / rel
        soup = load_soup(p)

        canonical = soup.find("link", rel="canonical")
        canonical_href = canonical.get("href") if canonical else None

        page_failures = {
            "file": rel,
            "missing_title": not bool(soup.title),
            "title_count": len(soup.find_all("title")),
            "h1_count": len(soup.find_all("h1")),
            "canonical_count": len(soup.find_all("link", rel="canonical")),
            "canonical_url_matches": canonical_href == expected_canonical(rel),
            "has_duplicate_ga": False,
            "literal_markdown": has_literal_markdown(soup),
            "missing_main": len(soup.find_all("main")) != 1,
            "missing_article": len(soup.find_all("article")) != 1,
            "duplicate_header": len(soup.find_all("header")) != 1,
            "duplicate_footer": len(soup.find_all("footer")) != 1,
            "jsonld_parse_errors": [],
            "internal_link_errors": [],
            "stylesheet_resolve_errors": [],
        }

        jsonld_ok = True
        for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
            text = tag.get_text(strip=True)
            if not text:
                continue
            try:
                json.loads(text)
            except json.JSONDecodeError:
                jsonld_ok = False
                page_failures["jsonld_parse_errors"].append("invalid-json-ld")
        page_failures["jsonld_parse_errors_ok"] = jsonld_ok

        root_rel = rel
        page_path = ROOT_DIR / root_rel
        current_dir = page_path.parent

        ga_src_count = 0
        ga_config_count = 0
        for script in soup.find_all("script"):
            src = (script.get("src") or "").strip()
            if src and GA_ID in src:
                ga_src_count += 1
            text = script.get_text(" ", strip=False)
            if not text:
                continue
            if f"gtag('config', '{GA_ID}')" in text or f'gtag("config", "{GA_ID}")' in text:
                ga_config_count += 1
        page_failures["has_duplicate_ga"] = ga_src_count != 1 or ga_config_count != 1

        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            split = urlsplit(href)
            if split.scheme or split.netloc:
                continue
            link_path = split.path
            if not link_path:
                continue
            target_path = ROOT_DIR / current_dir.relative_to(ROOT_DIR) / link_path
            if link_path.startswith("/"):
                target_path = ROOT_DIR / link_path.lstrip("/")
            if "/" in link_path:
                target_path = target_path
            if not target_path.exists():
                page_failures["internal_link_errors"].append(href)

        for link in soup.find_all("link", rel="stylesheet", href=True):
            href = link["href"].strip()
            if href.startswith("/"):
                if not (ROOT_DIR / href.lstrip("/")).exists():
                    page_failures["stylesheet_resolve_errors"].append(href)
            elif href and not href.startswith(("http://", "https://")):
                candidate = page_path.parent / href
                if not candidate.exists():
                    page_failures["stylesheet_resolve_errors"].append(href)

        if any(
            [
                page_failures["missing_title"],
                page_failures["title_count"] != 1,
                page_failures["h1_count"] != 1,
                page_failures["canonical_count"] != 1,
                not page_failures["canonical_url_matches"],
                page_failures["has_duplicate_ga"],
                page_failures["literal_markdown"],
                page_failures["missing_main"],
                page_failures["missing_article"],
                page_failures["duplicate_header"],
                page_failures["duplicate_footer"],
                page_failures["internal_link_errors"],
                page_failures["stylesheet_resolve_errors"],
                not page_failures["jsonld_parse_errors_ok"],
            ]
        ):
            failures.append(page_failures)

    return {
        "target": target,
        "checked": len(checks),
        "failures": failures,
    }


def check_phase2_unchanged(base_commit: str) -> dict:
    rows, report = build_inventory()
    phase2 = set(report["phase2_list"])
    if not phase2:
        return {"changed_phase2": []}

    import subprocess

    try:
        diff_output = subprocess.check_output(
            ["git", "diff", "--name-only", base_commit, "--"] + sorted(phase2),
            cwd=ROOT_DIR,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        diff_files = {
            line.strip().replace("\\", "/").lstrip("./")
            for line in diff_output.splitlines()
            if line.strip()
        }
    except Exception:
        diff_files = set()

    changed = []
    for row in rows:
        rel = row["file"]
        if row["classification"] != "article" or rel not in phase2:
            continue
        if rel in diff_files:
            changed.append(rel)

    return {"changed_phase2": changed}


def root_checkout_blob(commit: str, rel_path: str) -> bytes | None:
    import subprocess

    from subprocess import CalledProcessError
    try:
        raw = subprocess.check_output(["git", "show", f"{commit}:{rel_path}"], cwd=ROOT_DIR, text=False)
        return raw
    except Exception:
        return None


def write_file_hashes(paths: list[str]) -> dict[str, str]:
    return {rel: hashlib.sha256((ROOT_DIR / rel).read_bytes()).hexdigest() for rel in paths if (ROOT_DIR / rel).exists()}


def check_idempotence(target: str) -> dict:
    targets = normalize_targets(target)
    if not targets:
        return {"target": target, "error": "no targets"}

    before = write_file_hashes(targets)
    first_result = apply_normalization(target)
    after_first = write_file_hashes(targets)
    second_result = apply_normalization(target)
    after_second = write_file_hashes(targets)

    unstable = [p for p in targets if after_first.get(p) != after_second.get(p)]
    return {
        "target": target,
        "first_pass": {
            "changed_files": first_result["normalized"],
            "count": len(first_result["normalized"]),
        },
        "second_pass": {
            "changed_files": second_result["normalized"],
            "count": len(second_result["normalized"]),
        },
        "idempotent": len(unstable) == 0,
        "unstable_files": unstable,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("inventory")

    normalize = sub.add_parser("normalize")
    normalize.add_argument("scope", choices=["canary", "phase1"], help="normalization scope")

    validate = sub.add_parser("validate")
    validate.add_argument("scope", choices=["canary", "phase1"], help="validation scope")
    validate.add_argument("--base-commit", required=False, default="", help="base commit hash")
    validate.add_argument("--idempotence", action="store_true", help="run idempotence check after validate")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "inventory":
        report = write_inventory()
        print(json.dumps(report, indent=2))
        return

    if args.command == "normalize":
        result = apply_normalization(args.scope)
        print(json.dumps(result, indent=2))
        return

    if args.command == "validate":
        result = validate_pages(args.scope)
        if args.base_commit:
            phase2_result = check_phase2_unchanged(args.base_commit)
            result["phase2"] = phase2_result
        if args.idempotence:
            result["idempotence"] = check_idempotence(args.scope)
        print(json.dumps(result, indent=2))
        return


if __name__ == "__main__":
    main()
