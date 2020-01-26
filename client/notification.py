''' Module for notifications related tasks '''
import asyncio

from connection.league import LeagueConnection


async def delete_lb_notification(connection: LeagueConnection):
    ''' Deletes leaverbuster notification '''
    future = connection.async_delete('/lol-leaver-buster/v1/notifications/1')
    await asyncio.sleep(0)
    future.result()


async def post_honor_ack(connection: LeagueConnection):
    ''' Posts honor ack '''
    future = connection.async_post('/lol-honor-v2/v1/level-change/ack')
    await asyncio.sleep(0)
    future.result()
