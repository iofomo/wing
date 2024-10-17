#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Brief:  mk
# @Date:   2024.04.09 09:50:58
import csv

# --------------------------------------------------------------------------------------------------------------------------
class UtilCSV:

    def __init__(self, file):
        self.inFile = open(file, 'a')
        self.writer = csv.writer(self.inFile)

    # such as: ["name", "age"]
    def writeHeader(self, h):
        self.writer.writerow(h)

    # such as: ["Alice", 30]
    def writeData(self, d):
        self.writer.writerow(d)

    # such as: [["Alice", 30], ["Bob", 25]]
    def writeDatas(self, d):
        self.writer.writerows(d)

    def closeCSV(self):
        self.inFile.close()

    @staticmethod
    def readColumn(file, columnName):
        columns = []
        with open(file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            index = header.index(columnName)
            for row in reader: columns.append(row[index])
        return columns

# if __name__ == "__main__":
#     tst = UtilCSV("/Users/tst.csv")
#     tst.writeHeader(["a", "b"])
#     tst.writeData(["aa", "1,01"])
#     tst.writeDatas([["b.b", "1"], ["c,c", "2-"]])
#     tst.closeCSV()