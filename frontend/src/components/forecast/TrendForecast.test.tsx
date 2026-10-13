import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { TrendForecast } from "./TrendForecast";

vi.mock("../../api/queries", () => ({
  useImpactForecast: () => ({
    data: {
      categories: [{
        id: "cockpit",
        label: "Digital Cockpit & AI",
        subcategories: [{
          legacy_features: [{
            name: "Connected cockpit upgrade",
            pair_count: 22,
            impact_by_year: [
              { year: 1, impact_pct: 2 },
              { year: 4, impact_pct: 5 },
            ],
          }],
        }],
      }],
      isolated_feature_count: 1,
      legacy_feature_count: 1,
    },
    isLoading: false,
    isError: false,
  }),
}));

describe("legacy feature comparison", () => {
  it("lets a user exclude and restore a legacy feature from its row", async () => {
    const user = userEvent.setup();
    render(<MemoryRouter><TrendForecast /></MemoryRouter>);

    const row = screen.getByRole("checkbox", { name: "Include Connected cockpit upgrade in legacy feature comparison" });
    expect(row).toHaveAttribute("aria-checked", "true");
    await user.click(row);
    expect(row).toHaveAttribute("aria-checked", "false");
    await user.keyboard("{Enter}");
    expect(row).toHaveAttribute("aria-checked", "true");

    await user.click(screen.getByRole("button", { name: "Track Connected cockpit upgrade" }));
    expect(row).toHaveAttribute("aria-checked", "true");
  });
});
