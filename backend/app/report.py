"""Self-contained HTML report of the unified data, for checking results without the frontend.

Written by app.unify to data/unified/report.html; open it in a browser.
"""
import json
from collections import defaultdict

from app.schema import Observation, VehicleNode

EVIDENCE_METRICS = ["defect", "difficult_to_use", "want", "like", "mention"]
QUOTES_PER_METRIC = 2


def evidence(obs: list[Observation]) -> dict:
    """vehicle -> market -> attribute -> a few quotes with their raw reference."""
    out = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for o in obs:
        if not (o.attribute and o.text):
            continue
        for market in (o.market, "ALL"):
            quotes = out[o.vehicle][market][o.attribute]
            if sum(q["metric"] == o.metric for q in quotes) < QUOTES_PER_METRIC:
                quotes.append({"metric": o.metric, "text": o.text[:400], "source": o.source, "id": o.id,
                               "raw": f"{o.raw.file} · {o.raw.locator}"})
    for markets in out.values():
        for attrs in markets.values():
            for quotes in attrs.values():
                quotes.sort(key=lambda q: EVIDENCE_METRICS.index(q["metric"]) if q["metric"] in EVIDENCE_METRICS else 9)
    return out


def write(path, trees: dict[str, VehicleNode], obs: list[Observation], coverage: dict) -> None:
    slim = {}
    for v, tree in trees.items():
        d = tree.model_dump(exclude={"markets": {"__all__": {"categories": {"__all__": {"attributes": {
            "__all__": {"metrics": {"__all__": {"obs_ids"}}}}}}}}})
        slim[v] = d
    data = json.dumps({"trees": slim, "evidence": evidence(obs), "coverage": coverage}, ensure_ascii=False)
    path.write_text(TEMPLATE.replace("__DATA__", data.replace("</", "<\\/")))


TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Unified Data Report</title>
<style>
:root{--bg:#fff;--fg:#1d1d1f;--mute:#6e6e73;--line:#e5e5ea;--card:#f5f5f7;--accent:#1c69d4;
--both:#2e7d32;--int:#1c69d4;--ext:#b26a00;--none:#9e9e9e;--bad:#c62828}
@media (prefers-color-scheme:dark){:root{--bg:#161618;--fg:#f2f2f7;--mute:#a1a1a6;--line:#2c2c2e;--card:#1f1f22;
--accent:#5ea2ff;--both:#66bb6a;--int:#5ea2ff;--ext:#ffb74d;--none:#8e8e93;--bad:#ef5350}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif}
main{max-width:1100px;margin:auto;padding:16px}h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:24px 0 8px}
.mute{color:var(--mute)}select{font:inherit;padding:4px 8px;margin-right:8px;background:var(--card);color:var(--fg);
border:1px solid var(--line);border-radius:6px}
.bar{display:inline-block;width:90px;height:8px;background:var(--line);border-radius:4px;vertical-align:middle;margin-right:6px}
.bar i{display:block;height:100%;background:var(--accent);border-radius:4px}
details{border:1px solid var(--line);border-radius:8px;margin:6px 0;background:var(--card)}
summary{cursor:pointer;padding:8px 12px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
details details{margin:4px 12px;background:var(--bg)}.body{padding:4px 14px 12px}
.badge{font-size:11px;padding:1px 7px;border-radius:10px;border:1px solid currentColor}
.both{color:var(--both)}.internal_only{color:var(--int)}.external_only{color:var(--ext)}.no_data{color:var(--none)}
table{border-collapse:collapse;width:100%;margin:6px 0}td,th{text-align:left;padding:3px 8px;border-bottom:1px solid var(--line);
font-variant-numeric:tabular-nums}th{color:var(--mute);font-weight:500}
.q{border-left:3px solid var(--line);padding:4px 10px;margin:6px 0}.q.defect,.q.difficult_to_use{border-color:var(--bad)}
.q.like{border-color:var(--both)}.q.want{border-color:var(--ext)}.q small{display:block;color:var(--mute)}
.wrap{overflow-x:auto}.chips span{display:inline-block;background:var(--bg);border:1px solid var(--line);border-radius:6px;
padding:1px 6px;margin:2px;font-size:12px}
</style></head><body><main>
<h1>Unified Data Report</h1><div class="mute" id="meta"></div>
<h2>Coverage</h2><div class="wrap" id="cov"></div>
<h2>Explore</h2><div><select id="veh"></select><select id="mkt"></select><select id="filter">
<option value="">all attributes</option><option value="both">both</option><option value="internal_only">internal only</option>
<option value="external_only">external only</option><option value="no_data">no data</option></select></div>
<div id="tree"></div>
<h2>Unmapped labels in this view</h2><div class="chips" id="unmapped"></div>
</main><script>
const D=__DATA__;
const $=id=>document.getElementById(id), esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const f=(x,d=2)=>x==null?"–":(Math.abs(x)>=1000?Math.round(x).toLocaleString():x.toFixed(d));
const bar=s=>s==null?'<span class="mute">no score</span>':`<span class="bar"><i style="width:${s*100}%"></i></span>${f(s)}`;
function coverage(){const c=D.coverage,srcs=[...new Set([...Object.keys(c.mapped),...Object.keys(c.unmapped)])];
 $("cov").innerHTML=`<table><tr><th>source</th><th>mapped</th><th>unmapped</th></tr>`+srcs.map(s=>
 `<tr><td>${esc(s)}</td><td>${c.mapped[s]||0}</td><td>${c.unmapped[s]||0}</td></tr>`).join("")+"</table>";}
function metrics(ms){return `<table><tr><th>metric</th><th>value</th><th>unit</th><th>norm</th><th>n</th><th>sources</th></tr>`+
 Object.entries(ms).map(([k,m])=>`<tr><td>${esc(k)}</td><td>${f(m.value)}</td><td>${esc(m.unit)}</td><td>${f(m.norm)}</td><td>${m.n}</td><td>${esc(m.sources.join(", "))}</td></tr>`).join("")+"</table>";}
function render(){const v=$("veh").value,m=$("mkt").value,flt=$("filter").value,node=D.trees[v].markets[m];
 const ev=(D.evidence[v]||{})[m]||{};
 $("tree").innerHTML=Object.values(node.categories).map(c=>{
  const attrs=Object.values(c.attributes).filter(a=>!flt||a.status===flt); if(!attrs.length)return "";
  return `<details><summary><b>${esc(c.name)}</b>${bar(c.score)}<span class="mute">${attrs.length} attributes</span></summary>`+
  attrs.map(a=>`<details><summary>${esc(a.name)} ${bar(a.score)} <span class="badge ${a.status}">${a.status.replace("_"," ")}</span>
   <span class="mute">${Object.entries(a.sources).map(([s,n])=>esc(s)+" "+n).join(" · ")}</span></summary><div class="body">
   ${Object.keys(a.metrics).length?metrics(a.metrics):'<p class="mute">No data for this attribute in this market.</p>'}
   ${Object.entries(a.competitors).map(([cn,ms])=>`<b>Competitor: ${esc(cn)}</b>`+metrics(ms)).join("")}
   ${Object.keys(a.features).length?`<div class="chips"><span class="mute">raw labels:</span>${Object.entries(a.features).map(([l,n])=>`<span>${esc(l)} (${n})</span>`).join("")}</div>`:""}
   ${(ev[a.id]||[]).map(q=>`<div class="q ${q.metric}">${esc(q.text)}<small>${esc(q.metric)} · ${esc(q.id)} · ${esc(q.raw)}</small></div>`).join("")}
   </div></details>`).join("")+"</details>";}).join("");
 const um=Object.entries(node.unmapped);
 $("unmapped").innerHTML=um.length?um.map(([l,n])=>`<span>${esc(l)} (${n})</span>`).join(""):'<span class="mute">none</span>';}
function markets(){const ms=Object.keys(D.trees[$("veh").value].markets);$("mkt").innerHTML=ms.map(m=>`<option ${m==="ALL"?"selected":""}>${m}</option>`).join("");render();}
$("veh").innerHTML=Object.entries(D.trees).map(([k,t])=>`<option value="${k}">${k} – ${esc(t.line)}</option>`).join("");
$("meta").textContent=`${D.coverage.observations.toLocaleString()} observations · generated ${Object.values(D.trees)[0]?.generated_at||""}`;
$("veh").onchange=markets;$("mkt").onchange=render;$("filter").onchange=render;coverage();markets();
</script></body></html>
"""
