#!/usr/bin/env python3

import sys
import re

wid = re.compile(r'<(w\d+p?)>')

heads = {}
tags = {}

with open(sys.argv[1]) as fin:
    for line in fin:
        ls = line.split('\t')
        if len(ls) != 3:
            continue
        heads[ls[0]] = ls[1]
        tags[ls[0]] = ls[2].rstrip()

cur = []

def process_cur():
    global cur
    locs = {}
    ls = []
    for i, l in enumerate(cur):
        m = wid.search(l)
        if m and '<wp2>' not in l and '<wp3>' not in l:
            locs[m.group(1)] = i + 1
            ls.append(m.group(1))
        else:
            ls.append(None)
    new_lines = []
    for i, (loc, ln) in enumerate(zip(ls, cur), 1):
        if not loc:
            new_lines.append(ln.replace('$', f'<#{i}→{i}>$'))
        else:
            dest = heads.get(loc, str(i))
            h = locs.get(dest, dest)
            ins = tags.get(loc, '') + f'<#{i}→{h}>'
            new_lines.append(ln.replace('$', ins+'$'))
    for l in new_lines:
        sys.stdout.write(l)
    cur = []

for line in sys.stdin:
    if not line.strip():
        process_cur()
        sys.stdout.write(line)
        continue
    cur.append(line)
    if '<svb>' in line:
        process_cur()
if cur:
    process_cur()
