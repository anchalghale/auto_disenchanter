''' Main script of the program '''
import logging
import sys
import threading
import tkinter as tk

import urllib3


class LogWriter(object):
    ''' Class that writes to the console entry of gui '''

    def __init__(self, app):
        sys.stderr = self
        self.app = app

    def write(self, data):
        ''' Writes to the app console entry '''
        self.app.write_console(data)


class Gui:
    ''' Main gui class '''

    def __init__(self, master, title):
        LogWriter(self)
        import pygubu       # pylint:disable=import-outside-toplevel

        self.master = master
        self.master.title(title)
        self.builder = builder = pygubu.Builder()
        self.builder.add_from_file('main_frame.ui')
        self.mainwindow = builder.get_object('main_frame', master)
        self.builder.connect_callbacks(self)
