#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  utils for zip/unzip file
# @date:   2023.08.10 14:40:50

import sys, os


class ImportUtils:

    @staticmethod
    def initEnv():
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
            import _locale
            _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])
        except Exception as e:
            pass
        g_env_path = os.getcwd()
        g_this_file = os.path.realpath(sys.argv[0])
        g_this_path = os.path.dirname(g_this_file)
        return g_env_path, g_this_file, g_this_path

    @staticmethod
    def initPath(env_path):
        repo_path = env_path
        minGap = 1 if env_path.startswith(os.sep) else 4  # windows("C://")
        while True:
            if len(repo_path) <= minGap: assert 0
            if os.path.exists(repo_path + '/.repo/repo'):
                sys.path.append(repo_path + '/.repo/repo')
                break
            repo_path = os.path.dirname(repo_path)
        return repo_path
