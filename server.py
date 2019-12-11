''' Stores the auto league server related data '''
import requests

SERVER_URL = ''
SERVER_USERNAME = ''
SERVER_PASSWORD = ''
SERVER_AUTH = requests.auth.HTTPBasicAuth(SERVER_USERNAME, SERVER_PASSWORD)
