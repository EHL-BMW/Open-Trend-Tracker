import { useEffect } from "react";

/** Sets the browser tab title per page, e.g. "How it works · OpenTT – Open Trend Tracker". */
export function usePageTitle(page: string) {
  useEffect(() => {
    document.title = `${page} · OpenTT – Open Trend Tracker`;
  }, [page]);
}
