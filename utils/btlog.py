#!/usr/bin/python

__author__      = 'yangrq@kuxun.com'
__date__        = '2012-08-01'

import logging
import logging.handlers

'''
FILE_PATH   = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename="%s/log_processor.log" % (FILE_PATH),
                    filemode='a')
'''

__btlog_init__  = False
def btlog_init(logfile_name=None, console=False, logfile=True, maxBytes=52428800, verbose=False,
               level=logging.INFO, dayrotating=False):
    global __btlog_init__
    if __btlog_init__:
        return
    __btlog_init__ = True

    level_mapping   = {
        'DEBUG'     : logging.DEBUG,
        'INFO'      : logging.INFO,
        'WARNING'   : logging.WARNING,
        'ERROR'     : logging.ERROR,
        'CRITICAL'  : logging.CRITICAL,
        'NOTSET'    : logging.NOTSET,
    }

    if isinstance(level, str):
        level = level.upper()
    level = level_mapping.get(level, level)

    if verbose:
        fmt = "%(asctime)s %(levelname)-8s - %(message)s [%(filename)s:%(lineno)d](%(funcName)s)"
    else:
        fmt = "%(asctime)s %(levelname)-8s - %(message)s"

    if not logfile_name:
        logfile_name= "btlog.log"

    root_logger     = logging.getLogger()
    formatter       = logging.Formatter(fmt)

    if logfile:
        if dayrotating:
            from datetime import datetime
            logfile_name = logfile_name + ".%s" % datetime.now().strftime("%Y-%m-%d")
        hdlr = logging.handlers.RotatingFileHandler(logfile_name, maxBytes=maxBytes, backupCount=10)
        hdlr.setFormatter(formatter)
        root_logger.addHandler(hdlr)

    if console:
        hdlr1 = logging.StreamHandler()
        hdlr1.setFormatter(formatter)
        root_logger.addHandler(hdlr1)

    root_logger.setLevel(level)


def test_log():
    logging.debug('debug string')
    logging.info('info string')
    logging.warn('warn string')

def test():
    btlog_init('test.log', logfile=False, console=True, verbose=True)
    print 'before'
    test_log()
    logging.getLogger().setLevel(logging.DEBUG)
    print 'after'
    test_log()

def test2():
    btlog_init('test.log', logfile=True, console=True, verbose=True, level='warning', dayrotating=True)
    test_log()

if __name__ == '__main__':
    test2()
