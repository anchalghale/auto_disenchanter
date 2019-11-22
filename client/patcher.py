''' Module for patcher related tasks '''
import asyncio

from connection.league import LeagueConnection


async def get_patcher_state(connection: LeagueConnection):
    ''' Parses the patcher state of league of legends '''
    future = connection.async_get('/patcher/v1/products/league_of_legends/state')
    await asyncio.sleep(0)
    res = future.result()
    json_ = res.json()
    if 'action' in json_:
        return json_['action']
    return None
