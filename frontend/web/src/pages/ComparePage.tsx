import { HugeiconsIcon } from "@hugeicons/react"
import { ArrowLeft02Icon, ArrowUpRight01Icon, Tick02Icon } from "@hugeicons/core-free-icons"
import { useQuery } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"
import { Link, useSearchParams } from "react-router-dom"

import { VerificationBadge } from "@/components/charity/VerificationBadge"
import { api } from "@/lib/api"
import { formatPercent, formatUsd } from "@/lib/utils"
import { usePreferences } from "@/store/preferences"
import type { CharitySummary } from "@/types/api"

type ComparisonCharity = CharitySummary & {
  money_breakdown?: {
    year: number
    lines: Array<{
      label: { en: string; ru: string }
      amount_usd: number
      percent: number
    }>
  } | null
  top_executive_comp_usd?: number | null
  donation_url?: string
  primary_source_document?: {
    id: string
    kind: string
    label: { en: string; ru: string }
    url: string
  } | null
}

export function ComparePage() {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const [searchParams] = useSearchParams()
  const slugsParam = searchParams.get("slugs") || ""
  const slugs = slugsParam
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)

  const valid = slugs.length >= 2 && slugs.length <= 3

  const { data, isLoading, isError } = useQuery({
    queryKey: ["compare", slugs],
    queryFn: ({ signal }) => api.compareCharities(slugs, { signal }),
    enabled: valid,
  })

  if (!valid) {
    return (
      <div className="max-w-(--container-narrow) mx-auto px-6 py-24 text-center">
        <h1 className="text-h1 font-semibold text-ink mb-4 font-serif" style={{ fontWeight: 400 }}>
          {t("compare.emptyTitle")}
        </h1>
        <p className="text-body text-ink-2 mb-8 max-w-md mx-auto">{t("compare.emptyBody")}</p>
        <pre className="bg-surface border border-rule rounded-md px-4 py-3 font-mono text-body-sm text-ink-2 inline-block">
          /compare?slugs=givedirectly,heifer-international,oxfam-america
        </pre>
        <div className="mt-8">
          <Link
            to="/charities"
            className="inline-flex items-center gap-2 text-body text-ink underline-offset-4 underline decoration-rule hover:decoration-ink"
          >
            {t("compare.browseCatalog")} →
          </Link>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="max-w-(--container-wide) mx-auto px-6 lg:px-12 py-12">
        <div className="skeleton h-12 w-1/3 mb-8" />
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="skeleton h-64" />
          <div className="skeleton h-64" />
          <div className="skeleton h-64" />
        </div>
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="max-w-(--container-narrow) mx-auto px-6 py-24 text-center">
        <h1 className="text-h2 font-semibold text-ink mb-2">{t("common.error")}</h1>
        <p className="text-body text-ink-2">{t("common.errorBody")}</p>
      </div>
    )
  }

  const charities = data.charities as ComparisonCharity[]

  // Define all the rows we display in the comparison
  const rows: { key: string; label: string; render: (c: ComparisonCharity) => React.ReactNode }[] = [
    {
      key: "verified",
      label: t("compare.row.verified"),
      render: (c) =>
        c.verification_status === "verified" ? (
          <HugeiconsIcon icon={Tick02Icon} size={20} className="text-verified inline" />
        ) : (
          <span className="text-ink-3">—</span>
        ),
    },
    {
      key: "country",
      label: t("compare.row.country"),
      render: (c) => <span className="font-mono">{c.country}</span>,
    },
    {
      key: "registration",
      label: t("compare.row.registration"),
      render: (c) => <span className="font-mono">{c.registration_id}</span>,
    },
    {
      key: "revenue",
      label: t("compare.row.revenue"),
      render: (c) => (
        <span className="font-mono">{formatUsd(c.total_revenue_usd, { compact: true })}</span>
      ),
    },
    {
      key: "programs",
      label: t("compare.row.programs"),
      render: (c) => {
        const line = c.money_breakdown?.lines.find((l) => l.label.en === "Programs")
        return <span className="font-mono">{formatPercent(line?.percent ?? c.program_expense_pct)}</span>
      },
    },
    {
      key: "admin",
      label: t("compare.row.admin"),
      render: (c) => {
        const line = c.money_breakdown?.lines.find((l) => l.label.en === "Administration")
        return <span className="font-mono">{formatPercent(line?.percent)}</span>
      },
    },
    {
      key: "fundraising",
      label: t("compare.row.fundraising"),
      render: (c) => {
        const line = c.money_breakdown?.lines.find((l) => l.label.en === "Fundraising")
        return <span className="font-mono">{formatPercent(line?.percent)}</span>
      },
    },
    {
      key: "topExec",
      label: t("compare.row.topExec"),
      render: (c) => (
        <span className="font-mono">{formatUsd(c.top_executive_comp_usd, { compact: true })}</span>
      ),
    },
    {
      key: "filed",
      label: t("compare.row.lastFiled"),
      render: (c) => (
        <span className="font-mono">{c.last_filed_date?.slice(0, 7) ?? "—"}</span>
      ),
    },
    {
      key: "source",
      label: t("compare.row.source"),
      render: (c) =>
        c.primary_source_document ? (
          <a
            href={c.primary_source_document.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-verified hover:underline inline-flex items-center gap-1"
          >
            → {c.primary_source_document.label[lang] || c.primary_source_document.label.en}
          </a>
        ) : (
          <span className="text-ink-3">—</span>
        ),
    },
  ]

  return (
    <div className="max-w-(--container-wide) mx-auto px-6 lg:px-12 py-12">
      <Link
        to="/charities"
        className="inline-flex items-center gap-2 text-body-sm text-ink-3 hover:text-ink mb-8"
      >
        <HugeiconsIcon icon={ArrowLeft02Icon} size={16} />
        {t("compare.back")}
      </Link>

      <h1 className="font-serif text-ink mb-8" style={{ fontSize: "clamp(32px, 4vw, 48px)", fontWeight: 400, letterSpacing: "-0.01em" }}>
        {t("compare.title")}
      </h1>

      {/* DESKTOP TABLE — sticky first column + sticky header */}
      <div className="hidden md:block overflow-x-auto bg-surface border border-rule rounded-md">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-rule">
              <th className="text-left p-5 sticky left-0 bg-surface text-caption uppercase tracking-widest text-ink-3 font-medium w-44 z-10">
                &nbsp;
              </th>
              {charities.map((c) => {
                const name = c.name[lang] || c.name.en || c.slug
                return (
                  <th key={c.slug} className="text-left p-5 align-top">
                    <Link
                      to={`/charities/${c.slug}`}
                      className="block group"
                    >
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <span className="font-serif text-h3 text-ink group-hover:underline" style={{ fontWeight: 400 }}>
                          {name}
                        </span>
                      </div>
                      <VerificationBadge status={c.verification_status} size="sm" />
                    </Link>
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.key} className="border-b border-rule">
                <td className="p-5 sticky left-0 bg-surface text-body-sm text-ink-3 font-medium w-44 z-10">
                  {row.label}
                </td>
                {charities.map((c) => (
                  <td key={c.slug} className="p-5 text-body text-ink align-top">
                    {row.render(c)}
                  </td>
                ))}
              </tr>
            ))}
            <tr>
              <td className="p-5 sticky left-0 bg-surface w-44 z-10" />
              {charities.map((c) => (
                <td key={c.slug} className="p-5">
                  {c.donation_url && (
                    <a
                      href={c.donation_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 bg-ink text-paper px-4 py-2 rounded-md text-body-sm font-medium hover:bg-ink-2"
                    >
                      {t("compare.donate")}
                      <HugeiconsIcon icon={ArrowUpRight01Icon} size={14} />
                    </a>
                  )}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {/* MOBILE — stacked accordion (DESIGN.md §6.8) */}
      <div className="md:hidden space-y-6">
        {charities.map((c) => {
          const name = c.name[lang] || c.name.en || c.slug
          return (
            <details key={c.slug} className="bg-surface border border-rule rounded-md" open>
              <summary className="cursor-pointer p-5 flex items-center justify-between gap-3">
                <Link to={`/charities/${c.slug}`} className="font-serif text-h3 text-ink hover:underline" style={{ fontWeight: 400 }}>
                  {name}
                </Link>
                <VerificationBadge status={c.verification_status} size="sm" />
              </summary>
              <dl className="border-t border-rule">
                {rows.map((row) => (
                  <div key={row.key} className="flex items-center justify-between px-5 py-3 border-b border-rule last:border-b-0">
                    <dt className="text-body-sm text-ink-3">{row.label}</dt>
                    <dd className="text-body text-ink">{row.render(c)}</dd>
                  </div>
                ))}
              </dl>
              {c.donation_url && (
                <div className="p-5 border-t border-rule">
                  <a
                    href={c.donation_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full inline-flex items-center justify-center gap-2 bg-ink text-paper px-4 py-3 rounded-md text-body font-medium"
                  >
                    {t("compare.donate")}
                    <HugeiconsIcon icon={ArrowUpRight01Icon} size={16} />
                  </a>
                </div>
              )}
            </details>
          )
        })}
      </div>

      <p className="text-caption text-ink-3 mt-8 max-w-2xl font-mono">
        {t("compare.footnote")}
      </p>
    </div>
  )
}
