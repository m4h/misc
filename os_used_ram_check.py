'''
Auth    : Tom Lime
Date    : 09/12/2013
Purp    : CRITICAL if used memory > threshold; OK if less; UNKNOWN if any error 
occured
'''

import sys


def kb_to_gb(kb):
    return kb/1024.0/1024.0


def kb_to_mb(kb):
    return kb/1024.0


def parse_meminfo():
    meminfo = {}
    fn = '/proc/meminfo'
    for line in open(fn):
        elems = [elem for elem in line.split(' ') if elem != '']
        key = elems[0].strip(':')
        val = int(elems[1])
        meminfo.setdefault(key, val)
    return meminfo


def get_used_memory():
    meminfo = parse_meminfo()
    memtotl_kb = meminfo['MemTotal']
    memfree_kb = meminfo['MemFree']
    memused_kb = memtotl_kb - memfree_kb
    memused_gb = kb_to_gb(memused_kb)
    return memused_gb


if __name__ == '__main__':
    try:
        threshold = int(sys.argv[1])
    except Exception:
        threshold = 40

    try:
        used = get_used_memory()
        if used > threshold:
            print 'CRITICAL'
        else:
            print 'OK'
    except Exception as e:
        print 'UNKNOWN'

