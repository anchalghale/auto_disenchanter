''' Module for gameflow related tasks '''
import requests

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
        game = match_list['games']['games'][-1]
        participant = next((p for p in game['participantIdentities']
                            if p['player']['accountId'] == account_id), None)
        stats = next((p for p in game['participants']
                      if p['participantId'] == participant['participantId']), None)['stats']
        deltas = next(filter(lambda d: d['gameId'] == game['gameId'], deltas), None)
        return {
            'id': game['gameId'],
            'datetime': game['gameCreationDate'],
            'duration': game['gameDuration'],
            'queue_id': game['queueId'],
            'kills': stats['kills'],
            'deaths': stats['deaths'],
            'assists': stats['assists'],
            'wards_killed': stats['wardsKilled'],
            'exp': deltas['platformDelta']['xpDelta'],
        }
    except (KeyError, TypeError, requests.exceptions.RequestException):
        return None
