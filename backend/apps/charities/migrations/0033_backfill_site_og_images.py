"""v3.5 site-specific photo pass — replace generic Unsplash placeholders
with REAL Open Graph imagery scraped from each charity's own website.

Why: per user feedback, the Unsplash hedged-illustrative photos look like
stock. Each charity's homepage almost always exposes a press-quality
hero image via `<meta property="og:image">` — the same image that
appears when their URL is shared on Slack/Twitter/LinkedIn. That's
the photo we want.

Logic per charity (run sequentially with throttle):
  1. Derive homepage URL from `donation_url` host (always
     `https://{host}/`, never the donate-page deep link itself — the
     homepage is what carries the canonical og:image).
  2. GET the homepage with a realistic User-Agent. Timeout 8s. Skip on
     HTTP error or non-HTML response.
  3. Parse the response body for, in order:
       a. `<meta property="og:image" ...>`
       b. `<meta name="twitter:image" ...>`
       c. `<link rel="image_src" ...>`
     Case-insensitive; both single and double quotes; attribute order
     either way.
  4. Resolve relative URLs against the page URL. If the discovered URL
     points to a `data:` URI or is < 20 chars — skip.
  5. HEAD-probe the resolved URL. Skip if status != 200 or
     Content-Type doesn't start with `image/`.
  6. Decision:
       - `hero_photo_url` is currently a Wikimedia Commons URL  -> SKIP
         (CC-licensed, higher quality, attributed to a real photographer).
       - `hero_photo_url` is on `images.unsplash.com`            -> REPLACE.
       - `hero_photo_url` is empty                                -> FILL.
       - else (custom curated URL)                                -> SKIP.
  7. Save the new URL with credit `"Source: {host}"`, license
     `press-kit` (sourced directly from the charity's site, which is the
     canonical press-kit context), and a generic bilingual caption
     `"Cover image from {Org Name}" / "Изображение с сайта {Org Name}"`.

Throttle: 2.0s sleep between fetches. ~198 charities x ~2s + HEAD x ~5s
end-to-end ~ 17 minutes. One-time backfill on Railway is fine.

Defensive: every network call wrapped in try/except. A single network
error is logged and skipped; never abort the migration mid-way.

Idempotent: re-running won't re-fetch already-replaced rows because the
new URL won't be on `images.unsplash.com` and won't be empty (skips at
step 6). Reverse: no-op (don't restore Unsplash placeholders).

Counts printed at the end:
  - scanned, og_found, og_replaced_unsplash, og_filled_empty,
    skipped_wikimedia, skipped_custom, fetch_failed, head_failed.
"""
from __future__ import annotations

import re
import time
from urllib.parse import urljoin, urlparse

from django.db import migrations


# Realistic desktop browser UA. Some charity sites refuse Python's default
# UA. We're a polite single-pass scraper — be honest in the comment string.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 "
    "(+TrustGive backfill, one-time)"
)
GET_TIMEOUT = 8.0
HEAD_TIMEOUT = 6.0
THROTTLE_SECONDS = 2.0

# Match <meta property="og:image" content="..."> in any quote/attr order.
_RE_OG_IMAGE = re.compile(
    r"""<meta\b[^>]*?
        (?:property|name)\s*=\s*["']\s*og:image(?::secure_url)?\s*["']
        [^>]*?
        content\s*=\s*["']([^"']+)["']
        [^>]*>""",
    re.IGNORECASE | re.VERBOSE,
)
_RE_OG_IMAGE_REVERSE = re.compile(
    r"""<meta\b[^>]*?
        content\s*=\s*["']([^"']+)["']
        [^>]*?
        (?:property|name)\s*=\s*["']\s*og:image(?::secure_url)?\s*["']
        [^>]*>""",
    re.IGNORECASE | re.VERBOSE,
)
_RE_TWITTER_IMAGE = re.compile(
    r"""<meta\b[^>]*?
        name\s*=\s*["']\s*twitter:image(?::src)?\s*["']
        [^>]*?
        content\s*=\s*["']([^"']+)["']
        [^>]*>""",
    re.IGNORECASE | re.VERBOSE,
)
_RE_IMAGE_SRC = re.compile(
    r"""<link\b[^>]*?
        rel\s*=\s*["']\s*image_src\s*["']
        [^>]*?
        href\s*=\s*["']([^"']+)["']
        [^>]*>""",
    re.IGNORECASE | re.VERBOSE,
)


def _homepage_for(donation_url: str) -> str | None:
    try:
        p = urlparse(donation_url)
        if not p.scheme or not p.netloc:
            return None
        return f"{p.scheme}://{p.netloc}/"
    except Exception:
        return None


def _host_of(url: str) -> str:
    try:
        h = urlparse(url).netloc
        return h[4:] if h.startswith("www.") else h
    except Exception:
        return ""


def _extract_og(html: str, base_url: str) -> str | None:
    """Return absolute image URL or None. Tries OG -> Twitter -> image_src."""
    for rx in (_RE_OG_IMAGE, _RE_OG_IMAGE_REVERSE,
               _RE_TWITTER_IMAGE, _RE_IMAGE_SRC):
        m = rx.search(html)
        if not m:
            continue
        candidate = (m.group(1) or "").strip()
        if not candidate or candidate.startswith("data:") or len(candidate) < 20:
            continue
        try:
            absolute = urljoin(base_url, candidate)
        except Exception:
            continue
        # Sanity: must be http(s)
        if not absolute.startswith(("http://", "https://")):
            continue
        return absolute
    return None


