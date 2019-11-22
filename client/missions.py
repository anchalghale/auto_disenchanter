''' Module for missions related tasks '''
import asyncio

from connection.league import LeagueConnection

from constants import NPE_REWARDS


async def get_missions(connection: LeagueConnection):
    ''' Parses the missions data '''
    future = connection.async_get('/lol-missions/v1/missions')
    await asyncio.sleep(0)
    res = future.result()
    res_json = res.json()
    if res_json == []:
        return {}
    rewards_data = []
    for reward in NPE_REWARDS:
        rewards_data.append(
            next(filter(lambda x, r=reward: x['internalName'] == r, res_json), None))
    try:
        rewards_data.append(sorted(filter(
            lambda x: x['internalName'] == 'fwotd_mission', res_json
        ), key=lambda x: x['lastUpdatedTimestamp'], reverse=True)[0])
    except IndexError:
        pass
    try:
        rewards_data.append(sorted(filter(
            lambda x: x['internalName'] == 'prestige_02_v3', res_json
        ), key=lambda x: x['lastUpdatedTimestamp'])[0])
    except IndexError:
        pass

    rewards = {}
    for reward_data in rewards_data:
        rewards[reward_data['internalName']] = {
            'internalName': reward_data['internalName'],
            'id': reward_data['id'],
            'status': reward_data['status'],
            'completed_date': reward_data['completedDate']
        }
    return rewards
