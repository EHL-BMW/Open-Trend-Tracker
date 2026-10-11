/**
 * The China tech briefing shown on the Newsletter page. Source: china-tech-radar/china_megatrends_feed.json
 * (refresh with `npm run sync:newsletter`). Validated here so a format change shows a message, not a crash.
 */
import { z } from "zod";
import raw from "./china-briefing.json";

const newsItemSchema = z.object({
  id: z.string(),
  publish_time: z.string(),
  source: z.string(),
  source_tag: z.string().optional(),
  category: z.string(),
  impact: z.string(),
  title_en: z.string(),
  title_cn: z.string().optional(),
  summary_en: z.string(),
  bmw_relevance: z.string().optional(),
  pm_action: z.string().optional(),
  original_url: z.string().url().optional(),
  keywords: z.array(z.string()).default([]),
  threat_level: z.string().optional(),
});

const megatrendSchema = z.object({
  trend_id: z.string(),
  title_en: z.string(),
  status: z.string(),
  executive_takeaway: z.string(),
});

const briefingSchema = z.object({
  feed_metadata: z.object({
    feed_name: z.string(),
    last_updated: z.string(),
    sources_monitored: z.array(z.string()).default([]),
  }),
  megatrends_summary: z.array(megatrendSchema).default([]),
  news_items: z.array(newsItemSchema).default([]),
});

export type Briefing = z.infer<typeof briefingSchema>;
export type NewsItem = z.infer<typeof newsItemSchema>;
export type Megatrend = z.infer<typeof megatrendSchema>;

const parsed = briefingSchema.safeParse(raw);
if (!parsed.success) console.error("Newsletter feed has an unexpected format", parsed.error.issues);

export const briefing: Briefing | null = parsed.success ? parsed.data : null;

/** "1 hour ago • 09:45 CST" → "09:45 CST": the relative part was frozen when the feed was generated. */
export const clockTime = (publishTime: string) => publishTime.split("•").pop()?.trim() ?? publishTime;

/** "REGULATORY_BREAKTHROUGH" → "Regulatory breakthrough" */
export const humanize = (value: string) => {
  const s = value.replace(/_/g, " ").toLowerCase();
  return s.charAt(0).toUpperCase() + s.slice(1);
};
