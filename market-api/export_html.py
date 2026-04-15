"""Genera el reporte financiero completo como HTML autocontenido."""
import os, sys, json
import numpy as np, pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.api_data import get_data
from modules.returns import calculate_returns
from modules.technical import compute_indicators
from modules.portfolio import optimize_portfolio
from modules.signals import compute_signals
from modules.macro import analyze_macro
from modules.garch import compute_garch, compute_garch_comparison
from modules.capm import compute_capm
from modules.var import compute_var

ASSETS = ["NVDA", "AAPL", "GOOG", "TSLA", "JPM", "^GSPC"]
MARKET = "^GSPC"

def s(v):
    if pd.isna(v) or v is None: return None
    if isinstance(v, (np.integer,)): return int(v)
    if isinstance(v, (np.floating,)): return float(v)
    return v

def to_json_arr(df, cols):
    out = {}
    for c in cols:
        if c in df.columns:
            v = df[[c]].dropna()
            if len(v) > 0:
                out[c] = {"x": [str(i) for i in v.index], "y": [s(x) for x in v[c].values]}
    return out

def main():
    print("Ejecutando pipeline...")
    data = get_data(ASSETS)
    data = calculate_returns(data)
    data = compute_indicators(data)
    data = compute_signals(data)
    data = compute_capm(data, market_ticker=MARKET)
    data = compute_garch(data)
    data = compute_var(data, confidence_level=0.95)
    opt = optimize_portfolio(data)
    macro = None
    if opt and "max_sharpe" in opt:
        w = {a: s(opt["max_sharpe"][a]) for a in opt["assets"] if a in opt["max_sharpe"]}
        macro = analyze_macro(data, w)
    
    garch_comp = {}
    for t in ASSETS:
        if t == MARKET or t not in data: continue
        if "log_return" in data[t].columns:
            try:
                comp, fc, _, _ = compute_garch_comparison(data[t]["log_return"])
                garch_comp[t] = comp
            except: pass
    
    tickers = [t for t in ASSETS if t != MARKET]
    
    # Datos para tablas
    summary, capm, var_rows, sigs, garch_info = [], [], [], [], []
    charts = {}
    
    for t in tickers:
        if t not in data: continue
        df = data[t]
        last = df.iloc[-1] if len(df) > 0 else None
        if last is None: continue
        
        charts[t] = {
            "price": to_json_arr(df, ["Close", "SMA_20", "EMA_20"]),
            "rsi": to_json_arr(df, ["RSI"]),
            "macd": to_json_arr(df, ["MACD", "MACD_Signal", "MACD_Hist"]),
            "bb": to_json_arr(df, ["Close", "BB_Upper", "BB_Lower", "BB_Mid"]),
            "stoch": to_json_arr(df, ["STOCH_K", "STOCH_D"]),
            "garch": to_json_arr(df, ["GARCH_Vol"]),
            "returns": to_json_arr(df, ["return"]),
        }
        
        summary.append({"t": t, "p": s(last.get("Close")), "r": s(last.get("RSI")), "sig": s(last.get("Final_Signal")) or "N/A"})
        
        if "CAPM_Beta" in df.columns:
            capm.append({"t": t, "b": s(last.get("CAPM_Beta")), "er": s(last.get("CAPM_Expected_Return")), "rf": s(last.get("Risk_Free_Rate"))})
        
        if "VaR_95_Hist" in df.columns:
            var_rows.append({"t": t, "v95p": s(last.get("VaR_95_Param")), "v95h": s(last.get("VaR_95_Hist")),
                "v95m": s(last.get("VaR_95_MC")), "c95": s(last.get("CVaR_95")),
                "v99p": s(last.get("VaR_99_Param")), "c99": s(last.get("CVaR_99")),
                "kup": s(last.get("Kupiec_Status")) or "N/A"})
        
        if "GARCH_AIC" in df.columns:
            garch_info.append({"t": t, "aic": s(last.get("GARCH_AIC"))})
        
        sigs.append({"t": t, "r": s(last.get("RSI")), "m": s(last.get("MACD")),
            "bs": s(last.get("BB_Upper")), "bl": s(last.get("BB_Lower")),
            "sk": s(last.get("STOCH_K")), "sd": s(last.get("STOCH_D")),
            "sig": s(last.get("Final_Signal")) or "N/A"})
    
    pmax = {k: s(v) for k, v in opt.get("max_sharpe", {}).items() if k in opt.get("assets", [])} if opt else {}
    pmin = {k: s(v) for k, v in opt.get("min_vol", {}).items() if k in opt.get("assets", [])} if opt else {}
    
    mac = {}
    if macro:
        mac = {k: s(v) for k, v in macro.items() if k not in ["portfolio_cumulative", "benchmark_cumulative"]}
    
    payload = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tickers": tickers,
        "summary": summary, "capm": capm, "var": var_rows, "sigs": sigs,
        "garch_info": garch_info, "garch_comp": garch_comp,
        "pmax": pmax, "pmin": pmin, "macro": mac,
        "charts": charts,
    }
    
    out = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(out, "reporte_financiero_completo.html"), "w", encoding="utf-8") as f:
        f.write(build_html(json.dumps(payload, ensure_ascii=False, default=str)))
    
    print("OK: reporte_financiero_completo.html")

