''' Module that stores the paths '''
import os

RIOT_CLIENT_SERVICES_PATHS = ['C:/Riot Games/Riot Client/RiotClientServices.exe',
                              'D:/Riot Games/Riot Client/RiotClientServices.exe',
                              'E:/Riot Games/Riot Client/RiotClientServices.exe']


LEAGUE_CLIENT_PATHS = ['C:/Riot Games/League of Legends/LeagueClient.exe',
                       'D:/Riot Games/League of Legends/LeagueClient.exe',
                       'E:/Riot Games/League of Legends/LeagueClient.exe']


def get_path(paths):
    ''' Returns the first exisiting path of a list or None '''
    for path in paths:
        if os.path.exists(path):
            return path
    return None


RIOT_CLIENT_SERVICES_PATH = get_path(RIOT_CLIENT_SERVICES_PATHS)
LEAGUE_CLIENT_PATH = get_path(LEAGUE_CLIENT_PATHS)
