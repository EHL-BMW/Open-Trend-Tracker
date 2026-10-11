import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll } from "vitest";
import { resetMockDb } from "../mocks/handlers";
import { server } from "../mocks/node";

// jsdom has no IntersectionObserver (framer-motion's whileInView needs one). Report everything as visible.
if (typeof window !== "undefined" && !("IntersectionObserver" in window)) {
  class VisibleObserver {
    constructor(private readonly callback: IntersectionObserverCallback) {}
    observe(target: Element) {
      const rect = target.getBoundingClientRect();
      this.callback(
        [{ target, isIntersecting: true, intersectionRatio: 1, intersectionRect: rect } as IntersectionObserverEntry],
        this as unknown as IntersectionObserver,
      );
    }
    unobserve() {}
    disconnect() {}
    takeRecords() {
      return [];
    }
  }
  Object.assign(window, { IntersectionObserver: VisibleObserver });
}

// jsdom does not implement scrolling or media playback.
window.scrollTo = () => {};
Element.prototype.scrollIntoView = () => {};
if (typeof HTMLMediaElement !== "undefined") {
  HTMLMediaElement.prototype.play = () => Promise.resolve();
  HTMLMediaElement.prototype.pause = () => {};
}

// jsdom has <dialog> but not its modal API.
if (typeof HTMLDialogElement !== "undefined" && !HTMLDialogElement.prototype.showModal) {
  HTMLDialogElement.prototype.showModal = function showModal(this: HTMLDialogElement) {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function close(this: HTMLDialogElement) {
    this.removeAttribute("open");
    this.dispatchEvent(new Event("close"));
  };
}

// jsdom replaces AbortController, and Node's fetch rejects jsdom signals ("Expected signal to be an
// instance of AbortSignal"). Real browsers are unaffected; in tests, requests simply run unabortable.
// The wrapper goes on after server.listen() so it sits outside MSW's own fetch interceptor.
beforeAll(() => {
  server.listen({ onUnhandledRequest: "error" });
  const mswFetch = globalThis.fetch;
  globalThis.fetch = (input, init) => mswFetch(input, init ? { ...init, signal: undefined } : init);
});
afterEach(() => {
  cleanup();
  server.resetHandlers();
  resetMockDb();
});
afterAll(() => server.close());
