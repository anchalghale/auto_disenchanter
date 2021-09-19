''' Module that finds the client state and does macros '''
import asyncio
import logging
import os
import time

import lcu_connector_python as lcu
import requests
import urllib3

from client.chest import forge_all_tokens
from client.chest import forge_keys_and_open_generic_chests
from client.chest import forge_keys_and_open_masterwork_chests
from client.exceptions import AccountChangeNeededException
from client.exceptions import LogoutNeededException
from client.exceptions import LootRetrieveException
from client.exceptions import NoSessionException
from client.loot import disenchant
from client.loot import open_champion_capsules
from client.loot import redeem
from client.loot import redeem_free
from client.loot import redeem_waterloo
from client.summoner import change_icon
from client.summoner import get_blue_essence
from connection.league import LeagueConnection
from connection.league import LeagueConnectionException
from connection.riot import RiotConnection
from connection.riot import RiotConnectionException
from league_process import kill_league_client
from league_process import kill_riot_client
from logger import Logger
from process import is_running
from utils import naturaldelta

from .account import check_session_macro
from .account import get_league_connection_macro
from .account import get_riot_connection_macro
from .account import login_macro
from .store import buy_champ_by_be
from .summoner import check_username_macro


def handle_not_implemented():
    ''' Called when a feature is not implemented '''
    logging.error('Feature is not implemented')


class Macro:
    ''' Class for finding the state and doing macros '''

    def __init__(self, logger, settings):
        self.settings = settings
        self.logger = logger
        self.riot_connection = RiotConnection()
        self.league_connection = LeagueConnection()

        self.state = None

    async def handle_disenchant_tasks(self, options):
        ''' Handles disenchanting tasks '''
        state = [self.logger, self.league_connection]
        handlers = {
            'open_champion_capsules': (open_champion_capsules, state, {}),
            'open_generic_chests': (forge_keys_and_open_generic_chests, state, {}),
            'open_masterwork_chests': (forge_keys_and_open_masterwork_chests, state, {}),
            'forge_tokens': (forge_all_tokens, state, {}),
            'redeem_free': (redeem_free, state, {}),
            'redeem_450': (redeem, [*state, 450], {}),
            'redeem_1350': (redeem, [*state, 1350], {}),
            'redeem_3150': (redeem, [*state, 3150], {}),
            'redeem_4800': (redeem, [*state, 4800], {}),
            'redeem_6300': (redeem, [*state, 6300], {}),
            'redeem_waterloo': (redeem_waterloo, [*state], {}),
            'disenchant': (disenchant, state, {}),
            'buy_450': (buy_champ_by_be, [*state, 450], {}),
            'buy_1350': (buy_champ_by_be, [*state, 1350], {}),
            'buy_3150': (buy_champ_by_be, [*state, 3150], {}),
            'buy_4800': (buy_champ_by_be, [*state, 4800], {}),
            'buy_6300': (buy_champ_by_be, [*state, 6300], {}),
            'change_icon': (change_icon, [*state, self.settings.summoner_icon_id], {}),
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
                get_riot_connection_macro(
                    self.logger, self.riot_connection, self.settings)
                login_macro(self.logger, self.riot_connection, account)
                get_league_connection_macro(
                    self.logger, self.league_connection, self.settings)
                await check_session_macro(self.logger, self.league_connection, account)
                await check_username_macro(self.logger, self.league_connection, account.username)
                total_time = time.time() - start_time
                self.logger.log('Total time taken to login: {}'.format(
                    naturaldelta(total_time)))
                self.logger.write_line('console', '-'*75)

                output = await self.handle_disenchant_tasks(options)

                self.logger.log('Logging out')
                kill_league_client(self.settings)
                kill_riot_client(self.settings)
                return output
            except (AccountChangeNeededException, LootRetrieveException, LogoutNeededException):
                self.logger.log('Logging out')
                kill_league_client(self.settings)
                kill_riot_client(self.settings)
                await asyncio.sleep(5)
            except LeagueConnectionException:
                self.logger.log('League client connection failed')
                kill_league_client(self.settings)
            except NoSessionException:
                self.logger.log(
                    'No session was found. Restarting the client...')
                kill_league_client(self.settings)
            except RiotConnectionException:
                self.logger.log('Riot client connection failed')
                kill_riot_client(self.settings)
            except requests.exceptions.RequestException as exp:
                self.logger.log(str(exp))
            finally:
                self.logger.write_line('console', '-'*75)
