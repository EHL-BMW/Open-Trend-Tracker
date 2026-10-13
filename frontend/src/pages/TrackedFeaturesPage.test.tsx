import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { TrackButton } from "../components/TrackButton";
import { featureClusters } from "../content/featureNews";
import { useTrackedFeatures } from "../state/trackedFeatures";
import { server } from "../mocks/node";
import { TrackedFeaturesPage } from "./TrackedFeaturesPage";

vi.mock("../api/queries", () => ({
  useImpactForecast: () => ({
    data: {
      categories: [
        {
          id: "energy",
          label: "Energy & Charging",
          impact_by_year: [],
          subcategories: [
            {
              id: "battery_range",
              label: "Battery & range",
              pair_count: 5,
              impact_by_year: [{ year: 1, impact_pct: 20.8, lower_pct: 10, upper_pct: 30, pairs: 5 }],
              legacy_features: [],
              news_features: [{ id: "solid_state" }],
            },
          ],
        },
      ],
    },
  }),
  useCatalog: () => ({ data: null }),
}));

function WatchlistState() {
  return <span data-testid="tracked-count">{useTrackedFeatures().length}</span>;
}

describe("My Features", () => {
  it("shows a tracked feature from another page and lets the user remove it", async () => {
    server.use(http.get("/api/v1/agent/problems", () => HttpResponse.json({ problems: [] })));
    const feature = featureClusters.find((item) => item.id === "solid_state")!;
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <TrackButton id={feature.id} label={feature.label} />
        <WatchlistState />
        <TrackedFeaturesPage />
      </MemoryRouter>,
    );

    expect(screen.getByText("No tracked features yet")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: `Track ${feature.label}` }));
    expect(screen.getByRole("status")).toHaveTextContent("Find it in My Features");
    expect(screen.getByRole("heading", { name: feature.label })).toBeInTheDocument();
    expect(screen.getByTestId("tracked-count")).toHaveTextContent("1");
    expect(JSON.parse(localStorage.getItem("opentt.tracked-features.v1") ?? "[]")).toContain(feature.id);

    await user.click(screen.getByRole("button", { name: `Open report for ${feature.label}` }));
    expect(screen.getByRole("dialog", { name: `${feature.label} report` })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "12-week coverage trend" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Sales impact · years 1–4" })).toBeInTheDocument();
    expect(screen.getAllByText("Not available")).toHaveLength(3);
    await user.click(screen.getByRole("button", { name: "Close report" }));

    await user.click(screen.getAllByRole("button", { name: `Stop tracking ${feature.label}` })[0]!);
    expect(screen.getByText("No tracked features yet")).toBeInTheDocument();
    expect(screen.getByTestId("tracked-count")).toHaveTextContent("0");
  });
});
