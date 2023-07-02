# coding=utf-8

"""
搜索常见字全拼域名
"""
import argparse
import codecs
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

executor = ThreadPoolExecutor(max_workers=8)


def init():
    from pypinyin import lazy_pinyin
    phrases = []
    f = codecs.open('words.dic', encoding='utf-8')
    words = [x.strip() for x in f.read().splitlines()]
    words.append('')
    f.close()
    pinyins = set([lazy_pinyin(x)[0] for x in words if len(x) > 0])
    for i in pinyins:
        for j in pinyins:
            phrases.append(i + j)
    return [x for x in set(phrases)]


def init_pinyin_less(length=3):
    from pypinyin import lazy_pinyin
    phrases = []
    f = codecs.open('words.dic', encoding='utf-8')
    words = [x.strip() for x in f.read().splitlines()]
    words.append('')
    f.close()
    pinyins = set([lazy_pinyin(x)[0] for x in words if len(x) > 0])
    return [x for x in set(pinyins) if len(x) == length]


def init_popular_less_2():
    return init_popular_less(2)

def init_popular_less_3():
    return init_popular_less(3)

def init_popular_less(limit):
    phrases = []
    f = codecs.open('./popular_less_%d.txt' % limit, encoding='utf-8')
    words = [x.strip() for x in f.read().splitlines()]
    words.append('')
    f.close()
    return words


def init_26():
    lst = 'abcdefghijklmnopqrstuvwxyz'
    phrases = []
    for i in lst:
        words = ''
        for j in lst:
            for k in lst:
                for l in lst:
                    phrases.append(i + j + k + l)
    return phrases


def write_log(domain, lock, can):
    if lock.acquire():
        sys.stdout.write('%d, Domain: %s' % (time.time(), domain))
        if can == False:
            sys.stdout.write(' [x]\n')
        elif can == True:
            sys.stdout.write(' [v]\n')
        elif can == None:
            sys.stdout.write(' [ ]\n')
        else:
            sys.stdout.write(' [?]\n')
        sys.stdout.flush()
        lock.release()


def can_taken_via_whomsy(domain, lock):
    import urllib.request, urllib.error, urllib.parse
    can = False
    try:
        req = urllib.request.Request(
            url='http://whomsy.com/api/' + domain
        )
        urlf = urllib.request.urlopen(req, timeout=10)
        content = urlf.read()
        if not 'success' in content:
            return
        if 'No match' in content:
            can = True
    except Exception as e:
        can = None
    write_log(domain, lock, can)
    return can


def can_taken_via_whois(domain, lock):
    can = False
    try:
        process = subprocess.Popen('whois %s' % domain, shell=True,
                                   stdout=subprocess.PIPE)
        content = str(process.stdout.read(), encoding='utf-8')
        if 'No match' in content:
            can = True
    except Exception as e:
        can = None
    write_log(domain, lock, can)
    return can


def can_taken_via_dig(domain, lock):
    can = False
    try:
        process = subprocess.Popen('dig @114.114.114.114 NS %s' % domain, shell=True,
                                   stdout=subprocess.PIPE)
        content = str(process.stdout.read(), encoding='utf-8')
        if '.gtld-servers.net.' in content:
            can = True
    except Exception as e:
        can = None
    write_log(domain, lock, can)
    return can


def search(domains):
    now = datetime.now()
    lock = threading.Lock()
    sys.stdout.write('Date: %s' % now.strftime('%Y-%m-%d %H:%M:%S\n\n'))
    for domain in domains:
        # if domain in results:
        #     continue

        # thread.start_new(can_taken_via_whois, (domain, lock))
        # can_taken_via_whois(domain, lock)
        executor.submit(can_taken_via_dig, domain, lock)
    sys.stdout.write('\n')
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prefix', type=str, default='')
    parser.add_argument('--suffix', type=str, default='.com')
    parser.add_argument('--type', type=str, default='pinyin4', choices=['pinyin4', '26', 'en3', 'en2'])
    args = parser.parse_args()

    if args.type is None:
        parser.print_help()
        return

    prefix = args.prefix
    suffix = args.suffix
    if args.type == 'pinyin4':
        words = [prefix + x for x in init_pinyin_less(4)]
    elif args.type == '26':
        words = [prefix + x for x in init_26()]
    elif args.type == 'en3':
        words = [prefix + x for x in init_popular_less_3()]
    elif args.type == 'en2':
        words = [prefix + x for x in init_popular_less_2()]
    else:
        parser.print_help()
        return

    domains = [x + suffix for x in words]
    search(domains)


if __name__ == '__main__':
    main()
