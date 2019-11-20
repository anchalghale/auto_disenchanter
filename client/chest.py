''' Module for chest related tasks '''
import logging

from .loot import get_loot


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


def get_worlds_token_count(loot_json):
    ''' Returns the worlds token count '''
    key_fragment = list(
        filter(lambda l: l['lootId'] == 'MATERIAL_337', loot_json))
    if key_fragment == []:
        return 0
    return key_fragment[0]['count']


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


def forge(connection, repeat=1):
    ''' Forges key fragment to keys '''
    if repeat == 0:
        return
    logging.info('Forging %d keys', repeat)
    connection.post(
        '/lol-loot/v1/recipes/MATERIAL_key_fragment_forge/craft?repeat={}'.format(
            repeat), json=['MATERIAL_key_fragment'])


def forge_champion_from_worlds_token(connection, repeat=1):
    ''' Forges key fragment to keys '''
    if repeat == 0:
        return
    logging.info('Forging %d champion shards from worlds token', repeat)
    connection.post(
        '/lol-loot/v1/recipes/MATERIAL_337_FORGE_33/craft?repeat={}'.format(
            repeat), json=['MATERIAL_337'])


def open_generic_chests(connection, repeat=1):
    ''' Opens a chest and saves it data to json '''
    if repeat == 0:
        return
    logging.info('Opening %d generic chests', repeat)
    connection.post(
        '/lol-loot/v1/recipes/CHEST_generic_OPEN/craft?repeat={}'.format(
            repeat), json=['CHEST_generic', 'MATERIAL_key'])


def forge_keys_and_open_generic_chests(connection):
    ''' Forges all key fragments and opens all generic chests '''
    while True:
        loot_json = get_loot(connection)
        forgable_keys = get_key_fragment_count(loot_json)//3
        key_count = get_key_count(loot_json)
        generic_chest_count = get_generic_chest_count(loot_json)
        if (forgable_keys == 0 and key_count == 0) or generic_chest_count == 0:
            return
        if forgable_keys > 0:
            forge(connection, forgable_keys)
            continue
        if min(key_count, generic_chest_count) > 0:
            open_generic_chests(connection)


def forge_worlds_token(connection):
    ''' Forges all key fragments and opens all generic chests '''
    while True:
        loot_json = get_loot(connection)
        worlds_token_count = get_worlds_token_count(loot_json)
        forgable_champion_shards = worlds_token_count//50
        if forgable_champion_shards == 0:
            return
        forge_champion_from_worlds_token(connection, forgable_champion_shards)
