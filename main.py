''' Main script of the program '''
import asyncio
import logging
import threading
import tkinter as tk
import types
import subprocess

import urllib3
import pygubu

from file import export_csv, import_csv
from file.pickle import save_state, load_state, create_directories
from macro import Macro
from updater import update
from incidents import Incidents
from client.exceptions import AuthenticationFailureException, ConsentRequiredException
from settings import get_settings
from builder import Builder
from logger import TkinterLogger
from region import REGION, LOCALE

logging.getLogger().setLevel(logging.INFO)
urllib3.disable_warnings()

OPTIONS = [
    'open_generic_chests',
    'forge_tokens',
    'open_champion_capsules',
    'redeem_free',
    'redeem_450',
    'redeem_1350',
    'redeem_3150',
    'redeem_4800',
    'redeem_6300',
    'redeem_waterloo',
    'disenchant',
    'buy_450',
    'buy_1350',
    'buy_3150',
    'buy_4800',
    'buy_6300',
    'change_icon'
]


class Application:
    ''' Main gui class '''

    def __init__(self, root):
        version = subprocess.check_output('git rev-list --count HEAD').decode('utf-8')
        root.title(f'Auto Disenchanter v{version}')
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.builder = builder = pygubu.Builder()
        builder.add_from_file('main_frame.ui')
        builder.get_object('main_frame', root)
        builder.connect_callbacks(self)

        self.builder_wrapper = Builder(builder)
        self.root = root

        self.logger = TkinterLogger(self.builder, '%H:%M:%S')
        self.settings = get_settings(self.logger, debug=True)
        self.logger.log_format = self.settings.log_time_format
        self.macro = Macro(self.logger, self.settings)

        self.incidents = Incidents(self.logger, self.settings)
        self.incidents.start_thread()

        root.resizable(False, False)
        root.wm_attributes("-topmost", 1)

        state = load_state()
        if state is not None and 'options' in state:
            self.builder_wrapper.init_checkboxes(state['options'])
        else:
            self.builder_wrapper.init_checkboxes(dict.fromkeys(OPTIONS, False))
        if state is not None and 'accounts' in state:
            self.accounts = state['accounts']
            self.builder_wrapper.set_treeview('accounts', self.accounts)
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
                        region=REGION, locale=LOCALE)
                    response = await self.macro.do_macro(options, account_)
                    self.builder_wrapper.set_cell('accounts', idx, 3, response['blue_essence'])
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
            self.builder_wrapper.set_treeview('accounts', self.accounts)

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
