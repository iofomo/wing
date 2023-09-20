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
def doBuild(repoPath, projName, projPath, buildType, subModule):
    outPath = '%s/out/%s' % (repoPath, projName)
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


def doBuildAll(repoPath, buildType):
    if isDebug(buildType):
        ret = CmnUtils.doCmdCall('cd %s && python build.py debug' % (repoPath))
        assert 0 == ret or '0' == ret, 'Build all project fail for debug'
    elif isRelease(buildType):
        ret = CmnUtils.doCmdCall('cd %s && python build.py release' % (repoPath))
        assert 0 == ret or '0' == ret, 'Build all project fail for release'
    else:
        ret = CmnUtils.doCmdCall('cd %s && python build.py' % (repoPath))
        assert 0 == ret or '0' == ret, 'Build all project'


def run():
    """
    eg: repo -build [sub module name] [build type]
    repo -build
    repo -build d
    repo -build r
    repo -build jni
    repo -build jni d
    repo -build jni r
    """

    za = BasicArgumentsValue()
    repoPath, projPath, val1, val2 = za.get(0), za.get(1), za.get(2, ''), za.get(3, '')

    if isDebug(val1) or isRelease(val1):  # "repo -build d" or "repo -build r"
        buildType = val1
        subModule = ''
    elif isDebug(val2) or isRelease(val2):  # "repo -build jni d" or "repo -build jni r"
        buildType = val2
        subModule = val1
    else:  # "repo -build" or "repo -build jni"
        buildType = ''
        subModule = val1

    if len(projPath) <= len(repoPath):
        return doBuildAll(repoPath, buildType)

    projName = projPath[len(repoPath) + 1:]
    if isDebug(buildType): return doBuild(repoPath, projName, projPath, 'debug', subModule)
    if isRelease(buildType): return doBuild(repoPath, projName, projPath, 'release', subModule)

    # eg: repo -build [$sub_module], such as:
    # repo -build
    # repo -build jni
    doBuild(repoPath, projName, projPath, 'all', subModule)


if __name__ == "__main__":
    run()
