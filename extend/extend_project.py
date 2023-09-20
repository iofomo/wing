#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief: publish module to maven
# @date:   2023.08.10 14:40:50

# TODO, import system module here ...
import sys, os, time, datetime

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_file import FileUtils
from utils.utils_import import ImportUtils
from basic.git import BasicGit
from basic.arguments import BasicArgumentsValue
from basic.repoin import BasicRepoIn
from basic.gradle import BasicGradle

g_env_path, g_this_file, g_this_path = ImportUtils.initEnv()
g_repo_path = ImportUtils.initPath(g_env_path)


# --------------------------------------------------------------------------------------------------------------------------
class ProjectCollector:
    def __init__(self):
        self.repo = {}
        self.projects = []

    def doCollect(self):
        self.__doCollectRepo__()
        self.__doCollectModule__()

        jdata = {
            'repo': self.repo,
            'project': self.projects
        }
        FileUtils.saveJsonToFile(g_repo_path + '/out/project.json', jdata)

    def __doCollectRepo__(self):
        '''
          "repo": {
            "group": "xxx",
            "branch": "main",
            "manifest": "admin.xml"
            "remote": "repo"
          }
        '''
        repo = BasicRepoIn(g_repo_path)
        path = g_repo_path + '/.repo/manifests'
        branch, sname = ProjectCollector.getGitInfo(path)
        assert not CmnUtils.isEmpty(sname), "No repo.manifests found !"
        self.repo["name"] = "manifests"
        self.repo["path"] = path
        self.repo["branch"] = branch
        self.repo["remote"] = sname
        self.repo["group"] = repo.getGroup()
        self.repo["manifest"] = repo.getManifest()

    def __doCollectModule__(self):
        '''
          "${module name}": {
            "branch": "${git branch name}",
            "type": "${project type}"
            "remote": "$git remote name"
          }
        '''
        self.scanPath(g_repo_path, 1)

    def doParseBase(self, d, pname, branch, sname):
        pitem = {
            "name": pname,
            "path": d,
            "branch": branch,
            "remote": sname
        }
        return pitem

    def doParseWithAndroid(self, path, pitem):
        '''
          "${module name}": {
            "type": "aar"
          }
        '''
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
        # 获取该目录下所有的文件名称和目录名称
        ll = os.listdir(path)
        for l in ll:
            if l.startswith('.'): continue
            d = path + os.sep + l
            if not os.path.isdir(d): continue
            branch, sname = ProjectCollector.getGitInfo(d)
            if not CmnUtils.isEmpty(sname):
                pname = d[len(g_repo_path) + 1:]
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
        git = BasicGit(g_repo_path, projPath)
        return git.getCurrentBranch(), git.getServerName()


def run():
    '''
    repo -project
    '''
    argv = BasicArgumentsValue()
    projPath, envPath, cmd = argv.get(0), argv.get(1), argv.get(2)
    ProjectCollector().doCollect()


if __name__ == "__main__":
    run()
