export const ROUTES = {
  planner: "/",
  howItWorks: "/how-it-works",
  faq: "/faq",
  newsletter: "/newsletter",
} as const;

/** Main navigation, in display order. */
export const NAV_ITEMS = [
  { to: ROUTES.planner, label: "Planner" },
  { to: ROUTES.howItWorks, label: "How it works" },
  { to: ROUTES.faq, label: "FAQ" },
  { to: ROUTES.newsletter, label: "Newsletter" },
] as const;
