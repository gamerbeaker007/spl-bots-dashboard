import dash_bootstrap_components as dbc
from dash import Output, Input, dcc, State, ctx
from dateutil import parser

from src.configuration import store
from src.pages.filter_pages import filter_ids
from src.pages.main_dash import app
from src.pages.navigation_pages import nav_ids
from src.static.static_values_enum import KEEP_NUMBER_SEASONS
from src.utils.trace_logging import measure_duration

date_fmt = '%Y-%m-%d %H:%M (UTC)'


layout = dbc.InputGroup(
        [
            dbc.InputGroupText('Since season'),
            dcc.Dropdown(id=filter_ids.filter_season_dropdown,
                         clearable=False,
                         style={'width': '85px'},
                         className='dbc'),
            dbc.InputGroupText(id=filter_ids.filter_from_date_text,
                               children='2001-01-01T00:00:00.000Z'),

        ],
        className='mb-3',
    ),


@app.callback(
    Output(filter_ids.filter_settings, 'data'),
    Output(filter_ids.filter_from_date_text, 'children'),
    Input(filter_ids.filter_season_dropdown, 'value'),
    State(filter_ids.filter_settings, 'data'),
    prevent_initial_call=True,
)
@measure_duration
def filter_season_df(season_id, filter_settings):
    if season_id:
        season_end_date = store.season_end_dates.loc[(store.season_end_dates.id == int(season_id) - 1)].end_date.iloc[0]
        from_date = parser.parse(season_end_date)

        filter_settings['from_date'] = str(from_date)
        return filter_settings, str(from_date.strftime('%Y-%m-%d %H:%M (UTC)'))
    else:
        return filter_settings, ''


@app.callback(
    Output(filter_ids.filter_season_dropdown, 'options'),
    Output(filter_ids.filter_season_dropdown, 'value'),
    Input(nav_ids.trigger_daily, 'data'),
)
@measure_duration
def update_season_callback(trigger):
    season_played = store.season_end_dates.id.tolist()[-KEEP_NUMBER_SEASONS:]

    first_played_season = ''
    if len(season_played) > 1:
        first_played_season = season_played[0]
    return season_played, first_played_season
