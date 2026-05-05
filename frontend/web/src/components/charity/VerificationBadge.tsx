import { HugeiconsIcon } from "@hugeicons/react"
import { Tick02Icon } from "@hugeicons/core-free-icons"
import { useTranslation } from "react-i18next"

import { cn } from "@/lib/utils"

type Props = {
  status: "verified" | "listed" | "stale"
  size?: "sm" | "md"
}

export function VerificationBadge({ status, size = "md" }: Props) {
  const { t } = useTranslation()
  const isVerified = status === "verified"

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full font-medium",
        size === "sm" ? "text-caption px-2 py-0.5" : "text-body-sm px-3 py-1",
        isVerified ? "bg-verified-soft text-verified" : "border border-rule text-ink-3"
      )}
      role="status"
    >
      {isVerified && <HugeiconsIcon icon={Tick02Icon} size={size === "sm" ? 12 : 14} aria-hidden="true" />}
      <span className="sr-only">Verification status: </span>
      {t(`charity.${status}`)}
    </span>
  )
}
