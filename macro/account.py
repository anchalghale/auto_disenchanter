''' Macro module for account related macros '''
import asyncio
import time

from client.account import login, check_session
from client.summoner import set_summoner_name
from client.exceptions import AccountChangeNeededException

from utils import naturaldelta, epoch_time_to_iso


def login_macro(logger, connection, account):
    ''' Logs in to the client '''
    checkpoint_time = time.time()
    logger.log('Logging in')
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
            set_summoner_name(connection, account.username)
        await asyncio.sleep(1)
    logger.log('Session checking finished, took {}'.format(
        naturaldelta(time.time() - checkpoint_time)))


def patch_data_macro(logger, worker, blue_essence, summoner_data, missions):
    ''' Patches the namespace account object '''
    checkpoint_time = time.time()
    logger.log('Patching account data to the server')
    patch_data = {
        'blue_essence': blue_essence,
        'level': summoner_data[0]+summoner_data[1]/100,
    }
    for reward, value in NPE_REWARDS.items():
        if reward in missions:
            patch_data[value['database_name']] = missions[reward]['status']
    if 'fwotd_mission' in missions:
        completed_date = missions['fwotd_mission']['completed_date']
        if completed_date not in [-1, 0]:
            fwotd_available_at = epoch_time_to_iso(completed_date/1000 + 72000)  # adds 20 hours
            patch_data['fwotd_available_at'] = fwotd_available_at
    completed_date = 0
    if 'npe_rewards_login_v1_step1' in missions:
        npe_rewards = [missions[mission]['status'] == 'COMPLETED' for mission in NPE_REWARDS]
        if npe_rewards[0]:
            if npe_rewards[1]:
                completed_date = missions['npe_rewards_login_v1_step2']['completed_date']
            completed_date = missions['npe_rewards_login_v1_step1']['completed_date']
    if completed_date not in [-1, 0]:
        daily_reward_available_at = epoch_time_to_iso(completed_date/1000 + 64800)  # adds 18 hours
        patch_data['daily_reward_available_at'] = daily_reward_available_at

    old_id = worker.account.id
    worker.patch_data(**patch_data)
    logger.log('Patching colmpleted, took {}'.format(
        naturaldelta(time.time() - checkpoint_time)))

    if old_id != worker.account.id:
        logger.log(f'Server requested an account change.')
        raise AccountChangeNeededException
