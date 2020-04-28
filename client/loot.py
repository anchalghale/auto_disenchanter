''' Module for loot related tasks '''
import re
import time

from logger import Logger

from .exceptions import LootRetrieveException


def get_loot(logger: Logger, connection):
    ''' Parses the loot data '''
    res = connection.get('/lol-loot/v1/player-loot')
    res_json = res.json()
    if res_json == []:
        logger.log("Can't retrieve loot")
        raise LootRetrieveException
    return res_json


def process_redeem(logger: Logger, connection, array):
    ''' Does the redeeming task '''
    for loot in array:
        logger.log(f'Redeeming: {loot["itemDesc"]}, Count: {loot["count"]}')
        connection.post('/lol-loot/v1/player-loot/%s/redeem' % loot['lootName'])


def redeem_free(logger: Logger, connection):
    ''' Redeems all the free champion shards '''
    logger.log("Redeeming free shards")
    for _ in range(10):
        try:
            res_json = get_loot(logger, connection)
        except LootRetrieveException:
            time.sleep(1)
            continue

        loot_result = list(
            filter(lambda m: (
                m["upgradeEssenceValue"] == 0 and
                m["type"] == "CHAMPION" and
                m["redeemableStatus"] == "REDEEMABLE"
            ), res_json))
        if loot_result == []:
            return
        process_redeem(logger, connection, loot_result)
    raise LootRetrieveException


def redeem(logger, connection, value):
    ''' Redeems all the champion shards of a specific value '''
    logger.log(f"Redeeming {value} BE shards")
    for _ in range(10):
        try:
            res_json = get_loot(logger, connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        loot_result = list(
            filter(lambda m: (
                m["value"] == value and
                m["type"] == "CHAMPION_RENTAL" and
                m["redeemableStatus"] == "REDEEMABLE_RENTAL"
            ), res_json))

        if loot_result == []:
            return
        process_redeem(logger, connection, loot_result)
    raise LootRetrieveException

def redeem_waterloo(logger, connection):
    '''Redeems waterloo'''
    logger.log("Redeeming Waterloo(Miss Fortune)")
    for _ in range(3):
        data = ["CHAMPION_SKIN_RENTAL_21002", "CURRENCY_cosmetic"]
        res = connection.post('/lol-loot/v1/recipes/SKIN_upgrade/craft?repeat=1', json=data)
        if res.ok:
            break

def open_champion_capsules(logger: Logger, connection, retry_limit=1):
    ''' Opens  all champion capsules '''
    logger.log("Opening all champion capsules")
    for _ in range(retry_limit):
        try:
            res_json = get_loot(logger, connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        loot_result = list(
            filter(lambda m: re.fullmatch("CHEST_((?!(generic|224)).)*", m["lootId"]), res_json))
        if loot_result == []:
            return

        for loot in loot_result:
            logger.log(f'Opening chest: {loot["lootName"]}, Count: {loot["count"]}')
            url = "/lol-loot/v1/recipes/%s_OPEN/craft?repeat=%d" % (
                loot["lootName"], loot["count"])
            data = [loot["lootName"]]
            connection.post(url, json=data)
    raise LootRetrieveException


def disenchant(logger: Logger, connection, retry_limit=10):
    ''' Disenchants the champion shards '''
    logger.log("Disenchanting all champion shards")
    for _ in range(retry_limit):
        try:
            res_json = get_loot(logger, connection)
        except LootRetrieveException:
            time.sleep(1)
            continue

        loot_result = list(
            filter(lambda m: m["displayCategories"] == "CHAMPION", res_json))
        if loot_result == []:
            return

        for loot in loot_result:
            logger.log(f'Dienchanting: {loot["itemDesc"]}, Count: {loot["count"]}')
            url = "/lol-loot/v1/recipes/%s_disenchant/craft?repeat=%d" % (
                loot["type"], loot["count"])
            data = [loot["lootName"]]
            connection.post(url, json=data)
    raise LootRetrieveException
