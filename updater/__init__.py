''' Module that does updating related tasks '''
import os
import sys
import time
from subprocess import CalledProcessError, check_output, run

from gui.logger import Logger


def is_out_of_date(cwd):
    ''' Checks if the git version is out of date '''
    local = check_output('git fetch', shell=True, cwd=cwd)
    local = check_output('git rev-parse HEAD', shell=True, cwd=cwd)
    remote = check_output('git rev-parse @{u}', shell=True, cwd=cwd)
    if local != remote:
        return True
    return False


def update(logger: Logger):
    ''' Checks for updates and updates if out of date '''
    logger.log('Checking for updates...')
    try:
        updated = False
        if is_out_of_date(None):
            logger.log('Updating...')
            run('git pull', shell=True, check=True)
            updated = True
        if updated:
            logger.log('Successfully updated. Now, restarting.')
            time.sleep(5)
            os.execl(sys.executable, sys.executable, *sys.argv)
    except CalledProcessError:
        logger.log('Updating failed.')
