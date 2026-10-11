import { useEffect } from "react";

/** Sets the browser tab title per page, e.g. "How it works · OpenTT". */
export function usePageTitle(page: string) {
  useEffect(() => {
    document.title = `${page} · OpenTT`;
  }, [page]);
}
