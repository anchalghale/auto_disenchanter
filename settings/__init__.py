''' Configuration file for the program '''
import time
import json

from types import SimpleNamespace
from urllib.parse import urljoin

import requests

from server import SERVER_URL, SERVER_AUTH
from utils import get_base_dir


BASE_DIR = get_base_dir()


def get_settings(logger, debug=False):
    ''' Parses the settings locally or from the server according to the debug value '''
    if debug:
        with open('settings.json') as file:
            settings_ = json.load(file)
    else:
        while True:
            try:
                logger.log('Parsing settings from the server')
                settings_ = requests.get(urljoin(SERVER_URL, 'api/v1/settings/'),
                                         auth=SERVER_AUTH, timeout=30).json()
                break
            except requests.exceptions.RequestException:
                time.sleep(10)

    return SimpleNamespace(**settings_)
