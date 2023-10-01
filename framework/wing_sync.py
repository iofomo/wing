# -*- encoding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os, sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_file import FileUtils
from framework.wing_env import WingEnv
from framework.wing_git import WingGit
from framework.wing_manifest import ManifestHandler


# ----------------------------------------------------------------------------------------------------------------------
def doRefresh():
    LoggerUtils.println('do refresh ...')
    cmd = 'cd "%s" && python framework/wing_extend.py "%s" "%s" "%s"' % (WingEnv.getWingPath(), WingEnv.getSpacePath(), WingEnv.getEnvPath(), '-refresh')
    succ = CmnUtils.doCmdCall(cmd)
    assert succ, 'Error: refresh fail'


class WingSync:

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
    def do_sync_project(project, group, force):
        LoggerUtils.light('\n' + project.getPath())
        exist = WingGit.fetchGit(project.getPath(), project.getName())  # if local not found, then fetch
        projForce = force if exist else True
        remoteBranch = project.getRevision()
        if CmnUtils.isEmpty(remoteBranch): remoteBranch = group.getRevision()
        assert not CmnUtils.isEmpty(remoteBranch), 'Empty remote branch'
        currBranch = WingGit.getCurrentBranch(project.getPath())
        switch = projForce or len(currBranch) <= 0 or currBranch == remoteBranch
        if not switch: remoteBranch = currBranch
        # LoggerUtils.println(remoteBranch + " =?= " + currBranch)
        if not WingGit.fetchBranch(project.getPath(), remoteBranch, projForce, not exist): return
        if switch: project.doActions(projForce)

    @staticmethod
    def do_switch_project(project, group):
        LoggerUtils.light('\n' + project.getPath())
        exist = WingGit.fetchGit(project.getPath(), project.getName())  # if local not found, then fetch
        projForce = not exist
        remoteBranch = project.getRevision()
        if CmnUtils.isEmpty(remoteBranch): remoteBranch = group.getRevision()
        assert not CmnUtils.isEmpty(remoteBranch), 'Empty remote branch'
        if not WingGit.fetchBranch(project.getPath(), remoteBranch, projForce, projForce): return
        project.doActions(projForce)

    @staticmethod
    def doSync(force, isSwitch):
        if not WingEnv.isLocalMode():
            # update manifests
            WingGit.updateCurrentBranch('.wing/manifests', WingEnv.getSpaceBranch())

        indexXml = WingEnv.getSpacePath() + '/.wing/manifest.xml'
        xml = WingSync.parseBranchIndex(indexXml)
        realXml = WingEnv.getSpacePath() + '/.wing/manifests/' + xml
        mh = ManifestHandler.parseXml(WingEnv.getSpacePath(), realXml)

        group = mh.getGroup()
        projects = mh.getProjects()
        for project in projects:
            if isSwitch:
                WingSync.do_switch_project(project, group)
            else:
                WingSync.do_sync_project(project, group, force)
        CmnUtils.doCmd('chmod a+x %s/* ' % WingEnv.getSpacePath())
        doRefresh()


def run():
    # clean tmp
    path = WingEnv.getSpacePath() + '/.wing'
    ff = os.listdir(path)
    if not CmnUtils.isEmpty(ff):
        for f in ff:
            if not f.startswith('.tmp_'): continue
            FileUtils.remove(path + os.sep + f)

    force = False
    if 3 < len(sys.argv):
        for arg in sys.argv[3:]:
            if '-f' == arg:
                force = True
    return WingSync.doSync(force, False)


if __name__ == "__main__":
    """
    python wing_sync.py {space_path} {env_path} [arguments]
    """
    WingEnv.init(sys.argv[1], sys.argv[2])
    run()
