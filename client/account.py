''' Module for account related macros '''
import asyncio
import json
import time

import requests
from connection.league import LeagueConnection

from .exceptions import AccountBannedException
from .exceptions import AuthenticationFailureException
from .exceptions import ConsentRequiredException
from .exceptions import LogoutNeededException
from .exceptions import NoSessionException
from .exceptions import RateLimitedException

LOGIN_PHASES = [
    'WaitingForAuthentication',
    'WaitingForEula',
    'Done',
    'Disabled',
    'Login',
    '',
]

WAIT_FOR_LAUNCH_PHASES = [
    'WaitForLaunch',
]

SUCCESS_PHASES = [
    'WaitForSessionExit',
]

EULA_PHASES = [
    'Eula',
]


def check_riot_session(connection):
    ''' Checks session of riot client '''
    res = connection.get('/rso-auth/v1/authorization')
    if res.status_code == 404:
        return 'no_authorization'
    res = connection.get('/eula/v1/agreement')
    res_json = res.json()
    if 'acceptance' not in res_json:
        return 'no_authorization'
    if res_json['acceptance'] != 'Accepted':
        return 'agreement_not_accepted'
    return 'success'


def is_age_restricted(connection):
    '''Checks if riot client age restricted'''
    try:
        response = connection.get('/age-restriction/v1/age-restriction/products/league_of_legends')
        response = response.json()
        return response.get('restricted', False)
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return False


def is_country_region_missing(connection):
    '''Checks if riot client age restricted'''
    try:
        response = connection.get('/riot-client-auth/v1/userinfo')
        response = response.json()
        return response.get('country', 'npl') == 'nan'
    except (json.decoder.JSONDecodeError, requests.exceptions.RequestException):
        return False


def accept_agreement(connection):
    ''' Accepts the agreemnt '''
    connection.put('/eula/v1/agreement/acceptance')


async def check_session(connection: LeagueConnection):
    ''' Checks the session of an account '''
    future = connection.async_get('/lol-login/v1/session')
    await asyncio.sleep(0)
    res = future.result()

    if res.status_code == 404:
        raise NoSessionException

    res_json = res.json()
    if res_json["state"] == "IN_PROGRESS":
        return "in_progress"
    if 'isNewPlayer' not in res_json:
        return 'succeed'
    if res_json['isNewPlayer']:
        return 'new_player'
    if res_json['state'] == 'ERROR':
        if res_json['error']['messageId'] == 'ACCOUNT_BANNED':
            raise AccountBannedException
    return 'succeed'


async def get_username(connection: LeagueConnection):
    ''' Parses the username '''
    future = connection.async_get('/lol-login/v1/login-platform-credentials')
    await asyncio.sleep(0)
    res = future.result()
    res_json = res.json()
    if 'username' not in res_json:
        return None
    return res_json['username']


def wait_until_patched(logger, connection, time_limit=7200):
    ''' Waits for patching to be complete '''
    start_time = time.time()
    while True:
        try:
            time.sleep(10)
            time_elapsed = time.time() - start_time
            logger.log(f'Patching riot client. Time elapsed: {int(time_elapsed)}s.')
            if time_elapsed > time_limit:
                raise LogoutNeededException
            res = connection.get('/rnet-lifecycle/v1/product-context-phase')
            phase = res.json()
            if phase != 'WaitingForPatchStatus':
                break
        except requests.exceptions.RequestException:
            pass


def _login(connection, *args):
    username, password, region, locale = args
    state = check_riot_session(connection)
    if state == 'success':
        if is_age_restricted(connection):
            raise ConsentRequiredException
        if is_country_region_missing(connection):
            raise ConsentRequiredException
        return True
    if state == 'agreement_not_accepted':
        accept_agreement(connection)
        return True
    connection.put('/riotclient/region-locale',
                   json={'region': region, 'locale': locale, })
    res = connection.post(
        '/rso-auth/v2/authorizations',
        json={'clientId': 'riot-client', 'trustLevels': ['always_trusted']})
    data = {'username': username, 'password': password, 'persistLogin': False}
    res = connection.put('/rso-auth/v1/session/credentials', json=data)
    res_json = res.json()
    if 'message' in res_json:
        if res_json['message'] == 'authorization_error: consent_required: ':
            raise ConsentRequiredException
    if 'error' in res_json:
        if res_json['error'] == 'auth_failure':
            raise AuthenticationFailureException
        if res_json['error'] == 'rate_limited':
            raise RateLimitedException
    return False


def _launch_league(connection):
    connection.post('/product-launcher/v1/products/league_of_legends/patchlines/live')


def login(logger, connection, *args, time_limit=180):
    ''' Logs in to the client '''
    start_time = time.time()
    while True:
        if time.time() - start_time >= time_limit:
            raise NoSessionException
        res = connection.get('/rnet-lifecycle/v1/product-context-phase')
        phase = res.json() if res.status_code != 404 else 'Disabled'
        if phase == 'Unknown':
            raise NoSessionException
        if phase == 'WaitingForPatchStatus':
            wait_until_patched(logger, connection)
            continue
        if phase in SUCCESS_PHASES:
            break
        if phase in WAIT_FOR_LAUNCH_PHASES:
            _launch_league(connection)
            continue
        if phase in LOGIN_PHASES:
            if _login(connection, *args):
                break
        if phase in EULA_PHASES:
            accept_agreement(connection)
            time.sleep(2)
            continue
        time.sleep(2)
