''' Module that does updating related tasks '''
import os
import sys
import time
from subprocess import CalledProcessError, TimeoutExpired, check_output, run

from gui.logger import Logger


def is_out_of_date(cwd):
    ''' Checks if the git version is out of date '''
    local = check_output('git fetch', shell=True, cwd=cwd, timeout=30)
    local = check_output('git rev-parse HEAD', shell=True, cwd=cwd, timeout=30)
    remote = check_output('git rev-parse @{u}', shell=True, cwd=cwd, timeout=30)
    if local != remote:
        return True
    return False


def update(logger: Logger, disable_logging=False):
    ''' Checks for updates and updates if out of date '''
    if not disable_logging:
        logger.log('Checking for updates...')
    try:
        updated = False
        if is_out_of_date(None):
            logger.log('Updating...')
            run('git pull', shell=True, check=True, timeout=30)
            updated = True
        if updated:
            logger.log('Successfully updated. Now, restarting.')
            time.sleep(5)
            os.execl(sys.executable, sys.executable, *sys.argv)
    except (CalledProcessError, TimeoutExpired):
        logger.log('Updating failed.')
