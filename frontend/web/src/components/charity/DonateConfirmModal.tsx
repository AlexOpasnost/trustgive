import * as Dialog from "@radix-ui/react-dialog"
import { HugeiconsIcon } from "@hugeicons/react"
import { ArrowUpRight01Icon, Cancel01Icon } from "@hugeicons/core-free-icons"
import { useTranslation } from "react-i18next"

import { api } from "@/lib/api"
import { usePreferences } from "@/store/preferences"

type Props = {
  open: boolean
  onClose: () => void
  charityName: string
  charitySlug: string
  donationUrl: string
  sourcePage: "detail" | "comparison" | "seo_landing" | "search"
}

export function DonateConfirmModal({ open, onClose, charityName, charitySlug, donationUrl, sourcePage }: Props) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)

  const onContinue = () => {
    void api.logDonationRedirect({
      charity_slug: charitySlug,
      lang,
      source_page: sourcePage,
      client_event_id: crypto.randomUUID(),
    })
    window.open(donationUrl, "_blank", "noopener,noreferrer")
    onClose()
  }

  let siteHost = ""
  try {
    siteHost = new URL(donationUrl).hostname.replace(/^www\./, "")
  } catch {
    siteHost = donationUrl
  }

  return (
    <Dialog.Root open={open} onOpenChange={(o) => !o && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-paper/60 z-40 animate-in fade-in" />
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[min(480px,calc(100vw-2rem))] bg-surface-raised border border-rule rounded-md p-6 z-50 focus:outline-none">
          <div className="flex items-start justify-between gap-4 mb-4">
            <Dialog.Title className="text-h3 font-semibold text-ink">{t("charity.leavingTitle")}</Dialog.Title>
            <Dialog.Close asChild>
              <button type="button" aria-label="Close" className="text-ink-3 hover:text-ink">
                <HugeiconsIcon icon={Cancel01Icon} size={20} />
              </button>
            </Dialog.Close>
          </div>

          <Dialog.Description className="text-body text-ink-2 mb-4">
            {t("charity.leavingBody", { name: charityName })}
          </Dialog.Description>

          <ul className="space-y-2 text-body-sm text-ink-2 mb-6 list-disc list-inside">
            <li>0% platform fee</li>
            <li>We never see your money</li>
            <li>We never share your contact info</li>
          </ul>

          <button
            type="button"
            onClick={onContinue}
            className="w-full bg-verified text-verified-on rounded-md px-4 py-3 font-medium inline-flex items-center justify-center gap-2 hover:opacity-90"
          >
            {t("charity.continueTo", { site: siteHost })}
            <HugeiconsIcon icon={ArrowUpRight01Icon} size={16} />
          </button>

          <button
            type="button"
            onClick={onClose}
            className="block w-full mt-3 text-body-sm text-ink-3 hover:text-ink"
          >
            {t("charity.cancel")}
          </button>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
