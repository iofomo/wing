#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  utils for logger print
# @date:   2023.08.10 14:40:50

import traceback, os, sys, ctypes, threading
from utils.utils_import import ImportUtils

ImportUtils.initEnv()


# -------------------------------------------------------------
class LoggerUtils:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED_GRAY = '\033[95m'
    BLUE_GRAY = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'

    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE = -11
    STD_ERROR_HANDLE = -12

    FOREGROUND_BLACK = 0x0
    FOREGROUND_BLUE = 0x01  # text color contains blue.
    FOREGROUND_GREEN = 0x02  # text color contains green.
    FOREGROUND_RED = 0x04  # text color contains red.
    FOREGROUND_INTENSITY = 0x08  # text color is intensified.

    # BACKGROUND_BLUE = 0x10 # background color contains blue.
    # BACKGROUND_GREEN= 0x20 # background color contains green.
    # BACKGROUND_RED = 0x40 # background color contains red.
    # BACKGROUND_INTENSITY = 0x80 # background color is intensified.

    g_os_win = -1
    g_log_file = None
    g_log_size = None

    @classmethod
    def isOsWindows(cls):
        if cls.g_os_win < 0:
            opt = sys.platform.lower()
            cls.g_os_win = 1 if opt.startswith('win') else 0
        return 1 == cls.g_os_win

    @staticmethod
    def alignLine(txt, num=48):
        txt = txt if txt != None else ''
        tail = num - len(txt)
        if 0 < tail:
            for i in range(tail): txt += ' '
        return txt

    @staticmethod
    def printLine(title, txt=None, subTxt=None):
        if LoggerUtils.isOsWindows():
            # LoggerUtils.setColor(LoggerUtils.FOREGROUND_GREEN | LoggerUtils.FOREGROUND_INTENSITY)
            print((title if None != title else '') + (txt if None != txt else '') + (subTxt if None != subTxt else ''))
            # LoggerUtils.resetColor()
        else:
            _title = (LoggerUtils.GREEN + title + LoggerUtils.END) if None != title else ''
            _txt = (LoggerUtils.RED_GRAY + txt + LoggerUtils.END) if None != txt else ''
            _subTxt = (LoggerUtils.BLUE_GRAY + subTxt + LoggerUtils.END) if None != subTxt else ''
            print(_title + _txt + _subTxt)
        sys.stdout.flush()

    @staticmethod
    def info(msg):
        LoggerUtils.printBlue(msg)

    @staticmethod
    def i(msg):
        LoggerUtils.printBlue(msg)

    @staticmethod
    def light(msg):
        LoggerUtils.printGreen(msg)

    @staticmethod
    def warning(msg):
        LoggerUtils.printYellow(msg)

    @staticmethod
    def warn(msg):
        LoggerUtils.printYellow(msg)

    @staticmethod
    def w(msg):
        LoggerUtils.printYellow(msg)

    @staticmethod
    def error(msg, stack=False):
        LoggerUtils.printRed(msg)
        if not stack: return
        traceback.print_stack()
        traceback.print_exc()

    @staticmethod
    def e(msg, stack=False):
        LoggerUtils.printRed(msg)
        if not stack: return
        traceback.print_stack()
        traceback.print_exc()

    @staticmethod
    def exception(e):
        LoggerUtils.println(e)
        traceback.print_stack()
        traceback.print_exc()

    @staticmethod
    def println(*p):
        if 1 == len(p):
            print(p[0])
        else:
            print(p)
        sys.stdout.flush()

    @staticmethod
    def printClear():
        os.system('cls' if LoggerUtils.isOsWindows() else 'clear')
        sys.stdout.flush()

    std_out_handle = None

    @staticmethod
    def getHandler():
        if None == LoggerUtils.std_out_handle:
            LoggerUtils.std_out_handle = ctypes.windll.kernel32.GetStdHandle(LoggerUtils.STD_OUTPUT_HANDLE)
        return LoggerUtils.std_out_handle

    @staticmethod
    def setColor(color):
        """(color) -> bit
        Example: set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_INTENSITY)
        """
        try:
            return ctypes.windll.kernel32.SetConsoleTextAttribute(LoggerUtils.getHandler(), color)
        except Exception as e:
            pass

    @staticmethod
    def resetColor():
        LoggerUtils.setColor(LoggerUtils.FOREGROUND_RED | LoggerUtils.FOREGROUND_GREEN | LoggerUtils.FOREGROUND_BLUE)

    @staticmethod
    def printRed(txt):
        if LoggerUtils.isOsWindows():
            # LoggerUtils.setColor(LoggerUtils.FOREGROUND_RED | LoggerUtils.FOREGROUND_INTENSITY)
            print(txt)
            # LoggerUtils.resetColor()
        elif isinstance(txt, str) or isinstance(txt, unicode):
            print(LoggerUtils.RED + txt + LoggerUtils.END)
        else:
            print(txt)
        sys.stdout.flush()

    @staticmethod
    def printGreen(txt):
        if LoggerUtils.isOsWindows():
            # LoggerUtils.setColor(LoggerUtils.FOREGROUND_GREEN | LoggerUtils.FOREGROUND_INTENSITY)
            print(txt)
            # LoggerUtils.resetColor()
        elif isinstance(txt, str) or isinstance(txt, unicode):
            print(LoggerUtils.GREEN + txt + LoggerUtils.END)
        else:
            print(txt)
        sys.stdout.flush()

    @staticmethod
    def printBlue(txt):
        if LoggerUtils.isOsWindows():
            # LoggerUtils.setColor(LoggerUtils.FOREGROUND_BLUE | LoggerUtils.FOREGROUND_INTENSITY)
            print(txt)
            # LoggerUtils.resetColor()
        elif isinstance(txt, str) or isinstance(txt, unicode):
            print(LoggerUtils.BLUE + txt + LoggerUtils.END)
        else:
            print(txt)
        sys.stdout.flush()

    @staticmethod
    def printYellow(txt):
        if LoggerUtils.isOsWindows():
            # LoggerUtils.setColor(LoggerUtils.YELLOW | LoggerUtils.FOREGROUND_INTENSITY)
            print(txt)
            # LoggerUtils.resetColor()
        elif isinstance(txt, str) or isinstance(txt, unicode):
            print(LoggerUtils.YELLOW + txt + LoggerUtils.END)
        else:
            print(txt)
        sys.stdout.flush()

    @classmethod
    def __monitorLoggerFile__(cls, _fname):
        while None != cls.g_log_file:
            try:
                if not os.path.isfile(cls.g_log_file): continue
                currSize = os.path.getsize(cls.g_log_file)
                if currSize < cls.g_log_size: cls.g_log_size = currSize
                with open(cls.g_log_file, 'r') as f:
                    f.seek(cls.g_log_size, 1)
                    while None != cls.g_log_file:
                        line = f.readline()
                        if None == line: break  # exception
                        l = len(line)
                        if l <= 0: break  # finished
                        cls.g_log_size += l
                        print(line)
            except Exception as e:
                pass

    @classmethod
    def monitorFile(cls, fname):
        if None == cls.g_log_file:  # create
            try:
                os.remove(fname)
            except Exception as e:
                pass
            cls.g_log_size = 0
            cls.g_log_file = fname
            t = threading.Thread(target=LoggerUtils.__monitorLoggerFile__, args=(fname,))
            t.start()
        else:  # has running
            if cls.g_log_file == fname: return  # do nothing
            cls.g_log_size = 0
            cls.g_log_file = fname

    @classmethod
    def monitorFileCancel(cls):
        cls.g_log_size = 0
        cls.g_log_file = None


def run():
    LoggerUtils.println(None)
    LoggerUtils.println('a')
    LoggerUtils.println('a', 'b')
    LoggerUtils.println(['a'], 'b', {'c'})
    LoggerUtils.printBlue('blue')
    LoggerUtils.printRed('red')
    LoggerUtils.printGreen('green')


if __name__ == "__main__":
    run()
