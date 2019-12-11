''' Module for summoner related tasks '''
import time
import asyncio

import requests

from connection.league import LeagueConnection
from gui.logger import Logger

from .exceptions import BadUsernameException


def change_icon(logger: Logger, connection: LeagueConnection, icon_id):
    ''' Changes the summoner icon '''
    while get_icon(connection) != icon_id:
        json = {
            'profileIconId': icon_id
        }
        try:
            logger.log("Changing summoner icon")
            connection.put('/lol-summoner/v1/current-summoner/icon', json=json)
        except requests.RequestException:
            pass
        time.sleep(1)


def get_icon(connection: LeagueConnection):
    ''' Parses the current summoner icon '''
    try:
        res = connection.get('/lol-summoner/v1/current-summoner')
        res_json = res.json()
        return res_json["profileIconId"]
    except requests.RequestException:
        return -1


async def get_summoner_data(connection: LeagueConnection):
    ''' Parses the data of current sumoner '''
    future = connection.async_get('/lol-summoner/v1/current-summoner')
    await asyncio.sleep(1)
    res = future.result()
    json_ = res.json()
    return (
        json_['summonerLevel'] if 'summonerLevel' in json_ else -1,
        json_['percentCompleteForNextLevel'] if 'percentCompleteForNextLevel' in json_ else 0,
        json_['profileIconId'] if 'profileIconId' in json_ else -1,
    )


async def get_blue_essence(connection: LeagueConnection):
    ''' Parses the blue essence value '''
    future = connection.async_get('/lol-store/v1/wallet')
    await asyncio.sleep(0)
    res = future.result()
    res_json = res.json()
    if 'ip' not in res_json:
        return -1
    return res_json['ip']


async def init_tutorial(logger: Logger, connection: LeagueConnection):
    ''' Initializes tutorial '''
    logger.log('Initiating tutorial...')
    future1 = connection.async_patch('/lol-npe-tutorial-path/v1/tutorials/init')
    future2 = connection.async_post('/telemetry/v1/events/new_player_experience',
                                    json={"eventName": "show_screen",
                                          "plugin": "rcp-fe-lol-new-player-experience",
                                          "screenName": "npe_tutorial_modules"})
    future3 = connection.async_put('/lol-npe-tutorial-path/v1/settings',
                                   json={"hasSeenTutorialPath": True,
                                         "hasSkippedTutorialPath": False,
                                         "shouldSeeNewPlayerExperience": False})
    future1.result()
    future2.result()
    future3.result()


async def get_tutorial_status(logger: Logger, connection: LeagueConnection, gathering_data_limit):
    ''' Parses the tutorial status '''
    start_time = time.time()
    while True:
        if time.time() - start_time >= gathering_data_limit:
            return ('UNLOCKED', 'LOCKED', 'LOCKED')
        await init_tutorial(logger, connection)
        future = connection.async_get('/lol-npe-tutorial-path/v1/tutorials')
        await asyncio.sleep(0)
        res = future.result()
        res_json = res.json()
        if res_json == []:
            await asyncio.sleep(1)
            continue
        return res_json[0]["status"], res_json[1]["status"], res_json[2]["status"]


async def get_champions(connection: LeagueConnection):
    ''' Parses the champions data '''
    future = connection.async_get('/lol-champions/v1/owned-champions-minimal')
    await asyncio.sleep(0)
    res = future.result()
    res_json = res.json()

    available_names = []
    owned_names = []
    owned = []

    if "errorCode" in res_json:
        return [], [], []
    for champ in res_json:
        if champ["active"]:
            available_names.append(champ["alias"])
        if champ["ownership"]["owned"]:
            owned.append(champ["id"])
            owned_names.append(champ["alias"])
    return owned, owned_names, available_names


def set_summoner_name(logger: Logger, connection, name):
    ''' Sets the summoner name if available '''
    for _ in range(10):
        res = connection.get(
            '/lol-summoner/v1/check-name-availability-new-summoners/{}'.format(name))
        if res.json():
            data = {
                'name': name,
            }

            logger.log('Setting summoner name')
            connection.post('/lol-summoner/v1/summoners', json=data)
            connection.post('/lol-login/v1/new-player-flow-completed')
            return
    raise BadUsernameException


def get_owned_champions_count(connection):
    ''' Parses number of champions owned '''
    res = connection.get('/lol-champions/v1/owned-champions-minimal')
    if res.status_code == 404:
        return -1
    res_json = res.json()
    if res_json == []:
        return -1
    filtered = list(
        filter(lambda m: m["ownership"]["owned"], res_json))
    return len(filtered)
