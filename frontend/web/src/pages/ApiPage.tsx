/**
 * ApiPage — documentation for the public API (STRATEGY §3, Block C).
 *
 * The API has been open since the beginning; what was missing was any page
 * saying so. STRATEGY's argument for writing one is that documented public data
 * is what turns a site into infrastructure — the thing a course reading list or
 * a methods section can cite. The OpenAPI schema is generated, so this page is
 * prose around facts that already exist rather than a second source of truth.
 *
 * Every figure here is real: the rate limit is DEFAULT_THROTTLE_RATES in
 * settings/base.py, the endpoints are the ones in urls.py, and the counts in the
 * example come from the live catalogue.
 *
 * The "Using the data" block draws a line the page has to keep drawing: the
 * *compilation* is CC0 (operator's decision, 2026-08-04), the *filings* are the
 * registers' and carry whatever terms each register sets. Those are two
 * different things and merging them would be asserting rights over documents
 * this project does not own. The same licence URL is emitted as the Dataset
 * `license` in worker/index.ts; if one changes, change both.
 */

import { ArrowRight01Icon } from "@hugeicons/core-free-icons"
import { HugeiconsIcon } from "@hugeicons/react"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

import { useDocumentTitle } from "@/lib/useDocumentTitle"

const API_BASE = "https://api.trustgive.org"
const SCHEMA_URL = `${API_BASE}/api/schema/`
const SWAGGER_URL = `${API_BASE}/api/docs/`

type Endpoint = {
  method: string
  path: string
  descriptionKey: string
}

// Mirrors the urls.py files under backend/apps. Read-only endpoints only.
const ENDPOINTS: Endpoint[] = [
  { method: "GET", path: "/api/charities/", descriptionKey: "list" },
  { method: "GET", path: "/api/charities/{slug}/", descriptionKey: "detail" },
  {
    method: "GET",
    path: "/api/charities/{slug}/source-documents/",
    descriptionKey: "documents",
  },
  { method: "GET", path: "/api/charities/featured/", descriptionKey: "featured" },
  { method: "GET", path: "/api/hubs/", descriptionKey: "hubs" },
  { method: "GET", path: "/api/stats/", descriptionKey: "stats" },
  { method: "GET", path: "/api/causes/", descriptionKey: "causes" },
  { method: "GET", path: "/api/seo/charities/{slug}/", descriptionKey: "seo" },
  { method: "GET", path: "/api/feed.rss", descriptionKey: "feed" },
  { method: "GET", path: "/api/health/", descriptionKey: "health" },
]

const FILTERS = ["country", "cause", "registry", "bucket", "size", "q", "sort", "page"]

const EXAMPLE_REQUEST = `curl "https://api.trustgive.org/api/charities/?q=givewell&page_size=1"`

const EXAMPLE_RESPONSE = `{
  "count": 6,
  "page": 1,
  "page_size": 1,
  "next": "...?q=givewell&page=2&page_size=1",
  "previous": null,
  "results": [
    {
      "slug": "givewell",
      "name": { "en": "GiveWell (The Clear Fund)", "ru": "GiveWell (The Clear Fund)" },
      "country": "US",
      "registration_id": "208625442",
      "verification_status": "verified",
      "primary_source_kind": "irs_990",
      "last_filed_date": "2023-12-31",
      "total_revenue_usd": "219600000.00"
    }
  ]
}`

