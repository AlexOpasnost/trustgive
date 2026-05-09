"""Scrape OpenGraph site-specific photos for every charity.

Run via: `python manage.py scrape_og_images`

This was originally migration 0033 but was moved out of the migration
chain because Railway's healthcheck (~120s) times out long before the
198-charity scrape finishes (~17 min at 2s throttle). Migrations must
be fast; this is a one-shot backfill best run as a management command
either via `railway run python manage.py scrape_og_images` or via a
Railway service shell after deploy.

Logic identical to the original 0033 docstring:
  1. Homepage = `https://{donation_url-host}/`
  2. GET with realistic User-Agent, 8s timeout, expect text/html
  3. Parse `<meta property="og:image">`, `<meta name="twitter:image">`,
     or `<link rel="image_src">`. Both attribute orders.
  4. Resolve relatives against page URL. Skip data: / <20-char URIs.
  5. HEAD-probe (or 1-byte GET fallback). Need 200 + image/*.
  6. Update only if current `hero_photo_url` is on `images.unsplash.com`
     OR empty. Never overwrite Wikimedia Commons or custom curated.
  7. Save `hero_photo_credit = "Source: {host}"`, license `press-kit`,
     bilingual caption `"Cover image from {Org Name}"`.

Idempotent. Defensive try/except per charity.
"""
from __future__ import annotations

import re
import time
from urllib.parse import urljoin, urlparse

from django.core.management.base import BaseCommand

from apps.charities.models import Charity


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 "
    "(+TrustGive backfill, one-time)"
)
GET_TIMEOUT = 8.0
HEAD_TIMEOUT = 6.0
THROTTLE_SECONDS = 2.0


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
    for rx in (_RE_OG_IMAGE, _RE_OG_IMAGE_REVERSE, _RE_TWITTER_IMAGE, _RE_IMAGE_SRC):
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
        if not absolute.startswith(("http://", "https://")):
            continue
        return absolute
    return None


def _fetch_homepage(url: str):
    try:
        from urllib.request import Request, urlopen

        req = Request(
            url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        with urlopen(req, timeout=GET_TIMEOUT) as resp:
            ctype = resp.headers.get("Content-Type", "")
            if "html" not in ctype.lower():
                return None, None
            raw = resp.read(800_000)
            try:
                html = raw.decode("utf-8", errors="replace")
            except Exception:
                html = raw.decode("latin-1", errors="replace")
            final_url = resp.geturl() or url
            return html, final_url
    except Exception:
        return None, None


def _head_image(url: str) -> bool:
    try:
        from urllib.request import Request, urlopen

        req = Request(url, headers={"User-Agent": USER_AGENT}, method="HEAD")
        with urlopen(req, timeout=HEAD_TIMEOUT) as resp:
            if resp.status != 200:
                return False
            ctype = resp.headers.get("Content-Type", "").lower()
            return ctype.startswith("image/")
    except Exception:
        try:
            from urllib.request import Request, urlopen

            req = Request(
                url,
                headers={"User-Agent": USER_AGENT, "Range": "bytes=0-0"},
            )
            with urlopen(req, timeout=HEAD_TIMEOUT) as resp:
                if resp.status not in (200, 206):
                    return False
                ctype = resp.headers.get("Content-Type", "").lower()
                return ctype.startswith("image/")
        except Exception:
            return False


class Command(BaseCommand):
    help = "Scrape og:image / twitter:image from each charity's homepage and save as hero_photo_url."

    def handle(self, *args, **opts):
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

            if "wikimedia.org" in current or "wikipedia.org" in current:
                skipped_wikimedia += 1
                continue

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
                self.stdout.write(f"FETCH-FAIL {charity.slug} {homepage}")
                time.sleep(THROTTLE_SECONDS)
                continue

            og_url = _extract_og(html, final_url or homepage)
            if not og_url:
                time.sleep(THROTTLE_SECONDS)
                continue

            if not _head_image(og_url):
                head_failed += 1
                self.stdout.write(f"HEAD-FAIL {charity.slug} {og_url}")
                time.sleep(THROTTLE_SECONDS)
                continue

            og_found += 1
            host = _host_of(homepage) or _host_of(og_url) or "site"
            org_en = ""
            org_ru = ""
            try:
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

        self.stdout.write(self.style.SUCCESS(
            f"\nOG-image scrape complete:\n"
            f"  scanned                : {scanned} / {total}\n"
            f"  og_found               : {og_found}\n"
            f"  og_replaced_unsplash   : {og_replaced_unsplash}\n"
            f"  og_filled_empty        : {og_filled_empty}\n"
            f"  skipped_wikimedia      : {skipped_wikimedia}\n"
            f"  skipped_custom_curated : {skipped_custom}\n"
            f"  fetch_failed           : {fetch_failed}\n"
            f"  head_failed            : {head_failed}\n"
        ))
