''' Macro module for summoner related macros '''
import asyncio
import time

from client.account import get_username
from client.exceptions import AccountChangeNeededException, LogoutNeededException

from utils import naturaldelta


async def check_username_macro(logger, connection, username):
    ''' Checks if the current logged in account is correct '''
    checkpoint_time = time.time()
    logger.log('Getting username...')
    for _ in range(20):
        username_client = await get_username(connection)
        while username_client is None or username_client == '':
            asyncio.sleep(1)
            continue

        if username.lower() != username_client.lower():
            logger.log(
                f'Expected username: {username.lower()}. '
                'Current username: {username_client.lower()}')
            raise AccountChangeNeededException
        break
    else:
        raise LogoutNeededException
    logger.log('Got username, took {}'.format(naturaldelta(time.time() - checkpoint_time)))
