"""Find invisible and non-typeable characters in published copy.

Not an authorship check and not capable of being one: nothing here can tell who
or what wrote a sentence. What it does is catch characters that should not be in
site copy at all, whatever produced them — text pasted from a word processor, a
PDF, a chat window, or typed by hand on a keyboard with a compose key.

They matter for ordinary reasons. A zero-width space inside a word breaks the
browser's own find-on-page and breaks search indexing. A non-breaking space in
running text stops a line wrapping where it should. A soft hyphen is invisible
until it lands mid-word in a copied quote. None of this is visible in review,
which is exactly why it needs a script.

    .venv/Scripts/python.exe check_text_hygiene.py <path> [<path> ...]

Exits non-zero if anything is found, so it can go in CI.
"""

from __future__ import annotations

import pathlib
import sys
import unicodedata

# Characters that carry no visible glyph and no business being in copy.
INVISIBLE = {
    "­": "soft hyphen",
    "​": "zero-width space",
    "‌": "zero-width non-joiner",
    "‍": "zero-width joiner",
    "‎": "left-to-right mark",
    "‏": "right-to-left mark",
    "⁠": "word joiner",
    "﻿": "byte-order mark / zero-width no-break space",
    "᠎": "Mongolian vowel separator",
    " ": "line separator",
    " ": "paragraph separator",
}

# Visible, but not what a keyboard produces, and each has a plain equivalent.
LOOKALIKE = {
    " ": ("non-breaking space", "a normal space"),
    " ": ("narrow no-break space", "a normal space"),
    " ": ("figure space", "a normal space"),
    " ": ("thin space", "a normal space"),
    "‑": ("non-breaking hyphen", "-"),
    "−": ("minus sign", "-"),
    "ʼ": ("modifier letter apostrophe", "'"),
}


def scan(path: pathlib.Path) -> list[tuple[int, int, str, str]]:
    """Return (line, column, character, why) for everything worth flagging."""
    hits: list[tuple[int, int, str, str]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        for col, ch in enumerate(line, 1):
            if ch in INVISIBLE:
                hits.append((lineno, col, ch, f"invisible: {INVISIBLE[ch]}"))
            elif ch in LOOKALIKE:
                name, instead = LOOKALIKE[ch]
                hits.append((lineno, col, ch, f"{name} — use {instead}"))
            elif unicodedata.category(ch) == "Cc" and ch not in "\t":
                hits.append((lineno, col, ch, "control character"))
    return hits


def main() -> int:
    paths: list[pathlib.Path] = []
    for arg in sys.argv[1:]:
        p = pathlib.Path(arg)
        paths.extend(sorted(p.rglob("*"))) if p.is_dir() else paths.append(p)

    total = 0
    for path in paths:
        if not path.is_file() or path.suffix not in {".md", ".json", ".ts", ".tsx"}:
            continue
        hits = scan(path)
        if not hits:
            continue
        total += len(hits)
        print(f"{path}: {len(hits)}")
        for lineno, col, ch, why in hits[:20]:
            print(f"  {lineno}:{col}  U+{ord(ch):04X}  {why}")
        if len(hits) > 20:
            print(f"  … {len(hits) - 20} more")

    print(f"\nscanned {len([p for p in paths if p.is_file()])} file(s); {total} finding(s)")
    if total == 0:
        print("clean — nothing invisible, nothing that needs a special keyboard")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
