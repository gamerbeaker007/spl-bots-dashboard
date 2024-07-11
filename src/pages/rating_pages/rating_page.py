from io import StringIO

import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, Output, Input, ctx
from dash.exceptions import PreventUpdate
from dateutil import parser

from src import analyse
from src.configuration import store
from src.graphs import rating_graph
from src.pages.filter_pages import filter_battle_format, filter_ids, filter_season
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.pages.rating_pages import rating_ids
from src.static.static_values_enum import Leagues
from src.utils import chart_util
from src.utils.trace_logging import measure_duration

# Define the page layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Col(filter_season.layout),
            dbc.Col(filter_battle_format.layout),

        ]),
        html.Br(),
        html.Hr(),

        html.Center(html.H1("Novice")),
        dcc.Graph(id=rating_ids.novice_rating_graph),
        html.Center(html.H1("Bronze")),
        dcc.Graph(id=rating_ids.bronze_rating_graph),
        html.Center(html.H1("Silver")),
        dcc.Graph(id=rating_ids.silver_rating_graph),
        html.Center(html.H1("Gold")),
        dcc.Graph(id=rating_ids.gold_rating_graph),
        html.Center(html.H1("Diamond")),
        dcc.Graph(id=rating_ids.diamond_rating_graph),
        html.Center(html.H1("Champion")),
        dcc.Graph(id=rating_ids.champion_rating_graph),
        dcc.Store(id=rating_ids.filtered_rating_df),
        dcc.Store(id=rating_ids.filter_settings),

    ]),
])


@app.callback(
    Output(rating_ids.filtered_rating_df, 'data'),
    Input(filter_ids.filter_settings, 'data'),
)
@measure_duration
def filter_df(stored_filter_settings):
    if not stored_filter_settings:
        raise PreventUpdate

    if store.rating.empty:
        empty_df = pd.DataFrame()
        return empty_df.to_json(date_format='iso', orient='split')

    rating_df = store.rating.copy()

    # filter on
    rating_df = analyse.filter_date(rating_df, stored_filter_settings)
    rating_df = analyse.filter_format(rating_df, stored_filter_settings)

    if not rating_df.empty:
        rating_df.loc[:].sort_values(by='created_date', inplace=True)

    return rating_df.to_json(date_format='iso', orient='split')


for league in Leagues:
    @app.callback(
        Output('{}-rating-graph'.format(league.name), 'figure'),
        Input(rating_ids.filtered_rating_df, 'data'),
        Input(nav_ids.theme_store, 'data'),
        prevent_initial_call=True,
    )
    @measure_duration
    def update_rating_graph(filtered_df, theme):
        league_name = ctx.outputs_list['id'].split('-')[0]

        if not filtered_df:
            raise PreventUpdate

        filtered_df = pd.read_json(StringIO(filtered_df), orient='split')
        if not filtered_df.empty:
            monitored_accounts = store.monitoring_accounts.loc[
                (store.monitoring_accounts.league_name == league_name)]
            if not monitored_accounts.empty:
                filtered_df = filtered_df[filtered_df.account.isin(monitored_accounts.account_name.tolist())]
                if not filtered_df.empty:
                    return rating_graph.create_rating_graph(filtered_df, theme)

        return chart_util.blank_fig(theme)


