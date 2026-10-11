import { useEffect } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import { useCatalog } from "./api/queries";
import { ContentPageRoutes } from "./pages/ContentPageRoutes";
import { HomePage } from "./pages/HomePage";
import { PlannerPage } from "./pages/PlannerPage";
import { ROUTES } from "./routes";
import { PlannerProvider } from "./state/PlannerContext";

/**
 * Routes. The planner state sits above them once the catalog has loaded, so settings and the
 * current run survive switching pages. The text pages never wait for backend data.
 */
export function App() {
  const catalog = useCatalog();
  const { pathname, hash } = useLocation();

  // A new page starts at the top, unless the link points at an anchor such as #problem-<id>.
  useEffect(() => {
    if (!hash) window.scrollTo(0, 0);
  }, [pathname, hash]);

  const routes = (
    <Routes>
      <Route path={ROUTES.home} element={<HomePage />} />
      <Route path={ROUTES.planner} element={<PlannerPage />} />
      {ContentPageRoutes()}
    </Routes>
  );

  return catalog.data ? <PlannerProvider catalog={catalog.data}>{routes}</PlannerProvider> : routes;
}
