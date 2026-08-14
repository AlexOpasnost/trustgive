"""Print a published guide as readable markdown, straight from the locale file.

The prose that the site actually serves lives in
`frontend/web/src/locales/{en,ru}.json`, split into dozens of keys and mixed in
with every other string on the site. That is right for the application and
useless for reading, reviewing, or handing someone a copy.

So this renders it back out. Generated, never hand-maintained: a second copy of
an article that someone edits by hand is a copy that will disagree with the site
within a week, and the disagreement will be invisible until a reader finds it.
Regenerate rather than edit, and edit the locale file when the text should
change.

    .venv/Scripts/python.exe render_guide.py what-charity-registration-actually-proves en

Key order in the JSON is the article's order, which is how the block list in
`content/guides.ts` is written too. If the two ever disagree, the site is right
and this output is wrong.
"""

from __future__ import annotations

import json
import pathlib
import sys

LOCALES = pathlib.Path(__file__).resolve().parents[1] / "frontend" / "web" / "src" / "locales"


def render(slug: str, lang: str) -> str:
    data = json.loads((LOCALES / f"{lang}.json").read_text(encoding="utf-8"))
    try:
        article = data["guides"]["articles"][slug]
    except KeyError as exc:
        raise SystemExit(f"no guide {slug!r} in {lang}.json ({exc})") from exc

    out: list[str] = [f"# {article['title']}", "", f"*{article['standfirst']}*", ""]
    for key, value in article.items():
        if key in {"title", "standfirst"}:
            continue
        if not isinstance(value, str):
            # Lists, steps and FAQ blocks are nested objects keyed "0", "1", …
            for item in value.values():
                if isinstance(item, dict):  # FAQ: {q, a}
                    out += [f"**{item['q']}**", "", item["a"], ""]
                else:
                    out += [f"- {item}"]
            out.append("")
        elif key.endswith("Title"):
            out += [f"## {value}", ""]
        elif key.endswith("case"):
            # A worked example from this catalogue's own audits — set apart in
            # the rendered page too.
            out += ["> " + value.replace("\n", "\n> "), ""]
        else:
            out += [value, ""]
    return "\n".join(out).rstrip() + "\n"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("usage: render_guide.py <slug> <lang> [out-file]")
    text = render(sys.argv[1], sys.argv[2])
    if len(sys.argv) > 3:
        pathlib.Path(sys.argv[3]).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {sys.argv[3]} ({len(text)} chars)")
    else:
        print(text)
