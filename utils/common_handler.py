#!/usr/bin/python

__author__      = 'yangrq@kuxun.com'
__date__        = '2012-08-31'

import os
import sys

class CommonHandler:
    def ToUnicode(self, s, encoding='utf8'):
        result = u''
        if s is None:
            result = u''
        elif isinstance(s, unicode):
            result = s
        else:
            result = str(s).decode(encoding, 'ignore')
        return result

    def ToString(self, s, encoding='utf8'):
        result = ''
        if s is None:
            result = ''
        elif isinstance(s, unicode):
            result = s.encode(encoding, 'ignore')
        else:
            result = str(s)
        return result

    def ToInt(self, item, default=0):
        result = default
        try:
            result = int(item)
        except ValueError, e:
            result = default
        return result

    def LoadList(self,dataname,sep='\n'):
        content = self.LoadFile(dataname)
        list = content.split(sep)
        return list

    def LoadFile(self,filename,mode='r'):
        content = ''
        try:
            fp = open(filename,mode)
            try:
                content = fp.read()
            finally:
                fp.close()
        except IOError,e:
            print >>sys.stderr,'#Error:','open'+filename,str(e)
        return content


def main():
    ''' main function
    '''
    a = CommonHandler()
    a.LoadList('/home/aa')

if __name__ == '__main__':
    main()
