import numpy as np
import pandas as pd
import plotly.express as px

from src.static import static_values_enum
from src.static.static_values_enum import RatingLevel


def create_rating_graph(df, theme):
    df = df.copy()  # Create a copy of the DataFrame
    df['date'] = pd.to_datetime(df['created_date']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.sort_values(by='account')
    fig = px.scatter(
        df,
        x='date',
        y='rating',
        color='account',
        color_discrete_sequence=px.colors.qualitative.Set1,
        template=theme,
        height=800,
    )
    fig.update_layout(
        xaxis={'type': 'category', 'categoryorder': 'category ascending'},
    )

    # Start from 1 skip Novice
    for i in np.arange(1, len(static_values_enum.league_ratings)):
        y = static_values_enum.league_ratings[i]
        color = static_values_enum.league_colors[i]
        league_name = RatingLevel(i).name

        fig.add_hline(y=y,
                      line_width=1,
                      line_dash="dash",
                      annotation_text=league_name,
                      annotation_position="top left",
                      line_color=color)
    return fig
