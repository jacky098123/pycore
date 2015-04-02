import re
import sys 
import logging
from urlparse import urlparse

class KxSpiderUtil:
    def _to_unicode(self, s, encoding='utf8'):
        result = u''
        if s is None:
            result = u''
        elif isinstance(s, unicode):
            result = s
        else:
            result = str(s).decode(encoding, 'ignore')
        return result

    def _to_string(self, s, encoding='utf8'):
        result = ''
        if s is None:
            result = ''
        elif isinstance(s, unicode):
            result = s.encode(encoding, 'ignore')
        else:
            result = str(s)
        return result

    def _get_selector_single_item(self, _selector, _path):
        _lst = _selector.select(_path).extract()
        if len(_lst) == 0:
            return u''
        return _lst[0].strip()

    def _strip_tags(self, item_content):
        item_content = self._to_string(item_content)
        item_content = re.sub(r"(?i)<script[^>]*?>.*?</script>", "", item_content)
        item_content = re.sub(r"<[^>]*?>", "", item_content)
        pos = item_content.find(">")
        if pos >= 0:
            item_content = item_content[pos+1:]
        pos = item_content.find("<")
        if pos > 0:
            item_content = item_content[:pos]
        item_content = item_content.strip()
        return self._to_unicode(item_content)

    def _get_domain(self, url):
        url = self._to_string(url)
        o = urlparse(url)
        domain = o.netloc
        pos = domain.find(":")
        if pos > 0:
            domain = domain[0:pos]
        return self._to_unicode(domain)

    def _get_full_url(self, dest, src):
        dest = self._to_string(dest)
        src = self._to_string(src)
        if dest.startswith('http://'):
            return dest
        o = urlparse(src)
        if dest.startswith('/'):
            return self._to_unicode('http://' + o.netloc + dest)
        if dest.startswith('./'):
            pos = src.rfind('/')
            new_url = src[:pos] + dest[1:]
            return self._to_unicode(new_url)
        return self._to_unicode('http://' + o.netloc + '/' + dest)

    def _extract_boundary(self, html, former, latter, pos=0, strip_flag=False):
        html = self._to_string(html)
        logging.debug("html len: %d, former: [%s], latter: [%s], pos: %d, strip_flag: [%s]" % (len(html), former, latter, pos, str(strip_flag)))
        if former is None or len(former) == 0:
            former = ''
            pos = 0
        else:
            pos = html.find(former, pos)
        if pos < 0:
            return '', -1

        if latter is None or len(latter) == 0:
            latter = ''
            new_pos = len(html)
        else:
            new_pos = html.find(latter, pos+len(former))
        if new_pos < 0:
            return '', -1

        new_pos = new_pos + len(latter)
        if strip_flag:
            return html[pos+len(former):new_pos-len(latter)], new_pos
        return html[pos:new_pos], new_pos


if __name__ == '__main__':
    pass