def build_html(data_json):
    return """<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Teoría del Riesgo - Reporte</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"><""" + """/script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0a0e27;color:#e2e8f0;line-height:1.6}
header{background:linear-gradient(135deg,#7c3aed,#ec4899);padding:36px 20px;text-align:center}
header h1{font-size:2rem;font-weight:800}header p{opacity:.85;font-size:.95rem}
nav{background:#111639;border-bottom:1px solid #2a2f5e;padding:8px 16px;position:sticky;top:0;z-index:100}
nav a{color:#94a3b8;text-decoration:none;padding:8px 14px;border-radius:6px;font-size:.85rem;margin-right:4px;display:inline-block}
nav a:hover{background:#7c3aed;color:#fff}
.wrap{max-width:1400px;margin:0 auto;padding:20px}
section{margin:28px 0}
h2{font-size:1.4rem;color:#06b6d4;border-bottom:2px solid #2a2f5e;padding-bottom:6px;margin-bottom:16px}
h3{font-size:1.1rem;color:#7c3aed;margin:14px 0 8px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}
.card{background:#161b4a;border:1px solid #2a2f5e;border-radius:10px;padding:16px}
.card h4{color:#f59e0b;margin-bottom:6px;font-size:.95rem}
table{width:100%;border-collapse:collapse;margin:10px 0}
th,td{padding:8px 12px;text-align:left;border-bottom:1px solid #2a2f5e;font-size:.85rem}
th{background:#111639;color:#06b6d4;font-weight:600}
tr:hover td{background:rgba(124,58,237,.08)}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:.75rem;font-weight:700}
.buy{background:rgba(16,185,129,.2);color:#10b981}.sell{background:rgba(239,68,68,.2);color:#ef4444}
.hold{background:rgba(148,163,184,.2);color:#94a3b8}
.metric{font-size:1.6rem;font-weight:700}.lbl{font-size:.8rem;color:#94a3b8}
.pos{color:#10b981}.neg{color:#ef4444}
.chart-box{background:#161b4a;border:1px solid #2a2f5e;border-radius:10px;padding:10px;margin-bottom:14px}
details{background:#111639;border:1px solid #2a2f5e;border-radius:8px;margin:8px 0;overflow:hidden}
summary{padding:10px 14px;cursor:pointer;font-weight:600;list-style:none;color:#e2e8f0}
summary::before{content:"▸ ";color:#7c3aed}details[open] summary::before{content:"▾ "}
details .ct{padding:14px}
footer{text-align:center;padding:24px;color:#94a3b8;font-size:.8rem;border-top:1px solid #2a2f5e;margin-top:32px}
@media(max-width:700px){.grid{grid-template-columns:1fr}}
</style></head><body>
<header><h1>Teoría del Riesgo — Reporte Financiero</h1>
<p id="hdr"></p></header>
<nav>
<a href="#sec-sum">Resumen</a><a href="#sec-prices">Precios</a><a href="#sec-tech">Técnicos</a>
<a href="#sec-capm">CAPM</a><a href="#sec-var">VaR</a><a href="#sec-garch">GARCH</a>
<a href="#sec-sig">Señales</a><a href="#sec-port">Portafolio</a><a href="#sec-macro">Macro</a>
</nav>
<div class="wrap" id="app"></div>
<footer><p>Autora: Paula Español · Dashboard v3.0 · Modelos: CAPM, GARCH, VaR, CVaR, Markowitz, Monte Carlo</p></footer>
<script>
var D=""" + data_json + """;
var tickers=D.tickers;
var charts=D.charts;
var L={paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{color:'#e2e8f0',size:11},
margin:{l:40,r:15,t:30,b:30},xaxis:{gridcolor:'#2a2f5e',zerolinecolor:'#475569'},
yaxis:{gridcolor:'#2a2f5e',zerolinecolor:'#475569'},legend:{bgcolor:'rgba(0,0,0,0)',font:{size:10}}};
var C={responsive:true,displayModeBar:false};

document.getElementById('hdr').textContent='Generado: '+D.date+' · '+tickers.length+' activos · Benchmark: '+MARKET;
var MARKET='^GSPC';

var app=document.getElementById('app');
var html='';

// RESUMEN
html+='<section id="sec-sum"><h2>Resumen General</h2><div class="grid">';
D.summary.forEach(function(r){
  var cls=(r.sig||'hold').toLowerCase();
  html+='<div class="card"><h4>'+r.t+'</h4><div class="metric">'+(r.p!==null?'$'+r.p.toFixed(2):'N/A')+'</div>';
  html+='<div class="lbl">RSI: '+(r.r!==null?r.r.toFixed(1):'N/A')+' &nbsp; Señal: <span class="badge '+cls+'">'+r.sig+'</span></div></div>';
});
html+='</div></section>';

// PRECIOS
html+='<section id="sec-prices"><h2>Precios y Medias Móviles</h2><div class="grid">';
tickers.forEach(function(t){html+='<div class="chart-box" id="cp-'+t+'"></div>';});
html+='</div></section>';

// TECNICOS
html+='<section id="sec-tech"><h2>Indicadores Técnicos</h2>';
[['rsi','RSI (14)'],['macd','MACD (12,26,9)'],['bb','Bandas de Bollinger'],['stoch','Estocástico']].forEach(function(pair){
  var key=pair[0],label=pair[1];
  html+='<details open><summary>'+label+'</summary><div class="ct"><div class="grid">';
  tickers.forEach(function(t){html+='<div class="chart-box" id="c-'+key+'-'+t+'"></div>';});
  html+='</div></div></details>';
});
html+='</section>';

// CAPM
html+='<section id="sec-capm"><h2>Modelo CAPM</h2><table><thead><tr><th>Activo</th><th>Beta</th><th>Retorno Esperado</th><th>Rf</th></tr></thead><tbody>';
D.capm.forEach(function(r){
  var bc=r.b>1?'pos':(r.b<0.8?'neg':'');
  html+='<tr><td><b>'+r.t+'</b></td><td class="'+bc+'">'+(r.b!==null?r.b.toFixed(4):'N/A')+'</td>';
  html+='<td>'+(r.er!==null?(r.er*100).toFixed(2)+'%':'N/A')+'</td>';
  html+='<td>'+(r.rf!==null?(r.rf*100).toFixed(2)+'%':'N/A')+'</td></tr>';
});
html+='</tbody></table></section>';

// VaR
html+='<section id="sec-var"><h2>VaR y CVaR</h2><table><thead><tr><th>Activo</th><th>VaR 95% Param</th><th>VaR 95% Hist</th><th>VaR 95% MC</th><th>CVaR 95%</th><th>VaR 99%</th><th>CVaR 99%</th><th>Kupiec</th></tr></thead><tbody>';
D.var.forEach(function(r){
  html+='<tr><td><b>'+r.t+'</b></td><td>'+(r.v95p!==null?(r.v95p*100).toFixed(3)+'%':'N/A')+'</td>';
  html+='<td>'+(r.v95h!==null?(r.v95h*100).toFixed(3)+'%':'N/A')+'</td>';
  html+='<td>'+(r.v95m!==null?(r.v95m*100).toFixed(3)+'%':'N/A')+'</td>';
  html+='<td>'+(r.c95!==null?(r.c95*100).toFixed(3)+'%':'N/A')+'</td>';
  html+='<td>'+(r.v99p!==null?(r.v99p*100).toFixed(3)+'%':'N/A')+'</td>';
  html+='<td>'+(r.c99!==null?(r.c99*100).toFixed(3)+'%':'N/A')+'</td>';
  html+='<td><span class="badge '+(r.kup=='Accepted'?'buy':'sell')+'">'+r.kup+'</span></td></tr>';
});
html+='</tbody></table></section>';

// GARCH
html+='<section id="sec-garch"><h2>Volatilidad GARCH</h2><div class="grid">';
tickers.forEach(function(t){html+='<div class="chart-box" id="cg-'+t+'"></div>';});
html+='</div>';
if(Object.keys(D.garch_comp).length>0){
  html+='<h3>Comparación de Modelos</h3>';
  for(var gt in D.garch_comp){
    var cl=D.garch_comp[gt];
    html+='<details><summary>'+gt+'</summary><div class="ct"><table><thead><tr><th>Modelo</th><th>LogL</th><th>AIC</th><th>BIC</th><th>Params</th><th></th></tr></thead><tbody>';
    cl.forEach(function(c){
      html+='<tr><td>'+c.Modelo+'</td><td>'+c['Log-Likelihood']+'</td><td>'+c.AIC+'</td><td>'+c.BIC+'</td><td>'+c.Params+'</td><td>'+c.Mejor+'</td></tr>';
    });
    html+='</tbody></table></div></details>';
  }
}
html+='</section>';

// SEÑALES
html+='<section id="sec-sig"><h2>Señales de Trading</h2><table><thead><tr><th>Activo</th><th>RSI</th><th>MACD</th><th>BB Upper</th><th>BB Lower</th><th>Stoch K</th><th>Stoch D</th><th>Señal</th></tr></thead><tbody>';
D.sigs.forEach(function(r){
  var sc=(r.sig||'hold').toLowerCase();
  html+='<tr><td><b>'+r.t+'</b></td><td>'+(r.r!==null?r.r.toFixed(1):'')+'</td>';
  html+='<td>'+(r.m!==null?r.m.toFixed(5):'')+'</td>';
  html+='<td>'+(r.bs!==null?r.bs.toFixed(2):'')+'</td><td>'+(r.bl!==null?r.bl.toFixed(2):'')+'</td>';
  html+='<td>'+(r.sk!==null?r.sk.toFixed(1):'')+'</td><td>'+(r.sd!==null?r.sd.toFixed(1):'')+'</td>';
  html+='<td><span class="badge '+sc+'">'+r.sig+'</span></td></tr>';
});
html+='</tbody></table></section>';

// PORTAFOLIO
html+='<section id="sec-port"><h2>Optimización Markowitz</h2><div class="grid">';
html+='<div class="card"><h4>Máximo Sharpe Ratio</h4>';
for(var k in D.pmax){html+='<div style="display:flex;justify-content:space-between;padding:3px 0"><span>'+k+'</span><b>'+(D.pmax[k]*100).toFixed(1)+'%</b></div>';}
html+='</div><div class="card"><h4>Mínima Volatilidad</h4>';
for(var k in D.pmin){html+='<div style="display:flex;justify-content:space-between;padding:3px 0"><span>'+k+'</span><b>'+(D.pmin[k]*100).toFixed(1)+'%</b></div>';}
html+='</div></div></section>';

// MACRO
html+='<section id="sec-macro"><h2>Análisis Macro vs Benchmark</h2><div class="grid">';
var M=D.macro||{};
[['Retorno Anual Port.',M.port_ann_return,true],['Retorno Benchmark',M.bench_ann_return,true],
['Sharpe Benchmark',M.benchmark_sharpe,true],['Tracking Error',M.tracking_error,false],
['Information Ratio',M.information_ratio,true],['Máx Drawdown',M.max_drawdown,false]
].forEach(function(m){
  if(m[1]!==null&&m[1]!==undefined){
    var d=m[2]?m[1]*100:'':m[1];
    var ds=m[2]?d.toFixed(2)+'%':d.toFixed(4);
    var cls=m[1]>0?'pos':(m[1]<0?'neg':'');
    html+='<div class="card"><div class="lbl">'+m[0]+'</div><div class="metric '+cls+'">'+ds+'</div></div>';
  }
});
html+='</div></section>';

app.innerHTML=html;

// Render charts
function renderChart(elId, dataObj, title, extras){
  var el=document.getElementById(elId);
  if(!el||!dataObj||Object.keys(dataObj).length===0)return;
  var traces=[],x0;
  for(var col in dataObj){
    var d=dataObj[col];
    if(!x0)x0=d.x;
    traces.push({x:d.x,y:d.y,name:col,type:'scatter',mode:'lines',line:{width:2}});
  }
  if(!traces.length)return;
  var layout=JSON.parse(JSON.stringify(L));
  layout.title=title;
  if(extras){
    if(extras.hlines)layout.shapes=(extras.hlines||[]).map(function(h){
      return{type:'line',x0:x0[0],x1:x0[x0.length-1],y0:h.y,y1:h.y,line:{color:h.c,width:1,dash:'dash'}};
    });
    if(extras.notes)layout.annotations=extras.notes;
  }
  Plotly.newPlot(el.id,traces,layout,C);
}

// Price charts
tickers.forEach(function(t){
  if(charts[t]&&charts[t].price)renderChart('cp-'+t,charts[t].price,t+' - Precio y Medias Móviles');
});

// Technical charts
tickers.forEach(function(t){
  var ct=charts[t]||{};
  if(ct.rsi)renderChart('c-rsi-'+t,ct.rsi,t+' - RSI (14)',{hlines:[{y:30,c:'#10b981'},{y:70,c:'#ef4444'}]});
  if(ct.macd)renderChart('c-macd-'+t,ct.macd,t+' - MACD');
  if(ct.bb)renderChart('c-bb-'+t,ct.bb,t+' - Bollinger Bands');
  if(ct.stoch)renderChart('c-stoch-'+t,ct.stoch,t+' - Estocástico',{hlines:[{y:30,c:'#10b981'},{y:70,c:'#ef4444'}]});
  if(ct.garch)renderChart('cg-'+t,ct.garch,t+' - Volatilidad GARCH(1,1)');
});

// Smooth scroll
document.querySelectorAll('nav a').forEach(function(a){
  a.addEventListener('click',function(e){
    e.preventDefault();
    document.querySelector(this.getAttribute('href')).scrollIntoView({behavior:'smooth'});
  });
});
</script></body></html>"""

if __name__ == "__main__":
    main()
