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
def btlog_init(logfile_name=None, console=False, logfile=True, maxBytes=52428800, verbose=False):
    global __btlog_init__
    if __btlog_init__:
        return
    __btlog_init__ = True

    if verbose:
        fmt = "%(asctime)s %(levelname)-8s - %(message)s [%(filename)s:%(lineno)d](%(funcName)s)"
    else:
        fmt = "%(asctime)s %(levelname)-8s - %(message)s"

    if not logfile_name:
        logfile_name= "btlog.log"

    root_logger     = logging.getLogger()
    formatter       = logging.Formatter(fmt)

    if logfile:
        hdlr = logging.handlers.RotatingFileHandler(logfile_name, maxBytes=maxBytes, backupCount=10)
        hdlr.setFormatter(formatter)
        root_logger.addHandler(hdlr)

    if console:
        hdlr1 = logging.StreamHandler()
        hdlr1.setFormatter(formatter)
        root_logger.addHandler(hdlr1)

def test():
    btlog_init('test.log', logfile=False, console=True, verbose=True)

    logging.debug('debug string')
    logging.info('info string')
    logging.warn('warn string')


if __name__ == '__main__':
    test()
    logging.getLogger().setLevel(logging.DEBUG)
    test()
