import { Route, Routes } from "react-router-dom";
import { useCatalog } from "./api/queries";
import { ContentPageRoutes } from "./pages/ContentPageRoutes";
import { PlannerPage } from "./pages/PlannerPage";
import { ROUTES } from "./routes";
import { PlannerProvider } from "./state/PlannerContext";

/**
 * Routes. The planner state sits above them once the catalog has loaded, so settings and the
 * current run survive switching pages. The text pages never wait for backend data.
 */
export function App() {
  const catalog = useCatalog();

  const routes = (
    <Routes>
      <Route path={ROUTES.planner} element={<PlannerPage />} />
      {ContentPageRoutes()}
    </Routes>
  );

  return catalog.data ? <PlannerProvider catalog={catalog.data}>{routes}</PlannerProvider> : routes;
}
