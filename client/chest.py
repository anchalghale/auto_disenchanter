''' Module for chest related tasks '''
import time

from gui.logger import Logger

from .loot import get_loot
from .exceptions import LootRetrieveException


def get_player_loot_map(connection):
    ''' Get player loot map from the server '''
    res = connection.get('/lol-loot/v1/player-loot-map/')
    res_json = res.json()
    return res_json


def get_key_fragment_count(loot_json):
    ''' Returns the key fragment count '''
    key_fragment = list(
        filter(lambda l: l['lootId'] == 'MATERIAL_key_fragment', loot_json))
    if key_fragment == []:
        return 0
    return key_fragment[0]['count']


def get_loot_count(loot_json, lood_id):
    ''' Returns the worlds token count '''
    loot = list(
        filter(lambda l: l['lootId'] == lood_id, loot_json))
    if loot == []:
        return 0
    return loot[0]['count']


def get_key_count(loot_json):
    ''' Returns the key count '''
    key = list(
        filter(lambda l: l['lootId'] == 'MATERIAL_key', loot_json))
    if key == []:
        return 0
    return key[0]['count']


def get_generic_chest_count(loot_json):
    ''' Returns the generic chest count '''
    generic_chest = list(
        filter(lambda l: l['lootId'] == 'CHEST_generic', loot_json))
    if generic_chest == []:
        return 0
    return generic_chest[0]['count']


def forge(logger: Logger, connection, repeat=1):
    ''' Forges key fragment to keys '''
    if repeat == 0:
        return
    logger.log(f'Forging {repeat} keys')
    connection.post(
        '/lol-loot/v1/recipes/MATERIAL_key_fragment_forge/craft?repeat={}'.format(
            repeat), json=['MATERIAL_key_fragment'])


def forge_champion_from_token(logger: Logger, connection, forge_url, forge_json, repeat=1):
    ''' Forges key fragment to keys '''
    if repeat == 0:
        return
    logger.log(f'Forging {repeat} champion shards from worlds token')
    connection.post(f'/lol-loot/v1/recipes/{forge_url}/craft?repeat={repeat}', json=forge_json)


def open_generic_chests(logger: Logger, connection, repeat=1):
    ''' Opens a chest and saves it data to json '''
    if repeat == 0:
        return
    logger.log(f'Opening {repeat} generic chests')
    connection.post(
        '/lol-loot/v1/recipes/CHEST_generic_OPEN/craft?repeat={}'.format(
            repeat), json=['CHEST_generic', 'MATERIAL_key'])


def forge_keys_and_open_generic_chests(logger: Logger, connection):
    ''' Forges all key fragments and opens all generic chests '''
    for _ in range(10):
        try:
            loot_json = get_loot(logger, connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        forgable_keys = get_key_fragment_count(loot_json)//3
        key_count = get_key_count(loot_json)
        generic_chest_count = get_generic_chest_count(loot_json)
        if (forgable_keys == 0 and key_count == 0) or generic_chest_count == 0:
            return
        if forgable_keys > 0:
            forge(logger, connection, forgable_keys)
            continue
        if min(key_count, generic_chest_count) > 0:
            open_generic_chests(logger, connection)
    raise LootRetrieveException


def forge_worlds_token(logger: Logger, connection):
    ''' Forges all key fragments and opens all generic chests '''
    for _ in range(10):
        try:
            loot_json = get_loot(logger, connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        worlds_token_count = get_loot_count(loot_json, 'MATERIAL_337')
        forgable = worlds_token_count//50
        if forgable == 0:
            return
        forge_champion_from_token(logger, connection,
                                  'MATERIAL_337_FORGE_33', ['MATERIAL_337'],
                                  repeat=forgable)
    raise LootRetrieveException


def forge_night_and_dawn_tokens(logger: Logger, connection):
    ''' Forges all key fragments and opens all generic chests '''
    for _ in range(10):
        try:
            loot_json = get_loot(logger, connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        tokens_count = get_loot_count(loot_json, 'MATERIAL_347')
        forgable = tokens_count//50
        if forgable == 0:
            return
        forge_champion_from_token(logger, connection,
                                  'MATERIAL_347_FORGE_19',
                                  ['MATERIAL_347'], repeat=forgable,)
    raise LootRetrieveException
