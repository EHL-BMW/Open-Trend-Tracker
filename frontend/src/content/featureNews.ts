import briefingRaw from "./china-briefing.json";
import { trendRadarData, type TrendTopic } from "./trendRadar";

export const FEATURE_CATEGORIES = [
  "Energy & Charging",
  "Driving Assistance",
  "Digital Cockpit & AI",
  "Connected Ecosystem",
  "Smart Cabin",
  "Vehicle Dynamics & Safety",
  "Smart Exterior",
  "Market & Portfolio",
] as const;

export type FeatureCategory = (typeof FEATURE_CATEGORIES)[number];

export interface FeatureNewsItem {
  id: string;
  featureId: string;
  featureLabel: string;
  category: FeatureCategory;
  primaryBrand: string;
  brands: string[];
  title: string;
  source: string;
  date: string;
  publishedLabel?: string;
  url: string;
  summary?: string;
  bmwRelevance?: string;
  pmAction?: string;
  impact?: string;
  keywords: string[];
  origin: "trend-feed" | "briefing-detail";
}

export interface FeatureCluster {
  id: string;
  label: string;
  labelCn: string;
  category: FeatureCategory;
  weeklyCounts: number[];
  weeklyShare: number[];
  momentumPctChange: number | null;
  priority: number | null;
  signal: string;
  volumeRecent: number;
  breadthOutlets: number;
  items: FeatureNewsItem[];
  brandCounts: Array<{ brand: string; count: number }>;
}

interface BriefingItem {
  id: string;
  publish_time: string;
  source: string;
  category: string;
  impact: string;
  title_en: string;
  title_cn: string;
  summary_en: string;
  bmw_relevance: string;
  original_url: string;
  keywords: string[];
  pm_action: string;
}

interface BriefingData {
  news_items: BriefingItem[];
}

const briefing = briefingRaw as unknown as BriefingData;

const BRAND_RULES: Array<{ brand: string; pattern: RegExp }> = [
  { brand: "NIO", pattern: /\bNIO\b|蔚来|乐道|萤火虫|Firefly/i },
  { brand: "AITO / Huawei", pattern: /AITO|HIMA|问界|智界|尊界|享界|鸿蒙智行|华为|Huawei/i },
  { brand: "Xiaomi", pattern: /Xiaomi|小米|SU7|YU7/i },
  { brand: "XPeng", pattern: /XPeng|小鹏/i },
  { brand: "Li Auto", pattern: /Li Auto|理想(?:汽车|i|L|MEGA)/i },
  { brand: "Zeekr", pattern: /Zeekr|极氪/i },
  { brand: "BYD", pattern: /\bBYD\b|比亚迪|仰望|方程豹|腾势|Denza/i },
  { brand: "BMW", pattern: /\bBMW\b|宝马/i },
  { brand: "Mercedes-Benz", pattern: /Mercedes|奔驰/i },
  { brand: "Audi", pattern: /\bAudi\b|奥迪/i },
  { brand: "Volkswagen", pattern: /Volkswagen|大众|ID\./i },
  { brand: "Tesla", pattern: /Tesla|特斯拉|马斯克/i },
  { brand: "Geely", pattern: /Geely|吉利|银河/i },
  { brand: "IM Motors", pattern: /IM Motors|智己/i },
  { brand: "Leapmotor", pattern: /Leapmotor|零跑/i },
  { brand: "Deepal", pattern: /Deepal|深蓝/i },
  { brand: "Hongqi", pattern: /Hongqi|红旗/i },
  { brand: "Arcfox", pattern: /Arcfox|极狐/i },
  { brand: "GAC", pattern: /\bGAC\b|广汽|传祺|昊铂/i },
  { brand: "Chery", pattern: /Chery|奇瑞|星途/i },
  { brand: "Avatr", pattern: /Avatr|阿维塔/i },
  { brand: "Renault", pattern: /Renault|雷诺/i },
];

const FEATURE_RULES: Array<{ id: string; pattern: RegExp }> = [
  { id: "solid_state", pattern: /solid.?state|固态电池|500\s*Wh/i },
  { id: "battery_swap", pattern: /battery swap|power swap|换电|Firefly/i },
  { id: "ultra_charging", pattern: /(?:5C|6C|megawatt|supercharg|ultra.?charg|超充|快充)/i },
  { id: "hv_800v", pattern: /(?:800V|900V|925V|SiC|高压平台|碳化硅)/i },
  { id: "sodium_ion", pattern: /sodium.?ion|钠离子|钠电/i },
  { id: "v2g", pattern: /\bV2G\b|vehicle.?grid|车网互动|虚拟电厂/i },
  { id: "adas_chips", pattern: /ADAS.*(?:chip|silicon)|Turing.*chip|Journey\s*6|智驾芯片|地平线/i },
  { id: "robotaxi", pattern: /robotaxi|无人出租/i },
  { id: "l3_autonomy", pattern: /\bL3\b|conditional autonomy|有条件自动驾驶/i },
  { id: "e2e_vla", pattern: /end.?to.?end|\bVLA\b|ADS\s*3|端到端|无图/i },
  { id: "urban_noa", pattern: /urban NOA|city NOA|城市NOA|城区智驾/i },
  { id: "lidar", pattern: /LiDAR|激光雷达/i },
  { id: "cockpit_llm", pattern: /cockpit|HyperOS|LLM|AI agent|座舱|大模型|智能体/i },
  { id: "central_compute", pattern: /central compute|中央计算|舱驾融合/i },
  { id: "phone_car_eco", pattern: /phone.?car|car.?home|ecosystem|MagLink|互联|生态/i },
  { id: "ota", pattern: /\bOTA\b|software update|软件升级/i },
  { id: "active_suspension", pattern: /active suspension|Magic Carpet|主动悬架|空气悬架/i },
  { id: "steer_by_wire", pattern: /steer.?by.?wire|brake.?by.?wire|digital chassis|线控转向|线控制动|线控底盘/i },
  { id: "giga_casting", pattern: /giga.?cast|die.?cast|一体化压铸/i },
  { id: "smart_seats", pattern: /seat|cabin|interior space|座椅|座舱|车内空间/i },
  { id: "smart_lighting", pattern: /lighting|headlight|door|大灯|车灯|车门|门把手/i },
];

