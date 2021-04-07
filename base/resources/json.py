'''Module for parsing resources'''
import json
import os
from functools import lru_cache

__all__ = [
    'get_json',
    'get_json_by_path',
    'save_json_by_path',
]


@lru_cache()
def get_json_by_path(file_path):
    '''Parses a json'''
    with open(file_path) as file_pointer:
        return json.load(file_pointer)


@lru_cache()
def get_json(label):
    '''Parses a json'''
    with open(os.path.join('assets', 'json', f'{label}.json'), encoding='utf-8') as file_pointer:
        return json.load(file_pointer)


def save_json_by_path(file_path, data):
    '''Saves a json'''
    with open(file_path, 'w') as file_pointer:
        return json.dump(data, file_pointer)
