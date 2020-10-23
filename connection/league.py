''' Moudule for league client communication '''
import json
import os
import time

import lcu_connector_python as lcu
import requests
from league_process import open_league_client
from paths import LEAGUE_CLIENT_PATH

from . import Connection


class LeagueConnectionException(Exception):
    ''' Raised when there is error when connecting to league client '''


class LeagueConnection(Connection):
    ''' Connects to league client and communicates with it '''

    def get_connection(self, settings):
        ''' Parses connection url and port from lockfile '''
        try:
            connection = lcu.connect(os.path.expanduser(LEAGUE_CLIENT_PATH))
        except IndexError:
            raise LeagueConnectionException
        if connection == 'Ensure the client is running and that you supplied the correct path':
            raise LeagueConnectionException
        self.kwargs = {
            'verify': False,
            'auth': ('riot', connection['authorization']),
            'timeout': 30
        }
        self.url = 'https://' + connection['url']
        try:
            res = self.get('/lol-service-status/v1/lcu-status')
            if res.status_code != 200:
                raise LeagueConnectionException
        except (requests.RequestException, KeyError, json.decoder.JSONDecodeError):
            raise LeagueConnectionException

    def get_connection_ft(self, settings):
        ''' Parses connection url and port from lockfile fault tolerant version '''
        start_time = time.time()
        while True:
            time_elapsed = time.time() - start_time
            if time_elapsed > settings.connection_retry_limit:
                raise LeagueConnectionException
            try:
                open_league_client(settings)
                self.get_connection(settings)
                return
            except (LeagueConnectionException, OSError):
                time.sleep(1)
