''' Module for matchmaking related tasks '''
import asyncio

from connection.league import LeagueConnection


async def check_matchmaking_errors(connection: LeagueConnection):
    ''' Reutrns the matchmaking errors if exists '''
    future = connection.async_get("/lol-matchmaking/v1/search/errors")
    await asyncio.sleep(0)
    res = future.result()
    if res.status_code == 200:
        if res.json() == []:
            return None
        return res.json()


async def check_search_state(connection: LeagueConnection):
    ''' Reutrns the current search state'''
    future = connection.async_get("/lol-lobby/v2/lobby/matchmaking/search-state")
    await asyncio.sleep(0)
    res = future.result()
    res_json = res.json()
    if res_json["errors"] != []:
        return None
    return res_json["searchState"]


def start_matchmaking(connection: LeagueConnection):
    ''' Starts the matchmaking process '''
    connection.post("/lol-lobby/v2/lobby/matchmaking/search")


def accept_queue(connection: LeagueConnection):
    ''' Accepts the ready check '''
    connection.post("/lol-matchmaking/v1/ready-check/accept")


def accept_invitation(connection: LeagueConnection, invitation_id):
    '''Accepts the incoming invitation'''
    connection.post(
        f'/lol-lobby/v2/received-invitations/{invitation_id}/accept')


def send_invitations(connection: LeagueConnection, data):
    '''Send an game invite to given id'''
    connection.post('/lol-lobby/v2/lobby/invitations', json=data)
