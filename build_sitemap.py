#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote
from urllib.parse import urlparse

# =======================
# CONFIG – EDIT THIS PART
# =======================

# Your site URL, NO trailing slash
BASE_URL = "https://homeprotectionbasics.com"

# Root folder of your site files (where your index.html and folders live)
ROOT_DIR = Path(__file__).resolve().parent

# Output sitemap file name
OUTPUT_FILE = "sitemap.xml"

# Ignore these directories (add more if needed)
IGNORE_DIRS = {".git", ".github", "__pycache__", "node_modules", "artifacts", "scripts"}
IGNORE_PREFIXES = ("artifacts/", "scripts/", "rescue/")


# =======================
# HELPER FUNCTIONS
# =======================

def file_to_url(path_rel):
    """
    Convert a relative file path into a full URL.
    - Converts backslashes to forward slashes
    - Handles root index.html as /
    """
    path_rel = path_rel.replace(os.sep, "/")

    if path_rel == "index.html":
        return BASE_URL + "/"

    return BASE_URL + "/" + quote(path_rel)


def normalize_canonical(raw):
    """Normalize canonical links to absolute sitemap URLs."""
    if not raw:
        return ""
    href = raw.strip()
    if href.startswith("/"):
        return BASE_URL + href
    if href.startswith(("http://", "https://")):
        return href
    return BASE_URL + "/" + href


def expected_canonical(rel_path: str) -> str:
    rel = rel_path.replace("\\", "/")
    if rel == "index.html":
        return f"{BASE_URL}/"
    if rel.endswith("/index.html"):
        return f"{BASE_URL}/{Path(rel).parent.as_posix()}/"
    return f"{BASE_URL}/{quote(rel)}"


def canonical_to_file_path(canonical_url):
    parsed = urlparse(canonical_url)
    path = (parsed.path or "/").lstrip("/")
    if path == "":
        return Path("index.html")
    if path.endswith("/"):
        path = path + "index.html"
    elif not Path(path).suffix:
        path = f"{path}.html"
    return Path(path)


def get_git_first_commit(file_path, repo_root):
    """Get the LAST commit timestamp for a file using Git."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(file_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            first_line = result.stdout.strip().split('\n')[0]
            dt = datetime.fromisoformat(first_line.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        return None
    except (subprocess.SubprocessError, ValueError, OSError):
        return None


def get_file_modified(path_abs):
    """Get the file system modification time as fallback (full timestamp)."""
    mtime = os.path.getmtime(path_abs)
    dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_lastmod(path_abs, repo_root):
    """
    Get last modified timestamp in YYYY-MM-DDTHH:MM:SSZ format.
    Prefers Git commit date, falls back to file system date.
    """
    git_date = get_git_first_commit(path_abs, repo_root)
    if git_date:
        return git_date
    
    return get_file_modified(path_abs)


# =======================
# MAIN LOGIC
# =======================

def collect_urls():
    urls = []
    repo_root = ROOT_DIR
    canonical_map = {}
    duplicate_urls = []
    invalid_urls = []
    missing_canonical = []
    canonical_mismatches = []
    seen_urls = set()

    for root, dirs, files in os.walk(str(ROOT_DIR)):
        # Strip ignored dirs in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

        for fname in files:
            if not fname.lower().endswith(".html"):
                continue

            path_abs = os.path.join(root, fname)
            path_rel = os.path.relpath(path_abs, str(ROOT_DIR))
            rel_posix = Path(path_rel).as_posix()

            if rel_posix.startswith(IGNORE_PREFIXES) or rel_posix == "404.html":
                continue

            # Skip empty, non-indexable or non-public pages.
            try:
                from bs4 import BeautifulSoup
            except ImportError:
                # In environments without bs4, skip advanced filtering.
                canonical = file_to_url(path_rel)
                lastmod = get_lastmod(path_abs, repo_root)
                if canonical not in seen_urls:
                    urls.append((canonical, lastmod, rel_posix, "no_html_parser"))
                    seen_urls.add(canonical)
                else:
                    duplicate_urls.append((canonical, rel_posix))
                continue

            with open(path_abs, "r", encoding="utf-8", errors="replace") as f:
                soup = BeautifulSoup(f.read(), "html.parser")

            canonical_tag = soup.find("link", rel="canonical")
            canonical_href = canonical_tag.get("href", "").strip() if canonical_tag else ""
            if not canonical_href:
                missing_canonical.append(rel_posix)
                continue

            canonical = normalize_canonical(canonical_href)
            robots = soup.find("meta", attrs={"name": "robots"})
            robots_content = (robots.get("content") or "").lower() if robots else ""
            if "noindex" in robots_content:
                continue

            expected = expected_canonical(rel_posix)
            if canonical != expected:
                canonical_mismatches.append((rel_posix, canonical, expected))
                # Prefer the page's actual canonical URL, but still validate existence.

            target_path = canonical_to_file_path(canonical).as_posix()
            if not (repo_root / target_path).exists():
                invalid_urls.append((rel_posix, canonical))
                continue
            if not target_path.startswith(("emergency-prep/", "fire-safety/", "home-security/", "insurance-basics/", "guides/", "index.html")):
                continue

            url = file_to_url(path_rel)
            lastmod = get_lastmod(path_abs, repo_root)

            if canonical in seen_urls:
                duplicate_urls.append((canonical, rel_posix))
                continue

            urls.append((canonical, lastmod, rel_posix))
            seen_urls.add(canonical)

    report = {
        "total_candidates": len(urls) + len(duplicate_urls) + len(invalid_urls) + len(missing_canonical),
        "missing_canonical": missing_canonical,
        "invalid_urls": invalid_urls,
        "duplicate_urls": duplicate_urls,
        "canonical_mismatches": canonical_mismatches,
        "kept_count": len(urls),
    }

    return sorted([(url, lastmod) for url, lastmod, _ in urls], key=lambda x: x[0]), report

def write_sitemap_report(report):
    path = Path("artifacts/sitemap-report.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    import json
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Sitemap report written to {path}")


def build_sitemap(urls):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url, lastmod in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")

    lines.append("</urlset>")
    return "\n".join(lines)


def main():
    urls = collect_urls()
    if isinstance(urls, tuple):
        urls, report = urls
    else:
        report = {}
    sitemap_xml = build_sitemap(urls)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    print(f"Found {len(urls)} URLs.")
    print(f"Duplicate URL variants removed: {len(report.get('duplicate_urls', []))}")
    print(f"Canonical mismatches found: {len(report.get('canonical_mismatches', []))}")
    print(f"Missing canonical pages: {len(report.get('missing_canonical', []))}")
    print(f"Invalid canonical mappings removed: {len(report.get('invalid_urls', []))}")
    print(f"Sitemap written to {OUTPUT_FILE}")
    write_sitemap_report(report)


if __name__ == "__main__":
    main()
