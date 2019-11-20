''' Module for process related tasks '''
from connection.league import LeagueConnection


def process_control_quit(connection: LeagueConnection):
    ''' Quits league using proceses contrl '''
    connection.post('/process-control/v1/process/quit')
