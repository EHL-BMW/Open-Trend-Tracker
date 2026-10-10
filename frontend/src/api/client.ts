import type { ZodType } from "zod";
import { config } from "../config";
import { apiErrorBodySchema } from "./schemas";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code: string,
    readonly details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Absolute URL for an API path; relative base URLs resolve against the current page. */
export function apiUrl(path: string): string {
  return new URL(`${config.apiBaseUrl}${path}`, window.location.href).toString();
}

interface RequestOptions {
  method?: "GET" | "POST";
  body?: unknown;
  signal?: AbortSignal;
}

export async function request<T>(
  path: string,
  schema: ZodType<T>,
  { method = "GET", body, signal }: RequestOptions = {},
): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort("timeout"), config.requestTimeoutMs);
  const onAbort = () => controller.abort(signal?.reason);
  signal?.addEventListener("abort", onAbort, { once: true });

  let response: Response;
  try {
    response = await fetch(apiUrl(path), {
      method,
      headers: {
        Accept: "application/json",
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
  } catch (err) {
    if (controller.signal.reason === "timeout") {
      throw new ApiError("The server took too long to respond. Please try again.", 0, "timeout");
    }
    if (signal?.aborted) throw err;
    throw new ApiError("Can't reach the server. Check your connection and try again.", 0, "network_error");
  } finally {
    clearTimeout(timeout);
    signal?.removeEventListener("abort", onAbort);
  }

  const payload: unknown = await response.json().catch(() => undefined);

  if (!response.ok) {
    const parsed = apiErrorBodySchema.safeParse(payload);
    if (parsed.success) {
      const { code, message, details } = parsed.data.error;
      throw new ApiError(message, response.status, code, details);
    }
    throw new ApiError(`Request failed (${response.status}).`, response.status, "http_error");
  }

  const result = schema.safeParse(payload);
  if (!result.success) {
    // A contract mismatch is a bug on one side; surface it instead of rendering half-broken data.
    console.error(`Unexpected response from ${path}`, result.error.issues);
    throw new ApiError(
      "The server sent data in an unexpected format.",
      response.status,
      "invalid_response",
      result.error.issues,
    );
  }
  return result.data;
}

export const errorMessage = (err: unknown) =>
  err instanceof ApiError ? err.message : "Something went wrong. Please try again.";
