/**
 * Abstract organic SVG art — Anthropic-style generative hero asset.
 *
 * Why a custom shape and not stock art:
 *  - $0 budget; no illustrator
 *  - Anthropic's signature visual is generative organic forms with
 *    soft gradients — we approximate with hand-tuned SVG
 *  - The shape signals "research / publication" rather than SaaS
 *
 * Composition: three overlapping blob curves with the verified-soft
 * fill, on a clay-coloured circle backdrop. Subtle, doesn't compete
 * with text.
 */
type Props = {
  className?: string
}

export function GenerativeShape({ className }: Props) {
  return (
    <svg
      viewBox="0 0 480 480"
      className={className}
      fill="none"
      aria-hidden="true"
    >
      <defs>
        <radialGradient id="tg-blob-grad" cx="0.4" cy="0.35">
          <stop offset="0%" stopColor="var(--color-verified)" stopOpacity="0.18" />
          <stop offset="60%" stopColor="var(--color-verified)" stopOpacity="0.06" />
          <stop offset="100%" stopColor="var(--color-clay)" stopOpacity="0.0" />
        </radialGradient>
        <linearGradient id="tg-paper-grad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="var(--color-clay)" stopOpacity="0.25" />
          <stop offset="100%" stopColor="var(--color-clay)" stopOpacity="0.05" />
        </linearGradient>
        <pattern id="tg-dots" width="14" height="14" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="1" fill="var(--color-rule)" />
        </pattern>
      </defs>

      {/* Backdrop: subtle dot grid bounded by a circle */}
      <circle cx="240" cy="240" r="220" fill="url(#tg-dots)" opacity="0.9" />

      {/* Layer 1: large soft blob */}
      <path
        d="M 320 130 C 400 130, 420 230, 380 310 C 340 390, 220 410, 140 360 C 60 310, 80 200, 140 150 C 200 100, 260 100, 320 130 Z"
        fill="url(#tg-blob-grad)"
      />

      {/* Layer 2: paper-shape (a "document" silhouette, slightly tilted) */}
      <g transform="translate(140 90) rotate(-6)" opacity="0.85">
        <rect x="0" y="0" width="200" height="250" rx="6" fill="var(--color-surface)" stroke="var(--color-rule)" strokeWidth="1" />
        <rect x="20" y="30" width="140" height="6" rx="3" fill="var(--color-rule)" />
        <rect x="20" y="50" width="160" height="6" rx="3" fill="var(--color-rule)" />
        <rect x="20" y="70" width="100" height="6" rx="3" fill="var(--color-rule)" />
        <rect x="20" y="100" width="160" height="6" rx="3" fill="var(--color-rule)" />
        <rect x="20" y="120" width="120" height="6" rx="3" fill="var(--color-rule)" />
        <rect x="20" y="140" width="155" height="6" rx="3" fill="var(--color-rule)" />
        {/* The verified seal — subtle */}
        <circle cx="160" cy="200" r="22" fill="var(--color-verified-soft)" stroke="var(--color-verified)" strokeWidth="1.5" />
        <path d="M 152 200 L 158 206 L 170 194" stroke="var(--color-verified)" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </g>

      {/* Layer 3: subtle accent curve */}
      <path
        d="M 80 380 Q 240 320 400 380"
        stroke="var(--color-clay)"
        strokeWidth="1.5"
        fill="none"
        opacity="0.5"
      />
    </svg>
  )
}
