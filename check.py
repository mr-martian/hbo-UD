#!/usr/bin/env python3

import argparse
import sys

import utils

parser = argparse.ArgumentParser()
parser.add_argument('--macula', '-m', action='store_true')
parser.add_argument('book', action='store')
args = parser.parse_args()

m = 'macula-' if args.macula else ''
fgen = f'temp/{m}merged/{args.book}.conllu'
fref = f'data/checked/{args.book}.conllu'

gen = utils.load_conllu(fgen)
ref = utils.load_conllu(fref, True)

fail = []
for k in ref:
    if k in gen and gen[k][1] != ref[k][1]:
        #print(f'Sentence {gen[k][0]} ({k}) differs!')
        fail.append(str(gen[k][0]))

if fail:
    print(f'{len(fail)} sentences in {fgen} differ from accepted!')
    print(' '.join(fail))
    sys.exit(1)
