import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def plot_kpi(results: pd.DataFrame, level: str):

    sdf = results.query("level == @level").drop(["level", "uuid"], axis=1).sort_values(["kpi", "value"])

    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=['Costs', 'Netload', 'Self-sufficiency', 'Sustainability'],
    )

    pos = iter(
        [
            {"row": 1, "col": 1},
            {"row": 1, "col": 2},
            {"row": 2, "col": 1},
            {"row": 2, "col": 2},
        ]
    )

    colors= iter(['green', 'blue', 'gold', 'red'])

    for _, gdf in sdf.groupby("kpi"):
        fig.add_trace(
            go.Scatter(
                y=gdf["value"],
                mode="lines",
                line_color=next(colors),
            ),
            **next(pos)
        )
        fig.update_layout(title_text=level.capitalize(), showlegend=False)


    return fig
