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

g_wing_path = ImportUtils.initEnv(os.path.dirname(g_this_path))


# --------------------------------------------------------------------------------------------------------------------------
def __getProjectPath__(chkFile):
    path = WingEnv.getEnvPath()
    minGap = 3 if CmnUtils.isOsWindows() else 1
    while minGap < len(path):
        if os.path.exists(path + os.sep + chkFile): return path
        path = os.path.dirname(path)
    return WingEnv.getSpacePath()


def doBuild(argv):
    projPath = __getProjectPath__('mk.py')
    succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_build.py "%s" "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), projPath, CmnUtils.joinArgs(argv)))
    assert succ, 'Build fail'
    LoggerUtils.light('\ndone.')


def doGit(argv):
    projPath = __getProjectPath__('.git/config')
    succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_git.py "%s" "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), projPath, CmnUtils.joinArgs(argv)))
    assert succ, 'git command fail'


def doSwitch(argv):
    switchBranch(WingEnv.getSpacePath(), argv[0])
    LoggerUtils.light('\ndone.')


def doProject(argv):
    projPath = __getProjectPath__('.git/config')
    succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_project.py "%s" "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), projPath, CmnUtils.joinArgs(argv)))
    assert succ, 'project command fail'


def doExtendCommand(cname, argv):
    if not os.path.isfile(WingEnv.getWingPath() + ("/extend/extend_%s.py" % cname)):
        LoggerUtils.e('UNsupport: ' + cname)
        return
    succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_%s.py "%s" "%s" %s' % (WingEnv.getWingPath(), cname, WingEnv.getEnvPath(), WingEnv.getSpacePath(), CmnUtils.joinArgs(argv)))
    assert succ, cname + ' fail'
    LoggerUtils.light('\ndone.')


def doProperty(argv):
    """
        wing -prop
    """
    if CmnUtils.isEmpty(argv):
        items = PropertiesUtils.getAll(WingEnv.getWingPath() + '.properties')
        if None == items: return
        for k, v in items.items(): LoggerUtils.info(k + '=' + v)
        return

    """
    wing -prop {g/get} {key}
    """
    if 1 < len(argv) and (argv[0] ==  'g' or argv[0] == 'get'):
        LoggerUtils.light(PropertiesUtils.get(WingEnv.getWingPath() + '.properties', argv[1]))
        return

    """
    wing -prop {s/set} {key} [value]
    """
    if 1 < len(argv) and (argv[0] == 's' or argv[0] == 'set'):
        PropertiesUtils.set(WingEnv.getWingPath() + '.properties', argv[1], argv[2] if 2 < len(argv) else '')
        return


def doKey(argv):
    succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_key.py "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), CmnUtils.joinArgs(argv)))
    assert succ, 'key command fail'
    LoggerUtils.light('\ndone.')


def doCreate(argv):
    """
    wing -create b {new branch name} [base branch name]
    wing -create t {new tag name} [base branch name]
    """
    if argv[1] == 'b' or argv[1] == 't':
        return doGit(argv)

    projPath = __getProjectPath__('.git/config')
    succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_creator.py "%s" "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), projPath, CmnUtils.joinArgs(argv[1:])))
    assert succ, 'Create command fail'
    LoggerUtils.light('\ndone.')


def doTree(argv):
    """
    wing -tree [level] [l]
    """
    maxLevel = 0
    printLine = False
    l = 0 if None == argv else len(argv)
    if 0 < l:
        if argv[0] == 'l': printLine = True
        elif argv[0].isdigit(): maxLevel = int(argv[0])
    if 1 < l:
        if argv[1] == 'l': printLine = True
        elif argv[1].isdigit(): maxLevel = int(argv[1])

    LoggerUtils.printTree(WingEnv.getEnvPath(), maxLevel, printLine)
    LoggerUtils.light('\ndone.')


def doSpace(argv):
    """
    wing -space
    """
    cfg = os.path.dirname(WingEnv.getWingPath()) + os.sep + 'space.properties'
    if CmnUtils.isEmpty(argv):
        items = PropertiesUtils.getAll(cfg)
        if CmnUtils.isEmpty(items): return
        for k, v in items.items():
            #{space name}={host},{manifest git}, such as: "iofomo=git@github.com:iofomo,manifest.git"
            LoggerUtils.info('\n[' + k + ']\n')
            items = v.split(',')
            if 0 < len(items) and not CmnUtils.isEmpty(items[0]): LoggerUtils.println('      host: %s\n' % items[0])
            if 1 < len(items) and not CmnUtils.isEmpty(items[1]): LoggerUtils.println('  manifest: %s\n' % items[1])
            LoggerUtils.println('\n')
        return

    """
    wing -space add {space name} {host} {manifest git}
    """
    if argv[0] == 'add' and 3 <= len(argv):
        v = argv[2] if len(argv) < 4 else argv[2] + ',' + argv[3]
        PropertiesUtils.set(cfg, argv[1], v)
        return
    LoggerUtils.e('Error: unsupport command: ' + ' '.join(argv))


def doPlugin(argv):
    succ = CmnUtils.doCmdCall('cd "%s" && python extend/extend_plugin.py "%s" "%s" %s' % (WingEnv.getWingPath(), WingEnv.getEnvPath(), WingEnv.getSpacePath(), CmnUtils.joinArgs(argv)))
    assert succ, 'plugin command fail'
    LoggerUtils.light('\ndone.')


def run(_argv):
    typ, argv = _argv[0], (_argv[1:] if 1 < len(_argv) else [])
    if '-build' == typ: return doBuild(argv)
    if '-switch' == typ: return doSwitch(argv)

    if '-prop' == typ: return doProperty(argv)
    if '-space' == typ: return doSpace(argv)

    if '-key' == typ: return doKey(argv)
    if typ in ['-branch', '-push', '-status']: return doGit(_argv)
    if '-create' == typ: return doCreate(_argv)
    if '-tree' == typ: return doTree(argv)
    if typ in ['-jadx', '-apktool']: return doPlugin(_argv)

    return doExtendCommand(typ[1:], argv)


if __name__ == "__main__":
    """
    python wing_extend.py {space_path} {env_path} [arguments]
    """
    spacePath, envPath = sys.argv[1], sys.argv[2]
    WingEnv.init(spacePath, envPath)
    run(sys.argv[3:])
