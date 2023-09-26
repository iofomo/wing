#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os
import shutil
import subprocess
import sys

try:
    from urllib import request as urllib2
except:
    import urllib2

try:
    if sys.version_info.major < 3:  # 2.x
        reload(sys)
        sys.setdefaultencoding('utf8')
    elif 3 == sys.version_info.major and sys.version_info.minor <= 3:  # 3.0 ~ 3.3
        import imp

        imp.reload(sys)
    else:  # 3.4 <=
        import importlib

        importlib.reload(sys)
except Exception as e:
    pass

# wing version, wing -v
g_ver = '0.9.2' # sync with setup.py
# wing publish time, wing -v
g_date = '2023.09.22'
g_git_host = 'git@github.com:iofomo'
g_git_wing_remote = 'wing'
g_git_wing_branch = 'main'
# --------------------------------------------------------------------------------------------------------------------------
# init project env
g_env_path = os.getcwd()
g_wing_path = os.path.expanduser("~") + os.sep + '.wing/wing' #  such as: /Users/${username}/.wing/wing
g_this_wing_file = os.path.realpath(sys.argv[0])

g_space_path = g_env_path
while True:
    if os.path.exists(g_space_path + '/.wing/space.json'): break # found wing-space
    ppath = os.path.dirname(g_space_path)
    if len(g_space_path) <= len(ppath):
        g_space_path = None
        break
    g_space_path = ppath


# --------------------------------------------------------------------------------------------------------------------------
def println(*p):
    if 1 == len(p):
        print(p[0])
    else:
        print(p)
    sys.stdout.flush()


def isOsWindows(): return sys.platform.lower().startswith('win')


def isEmpty(s): return s is None or len(s) <= 0


def formatCommand(cmd):
    if not isOsWindows(): return cmd
    if cmd.startswith('chmod '): return None
    if cmd.startswith('cd '):
        pre = cmd[2:].strip()
        if pre.startswith('"'): pre = pre[1:]
        cmd = pre[:2] + ' && ' + cmd
    return cmd


def doCmd(cmd):
    cmd = formatCommand(cmd)
    if cmd is None: return ''

    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines = ''
        while p.poll() is None:
            line = p.stdout.readline().decode()
            if isEmpty(line): break
            lines += line
        return lines
    except Exception as e:
        println(e)
    return ''


def doCmdCall(cmd):
    cmd = formatCommand(cmd)
    if cmd is None: return True

    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        isWin = isOsWindows()
        while p.poll() is None:
            line = p.stdout.readline().decode()
            if isEmpty(line): break
            line = line.strip()
            if isWin:
                l1 = line.replace('\n', '').replace('\r', '')
                if len(l1) <= 0: continue
            print(line)
        return p.returncode is None or p.returncode == 0 or p.returncode == '0'
    except Exception as e:
        println(e)
    return False


def doWingSync():
    if not os.path.isdir(g_wing_path):
        os.makedirs(g_wing_path)

    fetchGitWing(g_wing_path)
    if not isOsWindows():
        doCmd('chmod a+x %s ' % g_wing_path)


def hasBranch(path, branch):
    branches = doCmd('cd %s && git branch' % path)
    if isEmpty(branches): return False
    bb = branches.split('\n')
    for b in bb:
        b = b.strip()
        if b.startswith('*'): b = b[1:].strip()
        if branch == b: return True
    return False


def getCurrentBranch(path):
    branches = doCmd('cd %s && git branch' % (path))
    if isEmpty(branches): return ''
    bb = branches.split('\n')
    for b in bb:
        b = b.strip()
        if not b.startswith('*'): continue
        b = b[1:].strip()
        return b
    return ''


def getVersion(rf):
    ver = None
    with open(rf, 'r') as f:
        for line in f.readlines():
            if not line.startswith('g_ver'): continue
            ver = line.split('=')[1].strip()
            break
    return ver


def compareVer(_sVer, _dVer):
    sVer = '' if isEmpty(_sVer) else _sVer
    dVer = '' if isEmpty(_dVer) else _dVer
    ss = sVer.split('.')
    dd = dVer.split('.')
    ls = len(ss)
    ld = len(dd)
    l = ls if ls < ld else ld
    if 0 < l:
        for i in range(l):
            if ss[i] < dd[i]: return -1
            if ss[i] > dd[i]: return 1
    if l < ls:
        return 1
    elif l < ld:
        return -1
    return 0


