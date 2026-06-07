import plotly.graph_objects as go
import pandas as pd

from charts._theme import BASE_LAYOUT, COLORS


def build_fear_greed_gauge(value: int, classification: str) -> go.Figure:
    """Fear & Greed Index gauge."""
    if value <= 20:
        bar_color = "#00C853"
    elif value <= 40:
        bar_color = "#69F0AE"
    elif value <= 60:
        bar_color = "#FFD740"
    elif value <= 80:
        bar_color = "#FF6D00"
    else:
        bar_color = "#FF1744"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(font=dict(size=36, color=bar_color)),
        title=dict(text=f"Fear & Greed<br><span style='font-size:13px;color:{bar_color}'>{classification}</span>",
                   font=dict(size=14, color="#E6EDF3")),
        gauge=dict(
            axis=dict(
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["0", "25", "50", "75", "100"],
                tickfont=dict(size=10, color="#8B949E"),
            ),
            bar=dict(color=bar_color, thickness=0.25),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[0, 20],   color="rgba(0,200,83,0.15)"),
                dict(range=[20, 40],  color="rgba(105,240,174,0.1)"),
                dict(range=[40, 60],  color="rgba(255,215,64,0.08)"),
                dict(range=[60, 80],  color="rgba(255,109,0,0.1)"),
                dict(range=[80, 100], color="rgba(255,23,68,0.15)"),
            ],
            threshold=dict(
                line=dict(color=bar_color, width=3),
                thickness=0.75,
                value=value,
            ),
        ),
    ))

    layout = BASE_LAYOUT.copy()
    layout.update(dict(height=260, margin=dict(t=60, b=10, l=20, r=20)))
    fig.update_layout(layout)
    return fig


def build_fear_greed_history(hist_df: pd.DataFrame) -> go.Figure:
    """Fear & Greed 365-day history chart."""
    if hist_df.empty:
        return go.Figure()

    fig = go.Figure(go.Scatter(
        x=hist_df.index,
        y=hist_df["value"],
        mode="lines",
        line=dict(color=COLORS["mri"], width=1.5),
        fill="tozeroy",
        fillcolor="rgba(167,139,250,0.06)",
        name="Fear & Greed",
    ))

    fig.add_hline(y=20, line=dict(color="rgba(0,200,83,0.4)", width=1, dash="dot"))
    fig.add_hline(y=80, line=dict(color="rgba(255,23,68,0.4)", width=1, dash="dot"))

    layout = BASE_LAYOUT.copy()
    layout.update(dict(
        title=dict(text="Fear & Greed — últimos 365 dias", font=dict(size=13)),
        yaxis=dict(range=[0, 100], gridcolor=COLORS["grid"]),
        xaxis=dict(gridcolor=COLORS["grid"]),
        height=200,
        showlegend=False,
        margin=dict(t=40, b=20, l=40, r=10),
    ))
    fig.update_layout(layout)
    return fig
