# -*- encoding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os, sys

g_this_file = os.path.realpath(sys.argv[0])
g_this_path = os.path.dirname(g_this_file)
sys.path.append(os.path.dirname(g_this_path))

from utils.utils_cmn import CmnUtils
from utils.utils_logger import LoggerUtils
from utils.utils_properties import PropertiesUtils
from utils.utils_import import ImportUtils
from framework.wing_env import WingEnv
from framework.wing_init import switchBranch

g_wing_path = ImportUtils.initEnv()


# --------------------------------------------------------------------------------------------------------------------------
class WingExtend:

    def __getProjectPath__(self, chkFile):
        path = WingEnv.getEnvPath()
        minGap = 3 if CmnUtils.isOsWindows() else 1
        while minGap < len(path):
            if os.path.exists(path + os.sep + chkFile): return path
            path = os.path.dirname(path)
        return WingEnv.getSpacePath()

    def doBuild(self, argv):
        projPath = self.__getProjectPath__('mk.py')
        succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_build.py "%s" "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), projPath, CmnUtils.joinArgs(argv)))
        assert succ, 'Build fail'
        LoggerUtils.light('done.')

    def doClean(self, argv):
        succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_clean.py "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), CmnUtils.joinArgs(argv)))
        assert succ, 'Clean fail'
        LoggerUtils.light('done.')

    def doRefresh(self, argv):
        succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_refresh.py "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), CmnUtils.joinArgs(argv)))
        assert succ, 'refresh fail'
        LoggerUtils.light('done.')

    def doADB(self, argv):
        succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_adb.py "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), CmnUtils.joinArgs(argv)))
        assert succ, 'adb fail'
        LoggerUtils.light('done.')

    def doGit(self, argv):
        projPath = self.__getProjectPath__('.git/config')
        succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_git.py "%s" "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), projPath, CmnUtils.joinArgs(argv)))
        assert succ, 'git command fail'

    def doSwitch(self, argv):
        switchBranch(WingEnv.getSpacePath(), argv[0])
        LoggerUtils.light('done.')

    def doProject(self, argv):
        projPath = self.__getProjectPath__('.git/config')
        succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_project.py "%s" "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), projPath, CmnUtils.joinArgs(argv)))
        assert succ, 'project command fail'

    def doSetProperty(self, k, v):
        PropertiesUtils.set(WingEnv.getWingPath() + '.properties', k, v)
        LoggerUtils.light('done.')

    def doGetProperty(self, k):
        LoggerUtils.light(PropertiesUtils.get(WingEnv.getWingPath() + '.properties', k))

    def doListProperty(self):
        items = PropertiesUtils.getAll(WingEnv.getWingPath() + '.properties')
        for k, v in items.items(): LoggerUtils.info(k + '=' + v)

    def doKey(self, argv):
        succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_key.py "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), CmnUtils.joinArgs(argv)))
        assert succ, 'key command fail'
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
    """
    python wing_extend.py {space_path} {env_path} [arguments]
    """
    spacePath, envPath = sys.argv[1], sys.argv[2]
    WingEnv.init(spacePath, envPath)
    WingExtend().doExtend(sys.argv[3:])
