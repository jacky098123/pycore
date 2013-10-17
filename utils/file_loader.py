#!/usr/bin/python

__author__      = 'yangrq@kuxun.com'
__date__        = '2012-08-31'

'''
file format:
    $heaer (one line)
    $content (multi line)
file encoding: only gbk

load data local infile '' into table biz_landmark(city_id,name,spell,type);
'''

import os
import sys

class FileLoader(object):
    def __init__(self):
        self.head_idx = {}
        
    # return list
    def GetColumns(self, flag=''):
        raise Exception, 'derive class must implementation'

    def _parse_header(self, line):
        self.head_idx = {}
        items = line.lower().split(self.line_sep)
        for field in self.GetColumns():
            for idx in range(len(items)):
                if items[idx] == field:
                    self.head_idx[field] = idx
                    break

        if len(self.head_idx) != len(self.GetColumns()):
            raise Exception, "header line error: %s" % self.head_idx.keys()

    def _parse_line(self, line):
        items = line.split(self.line_sep)

        tmp_list = []
        for field in self.GetColumns():
            tmp_list.append(items[self.head_idx[field]])

        return "\t".join(tmp_list)

    def Load(self, filename, line_sep=","):
        self.line_sep = line_sep

        line_list = []
        try:
            obj = open(filename, "r")
            for line in obj:
                line = line.strip()
                if len(line) == 0:
                    continue
                line_list.append(line)
        except IOError,e:
            print >>sys.stderr, '#Error: open', filename, str(e)

        if len(line_list) == 1:
            logging.warn("file: %s has no content" % filename)
            return []

        self._parse_header(line_list[0])

        new_line_list = []
#        new_line_list.append(self.head_idx.keys())
        for line in line_list[1:]:
            new_line = self._parse_line(line)
            new_line_list.append(new_line)

        return new_line_list

class TestLoader(FileLoader):
    def __init__(self):
        FileLoader.__init__(self)

    def GetColumns(self):
        return ["id", "name"]

def main():
    ''' main function
    '''
    a = TestLoader()

if __name__ == '__main__':
    main()
