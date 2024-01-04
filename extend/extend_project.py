#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: publish module to maven
# @date:   2023.08.10 14:40:50

import os
import sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_file import FileUtils
from utils.utils_import import ImportUtils
from basic.git import BasicGit
from basic.arguments import BasicArgumentsValue
from basic.space import BasicSpace
from basic.gradle import BasicGradle

g_wing_path = ImportUtils.initEnv(os.path.dirname(g_this_path))


# --------------------------------------------------------------------------------------------------------------------------
class ProjectCollector:
    def __init__(self, spacePath):
        self.mSpacePath = spacePath
        self.space = {}
        self.projects = []

    def doCollect(self):
        self.__doCollectSpace__()
        self.__doCollectModule__()

        jdata = {
            'space': self.space,
            'project': self.projects
        }
        FileUtils.saveJsonToFile(self.mSpacePath + '/out/project.json', jdata)

    def __doCollectSpace__(self):
        """
          "space": {
            "group": "xxx",
            "branch": "main",
            "manifest": "admin.xml"
            "remote": "wing"
          }
        """
        space = BasicSpace(self.mSpacePath)
        path = self.mSpacePath + '/.wing/manifests'
        branch, sname = ProjectCollector.getGitInfo(path)
        assert not CmnUtils.isEmpty(sname), "No manifests found !"
        self.space["name"] = "manifests"
        self.space["path"] = path
        self.space["branch"] = branch
        self.space["remote"] = sname
        self.space["group"] = space.getGroup()
        self.space["manifest"] = space.getManifest()

    def __doCollectModule__(self):
        """
          "${module name}": {
            "branch": "${git branch name}",
            "type": "${project type}"
            "remote": "$git remote name"
          }
        """
        self.scanPath(self.mSpacePath, 1)

    def doParseBase(self, d, pname, branch, sname):
        pitem = {
            "name": pname,
            "path": d,
            "branch": branch,
            "remote": sname
        }
        return pitem

    def doParseWithAndroid(self, path, pitem):
        """
          "${module name}": {
            "type": "aar"
          }
        """
        gradle = BasicGradle(path)
        if not gradle.isValid(): return False

        pitem['type'] = "gradle"
        modules = []
        pitem['module'] = modules
        for module in gradle.getModules():
            LoggerUtils.w('    :' + module)
            mm = {}
            mm['name'] = module
            mode = gradle.getMode(module)
            if None != mode: mm['mode'] = mode
            modulePath = gradle.getModulePath(module)
            if os.path.isfile(modulePath + '/.checkignore'): mm['ignore-check'] = True
            modules.append(mm)
        return True

    def scanPath(self, path, level):
        ll = os.listdir(path)
        for l in ll:
            if l.startswith('.'): continue
            d = path + os.sep + l
            if not os.path.isdir(d): continue
            branch, sname = ProjectCollector.getGitInfo(d)
            if not CmnUtils.isEmpty(sname):
                pname = d[len(self.mSpacePath) + 1:]
                LoggerUtils.light(pname)
                pitem = self.doParseBase(d, pname, branch, sname)
                self.projects.append(pitem)
                if self.doParseWithAndroid(d, pitem): continue
                # TODO add more parser here ...
                continue
            if 3 < level: continue
            self.scanPath(d, level + 1)

    @staticmethod
    def getGitInfo(projPath):
        git = BasicGit(projPath)
        return git.getCurrentBranch(), git.getServerName()


def run():
    """
    wing -project
    """
    argv = BasicArgumentsValue()
    envPath, spacePath, projPath, cmd = argv.get(0), argv.get(1), argv.get(2), argv.get(3)
    ProjectCollector(spacePath).doCollect()


if __name__ == "__main__":
    run()
