''' Module for lobby related tasks '''
from connection.league import LeagueConnection


def get_queue_id(connection: LeagueConnection):
    ''' Returns the current queue id if exists else returns -1 '''
    res = connection.get('/lol-lobby/v2/lobby')
    res_json = res.json()
    if res.status_code == 404:
        return -1
    return res_json["gameConfig"]["queueId"]


def create_lobby(connection: LeagueConnection, queue_id):
    ''' Creates a lobby with the queue id given '''
    data = {"queueId": queue_id}
    res = connection.post("/lol-lobby/v2/lobby", json=data)
    res = res.json()
    if 'errorCode' in res:
        return res['message']
    return None


def delete_lobby(connection: LeagueConnection):
    ''' Deletes the current lobby '''
    connection.delete("/lol-lobby/v2/lobby")
