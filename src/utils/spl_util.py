import pandas as pd
from pandas import json_normalize

from src.api import spl
from src.configuration import config
from src.utils import store_util


def get_battle_history_df(account):
    return spl.get_battle_history_df(account, store_util.get_management_token())


def get_rule_sets_list():
    rule_sets = config.settings['battles']['rulesets']
    list_of_ruleset = []
    for rule_set in rule_sets:
        list_of_ruleset.append(rule_set['name'])
    return list(list_of_ruleset)


def get_ability_list():
    cards = spl.get_card_details()
    abilities_df = json_normalize(cards['stats']).abilities.dropna()
    flattened_abilities = [ability for sublist in abilities_df for ability in sublist if sublist]

    unique_abilities = {ability for sublist in flattened_abilities for ability in
                        (sublist if isinstance(sublist, list) else [sublist])}

    series = pd.Series(list(unique_abilities))
    return series.sort_values()
