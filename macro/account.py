''' Macro module for account related macros '''
import asyncio
import time

from client.account import login, check_session
from client.summoner import set_summoner_name
from utils import naturaldelta


def login_macro(logger, connection, account):
    ''' Logs in to the client '''
    checkpoint_time = time.time()
    logger.log('Logging in...')
    login(connection, account.username, account.password,
          account.region, account.locale)
    logger.log('Logged in, took {}'.format(
        naturaldelta(time.time() - checkpoint_time)))


def get_riot_connection_macro(logger, connection, settings):
    ''' Parses connection url and port from lockfile of riot client '''
    checkpoint_time = time.time()
    logger.log('Getting riot client connection')
    connection.get_connection_ft(settings)
    logger.log('Riot client connection established, took {}'.format(
        naturaldelta(time.time() - checkpoint_time)))


def get_league_connection_macro(logger, connection, settings):
    ''' Parses connection url and port from lockfile of leagu client '''
    checkpoint_time = time.time()
    logger.log('Getting league client connection')
    connection.get_connection_ft(settings)
    logger.log('League client connection established, took {}'.format(
        naturaldelta(time.time() - checkpoint_time)))


async def check_session_macro(logger, connection, account):
    ''' Checks the session of an account '''
    checkpoint_time = time.time()
    logger.log('Checking session')
    while True:
        session = await check_session(connection)
        if session == 'succeed':
            break
        if session == 'new_player':
            set_summoner_name(logger, connection, account.username)
        await asyncio.sleep(1)
    logger.log('Session checking finished, took {}'.format(
        naturaldelta(time.time() - checkpoint_time)))
