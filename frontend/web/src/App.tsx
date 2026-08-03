import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"

import { Layout } from "./components/layout/Layout"
import { CatalogPage } from "./pages/CatalogPage"
import { AboutPage } from "./pages/AboutPage"
import { ApiPage } from "./pages/ApiPage"
import { CharityDetailPage } from "./pages/CharityDetailPage"
import { DataSourcesPage } from "./pages/DataSourcesPage"
import { HomePage } from "./pages/HomePage"
import { HubPage } from "./pages/HubPage"
import { LegitPage } from "./pages/LegitPage"
import { MethodologyPage } from "./pages/MethodologyPage"
import { NotFoundPage } from "./pages/NotFoundPage"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000,
      refetchOnWindowFocus: false,
    },
  },
})

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="charities" element={<CatalogPage />} />
            {/* v3.21 hub sections. Declared before the `:slug` detail route for
                readability — React Router ranks the static "country"/"cause"/
                "registry" segments above the dynamic one regardless of order. */}
            <Route path="charities/country/:slug" element={<HubPage kind="country" />} />
            <Route path="charities/cause/:slug" element={<HubPage kind="cause" />} />
            <Route path="charities/registry/:slug" element={<HubPage kind="registry" />} />
            <Route path="charities/:slug" element={<CharityDetailPage />} />
            <Route path="charities/:slug/legit" element={<LegitPage />} />
            {/* /compare route removed in v3.0 */}
            <Route path="compare" element={<Navigate to="/charities" replace />} />
            <Route path="methodology" element={<MethodologyPage />} />
            <Route path="about" element={<AboutPage />} />
            <Route path="data-sources" element={<DataSourcesPage />} />
            <Route path="api" element={<ApiPage />} />
            <Route path="ru" element={<Navigate to="/" replace />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
