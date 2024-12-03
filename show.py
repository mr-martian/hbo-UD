#!/usr/bin/env python3

import argparse
import sys

import utils

parser = argparse.ArgumentParser()
parser.add_argument('-c', action='store_true', help='Show CG only')
parser.add_argument('-g', action='store_true', help='Show generated conllu only')
parser.add_argument('-r', action='store_true', help='Show reference conllu only')
parser.add_argument('-R', action='store_true', help='Show CG input')
parser.add_argument('b', action='store', help='Book')
parser.add_argument('n', action='store', type=int, help='Sentence index')
args = parser.parse_args()

if not args.g and not args.r:
    with open(f'temp/macula-parsed-cg3/{args.b}.txt') as fin:
        print(fin.read().strip().split('\n\n')[int(args.n)-1])
    if args.c:
        sys.exit(0)

gen = utils.load_conllu(f'temp/macula-merged/{args.b}.conllu')
sid = None
for k in gen:
    if gen[k][0] == args.n:
        sid = k
        break
else:
    print(f'No sentence found at index {args.n}')
    sys.exit(1)

if args.r:
    ref = utils.load_conllu(f'data/checked/{args.b}.conllu', True)
    if sid in ref:
        print(ref[sid][1])
    else:
        print(f'Sentence at index {args.n} ({sid}) has not been confirmed.')
        sys.exit(1)
else:
    print(gen[sid][1])

if args.R:
    with open(f'temp/macula-cg3/{args.b}.txt') as fin:
        cur = []
        i = -1
        for line in fin:
            if not line.strip():
                continue
            cur.append(line.rstrip())
            if '#1→' in cur[-1]:
                if i == args.n:
                    print('\n'.join(cur[:-2]))
                    break
                else:
                    cur = cur[-2:]
                    i += 1
