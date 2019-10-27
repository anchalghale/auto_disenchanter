''' Moudule for league client communication '''
import os

import lcu_connector_python as lcu
import requests

from settings import LEAGUE_CLIENT_PATH

from . import Connection


class LeagueConnectionException(Exception):
    ''' Raised when there is error when connecting to league client '''


class LeagueConnection(Connection):
    ''' Connects to league client and communicates with it '''

    def get_connection(self):
        ''' Parses connection url and port from lockfile '''
        connection = lcu.connect(os.path.expanduser(LEAGUE_CLIENT_PATH))
        if connection == 'Ensure the client is running and that you supplied the correct path':
            raise LeagueConnectionException
        self.kwargs = {
            'verify': False,
            'auth': ('riot', connection['authorization']),
            'timeout': 30
        }
        self.url = 'https://' + connection['url']
        try:
            res = self.get('/lol-loot/v1/player-loot')
            if res.json() == []:
                raise LeagueConnectionException
        except requests.RequestException:
            raise LeagueConnectionException
