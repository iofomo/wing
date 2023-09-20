#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @brief:  utils for Properties file w/r
# @date:   2023.08.10 14:40:50

import sys, os


# ----------------------------------------------------------------------------------------------------------------------
class PropertiesUtils:

    @staticmethod
    def get(pf, k):
        if not os.path.isfile(pf): return ''

        k += '='
        with open(pf, 'r') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if len(line) < 3: continue
            if not line.startswith(k): continue
            return line[len(k):].strip()
        return ''

    @staticmethod
    def set(pf, k, v):
        k += '='
        newLines = []
        if os.path.isfile(pf):
            with open(pf, 'r') as f:
                lines = f.readlines()
            for line in lines:
                l = line.strip()
                if l.startswith(k): continue
                newLines.append(line)
        newLines.append(k + v + '\n')
        with open(pf, 'w') as f:
            f.writelines(newLines)

    @staticmethod
    def getAll(pf):
        if not os.path.isfile(pf): return ''

        items = {}
        with open(pf, 'r') as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if len(line) < 3: continue
            ll = line.split('=')
            items[ll[0]] = ll[1]
        return items
