import logging

import pandas as pd

from src.configuration import store
from src.static.static_values_enum import MatchType, Format
from src.utils import store_util, progress_util, spl_util


def log_battle_note(count):
    limit = 50
    if count == limit:
        logging.info(str(limit) + ' or more battles to process consider running this program more often')
        logging.info('SPL API limits ' + str(limit) + ' battle history')
    else:
        logging.info(str(count) + ' battles to process')


def add_rating_log(account, battle):
    if battle['player_1'] == account:
        final_rating = battle['player_1_rating_final']
    else:
        final_rating = battle['player_2_rating_final']

    match_format = get_battle_format(battle['format'])

    df = pd.DataFrame({'created_date': battle['created_date'],
                       'account': account,
                       'rating': final_rating,
                       'format': match_format,
                       }, index=[0])
    store.rating = pd.concat([store.rating, df], ignore_index=True)


def get_battle_format(battle_format):
    # format = null when wild
    if battle_format:
        return battle_format
    else:
        return Format.wild.value


def get_battles_to_process(account):
    battle_history = spl_util.get_battle_history_df(account)
    if battle_history is not None and \
            not battle_history.empty and \
            not store.last_processed.empty and \
            not store.last_processed.loc[(store.last_processed.account == account)].empty:
        # filter out already processed
        last_processed_date = \
            store.last_processed.loc[(store.last_processed.account == account)].last_processed.values[0]
        battle_history = battle_history.loc[(battle_history['created_date'] > last_processed_date)]
    return battle_history


def process_battle(account):
    if store_util.get_management_token():
        battle_history = get_battles_to_process(account)
        if battle_history is not None:
            log_battle_note(len(battle_history.index))
            if not battle_history.empty:
                for index, battle in battle_history.iterrows():
                    match_type = battle['match_type']

                    battle_details = battle.details
                    if not is_surrender(battle_details):
                        # If a ranked match also log the rating
                        if match_type and match_type == MatchType.RANKED.value:
                            add_rating_log(account, battle)

                    else:
                        logging.debug("Surrender match skip")

                last_processed_date = \
                    battle_history.sort_values(by='created_date', ascending=False)['created_date'].iloc[0]
                update_last_processed_df(account, last_processed_date)
            else:
                logging.debug('No battles to process.')
        else:
            logging.debug('None battles to process.')
    else:
        logging.info('Skip battle process... not token found for: ' + account)


def update_last_processed_df(account, last_processed_date):
    if store.last_processed.empty or store.last_processed.loc[(store.last_processed.account == account)].empty:
        # create
        new = pd.DataFrame({'account': [account],
                            'last_processed': [last_processed_date]},
                           index=[0])
        store.last_processed = pd.concat([store.last_processed, new], ignore_index=True)
    else:
        store.last_processed.loc[
            (store.last_processed.account == account),
            'last_processed'] = last_processed_date


def is_surrender(battle_details):
    return 'type' in battle_details and battle_details['type'] == 'Surrender'


def process_battles():
    progress_util.update_daily_msg("Start processing battles")
    monitoring_accounts = store_util.get_monitoring_account_names()
    total_accounts = len(monitoring_accounts)

    for count, account in enumerate(monitoring_accounts, start=1):
        msg = f'...processing ({count}/{total_accounts}): {account}'
        progress_util.update_daily_msg(msg)
        process_battle(account)
