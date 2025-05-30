#!/usr/bin/env python3

import argparse
import utils

parser = argparse.ArgumentParser()
parser.add_argument('b', action='store', help='Book')
parser.add_argument('n', action='store', type=int, help='Sentence index')
parser.add_argument('modes', nargs='*',
                    choices=['cg', 'conllu', 'raw', 'ref', 'docs', 'latex'])
args = parser.parse_args()

for m in args.modes or ['cg', 'conllu']:
    block = utils.show(args.b, args.n, m)
    if block is None:
        print(f'{args.b} {args.n} not found in mode {m}.')
    else:
        print(block)
