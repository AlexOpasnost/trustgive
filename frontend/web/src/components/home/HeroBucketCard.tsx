/**
 * HeroBucketCard — homepage above-the-fold bucket card (DESIGN.md v3.0 §A).
 *
 * One of three full-bleed cards on the homepage. Donor lands → instantly picks
 * intent (People / Animals / Planet) → goes to the bucket-filtered catalog.
 *
 * Layout:
 *   - Full-bleed <img> background, object-cover.
 *   - Bottom-fade gradient overlay (--overlay-photo-bottom in DESIGN.md §E.4).
 *   - Top-left: "BROWSE BY CAUSE" overline (uppercase EN, title-case RU).
 *   - Bottom-left: huge bucket name (Source Serif 4) + 1-line subtitle.
 *   - Bottom-right: photo credit microtext (white-50%).
 *   - Whole card is a <Link> — entire surface is clickable (KB-DESIGNER-INIT-002).
 *
 * Hover: photo scales 1.03 + overlay deepens slightly (240ms ease-out).
 * Focus-visible: 3px white inset ring on the photo background.
 * A11y: full card has aria-label combining label + subtitle. Img alt="" because
 * the visible serif label conveys identity (decorative photo).
 */

import { Link } from "react-router-dom"
import { useTranslation } from "react-i18next"

import type { Bucket } from "@/types/api"

type Props = {
  bucket: Bucket
  /** Full-bleed background photo URL. If null, a neutral gradient placeholder is used. */
  photoUrl: string | null
  /** Bucket name in current language ("People" / "Людям" etc.). */
  label: string
  /** 1-line subtitle e.g. "8 verified charities" or "8 проверенных фондов". */
  subtitle: string
  /** Where the card links to. Typically `/charities?bucket=people`. */
  href: string
  /** Photo credit microtext. Empty string = render nothing. */
  photoCredit?: string
}

export function HeroBucketCard({
  bucket,
  photoUrl,
  label,
  subtitle,
  href,
  photoCredit = "",
}: Props) {
  const { i18n } = useTranslation()
  const lang = i18n.language?.startsWith("ru") ? "ru" : "en"
  const overlineKey = "homepage.browseByCause"
  // RU overline uses sentence case ("Выберите по теме") — DESIGN.md §F.1 KB note.
  // The translation file already has the correct casing per language; we only
  // toggle uppercase + tracking on the EN side.
  const overlineClass =
    lang === "en" ? "uppercase tracking-[0.18em]" : "tracking-wide"

  return (
    <Link
      to={href}
      aria-label={`${label} — ${subtitle}`}
      data-bucket={bucket}
      className="
        group relative block overflow-hidden
        bg-ink
        min-h-[50vh] md:min-h-[60vh] lg:min-h-[70vh]
        focus-visible:outline-none
        focus-visible:ring-[3px] focus-visible:ring-white focus-visible:ring-offset-1 focus-visible:ring-offset-ink
      "
    >
      {/* Background photo (full-bleed). object-cover; eager load (above-the-fold). */}
      {photoUrl ? (
        <img
          src={photoUrl}
          alt=""
          loading="eager"
          decoding="async"
          fetchPriority="high"
          className="
            absolute inset-0 h-full w-full object-cover object-center
            transition-transform duration-300 ease-out
            group-hover:scale-[1.03]
            motion-reduce:transition-none motion-reduce:group-hover:scale-100
          "
        />
      ) : (
        // Fallback: warm-stone gradient if no photo. Keeps card legible.
        <div
          aria-hidden="true"
          className="absolute inset-0 bg-gradient-to-br from-stone-700 via-stone-800 to-stone-900"
        />
      )}

      {/* Bottom-fade gradient overlay — DESIGN.md §E.4. */}
      <div
        aria-hidden="true"
        className="
          absolute inset-0
          transition-opacity duration-300 ease-out
          group-hover:opacity-110
        "
        style={{
          background:
            "linear-gradient(to top, rgba(10,12,11,0.85) 0%, rgba(10,12,11,0.4) 50%, transparent 80%)",
        }}
      />

      {/* Top-left: overline label */}
      <div className="absolute top-6 left-6 md:top-8 md:left-8 z-10">
        <span
          className={`text-caption font-semibold text-white/85 ${overlineClass}`}
        >
          <TranslatedOverline keyName={overlineKey} />
        </span>
      </div>

      {/* Bottom-left: bucket name + subtitle */}
      <div className="absolute bottom-8 left-6 right-6 md:bottom-12 md:left-8 md:right-8 z-10">
        <h2
          className="font-serif text-white"
          style={{
            fontSize: "clamp(48px, 6vw, 80px)",
            lineHeight: 1.05,
            letterSpacing: "-0.02em",
            fontWeight: 700,
          }}
        >
          {label}
        </h2>
        <p className="mt-3 text-body-lg text-white/85 max-w-[28ch]">
          {subtitle}
        </p>
      </div>

      {/* Bottom-right: photo credit microtext */}
      {photoCredit && (
        <div className="absolute bottom-3 right-4 z-10">
          <span className="text-[10px] leading-tight text-white/50 font-sans">
            {photoCredit}
          </span>
        </div>
      )}
    </Link>
  )
}

/**
 * Tiny inner so we can call useTranslation once at the parent and still use
 * t() for the overline, without forcing the parent to thread the string in.
 */
function TranslatedOverline({ keyName }: { keyName: string }) {
  const { t } = useTranslation()
  return <>{t(keyName)}</>
}
