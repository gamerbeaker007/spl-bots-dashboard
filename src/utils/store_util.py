import logging
import os

import pandas as pd

from src import battle_store
from src.api import spl
from src.configuration import store, config
from src.static.static_values_enum import KEEP_NUMBER_SEASONS
from src.utils import progress_util


def update_season_end_dates():
    if store.season_end_dates.empty:
        from_season_id = 1
    else:
        from_season_id = store.season_end_dates.id.max() + 1

    till_season_id = spl.get_current_season()['id']
    # logging.info("Update season end dates for '" + str(till_season_id) + "' seasons")
    for season_id in range(from_season_id, till_season_id + 1):
        logging.info("Update season end date for season: " + str(season_id))

        store.season_end_dates = pd.concat([store.season_end_dates,
                                            spl.get_season_end_time(season_id)],
                                           ignore_index=True)
    save_stores()


def get_store_names():
    stores_arr = []
    for store_name, _store in store.__dict__.items():
        if isinstance(_store, pd.DataFrame):
            stores_arr.append(store_name)
    return stores_arr


def validate_store_name(name):
    for store_name, _store in store.__dict__.items():
        if isinstance(_store, pd.DataFrame):
            if name == store_name:
                return True
    return False


def get_store_file(name):
    return os.path.join(config.store_dir, str(name + config.file_extension))


def load_stores():
    for store_name in get_store_names():
        store_file = get_store_file(store_name)
        if os.path.isfile(store_file):
            store.__dict__[store_name] = pd.read_parquet(store_file, engine='pyarrow')


def save_stores():
    for store_name in get_store_names():
        store_file = get_store_file(store_name)
        store.__dict__[store_name].sort_index().to_csv(store_file)
        store.__dict__[store_name].sort_index().to_parquet(
            store_file,
            engine='pyarrow',
            compression='snappy'
        )


def save_single_store(store_name):
    if validate_store_name(store_name):
        store_file = get_store_file(store_name)
        store.__dict__[store_name].sort_index().to_csv(store_file)
        store.__dict__[store_name].sort_index().to_parquet(
            store_file,
            engine='pyarrow',
            compression='snappy'
        )
    else:
        logging.error("Invalid store name")


def get_management_account_names():
    if store.accounts.empty:
        return list()
    else:
        return store.accounts.account_name.tolist()


def get_monitoring_account_names():
    if store.monitoring_accounts.empty:
        return list()
    else:
        return store.monitoring_accounts.account_name.tolist()


def get_management_account_name():
    if store.accounts.empty:
        return ""
    else:
        return store.accounts.values[0][0]


def add_account(account_name):
    new_account = pd.DataFrame({'account_name': account_name}, index=[0])
    if store.accounts.empty:
        store.accounts = pd.concat([store.accounts, new_account], ignore_index=True)
    else:
        if store.accounts.loc[(store.accounts.account_name == account_name)].empty:
            store.accounts = pd.concat([store.accounts, new_account], ignore_index=True)
    save_stores()
    return store.accounts.account_name.tolist()


def add_monitoring_account(account_name, league_name):
    new_account = pd.DataFrame({'account_name': account_name, 'league_name': league_name}, index=[0])
    if store.monitoring_accounts.empty:
        store.monitoring_accounts = pd.concat([store.monitoring_accounts, new_account], ignore_index=True)
    else:
        if store.monitoring_accounts.loc[(store.monitoring_accounts.account_name == account_name)].empty:
            store.monitoring_accounts = pd.concat([store.monitoring_accounts, new_account], ignore_index=True)
        else:
            store.monitoring_accounts.loc[(store.monitoring_accounts.account_name == account_name), 'league_name'] = league_name
    save_stores()
    return store.monitoring_accounts.account_name.tolist()


def remove_account_from_store(store_name, search_column, account_name):
    _store = store.__dict__[store_name]
    if search_column in _store.columns.tolist():
        rows = _store.loc[(_store[search_column] == account_name)]
        if not rows.empty:
            _store = _store.drop(rows.index)
    return _store


def remove_data(account_name):
    for store_name in get_store_names():
        store.__dict__[store_name] = remove_account_from_store(store_name, 'account_name', account_name)
        store.__dict__[store_name] = remove_account_from_store(store_name, 'account', account_name)
        store.__dict__[store_name] = remove_account_from_store(store_name, 'player', account_name)
        store.__dict__[store_name] = remove_account_from_store(store_name, 'username', account_name)

    save_stores()


def remove_account(account_name):
    if store.accounts.empty:
        return list()
    else:
        account_row = store.accounts.loc[(store.accounts.account_name == account_name)]
        if not account_row.empty:
            remove_data(account_name)

    return store.accounts.account_name.tolist()


def remove_monitoring_account(account_name):
    if store.monitoring_accounts.empty:
        return list()
    else:
        account_row = store.monitoring_accounts.loc[(store.monitoring_accounts.account_name == account_name)]
        if not account_row.empty:
            remove_data(account_name)

    return store.monitoring_accounts.account_name.tolist()


def update_battle_log():
    progress_util.set_daily_title('Clean data older than \'' + str(KEEP_NUMBER_SEASONS) + '\' seasons')
    if not store.rating.empty:
        cut_off_date = store.season_end_dates.tail(KEEP_NUMBER_SEASONS).iloc[0].end_date
        store.rating = store.rating[store.rating['created_date'] > cut_off_date]
        save_stores()

    progress_util.set_daily_title('Update battles')
    battle_store.process_battles()

    save_stores()
    progress_util.update_daily_msg('Done')


def update_data(battle_update=True, season_update=False):
    try:
        if not spl.is_maintenance_mode():
            if battle_update:
                update_battle_log()
        else:
            logging.info("Splinterlands server is in maintenance mode skip this update cycle")
    except Exception as e:
        logging.error("Exception during update data")
        logging.exception(e)


def get_management_token():
    if not store.secrets.empty:
        get_management_account_name()
        row = store.secrets.loc[(store.secrets.username == get_management_account_name())]
        if not row.empty:
            row = row.iloc[0]
            params = {
                "username": row.username,
                'version': row.version,
                'token': row.token,
            }
            return params
    return None
