#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os
import shutil
import subprocess
import sys
os.system("") # Unable to explain this, just for Windows cmd color print

try:
    if sys.version_info.major < 3:  # 2.x
        reload(sys)
        sys.setdefaultencoding('utf8')
    elif 3 == sys.version_info.major and sys.version_info.minor <= 3:  # 3.0 ~ 3.3
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        import imp
        imp.reload(sys)
    else:  # 3.4 <=
        import importlib
        importlib.reload(sys)
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except Exception as e:
    pass

# wing version, wing -v
g_ver = '1.3.2'
# wing publish time, wing -v
g_date = '2024.10.10'
g_git_host = 'git@codeup.aliyun.com:63e5fbe89dee9309492bc30c'
g_git_wing_remote = 'platform/wing'
g_git_wing_branch = 'master'
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

def formatArgument(arg): return arg.replace('\\', '/') if isOsWindows() else arg

def doCmd(cmd):
    cmd = formatCommand(cmd)
    if cmd is None: return ''
    # println(cmd)
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        lines = ''
        while True:
            line = p.stdout.readline()
            # if not line: break
            if isEmpty(line):
                if p.poll() is not None: break
                continue
            line = line.decode().strip('\r\n')
            if 0 < len(line): lines += line + '\n'
        return lines
    except Exception as e:
        println(e)
    return ''


def doCmdCall(cmd):
    cmd = formatCommand(cmd)
    if cmd is None: return True
    # println(cmd)
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # isWin = isOsWindows()
        while True:
            line = p.stdout.readline()
            # if not line: break
            if isEmpty(line):
                if p.poll() is not None: break
                continue
            line = line.decode().strip('\r\n')
            if len(line) <= 0: continue
            println(line)
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
            ver = line.split('=')[1].strip()[1:-1]
            break
    return ver


def getVersionItem(ver):
    if isEmpty(ver): return 0,0,0,0
    vv = ver.split('.')
    vmajor = int(vv[0]) if 0 < len(vv) else 0
    vmid = int(vv[1]) if 1 < len(vv) else 0
    vmin = int(vv[2]) if 2 < len(vv) else 0
    vbuild = int(vv[3]) if 3 < len(vv) else 0
    return vmajor, vmid, vmin, vbuild


def compareVer(_sVer, _dVer):
    smajor, smid, smin, sbuild = getVersionItem(_sVer)
    dmajor, dmid, dmin, dbuild = getVersionItem(_dVer)

    if smajor < dmajor: return -1
    if smajor > dmajor: return 1
    if smid < dmid: return -1
    if smid > dmid: return 1
    if smin < dmin: return -1
    if smin > dmin: return 1
    if sbuild < dbuild: return -1
    if sbuild > dbuild: return 1
    return 0


def fetchGitWing(wingPath):
    """
    @param wingPath such as: /Users/${username}/.wing/wing
    """
    println('\nwing')
    localMode = False
    if os.path.isdir(wingPath + os.sep + '.git'):  # /Users/${user name}/.wing/wing/.git Exist, then git pull
        doCmd('cd %s && git pull' % wingPath)
    elif os.path.isfile(wingPath + '/framework/wing_init.py'):  # Exist, then local mode
        localMode = True
        print('local wing mode')
    else: # Not exist, then clone
        # git clone git@github.com:xxxxxx/${git name}
        # git clone git@codeup.aliyun.com.com:xxxxxx/${git name}
        # git clone ssh://xxxxxx@xxx.com:${port}/${git name}
        ret = doCmd('cd %s && git clone %s/%s%s' % (os.path.dirname(wingPath), g_git_host, g_git_wing_remote, ('' if g_git_wing_remote.endswith('.git') else '.git')))
        if not os.path.isdir(os.path.isdir(wingPath + os.sep + '.git')):
            println(ret)
            assert 0, 'Make sure have correct access rights for ' + g_git_wing_remote + ' !'

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

    localVer = getVersion(g_wing_path + '/wing.py')
    if 0 <= compareVer(g_ver, localVer): return
    shutil.copyfile(g_wing_path + os.sep + 'wing.py', g_this_wing_file)
    println('update wing %s -> %s\n' % (g_ver, localVer))


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
                    create wing-space, such as: 
                    wing init workspace1 develop dev.xml
                    wing init workspace2 tag_1.0 release.xml
           sync [f] sync code from remote from manifests
                 f: Force switch to new branch, discard all local changes
        
        wing tool commands
            -tree [l] Print directory structure

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
        cmd = 'cd "%s" && python framework/wing_init.py "%s" "%s" %s ' % (g_wing_path,
                                                                          formatArgument(g_env_path if isEmpty(g_space_path) else g_space_path),
                                                                          formatArgument(g_env_path),
                                                                          ' '.join(sys.argv[2:])
                                                                          )
    elif cmd == 'sync':
        assert not isEmpty(g_space_path), 'Invalid wing workspace'
        doWingSync()
        cmd = 'cd "%s" && python framework/wing_sync.py "%s" "%s" %s' % (g_wing_path,
                                                                         formatArgument(g_space_path),
                                                                         formatArgument(g_env_path),
                                                                         ' '.join(sys.argv[2:])
                                                                         )
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
        cmd = 'cd "%s" && python framework/wing_git.py "%s" "%s" %s' % (g_wing_path,
                                                                        formatArgument(g_space_path),
                                                                        formatArgument(g_env_path),
                                                                        cmdStr
                                                                        )
    elif cmd.startswith('-'):
        # assert not isEmpty(g_space_path), 'Invalid wing workspace'
        cmd = 'cd "%s" && python framework/wing_extend.py "%s" "%s" %s' % (g_wing_path,
                                                                           formatArgument(g_env_path if isEmpty(g_space_path) else g_space_path),
                                                                           formatArgument(g_env_path),
                                                                           ' '.join(sys.argv[1:])
                                                                           )
    else:
        # assert not isEmpty(g_space_path), 'Invalid wing workspace'
        cmd = 'cd "%s" && python framework/wing_git.py "%s" "%s" %s' % (g_wing_path,
                                                                        formatArgument(g_env_path if isEmpty(g_space_path) else g_space_path),
                                                                        formatArgument(g_env_path),
                                                                        ' '.join(sys.argv[1:])
                                                                        )
    # println(cmd)
    succ = doCmdCall(cmd)
    assert succ, 'Error: fail'


if __name__ == "__main__":
    run()
