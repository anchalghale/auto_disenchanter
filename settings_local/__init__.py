''' Configuration file for the program '''
import json
import types

import requests


def get_settings():
    ''' Parses the settings locally '''
    with open('settings.json') as file:
        settings_ = json.load(file)
    return types.SimpleNamespace(**settings_)
