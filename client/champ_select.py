
''' Module for champion select related tasks '''
from connection.league import LeagueConnection


def get_champion_select_data(connection: LeagueConnection):
    ''' Checks if in champ select '''
    res = connection.get('/lol-champ-select/v1/session')
    res_json = res.json()
    if res.status_code == 404:
        return None
    completed_list = []
    for action_list in res_json['actions']:
        for action in action_list:
            completed_list.append(action['completed'])
    if all(completed_list):
        return None
    return res_json


def get_pickable_champs(connection: LeagueConnection):
    ''' Fetches pickable champions '''
    res = connection.get('/lol-champ-select/v1/pickable-champions')
    res_json = res.json()
    return res_json['championIds']
