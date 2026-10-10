import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import { server } from "../mocks/node";
import { apiUrl, ApiError } from "./client";
import { api } from "./endpoints";

describe("api client", () => {
  it("returns validated data", async () => {
    const catalog = await api.getCatalog();
    expect(catalog.categories.sales.filters.map((g) => g.key)).toEqual(["line", "powertrain"]);
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
