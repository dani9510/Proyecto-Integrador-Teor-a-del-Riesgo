"""
Exporta el Dashboard completo como un archivo HTML autocontenido.
Incluye todos los análisis: CAPM, GARCH, VaR, señales técnicas, optimización de Markowitz, etc.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
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

def safe_json(o):
    """Convierte objetos numpy/pandas a tipos JSON serializables."""
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, pd.Timestamp):
        return str(o)
    if pd.isna(o):
        return None
    return o

def to_chart_json(df, y_cols, title):
    """Convierte un DataFrame a un dict JSON para Plotly.js. La fecha se toma del índice."""
    traces = []
    for y in y_cols:
        if y in df.columns:
            valid = df[[y]].dropna()
            if len(valid) > 0:
                traces.append({
                    "x": [str(v) for v in valid.index],
                    "y": [safe_json(v) for v in valid[y].values],
                    "name": y,
                })
    return {"title": title, "traces": traces}

def generate_report():
    print("📊 Descargando datos del mercado...")
    data = get_data(ASSETS)
    print("📈 Calculando retornos...")
    data = calculate_returns(data)
    print("📉 Indicadores técnicos...")
    data = compute_indicators(data)
    print("🧮 Señales de trading...")
    data = compute_signals(data)
    print("⚙️ CAPM...")
    data = compute_capm(data, market_ticker=MARKET)
    print("📊 GARCH...")
    data = compute_garch(data)
    print("💥 VaR / CVaR...")
    data = compute_var(data, confidence_level=0.95)
    print("📦 Optimización de portafolio...")
    opt = optimize_portfolio(data)
    print("🌍 Análisis macro...")
    macro = None
    if opt and "max_sharpe" in opt:
        w = {a: opt["max_sharpe"][a] for a in opt["assets"] if a in opt["max_sharpe"]}
        macro = analyze_macro(data, w)

    # ── GARCH Comparison para cada activo ──
    garch_comp = {}
    for t in ASSETS:
        if t == MARKET or t not in data:
            continue
        if "log_return" in data[t].columns:
            try:
                comp, fc, _, _ = compute_garch_comparison(data[t]["log_return"])
                garch_comp[t] = comp
            except Exception as e:
                print(f"⚠️ GARCH comparison error {t}: {e}")

    # ── Recopilar datos para HTML ──
    tickers = [t for t in ASSETS if t != MARKET]
    charts = {}

    # 1. Precios
    for t in tickers:
        if t in data:
            charts[f"price_{t}"] = to_chart_json(data[t], ["Close", "SMA_20", "EMA_20"], f"{t} - Precio y Medias Móviles")

    # 2. RSI
    for t in tickers:
        if t in data:
            charts[f"rsi_{t}"] = to_chart_json(data[t], ["RSI"], f"{t} - RSI (14)")

    # 3. MACD
    for t in tickers:
        if t in data:
            charts[f"macd_{t}"] = to_chart_json(data[t], ["MACD", "MACD_Signal", "MACD_Hist"], f"{t} - MACD (12,26,9)")

    # 4. Bollinger
    for t in tickers:
        if t in data:
            charts[f"bb_{t}"] = to_chart_json(data[t], ["Close", "BB_Upper", "BB_Lower", "BB_Mid"], f"{t} - Bandas de Bollinger")

    # 5. Stochastic
    for t in tickers:
        if t in data:
            charts[f"stoch_{t}"] = to_chart_json(data[t], ["STOCH_K", "STOCH_D"], f"{t} - Estocástico")

    # 6. Volatilidad GARCH
    for t in tickers:
        if t in data:
            charts[f"garch_{t}"] = to_chart_json(data[t], ["GARCH_Vol"], f"{t} - Volatilidad Condicional GARCH(1,1)")

    # 7. Retornos
    for t in tickers:
        if t in data:
            charts[f"ret_{t}"] = to_chart_json(data[t], ["return"], f"{t} - Retornos")

    # ── Tablas resumen ──
    summary = []
    capm_rows = []
    var_rows = []
    signals_summary = []
    garch_summary = []

    for t in tickers:
        if t not in data:
            continue
        df = data[t]
        last = df.iloc[-1] if len(df) > 0 else None
        if last is None:
            continue

        # Resumen general
        summary.append({
            "ticker": t,
            "precio": safe_json(last.get("Close")),
            "rsi": safe_json(last.get("RSI")),
            "senal": safe_json(last.get("Final_Signal")),
        })

        # CAPM
        if "CAPM_Beta" in df.columns:
            capm_rows.append({
                "ticker": t,
                "beta": safe_json(last.get("CAPM_Beta")),
                "expected_return": safe_json(last.get("CAPM_Expected_Return")),
                "rf": safe_json(last.get("Risk_Free_Rate")),
            })

        # VaR
        if "VaR_95_Hist" in df.columns:
            var_rows.append({
                "ticker": t,
                "var_95_param": safe_json(last.get("VaR_95_Param")),
                "var_95_hist": safe_json(last.get("VaR_95_Hist")),
                "var_95_mc": safe_json(last.get("VaR_95_MC")),
                "cvar_95": safe_json(last.get("CVaR_95")),
                "var_99_param": safe_json(last.get("VaR_99_Param")),
                "var_99_hist": safe_json(last.get("VaR_99_Hist")),
                "var_99_mc": safe_json(last.get("VaR_99_MC")),
                "cvar_99": safe_json(last.get("CVaR_99")),
                "kupiec": safe_json(last.get("Kupiec_Status")),
                "exceptions": safe_json(last.get("Kupiec_Exceptions")),
            })

        # GARCH AIC
        if "GARCH_AIC" in df.columns:
            garch_summary.append({
                "ticker": t,
                "garch_aic": safe_json(last.get("GARCH_AIC")),
            })

        signals_summary.append({
            "ticker": t,
            "rsi": safe_json(last.get("RSI")),
            "macd": safe_json(last.get("MACD")),
            "macd_signal": safe_json(last.get("MACD_Signal")),
            "bb_upper": safe_json(last.get("BB_Upper")),
            "bb_lower": safe_json(last.get("BB_Lower")),
            "stoch_k": safe_json(last.get("STOCH_K")),
            "stoch_d": safe_json(last.get("STOCH_D")),
            "signal": safe_json(last.get("Final_Signal")),
        })

    # Portafolio óptimo
    max_sharpe_w = {}
    min_vol_w = {}
    if opt:
        max_sharpe_w = {k: safe_json(v) for k, v in opt.get("max_sharpe", {}).items() if k in opt.get("assets", [])}
        min_vol_w = {k: safe_json(v) for k, v in opt.get("min_vol", {}).items() if k in opt.get("assets", [])}

    # Macro
    macro_data = {}
    if macro:
        macro_data = {
            "port_ann_return": safe_json(macro.get("port_ann_return")),
            "bench_ann_return": safe_json(macro.get("bench_ann_return")),
            "benchmark_sharpe": safe_json(macro.get("benchmark_sharpe")),
            "tracking_error": safe_json(macro.get("tracking_error")),
            "information_ratio": safe_json(macro.get("information_ratio")),
            "max_drawdown": safe_json(macro.get("max_drawdown")),
        }

    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "assets": tickers,
        "market": MARKET,
        "summary": summary,
        "capm": capm_rows,
        "var": var_rows,
        "garch": garch_summary,
        "garch_comparison": garch_comp,
        "signals": signals_summary,
        "portfolio": {
            "max_sharpe_weights": max_sharpe_w,
            "min_vol_weights": min_vol_w,
        },
        "macro": macro_data,
        "charts": charts,
    }

    return report


def build_html(report):
    """Construye el HTML completo con Plotly.js."""
    charts_json = json.dumps(report["charts"], ensure_ascii=False)
    report_json = json.dumps(report, ensure_ascii=False, default=str)

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Teoría del Riesgo · Reporte Financiero Completo</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
  :root {{
    --bg: #0a0e27; --bg2: #111639; --card: #161b4a;
    --border: #2a2f5e; --text: #e2e8f0; --text2: #94a3b8;
    --accent: #7c3aed; --green: #10b981; --red: #ef4444; --cyan: #06b6d4; --amber: #f59e0b;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Segoe UI',system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--text); line-height:1.6; }}
  header {{ background: linear-gradient(135deg,#7c3aed 0%,#ec4899 100%); padding:40px 20px; text-align:center; }}
  header h1 {{ font-size:2.2rem; font-weight:800; margin-bottom:4px; }}
  header p {{ opacity:.85; font-size:1rem; }}
  .container {{ max-width:1400px; margin:0 auto; padding:20px; }}
  nav {{ background:var(--bg2); border-bottom:1px solid var(--border); padding:10px 20px; position:sticky; top:0; z-index:100; }}
  nav a {{ color:var(--text2); text-decoration:none; padding:8px 16px; border-radius:6px; font-size:.9rem; margin-right:4px; }}
  nav a:hover, nav a.active {{ background:var(--accent); color:#fff; }}
  section {{ margin:30px 0; }}
  h2 {{ font-size:1.6rem; color:var(--cyan); border-bottom:2px solid var(--border); padding-bottom:8px; margin-bottom:20px; }}
  h3 {{ font-size:1.2rem; color:var(--accent); margin:16px 0 8px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:16px; }}
  .card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:20px; }}
  .card h4 {{ color:var(--amber); margin-bottom:8px; font-size:1rem; }}
  table {{ width:100%; border-collapse:collapse; margin:12px 0; }}
  th,td {{ padding:10px 14px; text-align:left; border-bottom:1px solid var(--border); font-size:.9rem; }}
  th {{ background:var(--bg2); color:var(--cyan); font-weight:600; }}
  tr:hover td {{ background:rgba(124,58,237,.1); }}
  .badge {{ display:inline-block; padding:3px 10px; border-radius:12px; font-size:.8rem; font-weight:700; }}
  .buy {{ background:rgba(16,185,129,.2); color:var(--green); }}
  .sell {{ background:rgba(239,68,68,.2); color:var(--red); }}
  .hold {{ background:rgba(148,163,184,.2); color:var(--text2); }}
  .metric {{ font-size:1.8rem; font-weight:700; }}
  .metric-label {{ font-size:.85rem; color:var(--text2); }}
  .positive {{ color:var(--green); }}
  .negative {{ color:var(--red); }}
  .chart-box {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:12px; margin-bottom:16px; }}
  .collapsible {{ background:var(--bg2); border:1px solid var(--border); border-radius:8px; margin:8px 0; overflow:hidden; }}
  .collapsible summary {{ padding:12px 16px; cursor:pointer; font-weight:600; color:var(--text); list-style:none; }}
  .collapsible summary::-webkit-details-marker {{ display:none; }}
  .collapsible summary::before {{ content:"▸ "; color:var(--accent); }}
  .collapsible[open] summary::before {{ content:"▾ "; }}
  .collapsible .content {{ padding:16px; }}
  footer {{ text-align:center; padding:30px; color:var(--text2); font-size:.85rem; border-top:1px solid var(--border); margin-top:40px; }}
  @media(max-width:768px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>

<header>
  <h1>📊 Teoría del Riesgo — Reporte Financiero Completo</h1>
  <p>Autora: Paula Español · {report["generated_at"]} · {len(report["assets"])} activos · {report["market"]} como benchmark</p>
</header>

<nav id="nav">
  <a href="#sec-resumen">📋 Resumen</a>
  <a href="#sec-precios">📈 Precios</a>
  <a href="#sec-tecnicos">📉 Técnicos</a>
  <a href="#sec-capm">⚙️ CAPM</a>
  <a href="#sec-var">💥 VaR / CVaR</a>
  <a href="#sec-garch">📊 GARCH</a>
  <a href="#sec-señales">🔔 Señales</a>
  <a href="#sec-portafolio">📦 Portafolio</a>
  <a href="#sec-macro">🌍 Macro</a>
</nav>

<div class="container">

<!-- RESUMEN -->
<section id="sec-resumen">
  <h2>📋 Resumen General de Activos</h2>
  <div class="grid">
"""

    # Tarjetas resumen
    for row in report["summary"]:
        t = row["ticker"]
        signal_cls = row["senal"].lower() if row["senal"] else "hold"
        html += f"""    <div class="card">
      <h4>{t}</h4>
      <div class="metric">${row["precio"]:.2f}</div>
      <div class="metric-label">RSI: {row["rsi"]:.1f} &nbsp; Señal: <span class="badge {signal_cls}">{row["senal"] or "N/A"}</span></div>
    </div>
"""

    html += """  </div>
</section>

<!-- PRECIOS -->
<section id="sec-precios">
  <h2>📈 Precios y Medias Móviles</h2>
  <div class="grid">
"""
    for t in report["assets"]:
        html += f'    <div class="chart-box" id="chart-price-{t}"></div>\n'
    html += "  </div>\n</section>\n\n"

    # TÉCNICOS
    html += '<section id="sec-tecnicos">\n  <h2>📉 Indicadores Técnicos</h2>\n'
    for indicator, label, icon in [("rsi", "RSI (14)", "📉"), ("macd", "MACD (12,26,9)", "📊"), ("bb", "Bandas de Bollinger", "📈"), ("stoch", "Estocástico", "")]:
        html += f"""  <details class="collapsible" open>
    <summary>{icon} {label}</summary>
    <div class="content">
      <div class="grid">
"""
        for t in report["assets"]:
            html += f'        <div class="chart-box" id="chart-{indicator}-{t}"></div>\n'
        html += "      </div>\n    </div>\n  </details>\n"
    html += "</section>\n\n"

    # CAPM
    html += """<section id="sec-capm">
  <h2>⚙️ Modelo CAPM</h2>
  <p style="color:var(--text2);margin-bottom:12px;">Beta y retorno esperado según el modelo de valoración de activos de capital.</p>
  <table><thead><tr><th>Activo</th><th>Beta (β)</th><th>Retorno Esperado</th><th>Tasa Libre de Riesgo</th></tr></thead><tbody>
"""
    for row in report["capm"]:
        beta = row["beta"]
        beta_cls = "positive" if beta > 1 else "negative" if beta < 0.8 else ""
        html += f"""<tr><td><b>{row["ticker"]}</b></td>
  <td class="{beta_cls}">{beta:.4f}</td>
  <td>{row["expected_return"]*100:.2f}%</td>
  <td>{row["rf"]*100:.2f}%</td>
</tr>
"""
    html += """</tbody></table>
</section>
"""

    # VaR
    html += """<section id="sec-var">
  <h2>💥 Value at Risk (VaR) y CVaR</h2>
  <p style="color:var(--text2);margin-bottom:12px;">Pérdida máxima esperada al 95% y 99% de confianza. Métodos: Paramétrico, Histórico, Monte Carlo.</p>
  <table><thead><tr><th>Activo</th><th>VaR 95% Param.</th><th>VaR 95% Hist.</th><th>VaR 95% MC</th><th>CVaR 95%</th><th>VaR 99% Param.</th><th>CVaR 99%</th><th>Kupiec</th></tr></thead><tbody>
"""
    for row in report["var"]:
        html += f"""<tr><td><b>{row["ticker"]}</b></td>
  <td>{row["var_95_param"]*100:.3f}%</td><td>{row["var_95_hist"]*100:.3f}%</td><td>{row["var_95_mc"]*100:.3f}%</td><td>{row["cvar_95"]*100:.3f}%</td>
  <td>{row["var_99_param"]*100:.3f}%</td><td>{row["cvar_99"]*100:.3f}%</td>
  <td><span class="badge {"buy" if row["kupiec"]=="Accepted" else "sell"}">{row["kupiec"]}</span> ({row["exceptions"]})</td>
</tr>
"""
    html += """</tbody></table>
</section>
"""

    # GARCH
    html += """<section id="sec-garch">
  <h2>📊 Volatilidad Condicional GARCH</h2>
"""
    for t in report["assets"]:
        html += f'  <div class="chart-box" id="chart-garch-{t}"></div>\n'

    # GARCH comparison table
    html += '  <h3 style="margin-top:24px;">Comparación de Modelos GARCH</h3>\n'
    for t, comp_list in report.get("garch_comparison", {}).items():
        if comp_list:
            html += f"""  <details class="collapsible">
    <summary>{t} - Comparación ARCH vs GARCH vs GJR-GARCH</summary>
    <div class="content">
      <table><thead><tr><th>Modelo</th><th>Log-Likelihood</th><th>AIC</th><th>BIC</th><th>Params</th><th>Mejor</th></tr></thead><tbody>
"""
            for c in comp_list:
                html += f"""<tr><td>{c["Modelo"]}</td><td>{c["Log-Likelihood"]}</td><td>{c["AIC"]}</td><td>{c["BIC"]}</td><td>{c["Params"]}</td><td>{c["Mejor"]}</td></tr>
"""
            html += """</tbody></table>
    </div>
  </details>
"""
    html += "</section>\n\n"

    # Señales
    html += """<section id="sec-señales">
  <h2>🔔 Señales de Trading (Combinadas)</h2>
  <p style="color:var(--text2);margin-bottom:12px;">Señal basada en votación mayoritaria de 5 indicadores: RSI, Bollinger, MACD, Golden/Death Cross, Estocástico.</p>
  <table><thead><tr><th>Activo</th><th>RSI</th><th>MACD</th><th>MACD Signal</th><th>BB Upper</th><th>BB Lower</th><th>Stoch %K</th><th>Stoch %D</th><th>Señal</th></tr></thead><tbody>
"""
    for row in report["signals"]:
        signal_cls = row["signal"].lower() if row["signal"] else "hold"
        html += f"""<tr><td><b>{row["ticker"]}</b></td>
  <td>{row["rsi"]:.1f}</td><td>{row["macd"]:.5f}</td><td>{row["macd_signal"]:.5f}</td>
  <td>{row["bb_upper"]:.2f}</td><td>{row["bb_lower"]:.2f}</td>
  <td>{row["stoch_k"]:.1f}</td><td>{row["stoch_d"]:.1f}</td>
  <td><span class="badge {signal_cls}">{row["signal"] or "N/A"}</span></td>
</tr>
"""
    html += """</tbody></table>
</section>
"""

    # Portafolio
    html += """<section id="sec-portafolio">
  <h2>📦 Optimización de Portafolio (Markowitz)</h2>
  <div class="grid">
    <div class="card">
      <h4> Máximo Sharpe Ratio</h4>
"""
    for t, w in report["portfolio"]["max_sharpe_weights"].items():
        html += f'      <div style="display:flex;justify-content:space-between;padding:4px 0;"><span>{t}</span><b>{w*100:.1f}%</b></div>\n'
    html += """    </div>
    <div class="card">
      <h4>🛡️ Mínima Volatilidad</h4>
"""
    for t, w in report["portfolio"]["min_vol_weights"].items():
        html += f'      <div style="display:flex;justify-content:space-between;padding:4px 0;"><span>{t}</span><b>{w*100:.1f}%</b></div>\n'
    html += """    </div>
  </div>
</section>
"""

    # Macro
    html += """<section id="sec-macro">
  <h2>🌍 Análisis Macro del Portafolio vs Benchmark</h2>
  <div class="grid">
"""
    m = report["macro"]
    metrics = [
        ("Retorno Anualizado Port.", m.get("port_ann_return", 0), True),
        ("Retorno Anualizado Benchmark", m.get("bench_ann_return", 0), True),
        ("Sharpe Benchmark", m.get("benchmark_sharpe", 0), True),
        ("Tracking Error", m.get("tracking_error", 0), False),
        ("Information Ratio", m.get("information_ratio", 0), True),
        ("Máximo Drawdown", m.get("max_drawdown", 0), False),
    ]
    for label, val, show_pct in metrics:
        if val is not None:
            display = f"{val*100:.2f}%" if show_pct else f"{val:.4f}"
            cls = "positive" if val > 0 else "negative" if val < 0 else ""
            html += f'    <div class="card"><div class="metric-label">{label}</div><div class="metric {cls}">{display}</div></div>\n'
    html += """  </div>
</section>

</div>

<footer>
  <p>Teoría del Riesgo · Dashboard v3.0 · Autora: Paula Español</p>
  <p style="margin-top:8px;">Modelos: CAPM, GARCH(1,1), GJR-GARCH, VaR Paramétrico/Histórico/Monte Carlo, CVaR, Markowitz, Monte Carlo Portfolio</p>
  <p style="margin-top:4px;">Generado el """ + report["generated_at"] + """</p>
</footer>

<script>
const chartsData = """ + charts_json + """;
const layout = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: '#e2e8f0', family: 'Segoe UI, sans-serif' },
  margin: { l:50, r:20, t:40, b:40 },
  xaxis: { gridcolor: '#2a2f5e', zerolinecolor: '#475569' },
  yaxis: { gridcolor: '#2a2f5e', zerolinecolor: '#475569' },
  legend: { bgcolor: 'rgba(0,0,0,0)' }
};
const config = { responsive: true, displayModeBar: true, modeBarButtonsToRemove: ['lasso2d','select2d'], displaylogo: false };

Object.entries(chartsData).forEach(([key, data]) => {
  const el = document.getElementById('chart-' + key);
  if (!el || !data.traces.length) return;
  const traces = data.traces.map(t => ({
    x: t.x, y: t.y, name: t.name, type: 'scatter', mode: 'lines',
    line: { width: 2 }
  }));
  // Añadir líneas de referencia para RSI y Estocástico
  if (key.startsWith('rsi_') || key.startsWith('stoch_')) {
    layout.shapes = [
      { type:'line', x0:data.traces[0].x[0], x1:data.traces[0].x[data.traces[0].x.length-1], y0:30, y1:30, line:{color:'#10b981',width:1,dash:'dash'} },
      { type:'line', x0:data.traces[0].x[0], x1:data.traces[0].x[data.traces[0].x.length-1], y0:70, y1:70, line:{color:'#ef4444',width:1,dash:'dash'} }
    ];
    layout.annotations = [
      { x:data.traces[0].x[data.traces[0].x.length-1], y:70, text:'Sobrecompra (70)', showarrow:false, font:{size:10}, yshift:12 },
      { x:data.traces[0].x[data.traces[0].x.length-1], y:30, text:'Sobreventa (30)', showarrow:false, font:{size:10}, yshift:12 }
    ];
  }
  Plotly.newPlot(el.id, traces, {...layout, title: data.title}, config);
});

// Smooth scroll
document.querySelectorAll('nav a').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    document.querySelector(a.getAttribute('href')).scrollIntoView({behavior:'smooth', block:'start'});
  });
});
</script>

</body>
</html>"""
    return html


def main():
    print("🚀 Generando reporte HTML completo...")
    report = generate_report()
    print("📝 Construyendo HTML...")
    html = build_html(report)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "reporte_financiero_completo.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ Reporte generado: {out_path}")
    print(f"   Ábralo en su navegador con doble clic.")
    print(f"   Tamaño: {len(html):,} bytes")


if __name__ == "__main__":
    main()
