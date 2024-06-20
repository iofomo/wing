#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: Mobile device test commands
# @date:  2024.02.10 14:40:50

import os
import shutil
import sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_import import ImportUtils
from utils.utils_file import FileUtils
from basic.arguments import BasicArgumentsValue

g_wing_path = ImportUtils.initEnv(os.path.dirname(g_this_path))

# --------------------------------------------------------------------------------------------------------------------------
def doTest(path, envPath, spacePath, argv):
    succ = CmnUtils.doCmdCall('cd "%s" && python test.py "%s" "%s" %s' % (path, envPath, spacePath, CmnUtils.joinArgs(argv)))
    assert succ, 'test run fail'


def run():
    """
    wing -test <cmds>
    """
    za = BasicArgumentsValue()
    envPath, spacePath, argv = za.get(0), za.get(1), za.getLast(2)
    if os.path.isfile(envPath + "/test.py"):
        doTest(envPath, envPath, spacePath, argv)
    elif os.path.isfile(spacePath + "/test.py"):
        doTest(spacePath, envPath, spacePath, argv)
    else:
        LoggerUtils.e('No test.py found !')


if __name__ == "__main__":
    run()
