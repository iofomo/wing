#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: build
# @date:   2023.08.10 14:40:50

import sys, os

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_import import ImportUtils
from basic.arguments import BasicArgumentsValue

ImportUtils.initEnv()


# --------------------------------------------------------------------------------------------------------------------------
def doBuild(spacePath, projName, projPath, buildType, subModule):
    outPath = '%s/out/%s' % (spacePath, projName)
    try:
        os.makedirs(outPath)
    except Exception as e:
        pass
    ret = CmnUtils.doCmdCall('cd %s && python mk.py %s %s %s' % (projPath, outPath, buildType, subModule))
    assert 0 == ret or '0' == ret, 'Build project fail'


def isDebug(buildType):
    return 'd' == buildType or 'debug' == buildType


def isRelease(buildType):
    return 'r' == buildType or 'release' == buildType


def doBuildAll(spacePath, buildType):
    if isDebug(buildType):
        ret = CmnUtils.doCmdCall('cd %s && python build.py debug' % spacePath)
        assert 0 == ret or '0' == ret, 'Build all project fail for debug'
    elif isRelease(buildType):
        ret = CmnUtils.doCmdCall('cd %s && python build.py release' % spacePath)
        assert 0 == ret or '0' == ret, 'Build all project fail for release'
    else:
        ret = CmnUtils.doCmdCall('cd %s && python build.py' % spacePath)
        assert 0 == ret or '0' == ret, 'Build all project'


def run():
    """
    eg: wing -build [inner module name] [build type]
    wing -build
    wing -build d
    wing -build r
    wing -build jni
    wing -build jni d
    wing -build jni r
    """

    za = BasicArgumentsValue()
    envPath, spacePath, projPath, val1, val2 = za.get(0), za.get(1), za.get(2), za.get(3, ''), za.get(4, '')

    if isDebug(val1) or isRelease(val1):  # "wing -build d" or "wing -build r"
        buildType = val1
        subModule = ''
    elif isDebug(val2) or isRelease(val2):  # "wing -build jni d" or "wing -build jni r"
        buildType = val2
        subModule = val1
    else:  # "wing -build" or "wing -build jni"
        buildType = ''
        subModule = val1

    if len(projPath) <= len(spacePath):
        return doBuildAll(spacePath, buildType)

    projName = projPath[len(spacePath) + 1:]
    if isDebug(buildType): return doBuild(spacePath, projName, projPath, 'debug', subModule)
    if isRelease(buildType): return doBuild(spacePath, projName, projPath, 'release', subModule)

    # eg: wing -build [$sub_module], such as:
    # wing -build
    # wing -build jni
    doBuild(spacePath, projName, projPath, 'all', subModule)


if __name__ == "__main__":
    run()
