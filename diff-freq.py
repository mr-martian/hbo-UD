#!/usr/bin/env python3

import utils
from collections import Counter, defaultdict
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('book', action='store')
parser.add_argument('-r', action='store')
parser.add_argument('-c', action='store', type=int, default=0)
args = parser.parse_args()

fgen = f'temp/macula-merged/{args.book}.conllu'
fref = f'data/checked/{args.book}.conllu'

gen = utils.load_conllu(fgen)
ref = utils.load_conllu(fref, True)

def parse(block):
    dct = {}
    for cols in utils.iter_words(block):
        dct[cols[0]] = (cols[6], cols[7])
    return dct

change = Counter()
first = defaultdict(list)
err_count = defaultdict(list)

word_count = 0

for sid in gen:
    g = parse(gen[sid][1])
    if sid in ref:
        r = parse(ref[sid][1])
    else:
        #print(f'Reference for {args.book} {gen[sid][0]} not found.')
        continue
    n = 0
    for k in g:
        word_count += 1
        if k not in r:
            continue
        if r[k] == g[k]:
            continue
        n += 1
        gh, gr = g[k]
        rh, rr = r[k]
        key = rr
        if rr != gr:
            key += '>'+gr
        #    change[key] += 1
        #if gh != rh:
        #    key += '*'
        if args.r and args.r not in key:
            continue
        change[key] += 1
        first[key].append(gen[sid][0])
    if n != 0:
        err_count[n].append(gen[sid][0])

total = 0
for key, count in change.most_common():
    ls = first[key]
    c = len(ls)
    if args.c > 0:
        ls = [l for l in ls if l in err_count[args.c]]
        c = len(ls)
    if ls:
        print(count if c == count else f'{c}/{count}', key.ljust(20).rjust(25), ls[:25])
    if key not in ['punct', 'punct*']:
        total += count
if not args.r:
    print('Total word errors:', total, '/', word_count, '=', str(round(100.0*total/word_count, 2))+'%')
if args.c == 0:
    for n, ls in sorted(err_count.items()):
        print(n, ls[:10], f'({len(ls)})')
