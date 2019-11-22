''' Main script of the program '''
import asyncio
import logging
import threading
import tkinter as tk
import types
import subprocess

import urllib3

from file import export_csv, import_csv
from file.pickle import save_state, load_state, create_directories
from macro import Macro
from updater import update
from incidents import Incidents
from client.exceptions import AuthenticationFailureException, ConsentRequiredException
from settings_local import get_settings
from gui import Gui
from gui.logger import Logger

logging.getLogger().setLevel(logging.INFO)
urllib3.disable_warnings()

OPTIONS = [
    'open_generic_chests',
    'forge_worlds_token',
    'open_champion_capsules',
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

    def __init__(self, root):
        version = subprocess.check_output('git rev-list --count HEAD').decode('utf-8')
        Gui.__init__(self, root, f'Auto Disenchanter v{version}')

        self.settings = get_settings()
        self.logger = Logger(self.builder, self.settings.log_time_format)
        self.macro = Macro(self.logger, self.settings)

        self.incidents = Incidents(self.logger, self.settings)
        self.incidents.start_thread()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        state = load_state()
        if state is not None and 'options' in state:
            self.logger.init_checkboxes(state['options'])
        else:
            self.logger.init_checkboxes(dict.fromkeys(OPTIONS, False))
        if state is not None and 'accounts' in state:
            self.accounts = state['accounts']
            self.logger.set_treeview('accounts', self.accounts)
        else:
            self.accounts = []

    def on_closing(self):
        ''' Callback for on closing event '''
        save_state({
            'options': self.get_options(),
            'accounts': self.accounts,
        })
        self.root.destroy()

    def get_options(self):
        ''' Returns a list of options and it's state '''
        options = {}
        for option in OPTIONS:
            if self.builder.get_object(option).instate(['selected']):
                options[option] = True
            else:
                options[option] = False
        return options

    def get_selected_options(self):
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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        thread = threading.Thread(target=loop.run_until_complete, args=[self.start_macro()])
        thread.daemon = True
        thread.start()

    async def start_macro(self):
        ''' Starts the main batch process '''
        options = self.get_selected_options()
        self.builder.get_object('start')['state'] = 'disabled'
        save_state({
            'options': self.get_options(),
            'accounts': self.accounts,
        })
        update(self.logger)

        for idx, account in enumerate(self.accounts):
            if len(account) == 2:
                tree = self.builder.get_object('accounts')
                child_id = tree.get_children()[idx]
                tree.focus(child_id)
                tree.selection_set(child_id)
                try:
                    account_ = types.SimpleNamespace(
                        username=account[0], password=account[1],
                        region=self.settings.region, locale=self.settings.locale)
                    response = await self.macro.do_macro(options, account_)
                    self.logger.set_cell('accounts', idx, 3, response['blue_essence'])
                    self.accounts[idx].append(response['blue_essence'])
                except AuthenticationFailureException:
                    logging.info('Account %s has invalid credentials', account[0])
                except ConsentRequiredException:
                    logging.info('Account %s needs consent', account[0])
            progress = (idx + 1) * 100 // len(self.accounts)
            self.builder.get_object('progress')['value'] = progress
        self.builder.get_object('start')['state'] = 'normal'

    def import_csv(self):
        ''' Called when import button is pressed '''
        accounts = import_csv()
        if accounts is not None:
            self.accounts = accounts
            self.logger.set_treeview('accounts', self.accounts)

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
    create_directories()
    main()
