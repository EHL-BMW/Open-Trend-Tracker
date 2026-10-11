export const ROUTES = {
  planner: "/",
  agent: "/agent",
  featureTrends: "/feature-trends",
  impactForecast: "/sales-impact-forecast",
  newsletter: "/newsletter",
  howItWorks: "/how-it-works",
  faq: "/faq",
} as const;

/** Main navigation, in display order. */
export const NAV_ITEMS = [
  { to: ROUTES.newsletter, label: "Newsletter" },
  { to: ROUTES.agent, label: "AI Agent" },
  { to: ROUTES.featureTrends, label: "Feature Radar" },
  { to: ROUTES.impactForecast, label: "Sales Impact Forecast" },
  { to: ROUTES.planner, label: "Planner" },
  { to: ROUTES.howItWorks, label: "How it works" },
  { to: ROUTES.faq, label: "FAQ" },
] as const;
