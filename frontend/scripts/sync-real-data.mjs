// Extracts the customer and product data the demo backend uses from the china-tech-radar module.
// Run after those CSVs changed: npm run sync:real-data
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const radar = resolve(here, "../../china-tech-radar");
const target = resolve(here, "../src/mocks/real-data.json");

/** Minimal RFC-4180 CSV parser (quoted fields may contain commas and line breaks). */
function parseCsv(file) {
  const text = readFileSync(resolve(radar, file), "utf8").replace(/^﻿/, "");
  const rows = [];
  let row = [];
  let cell = "";
  let quoted = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (quoted) {
      if (c === '"' && text[i + 1] === '"') {
        cell += '"';
        i++;
      } else if (c === '"') quoted = false;
      else cell += c;
    } else if (c === '"') quoted = true;
    else if (c === ",") {
      row.push(cell);
      cell = "";
    } else if (c === "\n") {
      row.push(cell.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      cell = "";
    } else cell += c;
  }
  if (cell || row.length) rows.push([...row, cell]);
  const header = rows.shift();
  return rows.filter((r) => r.length > 1).map((r) => Object.fromEntries(header.map((h, i) => [h, r[i] ?? ""])));
}

const clean = (s, max) => {
  const t = (s ?? "").replace(/\s+/g, " ").trim();
  return t.length > max ? `${t.slice(0, max - 1)}…` : t;
};

const customer = parseCsv("bmw_ev_technology_domain_records.csv").map((r) => ({
  id: r.feedback_id,
  cohort: r.cohort,
  powertrain: r.powertrain,
  country: r.country,
  type: r.feedback_type,
  domain: r.technology_domain,
  component: r.vfc_level2_component,
  verbatim: clean(r.customer_feedback_verbatim, 200),
}));

const praise = parseCsv("bmw_ev_technology_sentiment_pipeline.csv")
  .filter((r) => r.sentiment_type === "PRAISE")
  .map((r) => ({
    domain: r.domain_name,
    component: r.component_vfc,
    volume: Number(r.volume_count) || 0,
    sample: clean(r.verbatim_sample, 200),
  }));

const catalog = parseCsv("bmw_ev_phev_catalog.csv").map((r) => ({
  model: r.model,
  variant: r.variant,
  powertrain: r.powertrain,
  europeUnits: Number(r.europe_sales_units) || 0,
  basePriceEur: Number(r.base_price_eur) || 0,
  heatPump: r.heat_pump,
  dcChargingKw: Number(r.dc_charging_kw) || 0,
  headUpDisplay: r.head_up_display,
  audioSystem: r.audio_system,
  rangeKm: Number(r.electric_range_wltp_km) || 0,
  drivetrain: r.drivetrain,
  accel0to100: Number(r.accel_0_100_s) || 0,
  towingKg: Number(r.towing_capacity_kg) || 0,
  interior: r.interior_highlights,
  exterior: r.exterior_highlights,
  assistance: r.driver_assistance,
  highlights: [r.unique_selling_points, r.interior_highlights, r.exterior_highlights, r.driver_assistance].join(" | "),
}));

const out = {
  source: {
    module: "china-tech-radar",
    files: [
      "bmw_ev_technology_domain_records.csv",
      "bmw_ev_technology_sentiment_pipeline.csv",
      "bmw_ev_phev_catalog.csv",
    ],
  },
  customer,
  praise,
  catalog,
};
writeFileSync(target, `${JSON.stringify(out)}\n`);
console.log(
  `Real data written to ${target}: ${customer.length} customer records, ${praise.length} praise rows, ${catalog.length} catalogue variants`,
);
