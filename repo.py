#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  ......
# @date:   2023.05.10 14:40:50

import os, sys, shutil, subprocess, json
try: from urllib import request as urllib2
except: import urllib2

try:
    if sys.version_info.major < 3: # 2.x
        reload(sys)
        sys.setdefaultencoding('utf8')
    elif 3 == sys.version_info.major and sys.version_info.minor <= 3: # 3.0 ~ 3.3
        import imp
        imp.reload(sys)
    else: # 3.4 <=
        import importlib
        importlib.reload(sys)
except Exception as e:
    pass

g_ver = '0.9'# do not changed format !!!
g_date = '2023.05.12'
# g_git_host_fmt = 'ssh://%s@gerrit.xxx.com:29418'
g_git_host_fmt = 'git@codeup.aliyun.com:63e5fbe89dee9309492bc30c'
g_git_repo_remote = 'platform/repo'
g_git_repo_branch = 'master'
# --------------------------------------------------------------------------------------------------------------------------
# init project env
g_env_path = os.getcwd()
minGap = 1 if g_env_path.startswith(os.sep) else 4# windows("C://")
g_repo_path = g_env_path
while minGap < len(g_repo_path):
    if os.path.exists(g_repo_path + '/.repo/repo'): break
    g_repo_path = os.path.dirname(g_repo_path)
else:
    g_repo_path = g_env_path
# --------------------------------------------------------------------------------------------------------------------------
def println(*p):
    if 1 == len(p): print(p[0])
    else: print(p)
    sys.stdout.flush()

def doCmd(cmd):
    try:
        # print(cmd)
        # ret = subprocess.check_output(cmd, shell=True)
        # return ret.decode()
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        line, l = '', ' '
        while l != '' or p.poll() is None:
            l = p.stdout.readline().decode()
            line += l
        return line
    except Exception as e:
        println(e)
    return ''

def doCmdCall(cmd):
    try:
        # return subprocess.call(cmd, shell=True)
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        l = ' '
        while l != '' or p.poll() is None:
            l = p.stdout.readline().decode()
            print(l.strip())
        return p.returncode
    except Exception as e:
        println(e)
    return -100

def doRepoSync(path, userName):
    repoPath = path + os.sep + '.repo'
    if not os.path.isdir(repoPath):
        os.makedirs(repoPath)

    fetchGitRepo(repoPath, userName)
    doCmd('chmod a+x %s ' % repoPath)

def isEmpty(s):
    return None == s or len(s) <= 0

def hasBranch(path, branch):
    branches = doCmd('cd %s && git branch' % (path))
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

def getConfigFromLocal(path, k):
    try:
        path = path + os.sep + '.repo' + os.sep + 'cache.json'
        with open(path, 'rb') as f: content = f.read()
        #json.loads(content, ensure_ascii=False)
        jdata = json.loads(content)
        return jdata['repo'][k] if 'repo' in jdata else None
    except Exception as e:
        println(e)
    return None

def getRepoVersion(rf):
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
    if l < ls: return 1
    elif l < ld: return -1
    return 0

def fetchGitRepo(repoPath, userName):
    println('check repo')
    relPath = repoPath + os.sep + 'repo'  # /home/{project name}/.repo/repo
    if os.path.isdir(relPath): # Exist, then git pull
        doCmd('cd %s && git pull' % (relPath))
    else:# Not exist, then clone
        if not os.path.exists(repoPath): os.makedirs(repoPath)
        host = g_git_host_fmt % userName if 0 <= g_git_host_fmt.find('%s') else g_git_host_fmt
        doCmd('cd %s && git clone %s/%s' % (repoPath, host, g_git_repo_remote))
        assert os.path.isdir(relPath + os.sep + '.git'), 'Make sure have correct access rights for ' + g_git_repo_remote + ' !'

    if hasBranch(relPath, g_git_repo_branch):
        ret = doCmdCall('cd %s && git checkout %s' % (relPath, g_git_repo_branch))
        assert 0 == ret or '0' == ret, 'Error: git checkout origin'
    else:
        # ret = doCmdCall('cd %s && git fetch origin %s:%s' % (relPath, svrVer, svrVer))
        # assert 0 == ret or '0' == ret, 'Error: git fetch origin'
        ret = doCmdCall('cd %s && git checkout -b %s origin/%s' % (relPath, g_git_repo_branch, g_git_repo_branch))
        assert 0 == ret or '0' == ret, 'Error: git checkout origin'

    assert getCurrentBranch(relPath) == g_git_repo_branch

    # doCmdCall('cd %s && git branch --set-upstream-to=origin/%s %s' % (relPath, svrVer, svrVer))
    ret = doCmdCall('cd %s && git pull origin %s' % (relPath, g_git_repo_branch))
    assert 0 == ret or '0' == ret, 'Error: git pull origin'
    println('check repo done.')

    localVer = getRepoVersion(relPath + '/repo.py')
    if 0 <= compareVer(g_ver, localVer): return
    repo_file = os.path.realpath(sys.argv[0])
    shutil.copyfile(relPath + os.sep + 'repo.py', repo_file)
    println('update repo %s -> %d done.' % (g_ver, localVer))

def checkGitEnv():
    ret = doCmd('git --version')
    if None == ret: return False
    ret = ret.strip()
    return ret.startswith('git version ')

