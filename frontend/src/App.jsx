import { useEffect, useMemo, useState } from "react";
import "./app.css";

const fmt = (value, digits = 0) => value == null ? "–" : Number(value).toLocaleString(undefined, { maximumFractionDigits: digits });

async function jsonFetch(url, options) {
  const response = await fetch(url, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `Request failed (${response.status})`);
  return body;
}

function EvidencePage() {
  const [vehicles, setVehicles] = useState([]);
  const [vehicle, setVehicle] = useState(null);
  const [market, setMarket] = useState("ALL");
  const [node, setNode] = useState(null);

  useEffect(() => {
    jsonFetch("/api/vehicles").then((items) => {
      setVehicles(items);
      if (items.length) setVehicle(items[0].vehicle);
    });
  }, []);
  useEffect(() => {
    if (vehicle) jsonFetch(`/api/vehicles/${vehicle}/markets/${market}`).then(setNode);
  }, [vehicle, market]);

  const markets = vehicles.find((item) => item.vehicle === vehicle)?.markets ?? [];
  return <section>
    <h2>Unified evidence</h2>
    <div className="controls">
      <label>Vehicle<select value={vehicle ?? ""} onChange={(event) => { setVehicle(event.target.value); setMarket("ALL"); }}>
        {vehicles.map((item) => <option key={item.vehicle} value={item.vehicle}>{item.vehicle} – {item.line}</option>)}
      </select></label>
      <label>Market<select value={market} onChange={(event) => setMarket(event.target.value)}>
        {markets.map((item) => <option key={item}>{item}</option>)}
      </select></label>
    </div>
    {node && Object.values(node.categories).map((category) => <details key={category.id}>
      <summary>{category.name} — score {fmt(category.score, 2)}</summary>
      <ul>{Object.values(category.attributes).map((attribute) => <li key={attribute.id}>
        {attribute.name}: {fmt(attribute.score, 2)} <small>({attribute.status})</small>
      </li>)}</ul>
    </details>)}
  </section>;
}

function ForecastPage() {
  const [catalog, setCatalog] = useState(null);
  const [model, setModel] = useState("");
  const [market, setMarket] = useState("Global");
  const [selected, setSelected] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [prices, setPrices] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    jsonFetch("/api/forecast/catalog").then((data) => {
      setCatalog(data);
      setModel(Object.keys(data.bmw_sales_history)[0] || "");
    }).catch((reason) => setError(reason.message));
  }, []);
  useEffect(() => {
    if (!catalog || !model) return;
    const markets = catalog.bmw_sales_history[model] || {};
    if (!markets[market]) setMarket(markets.Global ? "Global" : Object.keys(markets)[0]);
  }, [catalog, model, market]);
  useEffect(() => {
    if (!model) return;
    const params = new URLSearchParams({ model, market });
    selected.forEach((feature) => params.append("feature", feature));
    jsonFetch(`/api/forecast/sales?${params}`).then(setForecast).catch((reason) => setError(reason.message));
    jsonFetch(`/api/forecast/prices/${model.split("/")[0]}?target_year=2030`).then(setPrices).catch(() => setPrices(null));
  }, [model, market, selected]);

  const markets = catalog?.bmw_sales_history[model] || {};
  const features = catalog?.features || [];
  const rows = useMemo(() => forecast?.years.map((year, index) => ({
    year, baseline: forecast.baseline[index], estimate: forecast.estimate[index],
    low: forecast.lower[index], high: forecast.upper[index], uplift: forecast.impact[index],
  })) || [], [forecast]);

  if (error) return <section><h2>Forecast</h2><p className="error">{error}</p></section>;
  if (!catalog) return <section><h2>Forecast</h2><p>Loading backend forecast…</p></section>;
  return <section>
    <h2>Forecast</h2>
    <p className="muted">{catalog.caveat}</p>
    <div className="controls">
      <label>BMW history<select value={model} onChange={(event) => setModel(event.target.value)}>
        {Object.keys(catalog.bmw_sales_history).map((item) => <option key={item}>{item}</option>)}
      </select></label>
      <label>Market<select value={market} onChange={(event) => setMarket(event.target.value)}>
        {Object.entries(markets).map(([code, item]) => <option key={code} value={code}>{item.label} ({code})</option>)}
      </select></label>
    </div>
    <h3>Feature scenarios</h3>
    <div className="feature-grid">{features.map((item) => <label className="feature" key={item.feature}>
      <input type="checkbox" checked={selected.includes(item.feature)} onChange={() => setSelected((current) => current.includes(item.feature) ? current.filter((name) => name !== item.feature) : [...current, item.feature])} />
      <span>{item.feature}<small>{item.category} · Y4 {fmt(item.estimate[3], 1)}%</small></span>
    </label>)}</div>
    <h3>Sales forecast</h3>
    <div className="cards">{rows.map((row) => <article className="card" key={row.year}>
      <strong>{row.year}</strong><span>{fmt(row.estimate)} vehicles</span>
      <small>baseline {fmt(row.baseline)} · uplift {fmt(row.uplift, 1)}% · range {fmt(row.low)}–{fmt(row.high)}</small>
    </article>)}</div>
    {prices && <details><summary>2030 option-price reference ({prices.items.length} priced features)</summary>
      <table><thead><tr><th>Feature</th><th>Current EUR</th><th>2030 EUR</th></tr></thead><tbody>
        {prices.items.map((item) => <tr key={item.feature_id}><td>{item.feature}</td><td>{fmt(item.current_price_eur)}</td><td>{fmt(item.forecast_price_eur)}</td></tr>)}
      </tbody></table><p className="muted">{prices.caveat}</p></details>}
  </section>;
}

