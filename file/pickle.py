''' Module to save and load data to file '''
import pickle
import os


def create_directories():
    "Creates necesesary directories"
    os.makedirs('data/', exist_ok=True)


def save_state(state):
    ''' Saves state to a file '''
    file_path = f'data/state.pickle'
    with open(file_path, 'wb') as file:
        pickle.dump(state, file)


def load_state():
    ''' Loads generations data from a file '''
    file_path = f'data/state.pickle'
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
            return data
    except FileNotFoundError:
        return None
