''' Module that finds the client state and does macros '''
import asyncio
import logging
import os
import time

import lcu_connector_python as lcu
import requests
import urllib3

from gui.logger import Logger

from connection.league import LeagueConnection, LeagueConnectionException
from connection.riot import RiotConnection, RiotConnectionException
from process import is_running
from utils import naturaldelta

from league_process import kill_league_client, kill_riot_client
from client.exceptions import AccountChangeNeededException, LogoutNeededException, NoSessionException
from client.summoner import change_icon
from client.loot import open_champion_capsules, redeem, redeem_free, disenchant
from client.chest import forge_keys_and_open_generic_chests, forge_worlds_token
from client.summoner import get_blue_essence

from .account import (login_macro, get_riot_connection_macro, get_league_connection_macro,
                      check_session_macro, patch_data_macro)
from .summoner import check_username_macro
from .store import buy_champ_by_be


def handle_not_implemented():
    ''' Called when a feature is not implemented '''
    logging.error('Feature is not implemented')


class Macro:
    ''' Class for finding the state and doing macros '''

    def __init__(self, logger, settings):
        self.settings = settings
        self.logger = logger
        self.riot_connection = RiotConnection(self.settings)
        self.league_connection = LeagueConnection(self.settings)

        self.state = None

    async def handle_disenchant_tasks(self, options):
        ''' Handles disenchanting tasks '''
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
            'buy_450': (buy_champ_by_be, [self.logger, self.league_connection, 450], {}),
            'buy_1350': (buy_champ_by_be, [self.logger, self.league_connection, 1350], {}),
            'buy_3150': (buy_champ_by_be, [self.logger, self.league_connection, 3150], {}),
            'buy_4800': (buy_champ_by_be, [self.logger, self.league_connection, 4800], {}),
            'buy_6300': (buy_champ_by_be, [self.logger, self.league_connection, 6300], {}),
            'change_icon': (change_icon, [self.league_connection, self.settings.summoner_icon_id], {}),
        }

        for option in options:
            if option not in handlers:
                handle_not_implemented()
                continue
            func = handlers[option]
            func[0](*func[1], *func[2])

        return {
            'blue_essence': await get_blue_essence(self.league_connection),
        }

    async def do_macro(self, options, account):
        ''' Calls the macro fucntion according to state '''
        while True:
            try:
                start_time = time.time()
                get_riot_connection_macro(self.logger, self.riot_connection, self.settings)
                login_macro(self.logger, self.riot_connection, account)
                get_league_connection_macro(self.logger, self.league_connection, self.settings)
                await check_session_macro(self.logger, self.league_connection, account)
                await check_username_macro(self.logger, self.league_connection, account.username)
                total_time = time.time() - start_time
                self.logger.log('Total time taken to login: {}'.format(naturaldelta(total_time)))
                self.logger.write_line('console', '-'*75)

                output = await self.handle_disenchant_tasks(options)

                self.logger.log('Logging out')
                kill_league_client(self.settings)
                kill_riot_client(self.settings)
                return output
            except (AccountChangeNeededException, LogoutNeededException):
                self.logger.log('Logging out')
                kill_league_client(self.settings)
                kill_riot_client(self.settings)
                await asyncio.sleep(5)
            except LeagueConnectionException:
                self.logger.log('League client connection failed')
                kill_league_client(self.settings)
            except NoSessionException:
                self.logger.log('No session was found. Restarting the client...')
                kill_league_client(self.settings)
            except RiotConnectionException:
                self.logger.log('Riot client connection failed')
                kill_riot_client(self.settings)
            except requests.exceptions.RequestException as exp:
                self.logger.log(str(exp))
            finally:
                self.logger.write_line('console', '-'*75)