def fetchGitWing(wingPath):
    """
    @param wingPath such as: /Users/${username}/.wing/wing
    """
    println('check wing')
    localMode = False
    if os.path.isdir(wingPath + os.sep + '.git'):  # /Users/${user name}/.wing/wing/.git Exist, then git pull
        doCmd('cd %s && git pull' % wingPath)
    elif os.path.isfile(wingPath + '/framework/wing_init.py'):  # Exist, then local mode
        localMode = True
        print('run with local mode')
    else: # Not exist, then clone
        doCmd('cd %s && git clone %s/%s' % (os.path.dirname(wingPath), g_git_host, g_git_wing_remote))
        assert os.path.isdir(wingPath + os.sep + '.git'), 'Make sure have correct access rights for ' + g_git_wing_remote + ' !'

    if not localMode:
        if hasBranch(wingPath, g_git_wing_branch):
            succ = doCmdCall('cd %s && git checkout %s' % (wingPath, g_git_wing_branch))
            assert succ, 'Error: git checkout origin'
        else:
            succ = doCmdCall('cd %s && git checkout -b %s origin/%s' % (wingPath, g_git_wing_branch, g_git_wing_branch))
            assert succ, 'Error: git checkout origin'

        assert getCurrentBranch(wingPath) == g_git_wing_branch

        succ = doCmdCall('cd %s && git pull origin %s' % (wingPath, g_git_wing_branch))
        assert succ, 'Error: git pull origin'
        println('check wing done.')

    localVer = getVersion(g_wing_path + '/wing.py')
    if 0 <= compareVer(g_ver, localVer): return
    shutil.copyfile(g_wing_path + os.sep + 'wing.py', g_this_wing_file)
    println('update wing %s -> %d done.' % (g_ver, localVer))


def checkGitEnv():
    ret = doCmd('git --version')
    if isEmpty(ret): return False
    ret = ret.strip()
    return ret.startswith('git version ')


def showHelp():
    hf = g_wing_path + '/res/help.txt'
    if os.path.isfile(hf):
        try:
            with open(hf, 'r') as f: print(f.read())
            return
        except Exception as e:
            println(e)
    print('''
        wing commands
           init {workspace name} {branch or tag name} {manifest name}
                create workspace, such as: 
                     wing init xxx develop android.xml
                     wing init xxx tag_1.0 service.xml
           sync [-f] [-i] sync code from remote where config from manifest
                 -f: force switch to new branch
                 -i: ignore git sync fail

           -status    print curren local branch and remote info
           
           -branch    print curren local branch and remote info
           
           -push
           
           -create [-b/-branch] [-t/-tag] [-p/-project]
                -b/-branch  <new branch name>
                -t/-tag <new tag name>
                -p/-project <template name> <project name> [module name={project name}]

           -clean   Restore working tree files
           
           -switch
           
           -build
           
           -refresh
           
           -setprop <key> <value>
           -getprop <key>
           -listprop
           
        git commands: all the git commands has remain
           <git command>
        ''')


def run():
    if len(sys.argv) < 2:
        showHelp()
        return

    if not checkGitEnv():
        println('Error: No git running environment found !')
        return

    cmd = sys.argv[1]
    if cmd in ['-h', '--h', '-help', '--help']:
        showHelp()
        return
    if cmd in ['-v', '--v', '-version', '--version']:
        println('wing %s, (%s)' % (g_ver, g_date))
        return

    if cmd == 'init':
        doWingSync()
        cmd = 'cd "%s" && python framework/wing_init.py "%s" "%s" %s ' % (g_wing_path, g_env_path if isEmpty(g_space_path) else g_space_path, g_env_path, ' '.join(sys.argv[2:]))
    elif cmd == 'sync':
        assert not isEmpty(g_space_path), 'Invalid wing workspace'
        doWingSync()
        cmd = 'cd "%s" && python framework/wing_sync.py "%s" "%s" %s' % (g_wing_path, g_space_path, g_env_path, ' '.join(sys.argv[2:]))
    elif cmd == 'manifest':
        println('Ignore command: ' + ' '.join(sys.argv))
        return
    elif cmd == 'forall':  # wing forall -c "git reset --hard"
        assert not isEmpty(g_space_path), 'Invalid wing workspace'
        cmdStr = ' '.join(sys.argv[2:])
        pos = cmdStr.find('git ')
        if pos < 0:
            println('Ignore command: ' + ' '.join(sys.argv))
            return
        cmdStr = cmdStr[pos + len('git '):]  # got "reset --hard"
        cmd = 'cd "%s" && python framework/wing_git.py "%s" "%s" %s' % (g_wing_path, g_space_path, g_env_path, cmdStr)
    elif cmd.startswith('-'):
        assert not isEmpty(g_space_path), 'Invalid wing workspace'
        cmd = 'cd "%s" && python framework/wing_extend.py "%s" "%s" %s' % (g_wing_path, g_space_path, g_env_path, ' '.join(sys.argv[1:]))
    else:
        assert not isEmpty(g_space_path), 'Invalid wing workspace'
        cmd = 'cd "%s" && python framework/wing_git.py "%s" "%s" %s' % (g_wing_path, g_space_path, g_env_path, ' '.join(sys.argv[1:]))
    # println(cmd)
    succ = doCmdCall(cmd)
    assert succ, 'Error: fail'


if __name__ == "__main__":
    run()
