"""Push an edited guide markdown back into the locale file. Inverse of render_guide.py.

The operator edits the readable copy in `content-drafts/`, not the locale JSON,
which is the sensible way round: the JSON is forty keys deep in a file holding
every string on the site. This carries those edits back.

Three rules, each of which exists because of something that went wrong here:

* **It does not touch the text.** Values move verbatim; the only transformation
  is JSON escaping. If a sentence reads badly, that is a separate conversation.
* **It edits in place, key by key, rather than re-serialising the file.** The
  locale files carry cosmetic blank lines between sections that `json.dumps`
  does not reproduce, so a full rewrite would show as a diff across the whole
  file and bury the actual change.
* **It takes the key order from the locale file itself**, exactly as
  `render_guide.py` does when writing the markdown out. Nothing about the
  document's shape is hardcoded here, so the two cannot drift apart — and if the
  markdown no longer lines up, it stops rather than writing one section's text
  into another section's key.

Afterwards, re-run `render_guide.py` and diff against the markdown: identical
output is the proof the import was faithful.

    .venv/Scripts/python.exe import_guide.py <slug> <lang> <markdown> [--apply]
"""

from __future__ import annotations

import io
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCALES = ROOT / "frontend" / "web" / "src" / "locales"


def chunks_of(markdown: str) -> list[str]:
    return [c.strip() for c in re.split(r"\r?\n\s*\r?\n", markdown) if c.strip()]


def flatten(chunk: str) -> str:
    return " ".join(line.strip() for line in chunk.split("\n")).strip()


def consume(article: dict, blocks: list[str]) -> list[tuple[str, object]]:
    """Walk the article's keys and the markdown blocks together.

    The pairing rules mirror `render_guide.py` exactly: a key whose value is a
    mapping was written out as a list (or as question/answer pairs), a key
    ending in "Title" as a `##` heading, one ending in "case" as a blockquote,
    and anything else as a plain paragraph.
    """
    updates: list[tuple[str, object]] = []
    i = 0

    def take() -> str:
        nonlocal i
        if i >= len(blocks):
            raise SystemExit("markdown ran out of blocks before the article's keys did")
        block = blocks[i]
        i += 1
        return block

    for key, value in article.items():
        if key in {"title", "standfirst"}:
            continue

        if isinstance(value, dict):
            is_faq = all(isinstance(v, dict) for v in value.values())
            if is_faq:
                rebuilt: dict[str, dict[str, str]] = {}
                for index in value:
                    question = flatten(take())
                    if not (question.startswith("**") and question.endswith("**")):
                        raise SystemExit(
                            f"expected a bold question for {key}.{index}, got: {question[:60]!r}"
                        )
                    rebuilt[index] = {"q": question.strip("*").strip(), "a": flatten(take())}
                updates.append((key, rebuilt))
            else:
                block = take()
                items = [re.sub(r"^-\s*", "", line).strip() for line in block.split("\n")]
                items = [item for item in items if item]
                if len(items) != len(value):
                    raise SystemExit(
                        f"{key} has {len(value)} items in the locale and {len(items)} in the "
                        f"markdown; the list changed length, so nothing was written"
                    )
                updates.append((key, {index: item for index, item in zip(value, items)}))
            continue

        block = take()
        if key.endswith("Title"):
            if not block.startswith("## "):
                raise SystemExit(f"expected a '## ' heading for {key}, got: {block[:60]!r}")
            updates.append((key, block[3:].strip()))
        elif key.endswith("case"):
            if not block.startswith(">"):
                raise SystemExit(f"expected a '>' blockquote for {key}, got: {block[:60]!r}")
            updates.append((key, flatten(re.sub(r"^>\s?", "", block, flags=re.M))))
        else:
            if block.startswith(("#", ">", "- ")):
                raise SystemExit(f"expected a paragraph for {key}, got: {block[:60]!r}")
            updates.append((key, flatten(block)))

    if i != len(blocks):
        raise SystemExit(
            f"{len(blocks) - i} markdown block(s) left over after the article's keys were "
            f"filled. Sections were added, so the mapping is not safe."
        )
    return updates


