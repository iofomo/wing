# -*- encoding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os, sys

from manager import repo_init

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_properties import PropertiesUtils
from manager.repo_env import RepoEnv


# --------------------------------------------------------------------------------------------------------------------------
class RepoExtend:
    def __init__(self, pp, ep):
        self.mRepoPath, self.mEnvPath = pp, ep

    def __getProjectPath__(self, default, chkFile='mk.py'):
        path = self.mEnvPath
        minGap = 3 if CmnUtils.isOsWindows() else 1
        while minGap < len(path):
            if os.path.exists(path + os.sep + chkFile): return path
            path = os.path.dirname(path)
        return default

    def doBuild(self, argv):
        projPath = self.__getProjectPath__(self.mRepoPath)
        ret = CmnUtils.doCmdCall('cd %s/.repo/repo && python extend/extend_build.py %s %s %s' % (
        self.mRepoPath, self.mRepoPath, projPath, CmnUtils.joinArgs(argv)))
        assert 0 == ret or '0' == ret, 'Build fail'
        LoggerUtils.light('done.')

    def doClean(self, argv):
        ret = CmnUtils.doCmdCall('cd %s/.repo/repo && python extend/extend_clean.py %s %s %s' % (
        self.mRepoPath, self.mRepoPath, self.mEnvPath, CmnUtils.joinArgs(argv)))
        assert 0 == ret or '0' == ret, 'Clean fail'
        LoggerUtils.light('done.')

    def doRefresh(self, argv):
        ret = CmnUtils.doCmdCall('cd %s/.repo/repo && python extend/extend_refresh.py %s %s' % (
        self.mRepoPath, self.mEnvPath, CmnUtils.joinArgs(argv)))
        assert 0 == ret or '0' == ret, 'refresh fail'
        LoggerUtils.light('done.')

    def doADB(self, argv):
        ret = CmnUtils.doCmdCall('cd %s/.repo/repo && python extend/extend_adb.py %s %s' % (
        self.mRepoPath, self.mEnvPath, CmnUtils.joinArgs(argv)))
        assert 0 == ret or '0' == ret, 'adb fail'
        LoggerUtils.light('done.')

    def doGit(self, argv):
        projPath = self.__getProjectPath__(self.mRepoPath, '.git/config')
        ret = CmnUtils.doCmdCall('cd %s/.repo/repo && python extend/extend_git.py %s %s %s' % (
        self.mRepoPath, projPath, self.mEnvPath, CmnUtils.joinArgs(argv)))
        assert 0 == ret or '0' == ret, 'git command fail'

    def doSwitch(self, argv):
        repo_init.switchBranch(self.mRepoPath, argv[0])
        LoggerUtils.light('done.')

    def doProject(self, argv):
        projPath = self.__getProjectPath__(self.mRepoPath, '.git/config')
        ret = CmnUtils.doCmdCall('cd %s/.repo/repo && python extend/extend_project.py %s %s %s' % (
        self.mRepoPath, projPath, self.mEnvPath, CmnUtils.joinArgs(argv)))
        assert 0 == ret or '0' == ret, 'project command fail'

    def doSetProperty(self, k, v):
        PropertiesUtils.set(self.mRepoPath + '/.repo/repo.properties', k, v)
        LoggerUtils.light('done.')

    def doGetProperty(self, k):
        LoggerUtils.light(PropertiesUtils.get(self.mRepoPath + '/.repo/repo.properties', k))

    def doListProperty(self):
        items = PropertiesUtils.getAll(self.mRepoPath + '/.repo/repo.properties')
        for k, v in items.items(): LoggerUtils.info(k + '=' + v)

    def doKey(self, argv):
        ret = CmnUtils.doCmdCall('cd %s/.repo/repo && python extend/extend_key.py %s %s' % (
        self.mRepoPath, self.mEnvPath, CmnUtils.joinArgs(argv)))
        assert 0 == ret or '0' == ret, 'fail'
        LoggerUtils.light('done.')

    def doExtend(self, _argv):
        type, argv = _argv[0], _argv[1:]
        if '-build' == type: return self.doBuild(argv)
        if '-clean' == type: return self.doClean(argv)
        if '-refresh' == type: return self.doRefresh(argv)
        if '-adb' == type: return self.doADB(argv)
        if '-switch' == type: return self.doSwitch(argv)
        if '-project' == type: return self.doProject(argv)
        if '-setprop' == type: return self.doSetProperty(argv[0], argv[1])
        if '-getprop' == type: return self.doGetProperty(argv[0])
        if '-listprop' == type: return self.doListProperty()
        if '-key' == type: return self.doKey(argv)
        if type in ['-branch', '-newbranch', '-push', '-status']: return self.doGit(_argv)
        LoggerUtils.e('UNsupport: ' + CmnUtils.joinArgs(_argv))


if __name__ == "__main__":
    projPath, envPath = sys.argv[1], sys.argv[2]
    RepoEnv.init(projPath)
    RepoExtend(projPath, envPath).doExtend(sys.argv[3:])
