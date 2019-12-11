''' Module for gameflow related tasks '''
import datetime

import requests

try:
    import humps
except ImportError as exp:
    print(str(exp))

from connection.league import LeagueConnection


def get_match_list(connection: LeagueConnection):
    ''' Parses the match list data '''
    return connection.async_get('/lol-match-history/v1/matchlist')


def get_delta(connection: LeagueConnection):
    ''' Parses the match list data '''
    return connection.async_get('/lol-match-history/v1/delta')


async def get_game_data(connection: LeagueConnection):
    ''' Parses the neccessary data from the game data '''
    try:
        match_list = get_match_list(connection)
        deltas = get_delta(connection)
        match_list = match_list.result()
        deltas = deltas.result()
        match_list = match_list.json()
        deltas = deltas.json()['deltas']
        account_id = match_list['accountId']
        games_count = match_list['games']['gameCount']
        games = match_list['games']['games']
        games = list(filter(lambda g: datetime.date.fromtimestamp(
            g['gameCreation'] // 1000) == datetime.date.today(), games))
        ids = [g['gameId'] for g in games]
        deltas = list(filter(lambda d: d['gameId'] in ids, deltas))
        games_output = []
        for game in games:
            participant = next((p for p in game['participantIdentities']
                                if p['player']['accountId'] == account_id), None)
            if participant is None:
                continue
            details = next((p for p in game['participants']
                            if p['participantId'] == participant['participantId']), None)
            if details is None:
                continue
            games_output.append({
                'id': game['gameId'],
                'game_delta': game['gameId'],
                'datetime': game['gameCreationDate'],
                'duration': game['gameDuration'],
                'version': game['gameVersion'],
                'map': game['mapId'],
                'queue_id': game['queueId'],
                'details': details
            })
        deltas_output = []
        for delta in deltas:
            delta['id'] = delta['gameId']
            deltas_output.append(delta)
        return {
            'games': humps.decamelize(games_output),
            'games_count': games_count,
            'game_deltas': humps.decamelize(deltas_output),
        }
    except (KeyError, requests.exceptions.RequestException):
        return None
