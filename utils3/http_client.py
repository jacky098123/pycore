#!/usr/bin/python

__author__      = 'yangrq@kuxun.com'
__date__        = '2012-09-26'

'''
for simple:
    urllib.urlopen(url, data)
    urllib.urlretrieve(url, filename)
'''

import logging
import traceback
import urllib
import os
import sys
import httplib
import urllib
import logging
import traceback

class HttpClient(object):
    def __init__(self, debug=False):
        self._http_debug = debug
        pass

    # method may by: GET/DELETE/PURGE for RFC
    def DoGet(self, host, port=80, uri='/', headers={}, method='GET'):
        return self._DoRequest(host, port, method, uri, '', headers)

    def DoPost(self, host, port=80, uri='/', body=None, headers={}):
        return self._DoRequest(host, port, 'POST', uri, body, headers)

    def _DoRequest(self, host, port, method, uri, body, headers):
        ret = None
        conn = httplib.HTTPConnection(host, int(port), timeout=8)

        if hasattr(self, '_http_debug') and self._http_debug:
            conn.set_debuglevel(9)
        try:
            new_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1",
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain",
                }
            for k,v in headers.iteritems():
                new_headers[k] = v

            logging.debug("@HttpClient host: %s, port: %s, method: %s, uri: %s, headers: %s, body length: %s"
                          % (host, str(port), method, uri, str(new_headers), len(body)))
            conn.request(method, uri, body, new_headers)
            resp = conn.getresponse()
            if resp.status == 200:
                logging.info("HTTP 200")
                ret = resp.read()
                logging.debug("status 200")
            else:
                logging.error("ERROR: reason: %s" % resp.reason)
        except:
            logging.error("ERROR: traceback: %s" % traceback.print_exc())

        conn.close()
        return ret


def test_get():
    c = HttpClient()
    data = c.DoGet('www.sohu.com')
    print 'data length: ', len(data)
    print data[0:300]

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    test_get()
