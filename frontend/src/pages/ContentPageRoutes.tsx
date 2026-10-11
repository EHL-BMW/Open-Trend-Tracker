import { Route } from "react-router-dom";
import { ROUTES } from "../routes";
import { HowItWorksPage } from "./HowItWorksPage";
import { NewsletterPage } from "./NewsletterPage";
import { FaqPage, NotFoundPage } from "./PlaceholderPages";

/** Routes for the text pages; returned as elements so <Routes> can use them directly. */
export function ContentPageRoutes() {
  return [
    <Route key="how" path={ROUTES.howItWorks} element={<HowItWorksPage />} />,
    <Route key="faq" path={ROUTES.faq} element={<FaqPage />} />,
    <Route key="news" path={ROUTES.newsletter} element={<NewsletterPage />} />,
    <Route key="404" path="*" element={<NotFoundPage />} />,
  ];
}
