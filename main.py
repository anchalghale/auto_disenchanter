''' Main script of the program '''
import logging
import threading
import tkinter as tk
import time

import urllib3

from connection.league import LeagueConnection
from connection.riot import RiotConnection, RiotConnectionException
from file import export_csv, import_csv
from macro import Macro
from macro.process import open_riot_client
from macro.exceptions import (AuthenticationFailureException,
                              ConsentRequiredException)
from process import kill_process
from settings import LEAGUE_CLIENT_PROCESS, RIOT_CLIENT_PROCESS
from gui import Gui

logging.getLogger().setLevel(logging.INFO)
urllib3.disable_warnings()

OPTIONS = [
    'open_chests',
    'redeem_free',
    'redeem_450',
    'redeem_1350',
    'redeem_3150',
    'redeem_4800',
    'redeem_6300',
    'disenchant',
    'buy_450',
    'buy_1350',
    'buy_3150',
    'buy_4800',
    'buy_6300',
    'change_icon'
]


class Application(Gui):
    ''' Main gui class '''

    def __init__(self, master):
        Gui.__init__(self, master, 'Auto Disenchanter')
        self.accounts = []

        self.init_checkboxes(OPTIONS)
        self.macro = Macro(RiotConnection(), LeagueConnection())

    def get_options(self):
        ''' Returns a list of options from checkboxes '''
        options = []
        for option in OPTIONS:
            if self.builder.get_object(option).instate(['selected']):
                options.append(option)
        return options

    def init_processes(self):
        ''' Closes running leauge processes and initilaizes new ones '''
        kill_process(LEAGUE_CLIENT_PROCESS)
        kill_process(RIOT_CLIENT_PROCESS)
        open_riot_client()
        while True:
            try:
                self.macro.riot_connection.get_connection()
                return
            except RiotConnectionException:
                time.sleep(1)

    def start(self):
        ''' Starts the macro thread '''
        if self.accounts == []:
            logging.error('No accounts imported')
            return
        thread = threading.Thread(target=self.start_macro)
        thread.daemon = True
        thread.start()

    def start_macro(self):
        ''' Starts the main batch process '''
        options = self.get_options()
        self.builder.get_object('start')['state'] = 'disabled'

        for idx, account in enumerate(self.accounts):
            tree = self.builder.get_object('accounts')
            child_id = tree.get_children()[idx]
            tree.focus(child_id)
            tree.selection_set(child_id)
            self.init_processes()
            try:
                response = self.macro.do_macro(options, *account)
                self.set_cell('accounts', idx, 3, response['blue_essence'])
                self.set_cell('accounts', idx, 4, response['owned_champions_count'])
            except AuthenticationFailureException:
                logging.info('Account %s has invalid credentials', account[0])
            except ConsentRequiredException:
                logging.info('Account %s needs consent', account[0])
            progress = (idx + 1) * 100 // len(self.accounts)
            self.builder.get_object('progress')['value'] = progress
        kill_process(LEAGUE_CLIENT_PROCESS)
        kill_process(RIOT_CLIENT_PROCESS)
        self.builder.get_object('start')['state'] = 'normal'

    def import_csv(self):
        ''' Called when import button is pressed '''
        self.accounts = import_csv()
        self.set_treeview('accounts', self.accounts)

    def export_csv(self):
        ''' Called when export button is pressed '''
        if export_csv(self.accounts):
            logging.info('Successfully exported')


def main():
    ''' Main function of the script '''
    root = tk.Tk()
    Application(root)
    root.mainloop()


if __name__ == '__main__':
    main()
