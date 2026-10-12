import raw from "./headlineNotes.json";

export interface HeadlineNote {
  titleEn: string;
  featureSummary: string;
}

/** Reviewed demo notes, keyed by both feature and headline to avoid stale matches after a re-scrape. */
export const HEADLINE_NOTES: Record<string, Record<string, HeadlineNote>> = raw;
