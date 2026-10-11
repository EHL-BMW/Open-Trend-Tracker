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

function ForecastPage({ documentId }) {
  const [catalog, setCatalog] = useState(null);
  const [model, setModel] = useState("");
  const [market, setMarket] = useState("Global");
  const [selected, setSelected] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [prices, setPrices] = useState(null);
  const [decisions, setDecisions] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

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
    const vehicle = model.split("/")[0];
    const query = documentId ? `?document_id=${encodeURIComponent(documentId)}` : "";
    jsonFetch(`/api/decision-dashboard/${vehicle}${query}`).then((data) => {
      setDecisions(data);
      setSelected(data.features.filter((item) => item.selected).map((item) => item.source_feature));
    }).catch((reason) => setError(reason.message));
  }, [model, documentId]);
  useEffect(() => {
    if (!model) return;
    const params = new URLSearchParams({ model, market });
    selected.forEach((feature) => params.append("feature", feature));
    jsonFetch(`/api/forecast/sales?${params}`).then(setForecast).catch((reason) => setError(reason.message));
    jsonFetch(`/api/forecast/prices/${model.split("/")[0]}?target_year=2030`).then(setPrices).catch(() => setPrices(null));
  }, [model, market, selected]);

  const markets = catalog?.bmw_sales_history[model] || {};
  const rows = useMemo(() => forecast?.years.map((year, index) => ({
    year, baseline: forecast.baseline[index], estimate: forecast.estimate[index],
    low: forecast.lower[index], high: forecast.upper[index], uplift: forecast.impact[index],
  })) || [], [forecast]);

  function editFeature(sourceFeature, field, value) {
    setDecisions((current) => ({ ...current, features: current.features.map((item) => item.source_feature === sourceFeature ? { ...item, [field]: value } : item) }));
  }
  async function saveFeature(item, patch = {}) {
    const update = { ...item, ...patch };
    setNotice(`Saving ${update.display_name}…`);
    await jsonFetch("/api/decision-dashboard/overrides", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        vehicle: decisions.vehicle, feature: update.source_feature, display_name: update.display_name,
        selected: update.selected, priority: Number(update.priority), engineering_status: update.engineering_status, note: update.note,
      }),
    }).then(() => setNotice(`Saved ${update.display_name}.`), (reason) => setNotice(`Not saved: ${reason.message}`));
  }
  async function toggleFeature(item) {
    const enabled = !item.selected;
    editFeature(item.source_feature, "selected", enabled);
    setSelected((current) => enabled ? [...new Set([...current, item.source_feature])] : current.filter((name) => name !== item.source_feature));
    await saveFeature(item, { selected: enabled });
  }

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
    <h3>Chinese-derived feature decisions</h3>
    <p className="muted">Comment source: {documentId ? `uploaded document ${documentId}` : `${model.split("/")[0]} internal customer feedback`}. Names, selection, priority, status, and notes are editable; source evidence remains unchanged.</p>
    {notice && <p className="muted">{notice}</p>}
    {decisions && <div className="decision-scroll"><table className="decision-table"><thead><tr><th>Use</th><th>Feature / PM name</th><th>Customer comments</th><th>Sales-impact trend</th><th>PM decision</th></tr></thead><tbody>
      {decisions.features.map((item) => <tr key={item.source_feature}>
        <td><input type="checkbox" checked={item.selected} onChange={() => toggleFeature(item)} /></td>
        <td><input className="name-input" value={item.display_name} onChange={(event) => editFeature(item.source_feature, "display_name", event.target.value)} /><small>{item.source_feature}<br />{item.category} · {item.pair_count} source pairs</small></td>
        <td><strong>{item.comments.mentions}</strong> mentions ({fmt(item.comments.mention_rate * 100, 1)}%)<br /><small>{item.comments.negative} negative · {item.comments.positive} positive · need {fmt(item.comments.need_share * 100, 1)}%</small>
          {item.comments.examples.length > 0 && <details><summary>Examples</summary>{item.comments.examples.map((example) => <p key={`${example.source}-${example.id}`}><small>{example.text}</small></p>)}</details>}</td>
        <td>{item.sales_impact_trend.estimate_pct.map((value, index) => <span className="trend" key={index}>Y{index + 1} {fmt(value, 1)}%</span>)}</td>
        <td><div className="decision-fields"><label>Priority<input type="number" min="1" value={item.priority} onChange={(event) => editFeature(item.source_feature, "priority", event.target.value)} /></label>
          <label>Status<select value={item.engineering_status} onChange={(event) => editFeature(item.source_feature, "engineering_status", event.target.value)}><option value="review">Review</option><option value="approved">Approved</option><option value="rejected">Rejected</option></select></label>
          <label>Note<textarea value={item.note} onChange={(event) => editFeature(item.source_feature, "note", event.target.value)} /></label>
          <button onClick={() => saveFeature(item)}>Save</button></div></td>
      </tr>)}</tbody></table></div>}
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

function CustomerInputPage({ onUseDocument }) {
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
      <button onClick={() => onUseDocument(result.document_id)}>Use this document on decision dashboard</button>
      <details><summary>Complaint data</summary><table><thead><tr><th>#</th><th>Statement</th><th>Sentiment</th><th>Feature</th></tr></thead><tbody>
        {result.complaints.map((item) => <tr key={item.id}><td>{item.id}</td><td>{item.complaint}</td><td>{item.sentiment}</td><td>{item.feature}</td></tr>)}
      </tbody></table></details>
    </>}
  </section>;
}

export default function App() {
  const [page, setPage] = useState("forecast");
  const [decisionDocument, setDecisionDocument] = useState(null);
  return <main>
    <header><div><h1>Open Trend Tracker</h1><p>Evidence-backed vehicle planning</p></div>
      <nav>{[["forecast", "Forecast"], ["customer", "Customer input"], ["evidence", "Evidence"]].map(([id, label]) => <button className={page === id ? "active" : ""} key={id} onClick={() => setPage(id)}>{label}</button>)}</nav>
    </header>
    {page === "forecast" && <ForecastPage documentId={decisionDocument} />}
    {page === "customer" && <CustomerInputPage onUseDocument={(documentId) => { setDecisionDocument(documentId); setPage("forecast"); }} />}
    {page === "evidence" && <EvidencePage />}
  </main>;
}
