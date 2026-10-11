export const ROUTES = {
  planner: "/",
  agent: "/agent",
  newsletter: "/newsletter",
  howItWorks: "/how-it-works",
  faq: "/faq",
} as const;

/** Main navigation, in display order. */
export const NAV_ITEMS = [
  { to: ROUTES.planner, label: "Planner" },
  { to: ROUTES.agent, label: "AI Agent" },
  { to: ROUTES.newsletter, label: "Newsletter" },
  { to: ROUTES.howItWorks, label: "How it works" },
  { to: ROUTES.faq, label: "FAQ" },
] as const;
