#!/usr/bin/env python3

def phrase_incomplete(phrase):
    if len(phrase) == 1:
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

def sentence_incomplete(sent, bd):
    ls = []
    cur = []
    for ln in sent.splitlines():
        if ln[0] == ';':
            if cur and bd in ln:
                ls.append(cur[:])
                cur = []
        elif ln[0] == '\t':
            cur[-1] += ' ' + ln.strip()
        else:
            cur.append(ln.strip())
    if cur:
        ls.append(cur)
    for p in ls:
        r = phrase_incomplete([l for l in p if '@punct' not in l])
        if r:
            return r
    return False

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('book', action='store')
parser.add_argument('-s', '--start', action='store', type=int, default=1)
parser.add_argument('-l', '--level', choices=['pb', 'cb', 'sb'], default='pb')
args = parser.parse_args()

with open(f'{args.book}.parsed.cg3.txt') as fin:
    sents = fin.read().strip().split('\n\n')
    n = 0
    for i, s in enumerate(sents, 1):
        r = sentence_incomplete(s, args.level)
        if r:
            n += 1
            if n == args.start + 10:
                break
            if n >= args.start:
                print(f'{n}\t{i}\t{r}')
