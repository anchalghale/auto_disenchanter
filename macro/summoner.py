''' Module for summoner related tasks '''
import logging
import time

import requests


def change_icon(connection, icon_id):
    ''' Changes the summoner icon '''
    while get_icon(connection) != icon_id:
        json = {
            "profileIconId": icon_id
        }
        try:
            logging.info("Changing summoner icon")
            connection.put('/lol-summoner/v1/current-summoner/icon', json=json)
        except requests.RequestException:
            pass
        time.sleep(1)


def get_icon(connection):
    ''' Parses the current summoner icon '''
    try:
        res = connection.get('/lol-summoner/v1/current-summoner')
        res_json = res.json()
        return res_json["profileIconId"]
    except requests.RequestException:
        return -1
