#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: check code by sonar
# @date:   2023.08.10 14:40:50

import os
import sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from basic.space import BasicSpace
from basic.gradle import BasicGradle


# --------------------------------------------------------------------------------------------------------------------------
class ExtendBase:
    def __init__(self, path):
        self.mBaseSpacePath = path

    def doActionWithManifest(self, inclueAll=False):
        space = BasicSpace(self.mBaseSpacePath)

        # do to projects
        for project in space.getManifestProjects():
            if not inclueAll and not CmnUtils.isEmpty(project.getRevision()): continue
            if not os.path.exists(self.mBaseSpacePath + os.sep + project.getPath()): continue
            self.onProjectCall(space, project)

    def doActionWithPath(self):
        space = BasicSpace(self.mBaseSpacePath)

        projects = []
        self.__do_scan__(self.mBaseSpacePath, projects)
        for project in projects: self.onProjectCall(space, project)

    def getGradle(self, path):
        gradle = BasicGradle(path)
        # gradle.println()
        return gradle if gradle.isValid() else None

    def __do_scan__(self, path, projects, level=0):
        ff = os.listdir(path)
        level += 1
        for fname in ff:
            f = os.path.join(path, fname)
            if not os.path.isdir(f): continue
            if os.path.exists(f + '/.git/config'):
                projects.append(f[len(self.mBaseSpacePath) + 1:])
                continue
            if 5 < level: continue
            self.__do_scan__(f, projects, level)

    def onProjectCall(self, space, project):
        pname = project.getPath()
        projPath = self.mBaseSpacePath + os.sep + pname
        if not os.path.isfile(projPath + os.sep + 'mk.py'): return  # Invalid build project

        # group = space.getGroup()
        # LoggerUtils.println(group)


def run():
    eb = ExtendBase('xxx', '/Users/xxx/workspace/demo')
    LoggerUtils.println('-----------------------------------')
    eb.doActionWithManifest()
    LoggerUtils.println('-----------------------------------')
    eb.doActionWithPath()


if __name__ == "__main__":
    run()
