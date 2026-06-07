import plotly.graph_objects as go
import pandas as pd

from charts._theme import BASE_LAYOUT, COLORS


def build_price_chart(df: pd.DataFrame) -> go.Figure:
    """BTC price chart with SMA50, SMA200 and Log Regression Bands (log Y axis)."""
    dates = df.index

    fig = go.Figure()

    # Band fills (top zone: red, bottom zone: green)
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

    # Log regression center line
    fig.add_trace(go.Scatter(
        x=dates, y=df["log_regression"],
        mode="lines",
        line=dict(color="rgba(255,255,255,0.35)", width=1, dash="dot"),
        name="Regressão Log",
    ))

    # SMAs
    fig.add_trace(go.Scatter(
        x=dates, y=df["sma200"],
        mode="lines",
        line=dict(color=COLORS["sma200"], width=1.2),
        name="SMA 200",
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=df["sma50"],
        mode="lines",
        line=dict(color=COLORS["sma50"], width=1.2),
        name="SMA 50",
    ))

    # BTC price
    fig.add_trace(go.Scatter(
        x=dates, y=df["close"],
        mode="lines",
        line=dict(color=COLORS["btc"], width=2),
        name="BTC / USD",
    ))

    layout = BASE_LAYOUT.copy()
    layout.update(dict(
        title=dict(text="Bitcoin — Cotação & Bandas de Regressão Logarítmica", font=dict(size=14)),
        yaxis=dict(type="log", title="Preço (USD)", tickformat="$,.0f", gridcolor=COLORS["grid"]),
        xaxis=dict(title="", gridcolor=COLORS["grid"], rangeslider=dict(visible=False)),
        hovermode="x unified",
        height=480,
    ))
    fig.update_layout(layout)
    return fig
