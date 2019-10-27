''' Module for account related macros '''
import logging

from process import kill_process
from settings import LEAGUE_CLIENT_PROCESS, REGION, LOCALE

from .exceptions import (AccountBannedException,
                         AuthenticationFailureException, BadUsernameException,
                         ConsentRequiredException, RateLimitedException)


def check_session(connection):
    ''' Checks the session of an account '''
    res = connection.get('/lol-login/v1/session')
    res_json = res.json()
    if 'isNewPlayer' not in res_json:
        return 'succeed'
    if res_json['isNewPlayer']:
        return 'new_player'
    if res_json['state'] == 'ERROR':
        if res_json['error']['messageId'] == 'ACCOUNT_BANNED':
            raise AccountBannedException
    return 'succeed'


def check_riot_session(connection):
    ''' Checks session of riot client '''
    res = connection.get('/rso-auth/v1/authorization')
    if res.status_code == 404:
        return 'no_authorization'
    res = connection.get('/eula/v1/agreement')
    res_json = res.json()
    if res_json['acceptance'] != 'Accepted':
        return 'agreement_not_accepted'
    return 'success'


def accept_agreement(connection):
    ''' Accepts the agreemnt '''
    logging.info('Accepting the agreement')
    connection.put('/eula/v1/agreement/acceptance')


def logout(riot_connection, league_connection):
    ''' Logs out from the client '''
    logging.info('Logging out')
    league_connection.delete('/lol-rso-auth/v1/session')
    res = riot_connection.get('/rso-auth/v1/authorization')
    if res.status_code == 404:
        kill_process(LEAGUE_CLIENT_PROCESS)


def login(connection, username, password):
    ''' Logs in to the client '''
    while check_riot_session(connection) != 'success':
        logging.info('Logging in, Username: %s, Password: %s', username, password)
        connection.put('/riotclient/region-locale',
                       json={'region': REGION, 'locale': LOCALE, })
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


def set_summoner_name(connection, name):
    ''' Sets the summoner name if available '''
    for _ in range(10):
        res = connection.get('/lol-summoner/v1/check-name-availability-new-summoners/{}'.format(name))
        if res.json():
            data = {
                'name': name,
            }

            logging.info('Setting summoner name')
            connection.post('/lol-summoner/v1/summoners', json=data)
            connection.post('/lol-login/v1/new-player-flow-completed')
            return
    raise BadUsernameException


def get_owned_champions_count(connection):
    ''' Parses number of champions owned '''
    res = connection.get('/lol-champions/v1/owned-champions-minimal')
    if res.status_code == 404:
        return -1
    res_json = res.json()
    if res_json == []:
        return -1
    filtered = list(
        filter(lambda m: m["ownership"]["owned"], res_json))
    return len(filtered)


def get_be(connection):
    ''' Parses the blue essence value '''
    logging.info("Checking blue essence")
    res = connection.get('/lol-store/v1/wallet')
    res_json = res.json()
    return res_json['ip']
