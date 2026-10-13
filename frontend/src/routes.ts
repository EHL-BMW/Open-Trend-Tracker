export const ROUTES = {
  home: "/",
  planner: "/planner",
  agent: "/agent",
  featureTrends: "/feature-trends",
  trackedFeatures: "/tracked-features",
  impactForecast: "/sales-impact-forecast",
  newsletter: "/newsletter",
  howItWorks: "/how-it-works",
  faq: "/faq",
} as const;

/** Main navigation, in display order. */
export const NAV_ITEMS = [
  { to: ROUTES.newsletter, label: "Newsletter" },
  { to: ROUTES.featureTrends, label: "Pain Points" },
  { to: ROUTES.impactForecast, label: "Sales Impact Forecast" },
  { to: ROUTES.trackedFeatures, label: "My Features" },
  { to: ROUTES.agent, label: "AI Agent" },
  { to: ROUTES.planner, label: "Planner" },
  { to: ROUTES.howItWorks, label: "How it works" },
  { to: ROUTES.faq, label: "FAQ" },
] as const;
