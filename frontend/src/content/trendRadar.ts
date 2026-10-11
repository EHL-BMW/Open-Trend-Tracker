/**
 * China EV-Tech Trend Radar data layer.
 * Loaded from `china_tech_trends.json`, which was produced by `scrape_china_tech_trends.py`.
 */
import raw from "./china_tech_trends.json";

export interface TrendHeadline {
  title: string;
  source: string;
  date: string;
  link: string;
}

export interface TrendTopic {
  id: string;
  label_en: string;
  label_cn: string;
  query: string;
  bmw_domain: string;
  weekly_counts: number[];
  weekly_share: number[];
  volume_recent: number;
  volume_prior: number;
  momentum: number;
  momentum_pct_change: number;
  p_momentum: number;
  mk_z: number;
  mk_p: number;
  sens_slope_share_pp_per_week: number;
  breadth_outlets: number;
  top_outlets: [string, number][];
  saturated_days?: number;
  resolved_quota_days?: number;
  recovered_quota_articles?: number;
  headlines: TrendHeadline[];
  share_of_voice: number;
  attention_pct: number;
  momentum_pct: number;
  bmw_exposure: number;
  priority: number;
  signal: "Accelerating" | "Cooling" | "Stable";
  quadrant: string;
}

export interface BmwDomainStat {
  complaints: number;
  share_pct: number;
  avg_severity: number;
  top_components: string;
  exposure: number;
}

export interface TrendRadarData {
  generated_at: string;
  window: {
    start: string;
    end: string;
    weeks: number;
    recent_weeks: number;
    week_starts: string[];
  };
  source: string;
  totals: {
    articles: number;
    outlets: number;
    topics: number;
  };
  bmw_domains: Record<string, BmwDomainStat>;
  method: {
    momentum: string;
    p_momentum: string;
    trend: string;
    breadth: string;
    exposure: string;
    priority: string;
    signal: string;
    quota_resolution?: string;
  };
  topics: TrendTopic[];
}

export const trendRadarData: TrendRadarData = raw as unknown as TrendRadarData;

export const DOMAIN_COLORS: Record<string, string> = {
  "Energy & Charging": "#38bdf8",
  "Driving Assistance": "#a78bfa",
  "Digital Cockpit & AI": "#fbbf24",
  "Connected Ecosystem": "#f472b6",
  "Vehicle Dynamics & Safety": "#34d399",
  "Smart Cabin": "#fb923c",
  "Smart Exterior": "#94a3b8",
};

export const SHORT_TOPIC_NAMES: Record<string, string> = {
  solid_state: "Solid-state battery",
  sodium_ion: "Sodium-ion",
  ultra_charging: "5C / MW charging",
  hv_800v: "800V & SiC",
  battery_swap: "Battery swap",
  v2g: "V2G",
  e2e_vla: "End-to-end / VLA",
  urban_noa: "Urban NOA",
  l3_autonomy: "L3 autonomy",
  lidar: "LiDAR",
  robotaxi: "Robotaxi",
  adas_chips: "ADAS chips",
  cockpit_llm: "Cockpit AI",
  central_compute: "Central compute",
  phone_car_eco: "Phone-car ecosystem",
  ota: "OTA",
  steer_by_wire: "Steer-by-wire",
  active_suspension: "Active suspension",
  giga_casting: "Giga-casting",
  smart_seats: "Smart seats",
  smart_lighting: "Smart exterior",
};

export const fmtPct = (v: number) => (v > 0 ? "+" : "") + Math.round(v) + "%";
export const fmtP = (p: number) => (p < 0.001 ? "p < 0.001" : "p = " + p.toFixed(3));
