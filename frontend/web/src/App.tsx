import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"

import { Layout } from "./components/layout/Layout"
import { CatalogPage } from "./pages/CatalogPage"
import { CharityDetailPage } from "./pages/CharityDetailPage"
import { ComparePage } from "./pages/ComparePage"
import { HomePage } from "./pages/HomePage"
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
            <Route path="charities/:slug" element={<CharityDetailPage />} />
            <Route path="compare" element={<ComparePage />} />
            <Route path="methodology" element={<MethodologyPage />} />
            <Route path="ru" element={<Navigate to="/" replace />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
