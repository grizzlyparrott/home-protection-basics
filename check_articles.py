import os

OUTLINE_FILE = "homeprotectionbasics-outline.md"

def load_outline_paths(outline_path):
    paths = []
    with open(outline_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip headings, comments, blank lines
            if not line or line.startswith("#"):
                continue
            if "|" not in line:
                continue

            left = line.split("|", 1)[0].strip()
            # Only care about .html lines
            if not left.endswith(".html"):
                continue

            # Normalize to forward-slash paths as stored in the outline
            paths.append(left)
    return paths

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    outline_path = os.path.join(root_dir, OUTLINE_FILE)

    if not os.path.exists(outline_path):
        print(f"Outline file not found: {outline_path}")
        return

    all_paths = load_outline_paths(outline_path)
    existing = []
    missing = []

    for rel_path in all_paths:
        # Convert to OS path (Windows vs Linux)
        fs_path = os.path.join(root_dir, rel_path.replace("/", os.sep))
        if os.path.exists(fs_path):
            existing.append(rel_path)
        else:
            missing.append(rel_path)

    total = len(all_paths)
    print(f"Total articles in outline: {total}")
    print(f"Existing HTML files: {len(existing)}")
    print(f"Missing HTML files: {len(missing)}")
    print()

    print("=== EXISTING ARTICLES ===")
    for p in existing:
        print(p)

    print("\n=== MISSING ARTICLES ===")
    for p in missing:
        print(p)

    # Optional: write a status file you can upload to ChatGPT if you want
    status_path = os.path.join(root_dir, "homeprotectionbasics-status.txt")
    with open(status_path, "w", encoding="utf-8") as out:
        out.write(f"Total: {total}\n")
        out.write(f"Existing: {len(existing)}\n")
        out.write(f"Missing: {len(missing)}\n\n")
        out.write("EXISTING:\n")
        for p in existing:
            out.write(p + "\n")
        out.write("\nMISSING:\n")
        for p in missing:
            out.write(p + "\n")

    print(f"\nStatus written to: {status_path}")

if __name__ == "__main__":
    main()
