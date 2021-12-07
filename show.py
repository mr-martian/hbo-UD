#!/usr/bin/env python3

import argparse
import sys

import utils

parser = argparse.ArgumentParser()
parser.add_argument('-c', action='store_true', help='Show CG only')
parser.add_argument('-g', action='store_true', help='Show generated conllu only')
parser.add_argument('-r', action='store_true', help='Show reference conllu only')
parser.add_argument('n', action='store', type=int, help='Sentence index')
args = parser.parse_args()

if not args.g and not args.r:
    with open('generated.cg3.txt') as fin:
        print(fin.read().strip().split('\n\n')[int(args.n)])
    if args.c:
        sys.exit(0)

gen = utils.load_conllu('generated.conllu')
sid = None
for k in gen:
    if gen[k][0] == args.n:
        sid = k
        break
else:
    print(f'No sentence found at index {args.n}')
    sys.exit(1)

if args.r:
    ref = utils.load_conllu('checked.conllu', True)
    if sid in ref:
        print(ref[sid][1])
    else:
        print(f'Sentence at index {args.n} ({sid}) has not been confirmed.')
        sys.exit(1)
else:
    print(gen[sid][1])
