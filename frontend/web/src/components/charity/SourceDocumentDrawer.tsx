import * as Dialog from "@radix-ui/react-dialog"
import { HugeiconsIcon } from "@hugeicons/react"
import {
  Cancel01Icon,
  Download04Icon,
  FileVerifiedIcon,
  LinkSquare02Icon,
} from "@hugeicons/core-free-icons"
import { useTranslation } from "react-i18next"

import type { SourceDocument } from "@/types/api"
import { usePreferences } from "@/store/preferences"

type Props = {
  document: SourceDocument | null
  charityName: string
  registrationId: string
  onClose: () => void
}

/**
 * The wedge feature UI per DESIGN.md §6.7. Choreographed like opening a vault.
 * Source-attribution line is mono-caption — making clear this is the actual
 * registry record, not a TrustGive opinion.
 */
export function SourceDocumentDrawer({ document, charityName, registrationId, onClose }: Props) {
  const { t } = useTranslation()
  const lang = usePreferences((s) => s.lang)
  const open = document !== null

  const label = document ? document.label[lang] || document.label.en : ""

  return (
    <Dialog.Root open={open} onOpenChange={(o) => !o && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-paper/60 z-40 animate-in fade-in" />
        <Dialog.Content
          className="fixed right-0 top-0 h-full w-full md:w-[600px] bg-surface-raised border-l border-rule z-50 flex flex-col shadow-none focus:outline-none"
        >
          {document && (
            <>
              <header className="border-b border-rule p-6 sticky top-0 bg-surface-raised">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <Dialog.Title className="text-h3 font-semibold text-ink">{label}</Dialog.Title>
                    <Dialog.Description className="text-body-sm text-ink-2 mt-1">
                      {charityName} · {registrationId && <span className="font-mono">EIN/Reg {registrationId}</span>}
                    </Dialog.Description>
                    {document.source_label && (
                      <p className="text-caption text-ink-3 font-mono mt-2">
                        Source: {document.source_label}
                        {document.filed_date && ` · ${document.filed_date}`}
                      </p>
                    )}
                  </div>
                  <Dialog.Close asChild>
                    <button
                      type="button"
                      aria-label="Close"
                      className="text-ink-3 hover:text-ink p-1"
                    >
                      <HugeiconsIcon icon={Cancel01Icon} size={20} />
                    </button>
                  </Dialog.Close>
                </div>
              </header>

              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {/*
                  Government registries (ProPublica, IRS, Charity Commission)
                  serve their PDFs with X-Frame-Options: DENY, so iframe
                  embedding is blocked. We instead show a stylised preview
                  card + prominent "Open original" CTA. Cross-origin PDF.js
                  remains a Phase 4.5+ option.
                */}
                <div className="aspect-[8.5/11] bg-paper border border-rule rounded-md flex flex-col items-center justify-center text-center px-8 py-10">
                  <HugeiconsIcon icon={FileVerifiedIcon} size={56} className="text-clay mb-6" />
                  <p className="font-serif text-h3 text-ink mb-2" style={{ fontWeight: 400 }}>
                    {label}
                  </p>
                  <p className="text-body-sm text-ink-3 max-w-xs">
                    {t("drawer.previewUnavailable")}
                  </p>
                </div>

                <div className="bg-verified-soft border-l-4 border-verified px-4 py-3">
                  <p className="text-body-sm text-ink-2">{t("drawer.notEdited")}</p>
                </div>

                <div className="flex flex-wrap gap-3">
                  <a
                    href={document.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-5 py-3 bg-ink text-paper rounded-md text-body font-medium hover:bg-ink-2"
                  >
                    <HugeiconsIcon icon={LinkSquare02Icon} size={16} />
                    {t("drawer.openOn", { source: document.source_label || "source" })}
                  </a>
                  <a
                    href={document.url}
                    download
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-5 py-3 border border-rule rounded-md text-body font-medium text-ink hover:bg-paper"
                  >
                    <HugeiconsIcon icon={Download04Icon} size={16} />
                    {t("drawer.download")}
                  </a>
                </div>

                <div className="pt-4 border-t border-rule">
                  <p className="text-caption text-ink-3 font-mono">
                    {t("drawer.howItWorks")}
                  </p>
                </div>
              </div>
            </>
          )}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
