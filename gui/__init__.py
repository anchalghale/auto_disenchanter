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

    def init_checkboxes(self, options):
        ''' Checks all the checkboxes at the start '''
        for option in options:
            self.init_checkbox(option, True)

    def set_treeview(self, name, values):
        ''' Sets the treeview component '''
        for value in values:
            self.set_row(name, value)

    def clear_treeview(self, name):
        ''' Clears the treeview component '''
        tree = self.builder.get_object(name)
        tree.delete(*tree.get_children())

    def set_row(self, name, value):
        ''' Sets a row value of a treeview component '''
        self.builder.get_object(name).insert(
            '', 'end', values=value)

    def init_checkbox(self, name, value):
        ''' Intializes a checkout component '''
        self.builder.get_object(name).state(['!alternate'])
        if value:
            self.builder.get_object(name).state(['selected'])
        else:
            self.builder.get_object(name).state(['!selected'])

    def write_console(self, text):
        ''' Writes the messages to console textbox component '''
        self.builder.get_object('console').insert(tk.END, text)
        self.builder.get_object('console').see('end')
