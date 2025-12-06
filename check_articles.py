import os
from pathlib import Path

ROOT = Path(__file__).parent
OUTLINE_FILE = ROOT / "homeprotectionbasics-outline.md"
STATUS_FILE = ROOT / "homeprotectionbasics-status.txt"

def load_expected_filenames():
    expected = []

    with OUTLINE_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Lines look like:
            # insurance-basics/homeowners-insurance-coverage-explained.html | Title
            # or:
            # homeowners-insurance-coverage-explained.html | Title
            parts = line.split("|", 1)
            raw_path = parts[0].strip()

            # Always compare by filename only
            filename = raw_path.split("/")[-1].split("\\")[-1].strip()

            if filename:
                expected.append(filename)

    return expected

def load_actual_filenames():
    actual = []

    for path in ROOT.rglob("*.html"):
        # ignore root index and 404 if you want; comment these lines out if not
        rel = path.relative_to(ROOT)
        if str(rel) in ("index.html", "404.html"):
            continue

        filename = path.name
        actual.append(filename)

    return actual

def main():
    expected = load_expected_filenames()
    actual = load_actual_filenames()

    expected_set = set(expected)
    actual_set = set(actual)

    existing = sorted(expected_set & actual_set)
    missing = sorted(expected_set - actual_set)
    extras = sorted(actual_set - expected_set)

    lines = []
    lines.append(f"Total in outline: {len(expected_set)}")
    lines.append(f"Existing: {len(existing)}")
    lines.append(f"Missing: {len(missing)}")
    lines.append(f"Extras: {len(extras)}")
    lines.append("")

    lines.append("=== EXISTING ===")
    for name in existing:
        lines.append(name)
    lines.append("")

    lines.append("=== MISSING ===")
    for name in missing:
        lines.append(name)
    lines.append("")

    lines.append("=== EXTRAS (ON DISK, NOT IN OUTLINE) ===")
    for name in extras:
        lines.append(name)

    STATUS_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Status written to: {STATUS_FILE}")

if __name__ == "__main__":
    main()
