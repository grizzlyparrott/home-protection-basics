#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone
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


def get_git_first_commit(file_path, repo_root):
    """Get the FIRST commit timestamp for a file using Git."""
    try:
        result = subprocess.run(
            ["git", "log", "--reverse", "--format=%cI", "--", str(file_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Get the first line (earliest commit)
            first_line = result.stdout.strip().split('\n')[0]
            # Parse the ISO format date from git and return full timestamp
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
    repo_root = Path(ROOT_DIR).resolve()

    for root, dirs, files in os.walk(ROOT_DIR):
        # Strip ignored dirs in-place
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]

        for fname in files:
            if not fname.lower().endswith(".html"):
                continue

            path_abs = os.path.join(root, fname)
            path_rel = os.path.relpath(path_abs, ROOT_DIR)

            url = file_to_url(path_rel)
            lastmod = get_lastmod(path_abs, repo_root)

            urls.append((url, lastmod))

    return sorted(urls, key=lambda x: x[0])


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
    sitemap_xml = build_sitemap(urls)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    print(f"Found {len(urls)} URLs.")
    print(f"Sitemap written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()