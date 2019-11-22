''' Main script of the program '''
import logging
import sys
import threading
import tkinter as tk
import pygubu

import urllib3


class Gui:
    ''' Main gui class '''

    def __init__(self, root, title):
        self.root = root
        self.root.title(title)
        self.builder = builder = pygubu.Builder()
        self.builder.add_from_file('main_frame.ui')
        self.main_frame = builder.get_object('main_frame', root)
        self.builder.connect_callbacks(self)
