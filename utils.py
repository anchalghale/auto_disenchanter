''' Utility module of the program '''
import os
import sys
import time

import humanize


def naturaldelta(delta):
    ''' Wrapper around humanize naturaldelta. Supports only floating values '''
    if delta < 1:
        return f'{int(delta*1000)} milliseconds'
    return humanize.naturaldelta(delta)


def epoch_time_to_iso(epoch_time):
    ''' Converts epoch time to iso time '''
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(epoch_time))


def get_base_dir():
    ''' Returns the base dir to use for the program '''
    if hasattr(sys, "_MEIPASS"):
        meipass = sys._MEIPASS  # pylint:disable=no-member, protected-access
        os.chdir(meipass)
        return meipass
    return os.getcwd()
