// Copies the China tech briefing from the china-tech-radar module into the frontend bundle.
// Run after the feed was refreshed there: npm run sync:newsletter
import { copyFileSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = resolve(here, "../../china-tech-radar/china_megatrends_feed.json");
const target = resolve(here, "../src/content/china-briefing.json");

if (!existsSync(source)) {
  console.error(`Feed not found: ${source}`);
  process.exit(1);
}
copyFileSync(source, target);
console.log(`Newsletter feed copied to ${target}`);
