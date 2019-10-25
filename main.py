''' Main script of the program '''
import logging
import threading
import tkinter as tk

import urllib3

from connection.league import LeagueConnection
from connection.riot import RiotConnection
from file import export_csv, import_csv
from macro import Macro
from macro.exceptions import (AuthenticationFailureException,
                              ConsentRequiredException)
from process import kill_process
from settings import LEAGUE_CLIENT_PROCESS, RIOT_CLIENT_PROCESS
from gui import Gui

logging.getLogger().setLevel(logging.INFO)
urllib3.disable_warnings()

OPTIONS = [
    'open_chests',
]


class Application(Gui):
    ''' Main gui class '''

    def __init__(self, master):
        Gui.__init__(self, master, 'Hello')
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

        kill_process(LEAGUE_CLIENT_PROCESS)
        kill_process(RIOT_CLIENT_PROCESS)
        for idx, account in enumerate(self.accounts):
            tree = self.builder.get_object('accounts')
            child_id = tree.get_children()[idx]
            tree.focus(child_id)
            tree.selection_set(child_id)

            try:
                self.macro.do_macro(options, *account)
            except AuthenticationFailureException:
                logging.info('Account %s has invalid credentials', account[0])
            except ConsentRequiredException:
                logging.info('Account %s needs consent', account[0])
            progress = (idx + 1) * 100 // len(self.accounts)
            self.builder.get_object('progress')['value'] = progress
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
