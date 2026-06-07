import plotly.graph_objects as go
import pandas as pd

from charts._theme import BASE_LAYOUT, COLORS


def build_price_chart(df: pd.DataFrame, show: dict | None = None) -> go.Figure:
    """BTC price chart with toggleable indicators (log Y axis)."""
    if show is None:
        show = {}

    s_sma50    = show.get("sma50", True)
    s_sma200   = show.get("sma200", True)
    s_log      = show.get("log_bands", True)
    s_bull     = show.get("bull_band", True)
    s_bb       = show.get("bollinger", False)

    dates = df.index
    fig = go.Figure()

    # ── Log Regression Bands ─────────────────────────────────────────────────
    if s_log:
        fig.add_trace(go.Scatter(
            x=dates, y=df["band_top2"],
            mode="lines", line=dict(width=0),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=df["band_top1"],
            mode="lines", line=dict(width=0.8, color="rgba(255,68,68,0.4)"),
            fill="tonexty", fillcolor="rgba(255,68,68,0.08)",
            name="+1σ → +2σ", hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=df["band_bot2"],
            mode="lines", line=dict(width=0),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=df["band_bot1"],
            mode="lines", line=dict(width=0.8, color="rgba(68,255,136,0.4)"),
            fill="tonexty", fillcolor="rgba(68,255,136,0.08)",
            name="-2σ → -1σ", hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=df["log_regression"],
            mode="lines",
            line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dot"),
            name="Regressão Log",
        ))

    # ── Bollinger Bands (20d, ±2σ) ───────────────────────────────────────────
    if s_bb:
        fig.add_trace(go.Scatter(
            x=dates, y=df["bb_upper"],
            mode="lines", line=dict(width=0),
            showlegend=False, hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=df["bb_lower"],
            mode="lines", line=dict(width=0.8, color="rgba(129,140,248,0.5)"),
            fill="tonexty", fillcolor="rgba(129,140,248,0.09)",
            name="Bollinger Bands (±2σ)", hoverinfo="skip",
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=df["bb_mid"],
            mode="lines",
            line=dict(color="rgba(129,140,248,0.55)", width=1, dash="dot"),
            name="BB Mid (SMA 20)",
        ))

    # ── Bull Market Support Band ──────────────────────────────────────────────
    if s_bull:
        fig.add_trace(go.Scatter(
            x=dates, y=df["bull_sma20w"],
            mode="lines",
            line=dict(color="#22C55E", width=1.3),
            name="Bull SMA 20w",
        ))
        fig.add_trace(go.Scatter(
            x=dates, y=df["bull_ema21w"],
            mode="lines",
            line=dict(color="#86EFAC", width=1.3, dash="dot"),
            name="Bull EMA 21w",
        ))

    # ── SMA 200 ───────────────────────────────────────────────────────────────
    if s_sma200:
        fig.add_trace(go.Scatter(
            x=dates, y=df["sma200"],
            mode="lines",
            line=dict(color=COLORS["sma200"], width=1.2),
            name="SMA 200",
        ))

    # ── SMA 50 ────────────────────────────────────────────────────────────────
    if s_sma50:
        fig.add_trace(go.Scatter(
            x=dates, y=df["sma50"],
            mode="lines",
            line=dict(color=COLORS["sma50"], width=1.2),
            name="SMA 50",
        ))

    # ── BTC Price (sempre visível, camada de cima) ────────────────────────────
    fig.add_trace(go.Scatter(
        x=dates, y=df["close"],
        mode="lines",
        line=dict(color=COLORS["btc"], width=2),
        name="BTC / USD",
    ))

    layout = BASE_LAYOUT.copy()
    layout.update(dict(
        title=dict(text="Bitcoin — Cotação & Indicadores", font=dict(size=14)),
        yaxis=dict(type="log", title="Preço (USD)", tickformat="$,.0f", gridcolor=COLORS["grid"]),
        xaxis=dict(title="", gridcolor=COLORS["grid"], rangeslider=dict(visible=False)),
        hovermode="x unified",
        height=500,
    ))
    fig.update_layout(layout)
    return fig
