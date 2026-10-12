import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import { server } from "../mocks/node";
import { apiUrl, ApiError } from "./client";
import { api } from "./endpoints";
import { technologyForecastSchema } from "./schemas";

describe("api client", () => {
  it("returns validated data", async () => {
    const catalog = await api.getCatalog();
    expect(catalog.categories.sales.filters.map((g) => g.key)).toEqual(["line", "powertrain"]);
  });

  it("accepts a signed four-year sales-impact trajectory", () => {
    const result = technologyForecastSchema.parse({
      technology: "smart-seats",
      label: "Smart seats",
      currentShare: 0.12,
      forecastShare: -0.08,
      impactByYear: [
        { year: 1, impact: 0.12, pairs: 8 },
        { year: 2, impact: 0.04, pairs: 8 },
        { year: 3, impact: -0.02, pairs: 8 },
        { year: 4, impact: -0.08, pairs: 8 },
      ],
    });
    expect(result.impactByYear?.map((point) => point.year)).toEqual([1, 2, 3, 4]);
  });

  it("turns the backend error body into an ApiError", async () => {
    server.use(
      http.get(apiUrl("/catalog"), () =>
        HttpResponse.json({ error: { code: "db_down", message: "Database unavailable." } }, { status: 503 }),
      ),
    );
    await expect(api.getCatalog()).rejects.toMatchObject({
      status: 503,
      code: "db_down",
      message: "Database unavailable.",
    });
  });

  it("rejects responses that break the contract", async () => {
    server.use(http.get(apiUrl("/catalog"), () => HttpResponse.json({ dataVersion: 1 })));
    vi.spyOn(console, "error").mockImplementation(() => {});
    await expect(api.getCatalog()).rejects.toMatchObject({ code: "invalid_response" });
  });

  it("reports network failures clearly", async () => {
    server.use(http.get(apiUrl("/catalog"), () => HttpResponse.error()));
    const err = await api.getCatalog().catch((e: unknown) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect((err as ApiError).code).toBe("network_error");
  });
});
