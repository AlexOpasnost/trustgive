import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"

export function NotFoundPage() {
  const { t } = useTranslation()
  return (
    <div className="max-w-(--container-narrow) mx-auto px-6 py-24 text-center">
      <h1 className="text-h1 font-semibold text-ink mb-4">{t("common.notFound")}</h1>
      <Link to="/" className="text-verified hover:underline">
        {t("nav.catalog")} →
      </Link>
    </div>
  )
}
