import plotly.graph_objects as go
import pandas as pd

from charts._theme import BASE_LAYOUT, COLORS


def build_mri_chart(df: pd.DataFrame) -> go.Figure:
    """Mean Reversion Index chart with reference bands."""
    df_mri = df.dropna(subset=["mri"])
    dates = df_mri.index
    mri = df_mri["mri"]

    fig = go.Figure()

    # Background shading for extreme zones
    for y0, y1, color in [
        (2.0, mri.max() + 0.5, "rgba(255,68,68,0.08)"),
        (-mri.min() - 0.5, -2.0, "rgba(68,255,136,0.08)"),
    ]:
        fig.add_hrect(y0=y0, y1=y1, fillcolor=color, line_width=0)

    # Reference lines
    for level, color, dash in [
        (2.0, "rgba(255,68,68,0.6)", "dash"),
        (1.0, "rgba(255,150,68,0.4)", "dot"),
        (0.0, "rgba(255,255,255,0.2)", "solid"),
        (-1.0, "rgba(68,255,136,0.4)", "dot"),
        (-2.0, "rgba(68,255,136,0.6)", "dash"),
    ]:
        fig.add_hline(y=level, line=dict(color=color, width=1, dash=dash))

    # MRI line (color gradient via scatter with colorscale)
    fig.add_trace(go.Scatter(
        x=dates,
        y=mri,
        mode="lines",
        line=dict(color=COLORS["mri"], width=1.5),
        name="MRI",
        fill="tozeroy",
        fillcolor="rgba(167,139,250,0.06)",
    ))

    layout = BASE_LAYOUT.copy()
    layout.update(dict(
        title=dict(text="Mean Reversion Index", font=dict(size=14)),
        yaxis=dict(title="Z-score", zeroline=False, gridcolor=COLORS["grid"]),
        xaxis=dict(title="", gridcolor=COLORS["grid"]),
        hovermode="x unified",
        height=320,
        annotations=[
            dict(x=0.01, y=2.1, xref="paper", yref="y", text="Sobrecomprado", showarrow=False,
                 font=dict(size=10, color="rgba(255,68,68,0.7)"), xanchor="left"),
            dict(x=0.01, y=-2.1, xref="paper", yref="y", text="Sobrevendido", showarrow=False,
                 font=dict(size=10, color="rgba(68,255,136,0.7)"), xanchor="left"),
        ],
    ))
    fig.update_layout(layout)
    return fig