function detectBrands(text: string): string[] {
  const matches = BRAND_RULES.filter((rule) => rule.pattern.test(text)).map((rule) => rule.brand);
  return matches.length ? matches : ["Industry / Multi-brand"];
}

function asCategory(value: string): FeatureCategory {
  return FEATURE_CATEGORIES.includes(value as FeatureCategory)
    ? (value as FeatureCategory)
    : "Market & Portfolio";
}

function matchFeature(item: BriefingItem): string {
  const text = [item.category, item.title_en, item.title_cn, item.summary_en, ...item.keywords].join(" ");
  return FEATURE_RULES.find((rule) => rule.pattern.test(text))?.id ?? "market_dynamics";
}

const topicById = new Map(trendRadarData.topics.map((topic) => [topic.id, topic]));
const capturedDate = trendRadarData.generated_at.slice(0, 10);
const items: FeatureNewsItem[] = [];

for (const topic of trendRadarData.topics) {
  for (const [index, headline] of topic.headlines.entries()) {
    const brands = detectBrands(headline.title);
    items.push({
      id: `trend-${topic.id}-${index}`,
      featureId: topic.id,
      featureLabel: topic.label_en,
      category: asCategory(topic.bmw_domain),
      primaryBrand: brands[0] ?? "Industry / Multi-brand",
      brands,
      title: headline.title,
      source: headline.source,
      date: headline.date,
      url: headline.link,
      keywords: [topic.label_en, topic.label_cn],
      origin: "trend-feed",
    });
  }
}

for (const detail of briefing.news_items) {
  const featureId = matchFeature(detail);
  const topic = topicById.get(featureId);
  const brands = detectBrands([detail.title_en, detail.title_cn, detail.summary_en, ...detail.keywords].join(" "));
  items.push({
    id: detail.id,
    featureId,
    featureLabel: topic?.label_en ?? "EV affordability & market pressure",
    category: topic ? asCategory(topic.bmw_domain) : "Market & Portfolio",
    primaryBrand: brands[0] ?? "Industry / Multi-brand",
    brands,
    title: detail.title_en,
    source: detail.source,
    date: capturedDate,
    publishedLabel: detail.publish_time,
    url: detail.original_url,
    summary: detail.summary_en,
    bmwRelevance: detail.bmw_relevance,
    pmAction: detail.pm_action,
    impact: detail.impact,
    keywords: detail.keywords,
    origin: "briefing-detail",
  });
}

function countBrands(news: FeatureNewsItem[]) {
  const counts = new Map<string, number>();
  for (const item of news) {
    for (const brand of item.brands) counts.set(brand, (counts.get(brand) ?? 0) + 1);
  }
  return [...counts.entries()]
    .map(([brand, count]) => ({ brand, count }))
    .sort((a, b) => b.count - a.count || a.brand.localeCompare(b.brand));
}

function clusterFromTopic(topic: TrendTopic): FeatureCluster {
  const related = items.filter((item) => item.featureId === topic.id);
  return {
    id: topic.id,
    label: topic.label_en,
    labelCn: topic.label_cn,
    category: asCategory(topic.bmw_domain),
    weeklyCounts: topic.weekly_counts,
    weeklyShare: topic.weekly_share,
    momentumPctChange: topic.momentum_pct_change,
    priority: topic.priority,
    signal: topic.signal,
    volumeRecent: topic.volume_recent,
    breadthOutlets: topic.breadth_outlets,
    items: related,
    brandCounts: countBrands(related),
  };
}

const marketItems = items.filter((item) => item.featureId === "market_dynamics");

export const featureClusters: FeatureCluster[] = [
  ...trendRadarData.topics.map(clusterFromTopic),
  ...(marketItems.length
    ? [
        {
          id: "market_dynamics",
          label: "EV affordability & market pressure",
          labelCn: "新能源车价格与市场压力",
          category: "Market & Portfolio" as const,
          weeklyCounts: [],
          weeklyShare: [],
          momentumPctChange: null,
          priority: null,
          signal: "New briefing",
          volumeRecent: marketItems.length,
          breadthOutlets: new Set(marketItems.map((item) => item.source)).size,
          items: marketItems,
          brandCounts: countBrands(marketItems),
        },
      ]
    : []),
].sort((a, b) => (b.priority ?? -1) - (a.priority ?? -1));

export const featureNewsItems = items;
export const brandStats = countBrands(items);

export const featureNewsMeta = {
  generatedAt: trendRadarData.generated_at,
  weekStarts: trendRadarData.window.week_starts,
  itemCount: items.length,
  featureCount: featureClusters.length,
  categoryCount: FEATURE_CATEGORIES.length,
};

