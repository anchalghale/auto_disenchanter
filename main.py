''' Main script of the program '''
import asyncio
import logging
import threading
import tkinter as tk
import types
import urllib3

from file import export_csv, import_csv
from macro import Macro
from client.exceptions import AuthenticationFailureException, ConsentRequiredException
from settings import get_settings
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

    def __init__(self, master):
        Gui.__init__(self, master, 'Auto Disenchanter')
        self.accounts = []

        self.init_checkboxes(OPTIONS)
        self.settings = get_settings()
        self.logger = Logger(self.builder, self.settings.log_time_format)
        self.macro = Macro(self.logger, self.settings)

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
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        thread = threading.Thread(target=loop.run_until_complete, args=[self.start_macro()])
        thread.daemon = True
        thread.start()

    async def start_macro(self):
        ''' Starts the main batch process '''
        options = self.get_options()
        self.builder.get_object('start')['state'] = 'disabled'

        for idx, account in enumerate(self.accounts):
            tree = self.builder.get_object('accounts')
            child_id = tree.get_children()[idx]
            tree.focus(child_id)
            tree.selection_set(child_id)
            try:
                account_ = types.SimpleNamespace(
                    username=account[0], password=account[1],
                    region=self.settings.region, locale=self.settings.locale)
                response = await self.macro.do_macro(options, account_)
                self.set_cell('accounts', idx, 3, response['blue_essence'])
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
