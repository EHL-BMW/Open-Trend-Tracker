// Copies the China tech briefing from the china-tech-radar module into the frontend bundle.
// Run after the feed was refreshed there: npm run sync:newsletter
import { copyFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const radarSource = resolve(here, "../../china-tech-radar/china_tech_trends.json");
const radarTarget = resolve(here, "../src/content/china_tech_trends.json");
const feedSource = resolve(here, "../../china-tech-radar/china_megatrends_feed.json");
const feedTarget = resolve(here, "../src/content/china-briefing.json");

if (existsSync(radarSource)) {
  copyFileSync(radarSource, radarTarget);
  console.log(`Trend radar data copied to ${radarTarget}`);
}
if (existsSync(feedSource)) {
  copyFileSync(feedSource, feedTarget);
  console.log(`Newsletter feed copied to ${feedTarget}`);
}
