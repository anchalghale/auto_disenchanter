''' Module for boots related tasks '''
import asyncio
from connection.league import LeagueConnection


async def get_active_boosts(connection: LeagueConnection):
    ''' Returns the data of active boosts    '''
    future = connection.async_get('/lol-active-boosts/v1/active-boosts')
    await asyncio.sleep(0)
    res = future.result()
    return res.json()
