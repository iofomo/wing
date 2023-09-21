# -*- encoding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os, sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from manager.repo_env import RepoEnv
from manager.repo_git import RepoGit
from manager.repo_manifest import ManifestHandler


# ----------------------------------------------------------------------------------------------------------------------
def doRefresh():
    LoggerUtils.println('do refresh ...')
    cmd = 'cd %s/.repo/repo && python manager/repo_extend.py %s %s %s' % (RepoEnv.getRootPath(), RepoEnv.getRootPath(), os.getcwd(), '-refresh')
    ret = CmnUtils.doCmdCall(cmd)
    assert 0 == ret or '0' == ret, 'Error: refresh fail'


class RepoSync:

    @staticmethod
    def parseBranchIndex(indexXml):
        with open(indexXml, 'r') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line.startswith('<include '): continue
            pos = line.find('name=')
            line = line[pos + len('name='):]
            pos = line.find('"')
            line = line[pos + 1:]
            pos = line.find('"')
            return line[:pos]
        return None

    @staticmethod
    def do_sync_project(force, ignoreFail, project, group):
        LoggerUtils.light(project.getPath())
        exist = RepoGit.fetchGit(project.getPath(), project.getName())  # if local not found, then fetch
        projForce = force if exist else True
        remoteBranch = project.getRevision()
        if CmnUtils.isEmpty(remoteBranch): remoteBranch = group.getRevision()
        assert not CmnUtils.isEmpty(remoteBranch), 'Empty remote branch'
        currBranch = RepoGit.getCurrentBranch(project.getPath())
        switch = projForce or len(currBranch) <= 0 or currBranch == remoteBranch
        if not switch: remoteBranch = currBranch
        # LoggerUtils.println(remoteBranch + " =?= " + currBranch)
        if not RepoGit.fetchBranch(project.getPath(), remoteBranch, projForce, ignoreFail, not exist): return
        if switch: project.doActions(projForce)

    @staticmethod
    def do_switch_project(ignoreFail, project, group):
        LoggerUtils.light(project.getPath())
        exist = RepoGit.fetchGit(project.getPath(), project.getName())  # if local not found, then fetch
        projForce = not exist
        remoteBranch = project.getRevision()
        if CmnUtils.isEmpty(remoteBranch): remoteBranch = group.getRevision()
        assert not CmnUtils.isEmpty(remoteBranch), 'Empty remote branch'
        if not RepoGit.fetchBranch(project.getPath(), remoteBranch, projForce, ignoreFail, projForce): return
        project.doActions(projForce)

    @staticmethod
    def doSync(force, ignoreFail, isSwitch=False):
        # update manifests
        RepoGit.updateCurrentBranch('.repo/manifests', RepoEnv.getRepoBranch())

        indexXml = RepoEnv.getRootPath() + os.sep + '.repo' + os.sep + 'manifest.xml'
        xml = RepoSync.parseBranchIndex(indexXml)
        realXml = RepoEnv.getRootPath() + os.sep + '.repo' + os.sep + 'manifests' + os.sep + xml
        mh = ManifestHandler.parseXml(RepoEnv.getRootPath(), realXml)

        group = mh.getGroup()
        projects = mh.getProjects()
        for project in projects:
            if isSwitch:
                RepoSync.do_switch_project(ignoreFail, project, group)
            else:
                RepoSync.do_sync_project(force, ignoreFail, project, group)
        CmnUtils.doCmd('chmod a+x %s/* ' % RepoEnv.getRootPath())
        doRefresh()

    @staticmethod
    def doSyncProject(force, ignoreFail, projectPath):
        # update manifests
        RepoGit.updateCurrentBranch('.repo/manifests', RepoEnv.getRepoBranch())

        indexXml = RepoEnv.getRootPath() + os.sep + '.repo' + os.sep + 'manifest.xml'
        xml = RepoSync.parseBranchIndex(indexXml)
        realXml = RepoEnv.getRootPath() + os.sep + '.repo' + os.sep + 'manifests' + os.sep + xml
        mh = ManifestHandler.parseXml(RepoEnv.getRootPath(), realXml)

        group = mh.getGroup()
        projects = mh.getProjects()
        for project in projects:
            if project.getPath() != projectPath: continue
            RepoSync.do_sync_project(force, ignoreFail, project, group)
            break
        else:
            LoggerUtils.error('Not found project: ' + projectPath)
        doRefresh()


def run():
    forceSwitch, ignoreFail, projectPath = False, False, None
    if 2 < len(sys.argv):
        for arg in sys.argv[2:]:
            if '-f' == arg:
                forceSwitch = True
            elif '-i' == arg:
                ignoreFail = True
            else:
                projectPath = arg

    if None == projectPath:
        return RepoSync.doSync(forceSwitch, ignoreFail)

    projectPath = projectPath.strip('/')
    return RepoSync.doSyncProject(forceSwitch, ignoreFail, projectPath)


if __name__ == "__main__":
    RepoEnv.init(sys.argv[1])
    run()
