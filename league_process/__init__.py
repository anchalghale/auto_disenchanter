''' Module for handling processes '''
import subprocess
import time

from paths import get_league_client_path
from paths import get_riot_client_path
from process import is_running
from process import kill_process


def open_riot_client(settings):
    ''' Starts riot client process '''
    while not is_running(settings.riot_client_process):
        subprocess.Popen([
            get_riot_client_path(),
            # "--headless",
            "--launch-product=league_of_legends",
            "--launch-patchline=live"])
        time.sleep(1)


def open_league_client(settings):
    ''' Starts league client process '''
    while not is_running(settings.league_client_process):
        try:
            subprocess.Popen([get_league_client_path(), "--headless"])
        except PermissionError:
            pass
        finally:
            time.sleep(1)


def kill_league_client(settings):
    ''' Kills the league client '''
    kill_process(settings.league_client_process)
    kill_process(settings.league_client_ux_process)
    kill_process(settings.league_client_ux_render_process)


def kill_riot_client(settings):
    ''' Kills the riot client '''
    kill_process(settings.riot_client_process)
    kill_process(settings.riot_client_crash_handler_process)
    kill_process(settings.riot_client_ux_process)
    kill_process(settings.riot_client_ux_render_process)


def kill_game(settings):
    ''' Kills the game '''
    kill_process(settings.game_process)
