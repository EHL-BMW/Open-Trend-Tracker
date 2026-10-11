import { Route } from "react-router-dom";
import { ROUTES } from "../routes";
import { AgentPage } from "./AgentPage";
import { FaqPage } from "./FaqPage";
import { HowItWorksPage } from "./HowItWorksPage";
import { NewsletterPage } from "./NewsletterPage";
import { NotFoundPage } from "./PlaceholderPages";

/** Routes for the text pages; returned as elements so <Routes> can use them directly. */
export function ContentPageRoutes() {
  return [
    <Route key="agent" path={ROUTES.agent} element={<AgentPage />} />,
    <Route key="how" path={ROUTES.howItWorks} element={<HowItWorksPage />} />,
    <Route key="faq" path={ROUTES.faq} element={<FaqPage />} />,
    <Route key="news" path={ROUTES.newsletter} element={<NewsletterPage />} />,
    <Route key="404" path="*" element={<NotFoundPage />} />,
  ];
}
