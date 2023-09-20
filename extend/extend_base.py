#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: check code by sonar
# @date:   2023.08.10 14:40:50

import sys, os

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from basic.repoin import BasicRepoIn
from basic.gradle import BasicGradle


# --------------------------------------------------------------------------------------------------------------------------
class ExtendBase:
    def __init__(self, repoPath):
        self.mBaseRepoPath = repoPath

    def doActionWithManifest(self, inclueAll=False):
        repo = BasicRepoIn(self.mBaseRepoPath)

        # do to projects
        for project in repo.getManifestProjects():
            if not inclueAll and not CmnUtils.isEmpty(project.getRevision()): continue
            if not os.path.exists(self.mBaseRepoPath + os.sep + project.getPath()): continue
            self.onProjectCall(repo, project)

    def doActionWithPath(self):
        repo = BasicRepoIn(self.mBaseRepoPath)

        projects = []
        self.__do_scan__(self.mBaseRepoPath, projects)
        for project in projects: self.onProjectCall(repo, project)

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
                projects.append(f[len(self.mBaseRepoPath) + 1:])
                continue
            if 5 < level: continue
            self.__do_scan__(f, projects, level)

    def onProjectCall(self, repo, project):
        pname = project.getPath()
        projPath = self.mBaseRepoPath + os.sep + pname
        if not os.path.isfile(projPath + os.sep + 'mk.py'): return  # Invalid repo project

        group = repo.getGroup()
        # LoggerUtils.println(group)


def run():
    eb = ExtendBase('xxx', '/Users/xxx/workspace/demo')
    LoggerUtils.println('-----------------------------------')
    eb.doActionWithManifest()
    LoggerUtils.println('-----------------------------------')
    eb.doActionWithPath()


if __name__ == "__main__":
    run()
