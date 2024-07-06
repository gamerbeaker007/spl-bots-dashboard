import dash_bootstrap_components as dbc
from dash import html

from src.api import spl
from src.utils import store_util


def get_layout():
    info_text = [
        'Posting is required for retrieving ratings.',
        html.Br(),
        'With this posting the spl token is retrieved and stored locally in secrets.csv.',
        html.Br(),
        'Posting key is not stored.',
    ]
    rows = [
        dbc.Row(html.H4('Management account status', className='mt-5')),
        dbc.Row(html.P(info_text, className='')),
    ]
    if store_util.get_management_account_name():
        children, color = check_spl_api()
        rows.append(
            dbc.Row([
                dbc.Col(
                    dbc.Alert(
                        children= children,
                        color=color,
                        style={'height': '38px'},
                        className='p-2'),
                )
            ])
        )
    else:
        rows.append(
            dbc.Row([
                dbc.Col(
                    dbc.Alert(
                        children=[
                            html.I(className='m-1 fas fa-exclamation-triangle'),
                            'No management account configured'
                        ],
                        color='danger',
                        style={'height': '38px'},
                        className='p-2'),
                )
            ])
        )

    return rows


def check_spl_api():
    account = store_util.get_management_account_name()
    if spl.verify_token(store_util.get_management_token()):
        children = [
            html.I(className='m-1 fas fa-check-circle'),
            str(account) + ' - connected'
        ]
        color = 'success'
    else:
        children = [html.I(className='m-1 fas fa-exclamation-triangle'),
                    str(account) + ' - not connected, provide token information']
        color = 'warning'
    return children, color