export function ApiPage() {
  const { t } = useTranslation()
  useDocumentTitle(t("api.title"))

  return (
    <article className="max-w-(--container-narrow) mx-auto px-6 lg:px-12 py-16 lg:py-24">
      <header>
        <h1
          className="font-serif text-ink mb-6"
          style={{
            fontSize: "clamp(34px, 4.5vw, 52px)",
            lineHeight: 1.1,
            fontWeight: 700,
            letterSpacing: "-0.02em",
          }}
        >
          {t("api.title")}
        </h1>
        <p className="text-body text-ink-2" style={{ fontSize: "20px", lineHeight: "34px" }}>
          {t("api.lead")}
        </p>
      </header>

      <hr className="border-rule my-12" />

      <Section title={t("api.accessTitle")}>
        <P>{t("api.accessBody")}</P>
        <dl className="mt-6 space-y-3">
          <Row term={t("api.baseUrl")} value={API_BASE} mono />
          <Row term={t("api.auth")} value={t("api.authValue")} />
          <Row term={t("api.format")} value="JSON (UTF-8)" mono />
          <Row term={t("api.rateLimit")} value={t("api.rateLimitValue")} />
        </dl>
      </Section>

      <hr className="border-rule my-12" />

      <Section title={t("api.endpointsTitle")}>
        <P>{t("api.endpointsBody")}</P>
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-rule">
                <th className="py-2 pr-4 text-caption font-medium uppercase tracking-wide text-ink-3">
                  {t("api.colEndpoint")}
                </th>
                <th className="py-2 text-caption font-medium uppercase tracking-wide text-ink-3">
                  {t("api.colWhat")}
                </th>
              </tr>
            </thead>
            <tbody>
              {ENDPOINTS.map((endpoint) => (
                <tr key={endpoint.path} className="border-b border-rule/60 align-top">
                  <td className="py-3 pr-4 whitespace-nowrap">
                    <span className="font-mono text-caption text-ink-3 mr-2">
                      {endpoint.method}
                    </span>
                    <span className="font-mono text-body-sm text-ink">{endpoint.path}</span>
                  </td>
                  <td className="py-3 text-body-sm text-ink-2">
                    {t(`api.endpoint.${endpoint.descriptionKey}`)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <p className="mt-6 text-body-sm text-ink-2">
          {t("api.filtersBody")}{" "}
          {FILTERS.map((filter, i) => (
            <span key={filter}>
              {i > 0 && ", "}
              <code className="font-mono text-ink">{filter}</code>
            </span>
          ))}
          .
        </p>
      </Section>

      <hr className="border-rule my-12" />

      <Section title={t("api.exampleTitle")}>
        <P>{t("api.exampleBody")}</P>
        <Pre>{EXAMPLE_REQUEST}</Pre>
        <Pre className="mt-4">{EXAMPLE_RESPONSE}</Pre>
      </Section>

      <hr className="border-rule my-12" />

      <Section title={t("api.termsTitle")}>
        <P>{t("api.termsBody")}</P>
        <p className="mt-6">
          <Link
            to="/data-sources"
            className="text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
          >
            {t("api.termsLink")}
          </Link>
        </p>
      </Section>

      <hr className="border-rule my-12" />

      <Section title={t("api.schemaTitle")}>
        <P>{t("api.schemaBody")}</P>
        <p className="mt-6 flex flex-wrap gap-x-6 gap-y-2">
          <ExternalLink href={SCHEMA_URL}>{t("api.linkSchema")}</ExternalLink>
          <ExternalLink href={SWAGGER_URL}>{t("api.linkSwagger")}</ExternalLink>
        </p>
      </Section>
    </article>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="text-h2 font-semibold text-ink mb-4 font-sans">{title}</h2>
      {children}
    </section>
  )
}

function P({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <p
      className={`text-body leading-relaxed text-ink-2 ${className}`}
      style={{ fontSize: "19px", lineHeight: "32px" }}
    >
      {children}
    </p>
  )
}

function Row({ term, value, mono = false }: { term: string; value: string; mono?: boolean }) {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1">
      <dt className="text-body-sm text-ink-3 min-w-[140px]">{term}</dt>
      <dd className={`text-body-sm text-ink ${mono ? "font-mono" : ""}`}>{value}</dd>
    </div>
  )
}

function Pre({ children, className = "" }: { children: string; className?: string }) {
  return (
    <pre
      className={`bg-paper border border-rule rounded-md p-4 overflow-x-auto text-caption font-mono text-ink leading-relaxed ${className}`}
    >
      <code>{children}</code>
    </pre>
  )
}

function ExternalLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-2 text-body text-ink underline decoration-rule decoration-1 underline-offset-4 hover:decoration-ink"
    >
      {children}
      <HugeiconsIcon icon={ArrowRight01Icon} size={14} aria-hidden="true" />
    </a>
  )
}
