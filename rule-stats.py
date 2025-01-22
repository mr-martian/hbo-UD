#!/usr/bin/env python3

import sys
import utils
from collections import Counter
book = sys.argv[1]

parsed = utils.load_conllu(f'temp/merged/{book}.conllu')
checked = utils.load_conllu(f'data/checked/{book}.conllu')
cg3 = []
with open(f'temp/parsed-cg3/{book}.txt') as fin:
    cg3 = fin.read().strip().split('\n\n')

right = Counter()
wrong = Counter()

def get_rules(cg):
    ret = []
    for l in cg.splitlines():
        if not l or l[0] != '\t':
            continue
        cur = []
        for w in l.split():
            if w.startswith('SETPARENT:') or w.startswith('MAP:'):
                cur.append(w)
        ret.append(cur)
    return ret

for k in checked:
    for rl in get_rules(cg3[parsed[k][0]-1]):
        right.update(rl)

def word_lines(block):
    for l in block.splitlines():
        ls = l.split('\t')
        if len(ls) != 10: continue
        if not ls[0].isnumeric(): continue
        yield ls[6], ls[7]

with open(f'temp/stats/{book}.txt', 'w') as fout:
    l = set(list(right.keys()) + list(wrong.keys()))
    for k in sorted(l):
        fout.write(f'{k}\t{right[k]}\t{wrong[k]}\n')
