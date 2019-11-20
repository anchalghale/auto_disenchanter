''' Module for gameflow related tasks '''
import asyncio
import random
from connection.league import LeagueConnection


async def check_gameflow(connection: LeagueConnection):
    '''
    Returns the current gamflow phase.
    Return values might include Lobby, EndOfGame, ReadyCheck,
    ChampSelect, WaitingForStats, Reconnect, PreEndOfGame, EndOfGame
    '''
    future = connection.async_get('/lol-gameflow/v1/session')
    await asyncio.sleep(0)
    res = future.result()
    if res.status_code == 404:
        return None
    return res.json()


def reconnect(connection: LeagueConnection):
    ''' Reconnects to the game '''
    connection.post('/lol-gameflow/v1/reconnect')


def skip_stats(connection: LeagueConnection):
    ''' Skips waiting for stats '''
    connection.post('/lol-end-of-game/v1/state/dismiss-stats')


def delete_pre_end_of_game(connection: LeagueConnection):
    ''' Deletes pre end of game sequence event '''
    res = connection.get('/lol-pre-end-of-game/v1/currentSequenceEvent')
    res_json = res.json()
    name = res_json['name']
    connection.post('/lol-pre-end-of-game/v1/complete/%s' % name)
    connection.delete('/lol-pre-end-of-game/v1/registration/%s' % name)


def get_honor_data(connection: LeagueConnection):
    ''' Gets a random player data for honoring if exists '''
    res = connection.get('/lol-honor-v2/v1/ballot')
    res_json = res.json()
    players = res_json['eligiblePlayers']
    if players == []:
        return None
    game_id = res_json['gameId']
    player = random.choice(players)
    data = {
        'gameId': game_id,
        'summonerId': player['summonerId'],
    }
    return data


def honor(connection: LeagueConnection, data):
    ''' Honors a player account of the given player data '''
    connection.post('/lol-honor-v2/v1/honor-player', json=data)
