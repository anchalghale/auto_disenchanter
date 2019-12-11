''' Moudule for riot client communication '''
import os
import time

import lcu_connector_python as lcu
import requests

from league_process import open_riot_client

from . import Connection


class RiotConnectionException(Exception):
    ''' Raised when there is error when connecting to riot client '''


class RiotConnection(Connection):
    ''' Connects to riot client and communicates with it '''

    def get_connection(self, settings):
        ''' Parses connection url and port from lockfile '''
        try:
            connection = lcu.connect(os.path.expanduser(settings.riot_client_config))
        except IndexError:
            raise RiotConnectionException
        if connection == 'Ensure the client is running and that you supplied the correct path':
            raise RiotConnectionException
        self.kwargs = {
            'verify': False,
            'auth': ('riot', connection['authorization']),
            'timeout': 30
        }
        self.url = 'https://' + connection['url']
        try:
            self.get('/riotclient/region-locale')
        except requests.RequestException:
            raise RiotConnectionException

    def get_connection_ft(self, settings):
        ''' Parses connection url and port from lockfile fault tolerant version '''
        start_time = time.time()
        while True:
            time_elapsed = time.time() - start_time
            if time_elapsed > settings.connection_retry_limit:
                raise RiotConnectionException
            try:
                open_riot_client(settings)
                self.get_connection(settings)
                return
            except (RiotConnectionException, OSError):
                time.sleep(1)
        raise RiotConnectionException