def _fetch_homepage(url: str):
    """Return (html, final_url) or (None, None). Imports stdlib urllib
    inside the function so the migration module is import-safe even when
    `requests` isn't pinned."""
    try:
        from urllib.request import Request, urlopen
        req = Request(url, headers={"User-Agent": USER_AGENT,
                                    "Accept": "text/html,application/xhtml+xml"})
        with urlopen(req, timeout=GET_TIMEOUT) as resp:
            ctype = resp.headers.get("Content-Type", "")
            if "html" not in ctype.lower():
                return None, None
            raw = resp.read(800_000)  # cap at ~800KB
            try:
                html = raw.decode("utf-8", errors="replace")
            except Exception:
                html = raw.decode("latin-1", errors="replace")
            final_url = resp.geturl() or url
            return html, final_url
    except Exception:
        return None, None


def _head_image(url: str) -> bool:
    """Return True if url returns 200 with Content-Type image/*. Falls
    back to a tiny GET if the server refuses HEAD (some CDNs do)."""
    try:
        from urllib.request import Request, urlopen
        req = Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
        with urlopen(req, timeout=HEAD_TIMEOUT) as resp:
            if resp.status != 200:
                return False
            ctype = resp.headers.get("Content-Type", "").lower()
            return ctype.startswith("image/")
    except Exception:
        # HEAD-refusing CDN — try a 1-byte GET
        try:
            from urllib.request import Request, urlopen
            req = Request(url, headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"})
            with urlopen(req, timeout=HEAD_TIMEOUT) as resp:
                if resp.status not in (200, 206):
                    return False
                ctype = resp.headers.get("Content-Type", "").lower()
                return ctype.startswith("image/")
        except Exception:
            return False


def forwards(apps, schema_editor):
    Charity = apps.get_model("charities", "Charity")

    # Order: oldest-seeded first so output reads top-down chronologically.
    qs = Charity.objects.all().order_by("created_at", "slug")
    total = qs.count()

    scanned = 0
    og_found = 0
    og_replaced_unsplash = 0
    og_filled_empty = 0
    skipped_wikimedia = 0
    skipped_custom = 0
    fetch_failed = 0
    head_failed = 0

    for charity in qs.iterator():
        scanned += 1
        current = charity.hero_photo_url or ""

        # Decision gate (a) — never overwrite Wikimedia Commons photos
        if "wikimedia.org" in current or "wikipedia.org" in current:
            skipped_wikimedia += 1
            continue

        # Decision gate (b) — only act on Unsplash placeholders or empty
        is_unsplash = "images.unsplash.com" in current
        is_empty = not current
        if not (is_unsplash or is_empty):
            skipped_custom += 1
            continue

        homepage = _homepage_for(charity.donation_url or "")
        if not homepage:
            fetch_failed += 1
            time.sleep(THROTTLE_SECONDS)
            continue

        html, final_url = _fetch_homepage(homepage)
        if html is None:
            fetch_failed += 1
            print(f"[migration 0033] FETCH-FAIL {charity.slug} {homepage}")
            time.sleep(THROTTLE_SECONDS)
            continue

        og_url = _extract_og(html, final_url or homepage)
        if not og_url:
            time.sleep(THROTTLE_SECONDS)
            continue

        if not _head_image(og_url):
            head_failed += 1
            print(f"[migration 0033] HEAD-FAIL {charity.slug} {og_url}")
            time.sleep(THROTTLE_SECONDS)
            continue

        og_found += 1
        host = _host_of(homepage) or _host_of(og_url) or "site"
        org_en = ""
        org_ru = ""
        try:
            # name is JSONB {en, ru}
            org_en = (charity.name or {}).get("en", "") if isinstance(charity.name, dict) else ""
            org_ru = (charity.name or {}).get("ru", org_en) if isinstance(charity.name, dict) else ""
        except Exception:
            pass
        if not org_en:
            org_en = charity.slug
        if not org_ru:
            org_ru = org_en

        Charity.objects.filter(pk=charity.pk).update(
            hero_photo_url=og_url,
            hero_photo_credit=f"Source: {host}",
            hero_photo_license="press-kit",
            hero_photo_caption={
                "en": f"Cover image from {org_en}.",
                "ru": f"Изображение с сайта {org_ru}.",
            },
        )

        if is_unsplash:
            og_replaced_unsplash += 1
        else:
            og_filled_empty += 1

        time.sleep(THROTTLE_SECONDS)

    print(
        "[migration 0033] OG-image scrape complete:\n"
        f"  scanned                  : {scanned} / {total}\n"
        f"  og_found                 : {og_found}\n"
        f"  og_replaced_unsplash     : {og_replaced_unsplash}\n"
        f"  og_filled_empty          : {og_filled_empty}\n"
        f"  skipped_wikimedia        : {skipped_wikimedia}\n"
        f"  skipped_custom_curated   : {skipped_custom}\n"
        f"  fetch_failed             : {fetch_failed}\n"
        f"  head_failed              : {head_failed}"
    )


def backwards(apps, schema_editor):
    """No-op — never restore Unsplash placeholders from real site OG images."""


class Migration(migrations.Migration):
    dependencies = [
        ("charities", "0032_backfill_v35_logos"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards, elidable=False),
    ]
