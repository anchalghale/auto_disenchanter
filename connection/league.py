''' Moudule for league client communication '''
import os
import time
import logging
import json

import lcu_connector_python as lcu
import requests

from league_process import open_league_client

from . import Connection


class LeagueConnectionException(Exception):
    ''' Raised when there is error when connecting to league client '''


class LeagueConnection(Connection):
    ''' Connects to league client and communicates with it '''

    def get_connection(self):
        ''' Parses connection url and port from lockfile '''
        connection = lcu.connect(os.path.expanduser(self.settings.league_client_path))
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
            if res.json()['status'] != 'online':
                logging.info('LCU is not online')
                raise LeagueConnectionException
        except (requests.RequestException, KeyError, json.decoder.JSONDecodeError):
            raise LeagueConnectionException

    def get_connection_ft(self, settings):
        ''' Parses connection url and port from lockfile fault tolerant version '''
        for _ in range(self.settings.connection_retry_count):
            try:
                open_league_client(settings)
                self.get_connection()
                return
            except (LeagueConnectionException, OSError):
                time.sleep(1)
        raise LeagueConnectionException
