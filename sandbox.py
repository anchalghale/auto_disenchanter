from pprint import pprint
from connection.league import LeagueConnection
from connection.riot import RiotConnection
from macro import Macro


riot = RiotConnection()
c = LeagueConnection()
m = Macro(riot, c)
riot.get_connection()
c.get_connection()
m.start_worlds_mission()

# c.get_connection()
# res = c.get('/lol-missions/v1/series')
# pprint(res.json())
