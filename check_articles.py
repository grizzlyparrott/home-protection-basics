import os
from termcolor import colored  # Optional, remove if you don't want colored output

OUTLINE_FILE = "homeprotectionbasics-outline.md"

def load_outline_paths(outline_path):
    paths = []
    with open(outline_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            left = line.split("|", 1)[0].strip()
            if not left.endswith(".html"):
                continue
            paths.append(left)
    return paths

def get_all_html_files():
    html_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".html") and file != "index.html" and file != "404.html":
                full_path = os.path.join(root, file).replace(".\\", "").replace("\\", "/")
                html_files.append(full_path)
    return html_files

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    outline_path = os.path.join(root_dir, OUTLINE_FILE)

    if not os.path.exists(outline_path):
        print(f"❌ Outline file not found: {outline_path}")
        return

    all_paths = load_outline_paths(outline_path)
    html_files = get_all_html_files()

    existing = []
    missing = []
    extras = []

    # Check for existing and missing
    for path in all_paths:
        if path in html_files:
            existing.append(path)
        else:
            missing.append(path)

    # Check for extras
    for html in html_files:
        if html not in all_paths:
            extras.append(html)

    # Print results
    print(colored(f"\n✅ Existing HTML files: {len(existing)}", "green"))
    print(colored(f"❌ Missing HTML files: {len(missing)}", "red"))
    print(colored(f"⚠️ Extra HTML files: {len(extras)}", "yellow"))

    print("\n=== EXISTING ARTICLES ===")
    for p in existing:
        print(p)

    print("\n=== MISSING ARTICLES ===")
    for p in missing:
        print(p)

    print("\n=== EXTRA ARTICLES (not in outline) ===")
    for p in extras:
        print(p)

    # Optional output to file
    status_path = os.path.join(root_dir, "homeprotectionbasics-status.txt")
    with open(status_path, "w", encoding="utf-8") as out:
        out.write(f"Total in outline: {len(all_paths)}\n")
        out.write(f"Existing: {len(existing)}\n")
        out.write(f"Missing: {len(missing)}\n")
        out.write(f"Extras: {len(extras)}\n")
        out.write("=== EXISTING ===\n")
        for p in existing:
            out.write(p + "\n")
        out.write("=== MISSING ===\n")
        for p in missing:
            out.write(p + "\n")
        out.write("=== EXTRAS ===\n")
        for p in extras:
            out.write(p + "\n")

    print(colored(f"\n📄 Status written to: {status_path}", "yellow"))

if __name__ == "__main__":
    main()
