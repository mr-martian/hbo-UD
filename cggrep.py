#!/usr/bin/env python3

import argparse
import re
import utils

parser = argparse.ArgumentParser()
parser.add_argument('book', action='store')
parser.add_argument('query', action='store')
parser.add_argument('-i', action='store_true')
parser.add_argument('-v', action='store')
parser.add_argument('-l', action='store_true')
args = parser.parse_args()

n = 1
cur = []
pat = re.compile(args.query, re.MULTILINE)
negpat = None
if args.v:
    negpat = re.compile(args.v)

ct = 0

with open(f'temp/macula-parsed-cg3/{args.book}.txt') as fin:
    for l in fin:
        if not l.strip():
            blk = '\n'.join(cur)
            if pat.search(blk) and (not negpat or not negpat.search(blk)):
                if not args.i:
                    print('----------')
                if args.l:
                    print(n, f'length={len(cur)}')
                else:
                    print(n)
                if not args.i:
                    print(blk)
                ct += 1
            cur = []
            n += 1
        else:
            cur.append(l.rstrip())

print('----------')
print(f'Showing {ct} matches')
