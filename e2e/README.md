# TrustGive E2E tests (Playwright)

End-to-end tests for the 3 critical user journeys:

1. **Homepage + language switch** — `homepage-and-language.spec.ts`
2. **Catalog → Detail → Source-document drawer** — `catalog-flow.spec.ts`
3. **Donate confirmation flow** — `donate-flow.spec.ts`

## Running

```bash
cd e2e
npm install
npm run install:browsers     # one-time chromium install
# Run frontend in another terminal first:
#   cd ../frontend/web && npm run dev
npm test
```

For CI-style runs:
```bash
E2E_FRONTEND_URL=https://trustgive.pages.dev npm test
```

## Notes

- Tests that require seeded backend data (catalog flow, donate flow) gracefully `test.skip()` when the catalog returns an error. This makes the suite usable against a brand-new local backend or against a public deploy.
- Mobile testing covered via the `mobile-iphone` Playwright project (iPhone 14 viewport).
- Full Playwright trace + screenshot captured on failure.