def article_span(raw: str, slug: str) -> tuple[int, int]:
    """Span of one article object inside the locale file, by brace matching."""
    anchor = re.search(rf'"{re.escape(slug)}"\s*:\s*\{{', raw)
    if not anchor:
        raise SystemExit(f"{slug!r} is not in this locale file")
    start = anchor.end() - 1
    depth, in_string, escaped = 0, False, False
    for i in range(start, len(raw)):
        ch = raw[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return start, i + 1
    raise SystemExit(f"could not find the end of {slug!r}")


def set_string(span: str, key: str, value: str) -> tuple[str, bool]:
    pattern = re.compile(rf'("{re.escape(key)}"\s*:\s*)"(?:[^"\\]|\\.)*"')
    match = pattern.search(span)
    if not match:
        raise SystemExit(f"key {key!r} not found in this article")
    encoded = json.dumps(value, ensure_ascii=False)
    changed = match.group(0) != match.group(1) + encoded
    return pattern.sub(lambda m: m.group(1) + encoded, span, count=1), changed


def main() -> int:
    slug, lang, markdown_path = sys.argv[1], sys.argv[2], sys.argv[3]
    apply = "--apply" in sys.argv

    path = LOCALES / f"{lang}.json"
    raw = io.open(path, encoding="utf-8", newline="").read()
    data = json.loads(raw)
    try:
        article = data["guides"]["articles"][slug]
    except KeyError as exc:
        raise SystemExit(f"no guide {slug!r} in {lang}.json ({exc})") from exc

    blocks = chunks_of(io.open(markdown_path, encoding="utf-8", newline="").read())
    if not blocks or not blocks[0].startswith("# "):
        raise SystemExit("first block must be the '# Title' heading")
    title = blocks[0][2:].strip()
    standfirst_block = blocks[1] if len(blocks) > 1 else ""
    if not (standfirst_block.startswith("*") and standfirst_block.endswith("*")):
        raise SystemExit("second block must be the italic standfirst")
    standfirst = standfirst_block.strip("*").strip()

    updates: list[tuple[str, object]] = [("title", title), ("standfirst", standfirst)]
    updates += consume(article, blocks[2:])

    start, end = article_span(raw, slug)
    span = raw[start:end]
    changed: list[str] = []

    for key, value in updates:
        if isinstance(value, str):
            span, did = set_string(span, key, value)
            if did:
                changed.append(key)
            continue

        # Nested values are rewritten whole. A bare key name would be ambiguous
        # here — every FAQ entry has a "q" and an "a", and every list has a "0".
        for index, item in value.items():
            if isinstance(item, dict):
                changed += [
                    f"{key}.{index}.{field}"
                    for field in ("q", "a")
                    if article[key][index][field] != item[field]
                ]
            elif article[key][index] != item:
                changed.append(f"{key}.{index}")
        span = replace_object(span, key, value)

    new_raw = raw[:start] + span + raw[end:]
    json.loads(new_raw)  # refuse to write something that would not parse

    print(f"{path.name}: {len(changed)} value(s) differ")
    for key in changed:
        print(f"  {key}")
    if not apply:
        print("\nпробный прогон, ничего не записано — добавьте --apply")
        return 0
    io.open(path, "w", encoding="utf-8", newline="").write(new_raw)
    print(f"\nзаписано в {path}")
    return 0


def replace_object(span: str, key: str, value: dict) -> str:
    """Replace one nested object's contents, preserving its indentation."""
    anchor = re.search(rf'("{re.escape(key)}"\s*:\s*)\{{', span)
    if not anchor:
        raise SystemExit(f"key {key!r} not found as an object")
    start = anchor.end() - 1
    depth, in_string, escaped = 0, False, False
    end = start
    for i in range(start, len(span)):
        ch = span[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    line_start = span.rfind("\n", 0, anchor.start()) + 1
    indent = span[line_start : anchor.start()]
    body = json.dumps(value, ensure_ascii=False, indent=2)
    body = body.replace("\n", "\r\n" + indent) if "\r\n" in span else body.replace("\n", "\n" + indent)
    return span[:start] + body + span[end:]


if __name__ == "__main__":
    raise SystemExit(main())
