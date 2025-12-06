#!/usr/bin/env python3

import os
import datetime
from urllib.parse import quote

# =======================
# CONFIG – EDIT THIS PART
# =======================

# Your site URL, NO trailing slash
BASE_URL = "https://homeprotectionbasics.com"

# Root folder of your site files (where your index.html and folders live)
ROOT_DIR = "."

# Output sitemap file name
OUTPUT_FILE = "sitemap.xml"

# Ignore these directories (add more if needed)
IGNORE_DIRS = {".git", ".github", "__pycache__", "node_modules"}


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


def get_lastmod(path_abs):
    """
    Get file last modified time in YYYY-MM-DD format (UTC).
    """
    ts = os.path.getmtime(path_abs)
    dt = datetime.datetime.utcfromtimestamp(ts)
    return dt.strftime("%Y-%m-%d")


def get_priority(path_rel):
    """
    Basic priority rules:
    - Root index.html: 1.0
    - Folder index.html: 0.8
    - Everything else: 0.6
    """
    path_rel = path_rel.replace(os.sep, "/")

    if path_rel == "index.html":
        return "1.0"

    if path_rel.endswith("/index.html") or "/index.html" in path_rel:
        return "0.8"

    return "0.6"


# =======================
# MAIN LOGIC
# =======================

def collect_urls():
    urls = []

    for root, dirs, files in os.walk(ROOT_DIR):
        # Strip ignored dirs in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

        for fname in files:
            if not fname.lower().endswith(".html"):
                continue

            path_abs = os.path.join(root, fname)
            path_rel = os.path.relpath(path_abs, ROOT_DIR)

            url = file_to_url(path_rel)
            lastmod = get_lastmod(path_abs)
            priority = get_priority(path_rel)

            urls.append((url, lastmod, priority))

    return sorted(urls, key=lambda x: x[0])


def build_sitemap(urls):
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url, lastmod, priority in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <changefreq>weekly</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    return "\n".join(lines)


def main():
    urls = collect_urls()
    sitemap_xml = build_sitemap(urls)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    print(f"Found {len(urls)} URLs.")
    print(f"Sitemap written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
