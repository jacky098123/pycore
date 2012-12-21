#/usr/bin/python

__author__      = 'yangrq@kuxun.com'
__date__        = '2012-08-30'

'''
for simple:
    urllib.urlopen(url, data)
    urllib.urlretrieve(url, filename)
'''

import logging
import traceback
import urllib
import httplib

class HttpClient:
    def __init__(self, host, port=None, secure_flag=False):
        if secure_flag:
            if not port:
                port = 443
            self.conn = httplib.HTTPSConnection(host, port)
        else:
            if not port:
                port = 80
            self.conn = httplib.HTTPConnection(host, port)
#        self.conn.set_debuglevel(5)


    def DoRequest(self, method, uri, body='', headers=None):
        logging.info('method: %s, uri: %s, heads: %s, body length: %d' % (
                method, uri, str(headers), len(body)))

        if not headers:
            headers = {}
        if not isinstance(headers, dict):
            raise Exception, 'http header is not dict'
        if not headers.has_key("User-Agent"):
            headers["User-Agent"]   = "Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1"
        if not headers.has_key("Content-type"):
            headers["Content-type"] = "application/x-www-form-urlencoded"
        if not headers.has_key("Accept"):
            headers["Accept"]       = "text/plain"

        ret = None
        try:
            self.conn.request(method, uri, body, headers)
            resp = self.conn.getresponse()
            if resp.status == 200:
                logging.info("HTTP 200")
                ret = resp.read()
            else:
                logging.error("ERROR: request %s error: %s", method, resp.reason)
        except:
            logging.error("traceback: %s" % traceback.print_exc())

        return ret


def test_get():
    c = HttpClient('www.sohu.com')
    ret = c.DoRequest('GET', '/')
    print 'data length: ', len(ret)


def test_post():
    headers = {"Content-type" : "application/x-www-form-urlencoded"}
    print headers

    body = "k1=%s&k2=%s" % (urllib.quote_plus("value 1"), urllib.quote_plus("v:%//2"))
    print body

    c = HttpClient('www.sohu.com')
    ret = c.DoRequest('POST', '/', body, headers)

    print ret

if __name__ == '__main__':
#    test_get()
    test_post()
