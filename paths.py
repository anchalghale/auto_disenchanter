''' Module that stores the paths '''
import os
from tkinter.filedialog import askopenfilename

RIOT_CLIENT_SERVICES_PATHS = [
    os.path.expanduser('C:/Riot Games/Riot Client/RiotClientServices.exe'),
    os.path.expanduser('D:/Riot Games/Riot Client/RiotClientServices.exe'),
    os.path.expanduser('E:/Riot Games/Riot Client/RiotClientServices.exe'),
]


LEAGUE_CLIENT_PATHS = [
    os.path.expanduser('C:/Riot Games/League of Legends/LeagueClient.exe'),
    os.path.expanduser('D:/Riot Games/League of Legends/LeagueClient.exe'),
    os.path.expanduser('E:/Riot Games/League of Legends/LeagueClient.exe'),
]


def get_path(paths):
    ''' Returns the first exisiting path of a list or None '''
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def get_league_client_path():
    path = get_path(LEAGUE_CLIENT_PATHS)
    if path is None:
        path = askopenfilename(title='LeagueClient.exe')
        if path is not None:
            LEAGUE_CLIENT_PATHS.append(path)
    return path


def get_riot_client_path():
    path = get_path(RIOT_CLIENT_SERVICES_PATHS)
    if path is None:
        path = askopenfilename(title='RiotClientServices.exe')
        if path is not None:
            RIOT_CLIENT_SERVICES_PATHS.append(path)
    return path