def parseInitArguments(path, argvs):
    '''
    # win: python repo.py init abc zhangsan develop xxx.xml
    # osx/Linux: repo init abc zhangsan develop xxx.xml
    '''
    svrMode = 0 < path.find('jenkins')
    return argvs, svrMode
    # user, project, branch, xml = None, None, None, None
    # for i in range(len(argvs)):
    #     if argvs[i] == '-u':
    #         tmp = argvs[i+1]
    #         tmp = tmp[len('ssh://'):]
    #         pos = tmp.find('@')
    #         user = tmp[:pos]
    #         tmp = tmp[pos:]
    #         pos = tmp.find('/')
    #         project = tmp[pos+1:]
    #     elif argvs[i] == '-b':
    #         branch = argvs[i+1]
    #     elif argvs[i] == '-m':
    #         xml = argvs[i+1]
    # assert None != user and None != project and None != branch and None != xml, 'Parse argument fail'
    # return [argvs[0], argvs[1], project, user, branch, xml], svrMode

def parseSyncArguments(argvs):
    '''
    # repo sync
    # repo sync -f
    '''
    for a in argvs:
        if a == '-d': return [argvs[0], argvs[1], '-f']
    return argvs

def showHelp():
    if None != g_repo_path and os.path.exists(g_repo_path + '/.repo/repo/help.txt'):
        try:
            with open(g_repo_path + '/.repo/repo/help.txt', 'r') as f: print(f.read())
            return
        except Exception as e:
            println(e)
    print('''
        repo commands
           init      first checkout code, like this: {project name} {user name} {branch name} {xml name}, such as: 
                        abc zhangsan develop client.xml
                        adb zhangsan develop server.xml
           sync [-f] [-i] update git code from repo manifest git, -f: force switch to repo branch, -i: ignore git sync fail
           
        git commands: work on the current change (see also: git help everyday)
           add       Add file contents to the index
           mv        Move or rename a file, a directory, or a symlink
           restore   Restore working tree files
           rm        Remove files from the working tree and from the index

        git commands: examine the history and state (see also: git help revisions)
           bisect    Use binary search to find the commit that introduced a bug
           diff      Show changes between commits, commit and working tree, etc
           grep      Print lines matching a pattern
           log       Show commit logs
           show      Show various types of objects
           status    Show the working tree status

        git commands: grow, mark and tweak your common history
           branch    List, create, or delete branches
           commit    Record changes to the repository
           merge     Join two or more development histories together
           rebase    Reapply commits on top of another base tip
           reset     Reset current HEAD to the specified state
           switch    Switch branches
           tag       Create, list, delete or verify a tag object signed with GPG

        git commands: collaborate (see also: git help workflows)
           fetch     Download objects and refs from another repository
           pull      Fetch from and integrate with another repository or a local branch
           push      Update remote refs along with associated objects
        ''')

def run():
    if len(sys.argv) < 2:
        showHelp()
        return

    if not checkGitEnv():
        println('No git command env found !!!')
        return

    cmd = sys.argv[1]
    if cmd in ['-v','--v','-version','--version']:
        println('repo %s (%s)' % (g_ver, g_date))
        return

    if cmd == 'init':
        argvs, svrMode = parseInitArguments(g_repo_path, sys.argv)
        # println(argvs)
        doRepoSync(g_repo_path, argvs[3])
        cmd = 'cd %s/.repo/repo && python manager/repo_init.py %s %s ' % (g_repo_path, g_repo_path, ' '.join(argvs[2:]))
    elif cmd == 'sync':
        assert None != g_repo_path, 'Invalid repo project'
        argvs = parseSyncArguments(sys.argv)
        doRepoSync(g_repo_path, getConfigFromLocal(g_repo_path, 'name'))
        cmd = 'cd %s/.repo/repo && python manager/repo_sync.py %s %s' % (g_repo_path, g_repo_path, ' '.join(argvs[2:]))
    elif cmd == 'manifest':
        println('Ignore command: ' + ' '.join(sys.argv))
        return
    elif cmd == 'forall':#repo forall -c "git reset --hard"
        assert None != g_repo_path, 'Invalid repo project'
        cmdStr = ' '.join(sys.argv[2:])
        pos = cmdStr.find('git ')
        if pos < 0:
            println('Ignore command: ' + ' '.join(sys.argv))
            return
        cmdStr = cmdStr[pos+len('git '):]# got "reset --hard"
        cmd = 'cd %s/.repo/repo && python manager/repo_git.py %s %s' % (g_repo_path, g_repo_path, cmdStr)
    elif cmd.startswith('-'):
        assert None != g_repo_path, 'Invalid repo project'
        cmd = 'cd %s/.repo/repo && python manager/repo_extend.py %s %s %s' % (g_repo_path, g_repo_path, g_env_path, ' '.join(sys.argv[1:]))
    else:
        assert None != g_repo_path, 'Invalid repo project'
        cmd = 'cd %s/.repo/repo && python manager/repo_git.py %s %s' % (g_repo_path, g_repo_path, ' '.join(sys.argv[1:]))
    # println(cmd)
    ret = doCmdCall(cmd)
    assert 0 == ret or '0' == ret,  'Error: fail'

if __name__ == "__main__":
    run()
