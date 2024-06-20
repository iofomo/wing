#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  utils for zip/unzip file
# @date:   2023.08.10 14:40:50

import sys, os


# --------------------------------------------------------------------------------------------------------------------------
class ImportUtils:

    g_inited = False
    g_space_path = None
    g_project_path = None

    @classmethod
    def getProjectPath(cls): return '' if None == cls.g_project_path else cls.g_project_path

    @classmethod
    def __init_coding__(cls):
        if cls.g_inited: return
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
                import io
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
                import importlib
                importlib.reload(sys)
            import _locale
            _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])
            cls.g_inited = True
        except Exception as e:
            pass

    @staticmethod
    def formatArgument(arg): return arg.replace('\\', '/') if sys.platform.lower().startswith('win') else arg

    @classmethod
    def initEnv(cls, projPath=None):
        if projPath is not None: cls.g_project_path = projPath

        ImportUtils.__init_coding__()
        wingPath = os.path.expanduser("~") + os.sep + '.wing/wing' #  such as: /Users/${username}/.wing/wing
        return ImportUtils.formatArgument(wingPath)

    @classmethod
    def initSpaceEnv(cls, path):
        if None != cls.g_space_path: return cls.g_space_path
        ImportUtils.__init_coding__()
        while True:
            if os.path.exists(path + '/.wing/space.json'):
                cls.g_space_path = path
                return cls.g_space_path# found wing-space
            ppath = os.path.dirname(path)
            if len(path) <= len(ppath): return None# invalid wing-space
            path = ppath
