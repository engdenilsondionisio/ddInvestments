import streamlit as st
from streamlit_autorefresh import st_autorefresh
import datetime

from data.fetcher import fetch_btc_history, fetch_mvrv_data, fetch_fear_greed
from indicators.log_regression import enrich_dataframe
from indicators.signals import generate_signal
from charts.price_chart import build_price_chart
from charts.mri_chart import build_mri_chart
from charts.mvrv_chart import build_mvrv_chart
from charts.fear_greed_gauge import build_fear_greed_gauge, build_fear_greed_history

st.set_page_config(
    page_title="BTC Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS — minimal & clean
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    h1 { font-size: 1.4rem !important; font-weight: 600 !important; color: #E6EDF3 !important; }
    .signal-banner {
        padding: 0.9rem 1.4rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255,255,255,0.07);
    }
    .signal-label { font-size: 1.1rem; font-weight: 700; letter-spacing: 0.04em; }
    .signal-meta  { font-size: 0.85rem; color: #8B949E; }
    .metric-card {
        background: #161B22;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 0.8rem 1rem;
        text-align: center;
    }
    .metric-label { font-size: 0.75rem; color: #8B949E; margin-bottom: 0.3rem; }
    .metric-value { font-size: 1.25rem; font-weight: 600; color: #E6EDF3; }
    .stPlotlyChart { border-radius: 8px; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# Auto-refresh every 5 minutes
st_autorefresh(interval=300_000, key="btc_dashboard_refresh")

# ── Header ──────────────────────────────────────────────────────────────────
now = datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC")
st.markdown(f"<h1>₿ Bitcoin Dashboard &nbsp; <span style='font-size:0.8rem;color:#8B949E;font-weight:400'>Atualizado: {now}</span></h1>", unsafe_allow_html=True)

# ── Load data ────────────────────────────────────────────────────────────────
with st.spinner("Carregando dados..."):
    btc_df   = fetch_btc_history()
    mvrv_df  = fetch_mvrv_data()
    fg_data  = fetch_fear_greed()

if btc_df.empty:
    st.error("Não foi possível carregar os dados de preço do Bitcoin.")
    st.stop()

btc_df = enrich_dataframe(btc_df)

# Current values
current_price  = float(btc_df["close"].iloc[-1])
current_sma200 = float(btc_df["sma200"].iloc[-1])
current_mri    = float(btc_df["mri"].dropna().iloc[-1]) if not btc_df["mri"].dropna().empty else 0.0
current_mvrv   = float(mvrv_df["mvrv"].iloc[-1]) if not mvrv_df.empty else 2.0
current_fg     = fg_data["value"]

signal = generate_signal(current_mri, current_mvrv, current_fg, current_price, current_sma200)

# ── Signal banner ─────────────────────────────────────────────────────────────
score_pct = int((signal["score"] + 2.0) / 4.0 * 100)
deviation  = (current_price - current_sma200) / current_sma200 * 100

st.markdown(f"""
<div class="signal-banner" style="background: linear-gradient(135deg, {signal['color']}18 0%, #161B22 100%);">
    <div>
        <div class="signal-label" style="color:{signal['color']}">● {signal['signal']}</div>
        <div class="signal-meta">Score: {signal['score']:+.2f} / 2.00</div>
    </div>
    <div style="flex:1; height:6px; background:#21262D; border-radius:3px; overflow:hidden;">
        <div style="width:{score_pct}%; height:100%; background:{signal['color']}; border-radius:3px;"></div>
    </div>
    <div style="text-align:right;">
        <div class="signal-label" style="color:#F7931A">${current_price:,.0f}</div>
        <div class="signal-meta">BTC / USD</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Quick metrics row ─────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
metrics = [
    ("MRI", f"{current_mri:+.2f}", c1),
    ("MVRV", f"{current_mvrv:.2f}", c2),
    ("Fear & Greed", f"{current_fg} — {fg_data['classification']}", c3),
    ("SMA 200", f"${current_sma200:,.0f}", c4),
    ("Desvio SMA 200", f"{deviation:+.1f}%", c5),
]
for label, value, col in metrics:
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Chart 1: Price + Bands ────────────────────────────────────────────────────
st.plotly_chart(build_price_chart(btc_df), use_container_width=True)

# ── Charts 2 & 3: MRI and MVRV ───────────────────────────────────────────────
col_mri, col_mvrv = st.columns(2)
with col_mri:
    st.plotly_chart(build_mri_chart(btc_df), use_container_width=True)
with col_mvrv:
    if not mvrv_df.empty:
        st.plotly_chart(build_mvrv_chart(mvrv_df), use_container_width=True)
    else:
        st.info("Dados de MVRV indisponíveis no momento.")

# ── Row: Fear & Greed gauge + history + score breakdown ──────────────────────
col_gauge, col_fghist, col_breakdown = st.columns([1, 1.6, 1.4])

with col_gauge:
    st.plotly_chart(
        build_fear_greed_gauge(current_fg, fg_data["classification"]),
        use_container_width=True,
    )

with col_fghist:
    if not fg_data["history"].empty:
        st.plotly_chart(
            build_fear_greed_history(fg_data["history"]),
            use_container_width=True,
        )

with col_breakdown:
    st.markdown("**Breakdown do Sinal**")
    score_labels = {2.0: "Compra Forte", 1.0: "Compra", 0.0: "Neutro", -1.0: "Venda", -2.0: "Venda Forte"}
    rows = []
    weights = {"MRI": "35%", "MVRV": "30%", "Fear & Greed": "20%", "SMA200 Dev.": "15%"}
    for ind, sc in signal["details"].items():
        label = score_labels.get(sc, str(sc))
        color = "#00C853" if sc > 0 else ("#FF1744" if sc < 0 else "#FFD740")
        rows.append(
            f"<tr><td style='color:#8B949E;padding:4px 8px'>{ind}</td>"
            f"<td style='color:#8B949E;padding:4px 8px;text-align:center'>{weights.get(ind,'')}</td>"
            f"<td style='color:{color};padding:4px 8px;text-align:center'>{label}</td></tr>"
        )
    st.markdown(
        "<table style='width:100%;border-collapse:collapse;font-size:0.82rem'>"
        "<tr><th style='color:#8B949E;text-align:left;padding:4px 8px'>Indicador</th>"
        "<th style='color:#8B949E;text-align:center;padding:4px 8px'>Peso</th>"
        "<th style='color:#8B949E;text-align:center;padding:4px 8px'>Sinal</th></tr>"
        + "".join(rows) + "</table>",
        unsafe_allow_html=True,
    )
