''' Module for missions related tasks '''
import time
import asyncio

from connection.league import LeagueConnection
from client.exceptions import LogoutNeededException, FwotdDataParseException

from constants import NPE_REWARDS


async def get_missions(connection: LeagueConnection, gathering_data_limit, get_fwotd=False):
    ''' Parses the missions data '''
    start_time = time.time()
    while True:
        if time.time() - start_time >= gathering_data_limit:
            raise LogoutNeededException
        future = connection.async_get('/lol-missions/v1/missions')
        await asyncio.sleep(0)
        res = future.result()
        res_json = res.json()
        if res_json == []:
            await asyncio.sleep(5)
            continue
        rewards_data = []
        for reward in NPE_REWARDS:
            rewards_data.append(
                next(filter(lambda x, r=reward: x['internalName'] == r, res_json), None))
        try:
            if get_fwotd:
                fwotd = sorted(filter(
                    lambda x: x['internalName'] == 'fwotd_mission', res_json
                ), key=lambda x: x['lastUpdatedTimestamp'], reverse=True)[0]
                if fwotd['status'] == 'COMPLETED':
                    if fwotd['completedDate'] in [0, -1]:
                        raise FwotdDataParseException
                rewards_data.append(fwotd)
        except (IndexError, KeyError, FwotdDataParseException):
            await asyncio.sleep(5)
            continue
        try:
            rewards_data.append(sorted(filter(
                lambda x: x['internalName'] == 'prestige_02_v3', res_json
            ), key=lambda x: x['lastUpdatedTimestamp'])[0])
        except IndexError:
            await asyncio.sleep(5)
            continue

        rewards = {}
        for reward_data in rewards_data:
            rewards[reward_data['internalName']] = {
                'internalName': reward_data['internalName'],
                'id': reward_data['id'],
                'status': reward_data['status'],
                'completed_date': reward_data['completedDate']
            }
        return rewards
