import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { apiUrl } from "./api/client";
import { App } from "./App";
import type { AnalysisRequest } from "./api/types";
import { buildCatalog, runAnalysis } from "./mocks/engine";
import { server } from "./mocks/node";
import { renderWithClient } from "./test/render";

/** The nav button once the catalog has loaded (the loading frame renders a disabled one). */
async function findRunButton() {
  await screen.findByText("No analysis yet");
  return screen.getAllByRole("button", { name: "Run analysis" })[0]!;
}

describe("App", () => {
  it("starts empty, loads filters from the backend and runs the analysis", async () => {
    const user = userEvent.setup();
    renderWithClient(<App />, { route: "/planner" });

    // Before the catalog arrives nothing is filled in.
    expect(screen.getByText("Loading sources…")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run analysis" })).toBeDisabled();

    expect(await screen.findByText("No analysis yet")).toBeInTheDocument();

    // Filters come from the catalog.
    await user.click(screen.getByRole("button", { name: /^Sales:/ }));
    expect(screen.getByRole("checkbox", { name: "BEV" })).toHaveAttribute("aria-checked", "true");
    expect(screen.getByRole("checkbox", { name: "iX" })).toBeInTheDocument();

    await user.click(screen.getAllByRole("button", { name: "Run analysis" })[0]!);
    expect(await screen.findAllByRole("button", { name: /^Show reasoning for/ })).toHaveLength(5);
    expect(screen.getAllByRole("list", { name: "What produced this rank" })).toHaveLength(5);
  });

  it("marks results as outdated after settings change and sends the new filters", async () => {
    const user = userEvent.setup();
    let lastBody: unknown;
    server.events.on("request:start", async ({ request }) => {
      if (request.method === "POST") lastBody = await request.clone().json();
    });
    renderWithClient(<App />, { route: "/planner" });

    await user.click(await findRunButton());
    await screen.findAllByRole("button", { name: /^Show reasoning for/ });

    await user.click(screen.getByRole("button", { name: /^Sales:/ }));
    await user.click(screen.getByRole("checkbox", { name: "PHEV" }));
    expect(await screen.findByText(/Settings changed since this run/)).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Run again" }));
    await waitFor(() => expect(screen.queryByText(/Settings changed since this run/)).not.toBeInTheDocument());
    expect(lastBody).toMatchObject({ filters: { sales: { powertrain: ["BEV"] } } });
    server.events.removeAllListeners();
  });

  it("opens the reasoning sheet with verdict and sources", async () => {
    const user = userEvent.setup();
    renderWithClient(<App />, { route: "/planner" });
    await user.click(await findRunButton());

    const [first] = await screen.findAllByRole("button", { name: /^Show reasoning for/ });
    await user.click(first!);
    const dialog = screen.getByRole("dialog", { hidden: true });
    expect(within(dialog).getByText(/^Ranks #1 with/)).toBeInTheDocument();
    expect(within(dialog).getByText("How the rank was built")).toBeInTheDocument();
  });

  it("shows a retryable error when the catalog can't load", async () => {
    server.use(
      http.get(apiUrl("/catalog"), () =>
        HttpResponse.json({ error: { code: "unavailable", message: "Service unavailable." } }, { status: 503 }),
      ),
    );
    renderWithClient(<App />, { route: "/planner" });
    expect(await screen.findByText("Couldn't load the data")).toBeInTheDocument();
    expect(screen.getByText("Service unavailable.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  });
  it("navigates between pages and keeps the current run", async () => {
    const user = userEvent.setup();
    renderWithClient(<App />, { route: "/planner" });
    await user.click(await findRunButton());
    await screen.findAllByRole("button", { name: /^Show reasoning for/ });

    const nav = screen.getByRole("navigation", { name: "Main" });
    await user.click(within(nav).getByRole("link", { name: "How it works" }));
    expect(await screen.findByRole("heading", { level: 1, name: "How it works" })).toBeInTheDocument();
    expect(document.title).toBe("How it works · OpenTT – Open Trend Tracker");

    await user.click(within(screen.getByRole("navigation", { name: "Main" })).getByRole("link", { name: "FAQ" }));
    expect(await screen.findByRole("heading", { level: 1, name: "FAQ" })).toBeInTheDocument();

    await user.click(within(screen.getByRole("navigation", { name: "Main" })).getByRole("link", { name: "Planner" }));
    expect(await screen.findAllByRole("button", { name: /^Show reasoning for/ })).toHaveLength(5);
  });

  it("opens on the home page and links to the planner", async () => {
    const user = userEvent.setup();
    renderWithClient(<App />);
    expect(screen.getByRole("heading", { level: 1, name: "OpenTT, Open Trend Tracker" })).toBeInTheDocument();
    expect(screen.getByText(/continuously discovers emerging vehicle features in China/)).toBeInTheDocument();

    await user.click(screen.getByRole("link", { name: "Open the planner" }));
    expect(await screen.findByRole("heading", { level: 1, name: "Plan your next series update." })).toBeInTheDocument();

    await user.click(screen.getByRole("link", { name: "OpenTT, go to the home page" }));
    expect(await screen.findByText(/continuously discovers emerging vehicle features in China/)).toBeInTheDocument();
  });

  it("shows content pages even when the backend is down", async () => {
    server.use(
      http.get(apiUrl("/catalog"), () =>
        HttpResponse.json({ error: { code: "x", message: "Down." } }, { status: 503 }),
      ),
    );
    renderWithClient(<App />, { route: "/how-it-works" });
    expect(await screen.findByRole("heading", { level: 1, name: "How it works" })).toBeInTheDocument();
  });
  it("shows the China EV-Tech Trend Radar on the Newsletter page", async () => {
    renderWithClient(<App />, { route: "/newsletter" });
    expect(await screen.findByRole("heading", { level: 1, name: "China EV-Tech Trend Radar" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Top 3 signals" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Trend map" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "All topics, ranked by priority" })).toBeInTheDocument();
    expect(screen.getAllByText("Solid-state batteries").length).toBeGreaterThan(0);
  });
  it("recovers when the backend data changed while the page was open", async () => {
    const user = userEvent.setup();
    renderWithClient(<App />, { route: "/planner" });
    const run = await findRunButton();
    // From now on the backend serves a newer data version and rejects requests for the old one.
    server.use(
      http.get(apiUrl("/catalog"), () => HttpResponse.json({ ...buildCatalog(), dataVersion: "demo-next" })),
      http.post(apiUrl("/analyses"), async ({ request }) => {
        const body = (await request.json()) as AnalysisRequest;
        if (body.dataVersion !== "demo-next")
          return HttpResponse.json(
            { error: { code: "stale_data_version", message: "The data was updated." } },
            { status: 409 },
          );
        return HttpResponse.json(runAnalysis(body, "retry", new Date().toISOString()), { status: 201 });
      }),
    );
    await user.click(run);
    expect(await screen.findAllByRole("button", { name: /^Show reasoning for/ }, { timeout: 4000 })).toHaveLength(5);
  });
});
