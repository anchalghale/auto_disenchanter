''' Moudle for checking incidents and handling thems '''
import time
import threading

from window import get_windows
from league_process import kill_game, kill_league_client
from process import is_running, kill_process
from gui.logger import Logger

GAME_ERROR_TITLES = [
    'Error',
    'Network Warning',
    'System Error',
    'Error de conexión'
    'Bağlantı Hatası',
    'Failed to Connect',
]


LEAGUE_CLIENT_ERROR_TITLES = [
    'Error',
    'LeagueClient.exe - Entry Point Not Found',
    'LeagueClient.exe - Application Error',
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

    def check_incidents(self):
        ''' Checks for incidents and handles it forever '''
        while True:
            window_list = [window.title for window in get_windows()]
            for title in GAME_ERROR_TITLES:
                if title in window_list:
                    self.logger.log(
                        f'Bad window title found: {title}. Killing League of Legends.exe...')
                    self.count += 1
                    self.logger.set_entry('incidents_count', self.count)
                    time.sleep(1)
                    kill_game(self.settings)
            for title in LEAGUE_CLIENT_ERROR_TITLES:
                if title in window_list:
                    self.logger.log(
                        f'Bad window title found: {title}. Killing LeagueClient.exe...')
                    self.count += 1
                    self.logger.set_entry('incidents_count', self.count)
                    time.sleep(1)
                    kill_league_client(self.settings)
            if is_running(self.settings.bug_splat_process):
                self.logger.log(f'BugSplat found, killing {self.settings.bug_splat_process}')
                self.count += 1
                self.logger.set_entry('incidents_count', self.count)
                time.sleep(1)
                kill_process(self.settings.bug_splat_process)
            time.sleep(5)
