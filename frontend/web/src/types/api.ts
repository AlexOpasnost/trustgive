/**
 * Hand-written API types matching API_SPEC.md §2 components.
 * Replace with `openapi-typescript`-generated types once the backend is live:
 *   npm run gen-api
 */

export type LocalizedString = {
  en: string
  ru: string
}

export type TrustBadge = {
  slug: string
  label: LocalizedString
  image_url: string | null
  issuer: string
  issued_date?: string | null
  verify_url?: string | null
}

export type SourceDocumentKind =
  | "irs_990"
  | "irs_990ez"
  | "irs_990pf"
  | "charity_commission_filing"
  | "minjust_registration"
  | "sonko_registration"
  | "audit"
  | "state_registration"
  | "annual_report"

export type SourceDocument = {
  id: string
  kind: SourceDocumentKind
  label: LocalizedString
  url: string
  filed_date: string | null
  source_label: string
  file_format: "pdf" | "html" | "xlsx" | "json" | null
}

export type Financial = {
  year: number
  total_revenue_usd: number | null
  program_expenses_usd: number | null
  admin_expenses_usd: number | null
  fundraising_expenses_usd: number | null
  top_executive_comp_usd: number | null
  top_executive_name: string
  source_url: string
  source_label: string
}

export type MoneyBreakdownLine = {
  label: LocalizedString
  amount_usd: number
  percent: number
}

export type MoneyBreakdown = {
  year: number
  lines: MoneyBreakdownLine[]
  source_label: string
  source_document_id: string | null
}

export type NewsMention = {
  url: string
  publisher: string
  title: string
  published_date: string
  language: "en" | "ru"
}

export type CharitySummary = {
  slug: string
  name: LocalizedString
  tagline: LocalizedString
  logo_url: string | null
  country: "US" | "GB" | "RU"
  registration_id: string
  cause_tags: string[]
  size_bucket: "small" | "medium" | "large" | ""
  verification_status: "verified" | "listed" | "stale"
  is_stale: boolean
  last_filed_date: string | null
  total_revenue_usd: number | null
  program_expense_pct: number | null
  trust_badges: TrustBadge[]
}

export type Charity = CharitySummary & {
  description: LocalizedString
  founded_year: number | null
  donation_url: string
  money_breakdown: MoneyBreakdown | null
  financial_history: Financial[]
  source_documents: SourceDocument[]
  news_mentions: NewsMention[]
  methodology_note: LocalizedString
  ingestion_source: "propublica" | "every_org" | "charitybase" | "manual_ru"
  data_freshness: { last_synced_at: string; source: string }
}

export type Cause = {
  slug: string
  name: LocalizedString
  parent_slug: string | null
  charity_count: number
  children?: Cause[]
}

export type Pagination = {
  count: number
  page: number
  page_size: number
  next: string | null
  previous: string | null
}

export type PaginatedCharitySummary = Pagination & {
  results: CharitySummary[]
}
