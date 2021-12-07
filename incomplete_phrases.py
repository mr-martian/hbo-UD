#!/usr/bin/env python3

import sys

def phrase_incomplete(phrase):
    if '@punct' in phrase[-1]:
        return phrase_incomplete(phrase[:-1])
    elif len(phrase) == 1:
        return False
    ls = []
    for w in phrase:
        for tg in w.split():
            if tg[0] == '#':
                slf, hd = tg[1:].split('->')
                ls.append((int(slf), int(hd)))
    minwd = ls[0][0]
    maxwd = ls[-1][0]
    selfhd = 0
    external = 0
    for s, h in ls:
        if h < minwd or h > maxwd:
            external += 1
        elif h == s:
            selfhd += 1
    #if (selfhd + external) > 1:
    if selfhd > 1:
        return f'{minwd}-{maxwd}'
    return False

def sentence_incomplete(sent):
    ls = []
    cur = []
    for ln in sent.splitlines():
        if ln[0] == ';':
            if cur:
                ls.append(cur[:])
                cur = []
        elif ln[0] == '\t':
            cur[-1] += ' ' + ln.strip()
        else:
            cur.append(ln.strip())
    if cur:
        ls.append(cur)
    for p in ls:
        r = phrase_incomplete(p)
        if r:
            return r
    return False

start = 0
lim = -1
if len(sys.argv) > 1:
    start = int(sys.argv[1])
    lim = start + 10

with open('generated.cg3.txt') as fin:
    sents = fin.read().strip().split('\n\n')
    n = 1
    for i, s in enumerate(sents, 1):
        r = sentence_incomplete(s)
        if r:
            n += 1
            if n >= start:
                print(f'{n}\t{i}\t{r}')
            if n == lim:
                break
