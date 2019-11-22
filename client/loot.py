''' Module for loot related tasks '''
import logging
import re
import time
from .exceptions import LootRetrieveException


def get_loot(connection):
    ''' Parses the loot data '''
    res = connection.get('/lol-loot/v1/player-loot')
    res_json = res.json()
    if res_json == []:
        logging.error("Can't retrieve loot")
        raise LootRetrieveException
    return res_json


def process_redeem(connection, array):
    ''' Does the redeeming task '''
    for loot in array:
        logging.info("Redeeming: %s, Count: %d",
                     loot["itemDesc"], loot["count"])
        connection.post("/lol-loot/v1/player-loot/%s/redeem" %
                        loot["lootName"])


def redeem_free(connection):
    ''' Redeems all the free champion shards '''
    logging.info("Redeeming free shards")
    for _ in range(10):
        try:
            res_json = get_loot(connection)
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
        process_redeem(connection, loot_result)
    raise LootRetrieveException


def redeem(connection, value):
    ''' Redeems all the champion shards of a specific value '''
    logging.info("Redeeming %d BE shards", value)
    for _ in range(10):
        try:
            res_json = get_loot(connection)
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
        process_redeem(connection, loot_result)
    raise LootRetrieveException


def open_champion_capsules(connection):
    ''' Opens  all champion capsules '''
    logging.info("Opening all champion capsules")
    for _ in range(10):
        try:
            res_json = get_loot(connection)
        except LootRetrieveException:
            time.sleep(1)
            continue
        loot_result = list(
            filter(lambda m: re.fullmatch("CHEST_((?!(generic|224)).)*", m["lootId"]), res_json))
        if loot_result == []:
            return

        for loot in loot_result:
            logging.info(
                "Opening chest: %s, Count: %d", loot["lootName"], loot["count"])
            url = "/lol-loot/v1/recipes/%s_OPEN/craft?repeat=%d" % (
                loot["lootName"], loot["count"])
            data = [loot["lootName"]]
            connection.post(url, json=data)
    raise LootRetrieveException


def disenchant(connection):
    ''' Disenchants the champion shards '''
    logging.info("Disenchanting all champion shards")
    for _ in range(10):
        try:
            res_json = get_loot(connection)
        except LootRetrieveException:
            time.sleep(1)
            continue

        loot_result = list(
            filter(lambda m: m["displayCategories"] == "CHAMPION", res_json))
        if loot_result == []:
            return

        for loot in loot_result:
            logging.info(
                "Dienchanting: %s, Count: %d", loot["itemDesc"], loot["count"])
            url = "/lol-loot/v1/recipes/%s_disenchant/craft?repeat=%d" % (
                loot["type"], loot["count"])
            data = [loot["lootName"]]
            connection.post(url, json=data)
    raise LootRetrieveException
