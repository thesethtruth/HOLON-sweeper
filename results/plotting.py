import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def plot_kpi(results: pd.DataFrame, level: str, sort_by: str = "costs"):
    sdf = (
        results.query("level == @level")
        .set_index("uuid")
        .pivot(columns="kpi", values="value")
        .sort_values(by=sort_by)
    )

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=["Costs", "Netload", "Self-sufficiency", "Sustainability"],
    )
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=20, r=20, b=50, t=50, pad=2),
    )
    fig.update_xaxes(showgrid=False, showticklabels=False)
    fig.update_yaxes(showgrid=False)

    pos = iter(
        [
            {"row": 1, "col": 1},
            {"row": 1, "col": 2},
            {"row": 2, "col": 1},
            {"row": 2, "col": 2},
        ]
    )

    colors = iter(["green", "blue", "gold", "red"])

    for kpi in sdf.columns:
        gdf = sdf[[kpi]].dropna()
        fig.add_trace(
            go.Scatter(
                x=gdf.index,
                y=gdf[kpi],
                mode="lines",
                line_color=next(colors),
            ),
            **next(pos)
        )
        fig.update_layout(
            title_text=level.capitalize(),
            showlegend=False,
        )

    return fig