function CustomerInputPage() {
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit(event) {
    event.preventDefault();
    const file = event.currentTarget.elements.document.files[0];
    if (!file) return;
    setBusy(true); setError("");
    const form = new FormData(); form.append("document", file);
    try { setResult(await jsonFetch("/api/customer-input/process", { method: "POST", body: form })); }
    catch (reason) { setError(reason.message); }
    finally { setBusy(false); }
  }
  return <section>
    <h2>Customer input processing</h2>
    <p className="muted">Upload TXT, Markdown, CSV, JSON, PDF, or DOCX. The backend returns complaint rows and generates the figure.</p>
    <form onSubmit={submit} className="upload"><input name="document" type="file" accept=".txt,.md,.csv,.json,.pdf,.docx" /><button disabled={busy}>{busy ? "Processing…" : "Process document"}</button></form>
    {error && <p className="error">{error}</p>}
    {result && <>
      <p><strong>{result.statement_count}</strong> statements processed from {result.filename}.</p>
      <img className="result-plot" src={result.figure_url} alt="Customer complaints grouped by feature" />
      <details><summary>Complaint data</summary><table><thead><tr><th>#</th><th>Statement</th><th>Sentiment</th><th>Feature</th></tr></thead><tbody>
        {result.complaints.map((item) => <tr key={item.id}><td>{item.id}</td><td>{item.complaint}</td><td>{item.sentiment}</td><td>{item.feature}</td></tr>)}
      </tbody></table></details>
    </>}
  </section>;
}

export default function App() {
  const [page, setPage] = useState("forecast");
  return <main>
    <header><div><h1>Open Trend Tracker</h1><p>Evidence-backed vehicle planning</p></div>
      <nav>{[["forecast", "Forecast"], ["customer", "Customer input"], ["evidence", "Evidence"]].map(([id, label]) => <button className={page === id ? "active" : ""} key={id} onClick={() => setPage(id)}>{label}</button>)}</nav>
    </header>
    {page === "forecast" && <ForecastPage />}
    {page === "customer" && <CustomerInputPage />}
    {page === "evidence" && <EvidencePage />}
  </main>;
}
