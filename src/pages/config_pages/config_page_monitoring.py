import logging

import dash_bootstrap_components as dbc
from dash import ctx, State
from dash import dash_table
from dash import html, Output, Input, dcc

from src.api import spl
from src.configuration import config, store
from src.pages.config_pages import config_page
from src.pages.config_pages import config_page_ids
from src.pages.main_dash import app
from src.static.static_values_enum import Leagues
from src.utils import store_util
from src.utils.trace_logging import measure_duration


def get_layout():
    layout = dbc.Row([
        html.H1('Add monitoring accounts'),
        html.P('Multiple account can be added at once with , separated'),
        html.Div(id=config_page_ids.monitoring_accounts),
        dbc.Row([
            dbc.Col([
                html.Div(
                    style=config_page.get_readonly_style(),
                    className='dbc',
                    children=[
                        dbc.Input(
                            id=config_page_ids.monitoring_accounts_input,
                            type='text',
                            placeholder='account-names',
                            className='m-1 border border-dark',
                        ),
                        dcc.Dropdown(
                            id=config_page_ids.monitoring_accounts_league_name_input,
                            options=Leagues.list_names(),
                            value=Leagues.list_names()[1],
                            className='m-1 dbc',
                            style={"width": "40%"},
                        ),
                        dbc.Button(
                            'Add/update',
                            id=config_page_ids.monitoring_accounts_add_button,
                            color='primary',
                            className='m-1',
                            n_clicks=0
                        ),
                        dbc.Button(
                            'Remove',
                            id=config_page_ids.monitoring_accounts_remove_button,
                            color='danger',
                            className='m-1',
                            n_clicks=0
                        ),
                    ]),
            ]),
            dbc.Row(children=config_page.get_readonly_text()),
            dbc.Row(id=config_page_ids.monitoring_accounts_account_text),

            dbc.Row([
                html.H4('All monitored accounts'),
                html.Div(id=config_page_ids.monitoring_accounts_table),
            ], className='dbc'),

            dcc.Store(id=config_page_ids.tigger_monitor_accounts_updated),
            # dcc.Store(id=config_page_ids.account_updated),
            # dcc.Store(id=config_page_ids.account_removed)
        ]),
    ])

    return layout


def is_management_account(account):
    return account in store_util.get_management_account_names()


@app.callback(
    Output(config_page_ids.tigger_monitor_accounts_updated, 'data'),
    Output(config_page_ids.monitoring_accounts_account_text, 'children'),
    Input(config_page_ids.monitoring_accounts_add_button, 'n_clicks'),
    State(config_page_ids.monitoring_accounts_input, 'value'),
    State(config_page_ids.monitoring_accounts_league_name_input, 'value'),
    prevent_initial_call=True,
)
@measure_duration
def add_monitoring_account(add_clicks, account_names, league_name):
    text = ''
    added = False
    class_name = 'text-warning'
    if config_page_ids.monitoring_accounts_add_button == ctx.triggered_id and account_names:
        if not config.read_only:
            logging.info('Add monitoring account button was clicked')
            accounts = [item.strip() for item in account_names.split(',')]

            incorrect_accounts = []
            for account in accounts:
                if not spl.player_exist(account):
                    incorrect_accounts.append(account)

            if len(incorrect_accounts) == 0:
                text = 'Accounts added/updated: ' + ','.join(accounts)
                for account in accounts:
                    if not is_management_account(account):
                        store_util.add_monitoring_account(account, league_name)
                        added = True
                        class_name = 'text-success'
                    else:
                        text = 'Do not add management account as monitor account please'
            else:
                text = 'Incorrect accounts found: ' + str(','.join(incorrect_accounts))
        else:
            text = 'This is not allowed in read-only mode'
            class_name = 'text-danger'

    return added, html.Div(text, className=class_name)


@app.callback(
    Output(config_page_ids.tigger_monitor_accounts_updated, 'data'),
    Output(config_page_ids.monitoring_accounts_account_text, 'children'),
    Input(config_page_ids.monitoring_accounts_remove_button, 'n_clicks'),
    State(config_page_ids.monitoring_accounts_input, 'value'),
    prevent_initial_call=True,
)
@measure_duration
def remove_monitoring_click(remove_clicks, account_names):
    text = ''
    removed = False
    class_name = 'text-warning'
    if config_page_ids.monitoring_accounts_remove_button == ctx.triggered_id and account_names:
        if not config.read_only:
            logging.info('Remove account button was clicked')
            accounts = [item.strip() for item in account_names.split(',')]
            for account in accounts:
                store_util.remove_monitoring_account(account)
                removed = True
                text = 'Accounts are removed, data is deleted...'
                class_name = 'text-success'
        else:
            text = 'This is not allowed in read-only mode'
            class_name = 'text-danger'

    return removed, html.Div(text, className=class_name)


@app.callback(
    Output(config_page_ids.monitoring_accounts_table, 'children'),
    Input(config_page_ids.tigger_monitor_accounts_updated, 'data'),
)
@measure_duration
def update_losing_table(trigger):
    df = store.monitoring_accounts.copy()
    if not df.empty:
        return dash_table.DataTable(
            columns=[{'name': i, 'id': i} for i in df.columns],
            # columns=[
            #     {'id': 'url_markdown', 'name': 'Card', 'presentation': 'markdown'},
            #     {'id': 'card_name', 'name': 'Name'},
            #     {'id': 'level', 'name': 'Level'},
            #     {'id': 'battles', 'name': 'battles'},
            #
            # ],
            data=df.to_dict('records'),
            row_selectable=False,
            row_deletable=False,
            editable=False,
            filter_action='native',
            sort_action='native',
            style_cell={
                'textAlign': 'left',  # Left align text
            },
            style_filter={
                'textAlign': 'left',  # Left align filter text
            },
            # style_table={'overflowX': 'auto'},
            # style_cell_conditional=[{'if': {'column_id': 'url'}, 'width': '200px'}, ],
            page_size=50,
        )

    else:
        return dash_table.DataTable()
