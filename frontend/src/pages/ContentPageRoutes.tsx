import { Navigate, Route } from "react-router-dom";
import { ROUTES } from "../routes";
import { AgentPage } from "./AgentPage";
import { FeatureTrendsPage } from "./FeatureTrendsPage";
import { TrackedFeaturesPage } from "./TrackedFeaturesPage";
import { FaqPage } from "./FaqPage";
import { HowItWorksPage } from "./HowItWorksPage";
import { NewsletterPage } from "./NewsletterPage";
import { ImpactForecastPage } from "./ImpactForecastPage";
import { NotFoundPage } from "./PlaceholderPages";

/** Routes for the text pages; returned as elements so <Routes> can use them directly. */
export function ContentPageRoutes() {
  return [
    <Route key="agent" path={ROUTES.agent} element={<AgentPage />} />,
    <Route key="feature-trends" path={ROUTES.featureTrends} element={<FeatureTrendsPage />} />,
    <Route key="tracked-features" path={ROUTES.trackedFeatures} element={<TrackedFeaturesPage />} />,
    <Route key="impact-forecast" path={ROUTES.impactForecast} element={<ImpactForecastPage />} />,
    // old address of the Impact Analysis page, kept so shared links still work
    <Route
      key="impact-forecast-old"
      path="/sales-impact-forecast"
      element={<Navigate to={ROUTES.impactForecast} replace />}
    />,
    <Route key="how" path={ROUTES.howItWorks} element={<HowItWorksPage />} />,
    <Route key="faq" path={ROUTES.faq} element={<FaqPage />} />,
    <Route key="news" path={ROUTES.newsletter} element={<NewsletterPage />} />,
    <Route key="404" path="*" element={<NotFoundPage />} />,
  ];
}
