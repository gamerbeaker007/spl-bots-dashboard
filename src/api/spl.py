import logging
from binascii import hexlify
from time import time

import pandas as pd
import requests
from beemgraphenebase.ecdsasig import sign_message
from dateutil import parser
from requests.adapters import HTTPAdapter

from src.api.logRetry import LogRetry

base_url = 'https://api2.splinterlands.com/'
land_url = 'https://vapi.splinterlands.com/'
prices_url = 'https://prices.splinterlands.com/'

retry_strategy = LogRetry(
    total=20,
    status_forcelist=[429, 500, 502, 503, 504],
    backoff_factor=2,  # wait will be [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    allowed_methods=['HEAD', 'GET', 'OPTIONS']
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount('https://', adapter)


def get_card_details():
    address = base_url + 'cards/get_details'
    return pd.DataFrame(http.get(address).json()).set_index('id')


def get_player_collection_df(username):
    address = base_url + 'cards/collection/' + username
    collection = http.get(address).json()['cards']
    df = pd.DataFrame(sorted(collection, key=lambda card: card['card_detail_id']))
    return df[['player', 'uid', 'card_detail_id', 'xp', 'gold', 'edition', 'level']].set_index('uid')


def get_battle_history_df(account_name, token_params):
    address = base_url + 'battle/history2'
    params = token_params
    params['player'] = account_name
    params['limit'] = 50
    wild_df = pd.DataFrame()
    wild_result = http.get(address, params=params)
    if wild_result.status_code == 200:
        wild_df = pd.DataFrame(wild_result.json()['battles'])

    params['format'] = 'modern'
    modern_result = http.get(address, params=params)
    modern_df = pd.DataFrame()
    if modern_result.status_code == 200:
        modern_df = pd.DataFrame(modern_result.json()['battles'])

    if wild_df.empty and modern_df.empty:
        return None
    else:
        return pd.concat([wild_df, modern_df])


def get_current_season():
    address = base_url + 'settings'
    current_season = http.get(address).json()['season']

    return current_season


def get_settings():
    address = base_url + 'settings'
    return http.get(address).json()


def is_maintenance_mode():
    return get_settings()['maintenance_mode']


def get_season_end_time(season_id):
    address = base_url + 'season'
    params = {'id': season_id}
    result = http.get(address, params=params)
    if result.status_code == 200:
        date = parser.parse(str(result.json()['ends']))
        result = pd.DataFrame({'id': season_id, 'end_date': str(date)}, index=[0])
    else:
        logging.error('Failed call: '' + str(address) + ''')
        logging.error('Unable to determine season end date return code: ' + str(result.status_code))
        logging.error('This interrupts all other calculations, try re-execution.')
        logging.error('Stopping program now ... ')
        exit(1)
    return result


def player_exist(account_name):
    address = base_url + 'players/details'
    params = {'name': account_name}
    result = http.get(address, params=params)
    if result.status_code == 200 and 'error' not in result.json():
        return True
    else:
        return False


def compute_sig(string_to_sign: str, private_key: str):
    bytestring_signature = sign_message(string_to_sign, private_key)
    sig = hexlify(bytestring_signature).decode('ascii')
    return sig


def get_token(username: str, private_key: str):
    login_endpoint = base_url + 'players/v2/login'
    ts = int(time() * 1000)
    sig = compute_sig(username + str(ts), private_key)
    params = {
        'name': username,
        'ts': ts,
        'sig': sig
    }
    result = http.get(login_endpoint, params=params)
    token = ""
    version = ""
    if result and result.status_code == 200:
        result = result.json()
        if 'error' in result:
            raise ValueError(result['error'])

        version = result['timestamp']
        token = result['token']
    return token, version


def verify_token(token_params):
    # Verify token is now done via battle history 2 that needs a specific user token to retrieve data
    if token_params:
        address = base_url + 'battle/history2'
        params = token_params
        result = http.get(address, params=params)
        if result.status_code == 200:
            return True
    return False

