''' Module for account related macros '''
import time
import asyncio

import requests

from connection.league import LeagueConnection

from .exceptions import (AccountBannedException,
                         AuthenticationFailureException,
                         ConsentRequiredException, RateLimitedException,
                         NoSessionException, LogoutNeededException)


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


def login(logger, connection, *args, time_limit=180):
    ''' Logs in to the client '''
    username, password, region, locale = args
    start_time = time.time()
    while True:
        if time.time() - start_time >= time_limit:
            raise LogoutNeededException
        res = connection.get('/rnet-lifecycle/v1/product-context-phase')
        phase = res.json()
        if phase == 'WaitingForPatchStatus':
            wait_until_patched(logger, connection)
            continue
        if phase not in ['WaitingForAuthentication', 'WaitingForEula', 'Done']:
            logger.log(f'Riot client phase: {phase}.')
            time.sleep(2)
            continue
        state = check_riot_session(connection)
        if state == 'success':
            return
        if state == 'agreement_not_accepted':
            accept_agreement(connection)
            return
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
