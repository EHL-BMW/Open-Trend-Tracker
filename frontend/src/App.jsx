import { useEffect, useState } from "react";

const fmt = (x) => (x == null ? "–" : x.toFixed(2));

// Placeholder view: browse the unified tree (vehicle -> market -> category -> attribute).
export default function App() {
  const [vehicles, setVehicles] = useState([]);
  const [vehicle, setVehicle] = useState(null);
  const [market, setMarket] = useState("ALL");
  const [node, setNode] = useState(null);

  useEffect(() => {
    fetch("/api/vehicles").then((r) => r.json()).then((vs) => {
      setVehicles(vs);
      if (vs.length) setVehicle(vs[0].vehicle);
    });
  }, []);

  useEffect(() => {
    if (!vehicle) return;
    fetch(`/api/vehicles/${vehicle}/markets/${market}`).then((r) => r.json()).then(setNode);
  }, [vehicle, market]);

  const markets = vehicles.find((v) => v.vehicle === vehicle)?.markets ?? [];
  return (
    <main style={{ fontFamily: "system-ui", padding: 16, maxWidth: 960, margin: "auto" }}>
      <h1>Open-Trend-Tracker</h1>
      <select value={vehicle ?? ""} onChange={(e) => { setVehicle(e.target.value); setMarket("ALL"); }}>
        {vehicles.map((v) => <option key={v.vehicle} value={v.vehicle}>{v.vehicle} – {v.line}</option>)}
      </select>{" "}
      <select value={market} onChange={(e) => setMarket(e.target.value)}>
        {markets.map((m) => <option key={m}>{m}</option>)}
      </select>
      {node && Object.values(node.categories).map((c) => (
        <details key={c.id}>
          <summary>{c.name} — score {fmt(c.score)}</summary>
          <ul>
            {Object.values(c.attributes).map((a) => (
              <li key={a.id}>{a.name}: {fmt(a.score)} <small>({a.status})</small></li>
            ))}
          </ul>
        </details>
      ))}
    </main>
  );
}
