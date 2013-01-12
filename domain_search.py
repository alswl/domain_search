#coding=utf-8

"""
搜索常见字全拼域名
"""

import sys
import urllib2
import codecs
import time
from datetime import datetime

try:
    import gevent.monkey; gevent.monkey.patch_all()
except ImportError:
    pass
import pinyin

def init():
    phrases = []
    f = codecs.open('words.dic', encoding='utf-8')
    words = [x.strip() for x in f.read().splitlines()]
    words.append(u'')
    f.close()
    pinyins = set([pinyin.get_pinyin(x) for x in words if len(x) > 0])
    for i in pinyins:
        for j in pinyins:
            phrases.append(i + j)
    return [x for x in set(phrases)]

def can_taken(domain):
    try:
        req = urllib2.Request(
            url='http://whomsy.com/api/' + domain
        )
        urlf = urllib2.urlopen(req, timeout=10)
        content = urlf.read()
        if 'No match' in content:
            return True
    except Exception, e:
        pass
    return False

def search(domains, results):
    i = 0
    now = datetime.now()
    sys.stdout.write('Date: %s' %now.strftime('%Y-%m-%d %H:%M:%S\n\n'))
    for domain in domains:
        if domain in results:
            continue
        sys.stdout.write('Domain: %s' %domain)
        if can_taken(domain):
            sys.stdout.write(' [v]\n')
            i += 1
        else:
            sys.stdout.write(' [x]\n')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\nTotal: %d, avaiable: %d\n\n' %(len(domains), i))
    sys.stdout.flush()

def main():
    words = init()
    domains = [x + '.com' for x in words]
    results_file = codecs.open('results.txt', encoding='utf-8')
    results = results_file.read()
    results_file.close()
    search(domains, results)

if __name__ == '__main__':
    main()
