#!/usr/bin/python

__author__      = 'yangrq@kuxun.com'
__date__        = '2012-08-31'

import os
import sys
import logging

def _tmp_cmp(x,y):
    if x == y:
        return 0
    elif x < y:
        return -1
    else:
        return 1

class CommonHandler(object):

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

    def LoadFile(self, filename, mode='r'):
        content = ''
        try:
            obj = open(filename, mode)
            try:
                content = obj.read()
            except Exception,e:
                print >> sys.stderr, '#Error: read', filename, str(e) 
            finally:
                obj.close()
        except IOError,e:
            print >>sys.stderr, '#Error: open', filename, str(e)
        return content

    def LoadList(self, dataname, sep='\n', trim_last_empty_line=True):
        content = self.LoadFile(dataname)
        l = content.split(sep)
        if trim_last_empty_line and len(l[-1]) == 0:
            l = l[:-1]
        return l

    def SaveFile(self, filename, content, mode="w"):
        ret = False
        try:
            obj = open(filename, mode)
            try:
                obj.write(content)
                ret = True
            except Exception,e:
                print >> sys.stderr, '#Error: write', filename, str(e)
            finally:
                obj.close()
        except IOError, e:
            print >> sys.stderr, 'Error: open', filename, str(e)
        return ret

    def SaveList(self, filename, content_list, mode="w"):
        ret = False
        try:
            obj = open(filename, mode)
            try:
                for line in content_list:
                    obj.write(line + "\n")
                ret = True
            except Exception,e:
                print >> sys.stderr, '#Error: write', filename, str(e)
            finally:
                obj.close()
        except IOError, e:
            print >> sys.stderr, 'Error: open', filename, str(e)
        return ret

    def CrawlUrl(self, url, try_times=1, timeout=10):
        import urllib2
        html = ""
        logging.info(url)
        for i in range(try_times):
            try:
                html = urllib2.urlopen(url, timeout=timeout).read()
            except Exception, e:
                logging.warn("CrawlUrl error: %s" % str(e))
                continue
            if len(html) > 0:
                break
        return html

    # list format: [[],[]]
    def DiffList(self, list1, list2, compare=_tmp_cmp):
        idx1 = 0
        idx2 = 0

        only_exists_in_list1 = []
        only_exists_in_list2 = []
        both_exists          = []
        while idx1 < len(list1) and idx2 < len(list2):
            if len(list1[idx1]) != len(list2[idx2]):
                raise Exception, 'length error: %d [%s], %d [%s]' % (idx1, str(list1[idx1]), idx2, str(list2[idx2]))
            offset = 0
            offset_len = len(list1[idx1])
            cmp_ret = 0
            while offset < offset_len:
                cmp_ret = compare(list1[idx1][offset], list2[idx2][offset])
                if cmp_ret != 0:
                    break
                offset += 1

            if cmp_ret < 0:
                only_exists_in_list1.append(list1[idx1])
                idx1 += 1
            elif cmp_ret > 0:
                only_exists_in_list2.append(list2[idx2])
                idx2 += 1
            else:
                both_exists.append(list1[idx1])
                idx1 += 1
                idx2 += 1
#            print cmp_ret, only_exists_in_list1, both_exists, only_exists_in_list2 

        while idx1 < len(list1):
            only_exists_in_list1.append(list1[idx1])
            idx1 += 1

        while idx2 < len(list2):
            only_exists_in_list2.append(list2[idx2])
            idx2 += 1

        return (only_exists_in_list1, both_exists, only_exists_in_list2)

    # list is [1,2,3]
    def SimpleDiffList(self, list1, list2, compare=_tmp_cmp):
        idx1 = 0
        idx2 = 0

        only_exists_in_list1 = []
        only_exists_in_list2 = []
        both_exists          = []
        while idx1 < len(list1) and idx2 < len(list2):
            cmp_ret = compare(list1[idx1], list2[idx2])
            if cmp_ret < 0:
                only_exists_in_list1.append(list1[idx1])
                idx1 += 1
            elif cmp_ret > 0:
                only_exists_in_list2.append(list2[idx2])
                idx2 += 1
            else:
                both_exists.append(list1[idx1])
                idx1 += 1
                idx2 += 1
#            print cmp_ret, only_exists_in_list1, both_exists, only_exists_in_list2 

        while idx1 < len(list1):
            only_exists_in_list1.append(list1[idx1])
            idx1 += 1

        while idx2 < len(list2):
            only_exists_in_list2.append(list2[idx2])
            idx2 += 1

        return (only_exists_in_list1, both_exists, only_exists_in_list2)


def test_diff():
    l1 = [[1], [2], [3], [4], [5], [7]]
    l2 = [[1], [2], [3], [4], [6], [8]]
    a = CommonHandler()
    print a.DiffList(l1, l2)

def simple_diff():
    l1 = [1,2,3,4,5,7]
    l2 = [1,2,3,4,6,8]
    a = CommonHandler()
    print a.SimpleDiffList(l1, l2)

def main():
    ''' main function
    '''
    a = CommonHandler()
    l = a.LoadList('/home/yangrq/hadoop.sql')
    for i in l:
        print i

if __name__ == '__main__':
    main()
