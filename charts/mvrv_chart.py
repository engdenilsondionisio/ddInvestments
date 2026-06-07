import plotly.graph_objects as go
import pandas as pd

from charts._theme import BASE_LAYOUT, COLORS


def build_mvrv_chart(df: pd.DataFrame) -> go.Figure:
    """MVRV ratio chart with historical reference zones."""
    df = df.dropna(subset=["mvrv"])
    dates = df.index
    mvrv = df["mvrv"]

    fig = go.Figure()

    # Background zones
    fig.add_hrect(y0=3.7, y1=max(mvrv.max() + 0.5, 5.0), fillcolor="rgba(255,68,68,0.08)", line_width=0)
    fig.add_hrect(y0=0, y1=1.0, fillcolor="rgba(68,255,136,0.08)", line_width=0)

    # Reference lines
    for level, label, color in [
        (3.7, "Topo histórico (3.7)", "rgba(255,68,68,0.6)"),
        (1.5, "Neutro (1.5)", "rgba(255,255,255,0.2)"),
        (1.0, "Fundo histórico (1.0)", "rgba(68,255,136,0.6)"),
    ]:
        fig.add_hline(
            y=level,
            line=dict(color=color, width=1, dash="dash"),
            annotation_text=label,
            annotation_position="top right",
            annotation_font=dict(size=10, color=color),
        )

    # MVRV line
    fig.add_trace(go.Scatter(
        x=dates,
        y=mvrv,
        mode="lines",
        line=dict(color=COLORS["mvrv"], width=1.5),
        name="MVRV",
        fill="tozeroy",
        fillcolor="rgba(251,146,60,0.06)",
    ))

    layout = BASE_LAYOUT.copy()
    layout.update(dict(
        title=dict(text="MVRV — Market Value to Realized Value", font=dict(size=14)),
        yaxis=dict(title="MVRV Ratio", zeroline=False, gridcolor=COLORS["grid"]),
        xaxis=dict(title="", gridcolor=COLORS["grid"]),
        hovermode="x unified",
        height=320,
    ))
    fig.update_layout(layout)
    return fig
