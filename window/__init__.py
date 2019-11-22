''' Moudle for window management using only ctypes '''
import ctypes
from ctypes import wintypes
from collections import namedtuple

import win32con
import win32gui


USER32 = ctypes.WinDLL('user32', use_last_error=True)

WindowInfo = namedtuple('WindowInfo', 'pid title')

WNDENUMPROC = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HWND,    # _In_ hWnd
    wintypes.LPARAM,)  # _In_ lParam


def get_windows():
    '''Return a sorted list of visible windows.'''
    result = []
    @WNDENUMPROC
    def enum_proc_cb(hwnd, l_param):
        ''' Callback for enum windows '''
        if USER32.IsWindowVisible(hwnd):
            pid = wintypes.DWORD()
            _ = USER32.GetWindowThreadProcessId(
                hwnd, ctypes.byref(pid))
            length = USER32.GetWindowTextLengthW(hwnd) + 1
            title = ctypes.create_unicode_buffer(length)
            USER32.GetWindowTextW(hwnd, title, length)
            result.append(WindowInfo(pid.value, title.value))
        return True
    USER32.EnumWindows(enum_proc_cb, 0)
    return sorted(result)


def get_window_handle(title):
    ''' Returns the handle of the window '''
    try:
        return win32gui.FindWindow(None, title)
    except win32gui.error:
        return None


def close_window(title):
    ''' Finds and closes a window with a title '''
    try:
        handle = get_window_handle(title)
        if handle is not None:
            win32gui.PostMessage(handle, win32con.WM_CLOSE, 0, 0)
    except win32gui.error:
        pass
