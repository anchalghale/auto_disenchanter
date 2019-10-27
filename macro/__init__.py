''' Module that finds the client state and does macros '''
import logging
import os
import time

import lcu_connector_python as lcu
import requests
import urllib3

from connection.league import LeagueConnectionException
from connection.riot import RiotConnectionException
from process import is_running
from settings import (
    LEAGUE_CLIENT_PATH, LEAGUE_CLIENT_PROCESS, RIOT_CLIENT_PROCESS,
    RIOT_CLIENT_SERVICES_PATH, SUMMONER_ICON_ID
)

from .loot import redeem, redeem_free, open_champion_capsules, disenchant
from .store import buy_champ_by_be
from .summoner import change_icon
from .chest import forge_keys_and_open_generic_chests, forge_worlds_token
from .process import open_league_client, open_riot_client
from .account import (
    accept_agreement, check_riot_session, check_session, login, logout,
    set_summoner_name, get_be, get_owned_champions_count)
from .exceptions import (
    AccountBannedException, AuthenticationFailureException,
    BadUsernameException, ConsentRequiredException, RateLimitedException)


def handle_not_implemented():
    ''' Called when a feature is not implemented '''
    logging.error('Feature is not implemented')


class Macro:
    ''' Class for finding the state and doing macros '''

    def __init__(self, riot_connection, league_connection):
        self.riot_connection = riot_connection
        self.league_connection = league_connection

        self.state = None

    def get_league_connection(self):
        ''' Parses the league connection from lockfile '''
        while True:
            try:
                self.league_connection.get_connection()
                return
            except LeagueConnectionException:
                time.sleep(1)

    def do_macro(self, options, username, password):
        ''' Calls the macro fucntion according to state '''

        login(self.riot_connection, username, password)
        logging.info('Login successful')
        logging.info('Waiting for league client to come online')
        self.get_league_connection()
        handlers = {
            'open_champion_capsules': (open_champion_capsules, [self.league_connection], {}),
            'open_generic_chests': (forge_keys_and_open_generic_chests, [self.league_connection], {}),
            'forge_worlds_token': (forge_worlds_token, [self.league_connection], {}),
            'redeem_free': (redeem_free, [self.league_connection], {}),
            'redeem_450': (redeem, [self.league_connection, 450], {}),
            'redeem_1350': (redeem, [self.league_connection, 1350], {}),
            'redeem_3150': (redeem, [self.league_connection, 3150], {}),
            'redeem_4800': (redeem, [self.league_connection, 4800], {}),
            'redeem_6300': (redeem, [self.league_connection, 6300], {}),
            'disenchant': (disenchant, [self.league_connection], {}),
            'buy_450': (buy_champ_by_be, [self.league_connection, 450], {}),
            'buy_1350': (buy_champ_by_be, [self.league_connection, 1350], {}),
            'buy_3150': (buy_champ_by_be, [self.league_connection, 3150], {}),
            'buy_4800': (buy_champ_by_be, [self.league_connection, 4800], {}),
            'buy_6300': (buy_champ_by_be, [self.league_connection, 6300], {}),
            'change_icon': (change_icon, [self.league_connection, SUMMONER_ICON_ID], {}),
        }

        for option in options:
            if option not in handlers:
                handle_not_implemented()
                continue
            func = handlers[option]
            func[0](*func[1], *func[2])

        return {
            'blue_essence': get_be(self.league_connection),
            'owned_champions_count': get_owned_champions_count(self.league_connection),
        }
