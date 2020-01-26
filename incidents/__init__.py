''' Moudle for checking incidents and handling thems '''
import time
import threading

from window import get_windows, close_window_by_title
from league_process import kill_game, kill_league_client
from process import is_running, kill_process
from logger import Logger

GAME_ERROR_TITLES = [
    'Error',
    'Network Warning',
    'System Error',
    'Failed to Connect',
    'Bağlantı Hatası',
    'Error de conexión',
    'Aviso de red',
]


LEAGUE_CLIENT_ERROR_TITLES = [
    'Error',
    'LeagueClient.exe - Entry Point Not Found',
    'Data is corrupt.',
]

CSRSS_ERROR_TITILES = [
    'LeagueClient.exe - System Error',
    'League of Legends.exe - System Error',
    'RiotClientServices.exe - System Error',
    'LeagueClient.exe - Application Error',
    'League of Legends.exe - Application Error',
    'RiotClientServices.exe - Application Error',
]


class Incidents:
    ''' Class that keeps track of incidents '''

    def __init__(self, logger: Logger, settings, count: int = 0):
        self.logger = logger
        self.settings = settings
        self.count = count
        self.set_incidents_count()

    def start_thread(self):
        ''' Starts checking for incidents in a thread '''
        thread = threading.Thread(target=self.check_incidents)
        thread.daemon = True
        thread.start()

    def set_incidents_count(self):
        ''' Sets the incidents count entry in the gui '''
        self.logger.set_entry('incidents_count', self.count)

    def increment_count(self):
        ''' Sets the incidents count by one '''
        self.count += 1
        self.logger.set_entry('incidents_count', self.count)
        time.sleep(1)

    def check_incidents(self):
        ''' Checks for incidents and handles it forever '''
        while True:
            window_list = [window.title for window in get_windows()]
            for title in GAME_ERROR_TITLES:
                if title in window_list:
                    self.logger.log(
                        f'Bad window title found: {title}. Killing League of Legends.exe...')
                    self.increment_count()
                    kill_game(self.settings)
            for title in LEAGUE_CLIENT_ERROR_TITLES:
                if title in window_list:
                    self.logger.log(
                        f'Bad window title found: {title}. Killing LeagueClient.exe...')
                    self.increment_count()
                    kill_league_client(self.settings)
            for title in CSRSS_ERROR_TITILES:
                if title in window_list:
                    self.logger.log(
                        f'Bad window title found: {title}. Closing the {title} window...')
                    self.increment_count()
                    close_window_by_title(title)
            if is_running(self.settings.bug_splat_process):
                self.logger.log(f'BugSplat found, killing {self.settings.bug_splat_process}...')
                self.increment_count()
                kill_process(self.settings.bug_splat_process)
            if is_running('Werfault.exe'):
                self.logger.log(f'Werfault.exe found, killing Werfault.exe...')
                self.increment_count()
                kill_process('Werfault.exe')
            time.sleep(5)
