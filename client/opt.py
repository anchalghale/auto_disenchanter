''' Module for opting related tasks '''
import asyncio

from connection.league import LeagueConnection


async def worlds_opt_in(connection: LeagueConnection):
    ''' Opt into worlds mission '''
    future = connection.async_get('/lol-missions/v1/series')
    await asyncio.sleep(0)
    res = future.result()
    res_json = res.json()
    worlds = list(filter(lambda m: m['internalName'] == 'Worlds2019B_series', res_json))
    if worlds == []:
        return
    if worlds[0]['status'] == 'PENDING':
        future = connection.async_put('/lol-missions/v2/player/opt',
                                      json={"seriesId": worlds[0]['id'], "option": "OPT_IN"})
        await asyncio.sleep(0)
        future.result()
    return


async def npe_opt_in(connection: LeagueConnection):
    ''' Opt into npe rewards '''
    future = connection.async_post('/lol-npe-rewards/v1/challenges/opt')
    await asyncio.sleep(0)
    future.result()


async def trackers_opt_int(connection: LeagueConnection):
    ''' Opt into all the missions in trackers '''
    future = connection.async_get('/lol-missions/v1/series')
    await asyncio.sleep(0)
    res = future.result()
    res_json = res.json()
    missions = list(filter(lambda m: m['displayType'] ==
                           'TRACKER' and m['status'] == 'PENDING', res_json))
    _ = [connection.async_put(
        '/lol-missions/v2/player/opt',
        json={"seriesId": mission['id'], "option": "OPT_IN"}) for mission in missions]
