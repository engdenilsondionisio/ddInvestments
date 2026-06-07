COLORS = {
    "btc":        "#F7931A",
    "sma50":      "#4ADE80",
    "sma200":     "#60A5FA",
    "mri":        "#A78BFA",
    "mvrv":       "#FB923C",
    "grid":       "#21262D",
    "background": "#0D1117",
    "surface":    "#161B22",
    "text":       "#E6EDF3",
    "subtext":    "#8B949E",
}

BASE_LAYOUT = dict(
    paper_bgcolor=COLORS["background"],
    plot_bgcolor=COLORS["background"],
    font=dict(color=COLORS["text"], family="sans-serif"),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        font=dict(size=11, color=COLORS["subtext"]),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    margin=dict(t=50, b=30, l=50, r=20),
    xaxis=dict(
        showgrid=True,
        gridcolor=COLORS["grid"],
        gridwidth=0.5,
        zeroline=False,
        showline=False,
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor=COLORS["grid"],
        gridwidth=0.5,
        zeroline=False,
        showline=False,
    ),
)
