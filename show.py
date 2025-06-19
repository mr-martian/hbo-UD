#!/usr/bin/env python3

import argparse
import utils

parser = argparse.ArgumentParser()
parser.add_argument('b', action='store', help='Book')
parser.add_argument('n', action='store', type=int, help='Sentence index')
parser.add_argument('modes', nargs='*',
                    choices=['cg', 'conllu', 'raw', 'ref', 'docs',
                             'latex', 'latexnp'])
parser.add_argument('-w', '--words', action='store')
args = parser.parse_args()

words = None
if args.words:
    a, b = args.words.split('-')
    words = (int(a), int(b))

for m in args.modes or ['cg', 'conllu']:
    block = utils.show(args.b, args.n, m, wrange=words)
    if block is None:
        print(f'{args.b} {args.n} not found in mode {m}.')
    else:
        print(block)
