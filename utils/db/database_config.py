#/usr/bin/python

__author__      = 'yangrq@kuxun.com'
__date__        = '2012-08-31'

import os
import sys
import glob

class DatabaseConfig:
    def __init__(self):
        self.config_path    = None
        self.db_config      = dict()


    def LoadConfig(self, path):
        self.config_path    = os.path.realpath(path)
        sys.path.append(self.config_path)

        file_list = glob.glob(self.config_path + '/*.py')
        for file in file_list:
            module_name  = os.path.basename(file)[:-3]
            if module_name in ['__init__', ]:
                continue
            module = __import__(module_name)

            module_items    = {}
            for target in dir(module):
                if target in ['__builtins__', '__doc__', '__file__', '__name__']:
                    continue
                v = getattr(module, target)
                if not isinstance(v, dict):
                    continue
                if not v.has_key('host') or not v.has_key('user') or not v.has_key('password') or not v.has_key('db'):
                    err_str = 'invalid target: %s, values: %s' % (target, str(v))
                    raise Exception, err_str
                module_items[target] = v
            if module_items:
                self.db_config[module_name] = module_items

        sys.path.pop() # pop lastest added path


    def GetConfig(self, module, target):
        if not self.db_config.has_key(module):
            logging.error('no module: %s' % module)
            return None
        if not self.db_config[module].has_key(target):
            logging.error('module: %s has no target: %s' % (module, target))
            return None
        return self.db_config[module][target]


    def Dump(self):
        for module_name, module  in self.db_config.iteritems():
            print 'DatabaseConfig %s %s %s' % ('*' * 20, module_name, '*' * 20)
            for target, d in module.iteritems():
                print target, ' = {'
                for k,v in d.iteritems():
                    print '\t', k, '\t', v
                print '}'


def test():
    c = DatabaseConfig()
    c.LoadConfig('../../tiger/pylib/config/')
    c.Dump()


if __name__ == '__main__':
    test()
