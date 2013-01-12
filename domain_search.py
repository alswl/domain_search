#coding=utf-8

"""
搜索常见字全拼域名
"""

import sys
import urllib2
import codecs
import time
from datetime import datetime
import thread

import gevent.monkey; gevent.monkey.patch_all()
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

def can_taken_via_whomsy(domain, lock):
    can = False
    try:
        req = urllib2.Request(
            url='http://whomsy.com/api/' + domain
        )
        urlf = urllib2.urlopen(req, timeout=10)
        content = urlf.read()
        if not 'success' in content:
            return
        if 'No match' in content:
            can = True
    except Exception, e:
        pass
    if lock.acquire():
        sys.stdout.write('Domain: %s' %domain)
        if can:
            sys.stdout.write(' [v]\n')
        else:
            sys.stdout.write(' [x]\n')
        sys.stdout.flush()
        lock.release()

def can_taken_via_whois(domain, lock):
    can = False
    try:
        process = subprocess.Popen('whois "log4d.com"', shell=True,
                                   stdout=subprocess.PIPE)
        content = process.stdout.read()
        if 'No match' in content:
            can = True
    except Exception, e:
        pass
    if lock.acquire():
        sys.stdout.write('Domain: %s' %domain)
        if can:
            sys.stdout.write(' [v]\n')
        else:
            sys.stdout.write(' [x]\n')
        sys.stdout.flush()
        lock.release()

def search(domains, results):
    now = datetime.now()
    lock = thread.allocate()
    sys.stdout.write('Date: %s' %now.strftime('%Y-%m-%d %H:%M:%S\n\n'))
    for domain in domains:
        if domain in results:
            continue

        #thread.start_new(can_taken, (domain, lock))
        can_taken_via_whois(domain, lock)
        time.sleep(0.5)
    sys.stdout.write('\n')
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
